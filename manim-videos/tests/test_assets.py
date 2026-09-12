"""Automatic photo downscaling — the guard against renders dominated by pixels.

An oversized image in assets/raw is downscaled in place on every compile, with
the original preserved in assets/raw/_full. Screenplay paths never change.
"""

from __future__ import annotations

from PIL import Image

from presenting_lib.assets import LONG_EDGE_LIMIT, normalize_images


def make_deck(tmp_path, name, size, mode="RGB"):
    raw = tmp_path / "assets" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    Image.new(mode, size, "red").save(raw / name)
    return raw / name


def test_oversized_image_downscaled_and_original_kept(tmp_path):
    path = make_deck(tmp_path, "photo.png", (3200, 1800))
    done = normalize_images(tmp_path)
    assert [d.name for d in done] == ["photo.png"]
    assert Image.open(path).size == (1600, 900)
    assert Image.open(tmp_path / "assets" / "raw" / "_full" / "photo.png").size == (3200, 1800)


def test_portrait_long_edge_is_the_height(tmp_path):
    path = make_deck(tmp_path, "tall.png", (1000, 3200))
    normalize_images(tmp_path)
    assert Image.open(path).size == (500, 1600)


def test_image_at_or_under_limit_untouched(tmp_path):
    path = make_deck(tmp_path, "ok.png", (LONG_EDGE_LIMIT, 900))
    before = path.read_bytes()
    assert normalize_images(tmp_path) == []
    assert path.read_bytes() == before
    assert not (tmp_path / "assets" / "raw" / "_full").exists()


def test_alpha_survives(tmp_path):
    path = make_deck(tmp_path, "trans.png", (3200, 1800), mode="RGBA")
    normalize_images(tmp_path)
    assert Image.open(path).mode == "RGBA"


def test_stale_backup_replaced_by_current_original(tmp_path):
    full = tmp_path / "assets" / "raw" / "_full"
    full.mkdir(parents=True)
    Image.new("RGB", (9999, 100), "blue").save(full / "photo.png")
    make_deck(tmp_path, "photo.png", (3200, 1800))
    normalize_images(tmp_path)
    assert Image.open(full / "photo.png").size == (3200, 1800)


def test_idempotent_and_missing_dir_safe(tmp_path):
    make_deck(tmp_path, "photo.png", (3200, 1800))
    normalize_images(tmp_path)
    assert normalize_images(tmp_path) == []
    assert normalize_images(tmp_path / "nowhere") == []
