"""Re-download the Rio data used by the geo-folium deck and its notebook.

The CSVs need only the standard library; simplifying the bairro polygons needs
shapely >= 2.1. Run it in a throwaway environment:

    uv run --no-project --with shapely python fetch_data.py   # writes four files here

Every download is checked before it touches the file it replaces: row counts
within sane bounds, required columns filled, school coordinates inside Rio's
bounding box, polygons valid. A file is written to a temporary name and swapped
in only when its check passes, so a short or partial response from the server
leaves the previous good file in place. The script exits 1 if any file failed.

Every source is the Prefeitura do Rio's public ArcGIS server (pgeo3.rio.rj.gov.br),
which is what the DATA.RIO portal (https://www.data.rio) serves its geo datasets
from. No account, no key. All four datasets are listed on DATA.RIO under
CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Attribution:
"Prefeitura da Cidade do Rio de Janeiro / Instituto Pereira Passos (IPP), DATA.RIO".

Files and sources
-----------------
bairros.geojson
    Limite de Bairros (167 neighbourhood polygons), IPP.
    Dataset: https://www.data.rio/datasets/PCRJ::limite-de-bairros/about
    Service: https://pgeo3.rio.rj.gov.br/arcgis/rest/services/Cartografia/Limites_administrativos/FeatureServer/4
    Licence: CC BY 4.0.
    Downloaded at full resolution (~4 MB) and simplified here to ~0.9 MB with
    shapely.coverage_simplify (tolerance 0.00005 deg, about 5 m; shared borders
    stay shared) and set_precision (grid 0.00001 deg, about 1 m), which keeps
    every polygon valid. Simplifying on the server instead (maxAllowableOffset /
    geometryPrecision) leaves self-intersections in Caju, Catumbi and Rio
    Comprido. Fine for teaching and for embedding in a folium map; not for
    cadastral work.
    Kept: codbairro, nome, regiao_adm (trailing spaces stripped), rp.
    codbairro is published as a zero-padded string ("001"); it is written as an
    integer here and in populacao_bairros.csv, so the two merge without a dtype
    argument.

escolas.csv
    Escolas Municipais (~1,590 units run by the Secretaria Municipal de
    Educação: schools, crèches, EDIs, CIEPs...), SME and IPP.
    Dataset: https://www.data.rio/ (search "Escolas Municipais"; item 0a220ea7972449e39a28210dd317f636)
    Service: https://pgeo3.rio.rj.gov.br/arcgis/rest/services/Educacao/SME/FeatureServer/1
    Licence: CC BY 4.0.
    Columns as published: designacao, denominacao, tipo, cre, latitude, longitude.
    `cre` is written as an integer (the service stores it as a float).

cre.csv
    Limites CRE: the 11 Coordenadorias Regionais de Educação, attributes only.
    Dataset: https://www.data.rio/ (search "Limites CRE"; item fbfcbfae92654e248bdf1452cf260626)
    Service: https://pgeo3.rio.rj.gov.br/arcgis/rest/services/Educacao/SME/FeatureServer/0
    Licence: CC BY 4.0.
    Columns: cre (int, joins escolas.cre), nome, area_km2 (the service's
    Shape__Area, computed in EPSG:31983 / UTM 23S, so m², divided by 1e6).

populacao_bairros.csv
    Censo 2022: População e domicílios por bairros (dados preliminares), IPP
    from IBGE Censo 2022.
    Dataset: https://www.data.rio/ (search "Censo 2022 bairros"; item fd354740f1934bf5bf8e9b0e2b509aa9)
    Service: https://pgeo3.rio.rj.gov.br/arcgis/rest/services/Censo/Limites_administrativos_Censo_2022/MapServer/2
    Licence: CC BY 4.0.
    Columns: codbairro, nome, populacao_2022. 165 bairros: two bairros in
    bairros.geojson (166 Argentino, 167 Ingleses) have no row here, so a left
    merge on codbairro leaves them NaN. Merge on codbairro, not on nome:
    São Cristóvão is "Imperial de São Cristóvão" in the boundary layer.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCGIS = "https://pgeo3.rio.rj.gov.br/arcgis/rest/services"

BAIRROS = f"{ARCGIS}/Cartografia/Limites_administrativos/FeatureServer/4"
ESCOLAS = f"{ARCGIS}/Educacao/SME/FeatureServer/1"
CRE = f"{ARCGIS}/Educacao/SME/FeatureServer/0"
POPULACAO = f"{ARCGIS}/Censo/Limites_administrativos_Censo_2022/MapServer/2"

#: Most pages a paginated query may take. The largest layer here (the schools)
#: fits in one page of 2,000 records; a query still asking for more after this
#: many pages is a misbehaving server, not data.
MAX_PAGES = 20
#: The municipality's bounding box with a margin, in degrees.
RIO_LAT = (-23.2, -22.7)
RIO_LON = (-43.9, -43.0)


class BadDownload(RuntimeError):
    """A response that would have replaced a good file with a bad one."""


def query(layer: str, **params) -> dict:
    """One ArcGIS REST query; follows pagination for JSON results."""
    base = {"where": "1=1", "f": "json"}
    base.update(params)
    features: list = []
    for _ in range(MAX_PAGES):
        page = dict(base, resultOffset=len(features)) if base["f"] == "json" else base
        url = f"{layer}/query?{urllib.parse.urlencode(page)}"
        request = urllib.request.Request(url, headers={"User-Agent": "geo-folium-deck/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
        if "error" in data:
            raise BadDownload(f"{layer}: {data['error']}")
        if base["f"] != "json":
            if data.get("exceededTransferLimit") or (isinstance(data.get("properties"), dict) and data["properties"].get("exceededTransferLimit")):
                raise BadDownload(f"{layer}: transfer limit exceeded on geojson")
            return data
        features += data.get("features", [])
        if not data.get("exceededTransferLimit"):
            return {"features": features}
    raise BadDownload(f"{layer}: still paginating after {MAX_PAGES} pages "
                      f"({len(features)} records); refusing to trust it")


def check_rows(name: str, rows: list[dict], *, columns: list[str],
               count: tuple[int, int]) -> None:
    """Row count within bounds and every required column filled, or BadDownload."""
    low, high = count
    if not low <= len(rows) <= high:
        raise BadDownload(f"{name}: {len(rows)} rows, expected {low} to {high}")
    for column in columns:
        empty = sum(1 for row in rows if row.get(column) in (None, ""))
        if empty:
            raise BadDownload(f"{name}: {empty} rows have no {column}")


def replace_atomically(path: Path, write) -> None:
    """Write through a temporary file next to `path`, then swap it in."""
    tmp = path.with_name(path.name + ".tmp")
    try:
        write(tmp)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    def write(tmp: Path) -> None:
        with tmp.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({c: row[c] for c in columns})

    replace_atomically(path, write)
    print(f"{path.name}: {len(rows)} rows")


def fetch_bairros() -> None:
    try:
        import shapely
        from shapely.geometry import mapping, shape
    except ImportError as exc:                       # pragma: no cover
        raise SystemExit("bairros.geojson needs shapely >= 2.1: "
                         "uv run --no-project --with shapely python fetch_data.py") from exc

    data = query(BAIRROS, outFields="codbairro,nome,regiao_adm,rp", outSR=4326,
                 orderByFields="codbairro", f="geojson")
    check_rows("bairros", [f["properties"] for f in data.get("features", [])],
               columns=["codbairro", "nome"], count=(150, 200))
    raw = [shape(f["geometry"]) for f in data["features"]]
    simplified = shapely.coverage_simplify(raw, tolerance=0.00005)
    snapped = shapely.set_precision(simplified, grid_size=0.00001)
    if not (shapely.is_valid(snapped).all() and not shapely.is_empty(snapped).any()):
        raise BadDownload("bairros: simplified polygons are invalid or empty")

    def rounded(coords):
        if isinstance(coords[0], (int, float)):
            return [round(c, 5) for c in coords]
        return [rounded(c) for c in coords]

    features = []
    for feature, geometry in zip(data["features"], snapped):
        props = feature["properties"]
        geo = mapping(geometry)
        features.append({
            "type": "Feature",
            "properties": {
                "codbairro": int(props["codbairro"]),
                "nome": props["nome"],
                "regiao_adm": (props["regiao_adm"] or "").strip(),
                "rp": props["rp"],
            },
            "geometry": {"type": geo["type"], "coordinates": rounded(geo["coordinates"])},
        })
    out = {"type": "FeatureCollection", "features": features}
    path = HERE / "bairros.geojson"
    replace_atomically(path, lambda tmp: tmp.write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"))
    print(f"{path.name}: {len(features)} polygons, {path.stat().st_size // 1000} KB")


def fetch_escolas() -> None:
    data = query(ESCOLAS, outFields="designacao,denominacao,tipo,cre,latitude,longitude",
                 returnGeometry="false", orderByFields="designacao")
    rows = [dict(feature["attributes"]) for feature in data["features"]]
    check_rows("escolas", rows, count=(1000, 3000),
               columns=["designacao", "denominacao", "tipo", "cre", "latitude", "longitude"])
    outside = [row["designacao"] for row in rows
               if not (RIO_LAT[0] <= row["latitude"] <= RIO_LAT[1]
                       and RIO_LON[0] <= row["longitude"] <= RIO_LON[1])]
    if outside:
        raise BadDownload(f"escolas: {len(outside)} schools outside Rio's bounding box, "
                          f"e.g. designacao {outside[:3]}")
    for row in rows:
        row["cre"] = int(row["cre"])
        row["denominacao"] = row["denominacao"].strip()
    write_csv(HERE / "escolas.csv", rows,
              ["designacao", "denominacao", "tipo", "cre", "latitude", "longitude"])


def fetch_cre() -> None:
    data = query(CRE, outFields="codigo,nome,Shape__Area", returnGeometry="false")
    attributes = [f["attributes"] for f in data["features"]]
    # Exactly the 11 regions: a partial page of a list this short would still
    # look plausible against looser bounds. A real 12th CRE fails loudly here.
    check_rows("cre", attributes, columns=["codigo", "nome", "Shape__Area"], count=(11, 11))
    rows = [{"cre": int(a["codigo"]), "nome": a["nome"],
             "area_km2": round(a["Shape__Area"] / 1e6, 2)} for a in attributes]
    if any(row["area_km2"] <= 0 for row in rows):
        raise BadDownload("cre: a region with no area")
    rows.sort(key=lambda r: r["cre"])
    write_csv(HERE / "cre.csv", rows, ["cre", "nome", "area_km2"])


def fetch_populacao() -> None:
    data = query(POPULACAO, outFields="codbairro,nome,Total_de_pessoas_2022",
                 returnGeometry="false", orderByFields="codbairro")
    attributes = [f["attributes"] for f in data["features"]]
    check_rows("populacao", attributes, count=(150, 200),
               columns=["codbairro", "nome", "Total_de_pessoas_2022"])
    rows = [{"codbairro": int(a["codbairro"]), "nome": a["nome"],
             "populacao_2022": a["Total_de_pessoas_2022"]} for a in attributes]
    total = sum(row["populacao_2022"] for row in rows)
    if not 5_000_000 <= total <= 8_000_000:
        raise BadDownload(f"populacao: {total:,} residents in total, not a whole city")
    write_csv(HERE / "populacao_bairros.csv", rows, ["codbairro", "nome", "populacao_2022"])


if __name__ == "__main__":
    failed = []
    for fetch in (fetch_bairros, fetch_escolas, fetch_cre, fetch_populacao):
        try:
            fetch()
        except (BadDownload, OSError) as error:
            failed.append(fetch.__name__)
            print(f"{fetch.__name__}: {error}; kept the previous file", file=sys.stderr)
    sys.exit(1 if failed else 0)
