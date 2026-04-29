from __future__ import annotations

import ast
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

PLUGIN_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
MANIM_PROJECT_ROOT = REPO_ROOT / "manim-videos"
IGNORED_DIRS = {".venv", "__pycache__", "media"}
QUALITY_FLAGS = {
    "low": "-ql",
    "medium": "-qm",
    "high": "-qh",
    "production": "-qp",
    "4k": "-qk",
}
SCENE_BASE_NAMES = {
    "MovingCameraScene",
    "Scene",
    "ThreeDScene",
    "ZoomedScene",
}

mcp = FastMCP("Presenting Manim", json_response=True)


def _project_ready() -> None:
    if not MANIM_PROJECT_ROOT.exists():
        raise ToolError(f"Manim project root not found: {MANIM_PROJECT_ROOT}")


def _is_inside(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_project_path(path: str) -> Path:
    _project_ready()
    candidate = (MANIM_PROJECT_ROOT / path).resolve()
    if not _is_inside(MANIM_PROJECT_ROOT.resolve(), candidate):
        raise ToolError(f"Path escapes the Manim project: {path}")
    if not candidate.exists():
        raise ToolError(f"Path does not exist: {path}")
    return candidate


def _iter_python_files() -> list[Path]:
    _project_ready()
    files: list[Path] = []
    for path in MANIM_PROJECT_ROOT.rglob("*.py"):
        relative_parts = set(path.relative_to(MANIM_PROJECT_ROOT).parts)
        if relative_parts & IGNORED_DIRS:
            continue
        files.append(path)
    return sorted(files)


def _scene_base_name(base: ast.expr) -> str | None:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def _extract_scene_classes(path: Path) -> list[dict[str, Any]]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ToolError(f"Failed to read {path}: {exc}") from exc

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise ToolError(f"Failed to parse {path}: {exc}") from exc

    classes: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        base_names = [name for base in node.bases if (name := _scene_base_name(base))]
        if any(name in SCENE_BASE_NAMES or name.endswith("Scene") for name in base_names):
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "bases": base_names,
                }
            )
    return classes


def _trim_text(text: str, max_lines: int = 80) -> str:
    lines = text.strip().splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    kept = lines[: max_lines - 1]
    kept.append(f"... ({len(lines) - max_lines + 1} more lines)")
    return "\n".join(kept)


def _artifact_paths(output: str) -> list[str]:
    matches = re.findall(r"['\"](/[^'\"]+)['\"]", output)
    unique_paths: list[str] = []
    for match in matches:
        normalized = "".join(match.split())
        if normalized not in unique_paths:
            unique_paths.append(normalized)
    return unique_paths


def _run(command: list[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("UV_LINK_MODE", "copy")
    env.pop("VIRTUAL_ENV", None)
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def _scene_choices_for_file(target: Path) -> list[dict[str, Any]]:
    classes = _extract_scene_classes(target)
    if not classes:
        raise ToolError(
            f"No Manim Scene subclasses found in {target.relative_to(MANIM_PROJECT_ROOT)}"
        )
    return classes


@mcp.tool()
def project_summary() -> dict[str, Any]:
    """Describe the active Manim project and current scene inventory."""
    _project_ready()
    scene_files = []
    for path in _iter_python_files():
        scenes = _extract_scene_classes(path)
        if not scenes:
            continue
        scene_files.append(
            {
                "file": path.relative_to(MANIM_PROJECT_ROOT).as_posix(),
                "scenes": scenes,
            }
        )

    return {
        "repo_root": str(REPO_ROOT),
        "manim_project_root": str(MANIM_PROJECT_ROOT),
        "preferred_scene_dir": "manim-videos/scenes",
        "legacy_motion_canvas_dir": "old/motion-canvas",
        "scene_file_count": len(scene_files),
        "scene_files": scene_files,
    }


@mcp.tool()
def list_scenes(pattern: str | None = None) -> list[dict[str, Any]]:
    """List Manim scene classes discovered under manim-videos."""
    lowered = pattern.lower() if pattern else None
    results: list[dict[str, Any]] = []

    for path in _iter_python_files():
        scenes = _extract_scene_classes(path)
        if not scenes:
            continue

        relative = path.relative_to(MANIM_PROJECT_ROOT).as_posix()
        if lowered:
            haystacks = [relative.lower(), *(scene["name"].lower() for scene in scenes)]
            if not any(lowered in item for item in haystacks):
                continue

        results.append({"file": relative, "scenes": scenes})

    return results


@mcp.tool()
def read_source(path: str, start_line: int = 1, max_lines: int = 200) -> dict[str, Any]:
    """Read a slice of a Manim source file relative to manim-videos."""
    if start_line < 1:
        raise ToolError("start_line must be >= 1")
    if max_lines < 1 or max_lines > 400:
        raise ToolError("max_lines must be between 1 and 400")

    target = _resolve_project_path(path)
    if target.suffix != ".py":
        raise ToolError("read_source only supports Python files")

    lines = target.read_text(encoding="utf-8").splitlines()
    start_index = start_line - 1
    end_index = start_index + max_lines
    excerpt = lines[start_index:end_index]

    return {
        "path": target.relative_to(MANIM_PROJECT_ROOT).as_posix(),
        "start_line": start_line,
        "end_line": start_line + len(excerpt) - 1,
        "contents": "\n".join(excerpt),
    }


@mcp.tool()
def render_scene(
    path: str,
    scene_name: str | None = None,
    quality: str = "low",
    save_last_frame: bool = False,
    format: str = "mp4",
    output_name: str | None = None,
) -> dict[str, Any]:
    """Render a Manim scene from manim-videos using uv."""
    quality_flag = QUALITY_FLAGS.get(quality)
    if quality_flag is None:
        raise ToolError(f"Unsupported quality: {quality}")

    if format not in {"mp4", "gif", "webm"}:
        raise ToolError("format must be one of: mp4, gif, webm")

    target = _resolve_project_path(path)
    if target.suffix != ".py":
        raise ToolError("render_scene expects a Python scene file")

    scene_choices = _scene_choices_for_file(target)
    resolved_scene_name = scene_name
    if resolved_scene_name is None:
        if len(scene_choices) != 1:
            available = ", ".join(scene["name"] for scene in scene_choices)
            raise ToolError(
                f"Multiple scene classes found in {path}. Pick one of: {available}"
            )
        resolved_scene_name = scene_choices[0]["name"]

    command = [
        "uv",
        "run",
        "--project",
        str(MANIM_PROJECT_ROOT),
        "manim",
        quality_flag,
    ]
    if save_last_frame:
        command.append("-s")
    if format != "mp4":
        command.extend(["--format", format])
    if output_name:
        command.extend(["--output_file", output_name])
    command.extend(
        [
            target.relative_to(MANIM_PROJECT_ROOT).as_posix(),
            resolved_scene_name,
        ]
    )

    completed = _run(command, cwd=MANIM_PROJECT_ROOT)
    combined_output = "\n".join(
        part for part in [completed.stdout.strip(), completed.stderr.strip()] if part
    )
    artifacts = _artifact_paths(combined_output)

    if completed.returncode != 0:
        raise ToolError(
            "\n".join(
                [
                    f"Render failed for {path}:{resolved_scene_name}",
                    _trim_text(combined_output or "No process output captured."),
                ]
            )
        )

    return {
        "success": True,
        "path": target.relative_to(MANIM_PROJECT_ROOT).as_posix(),
        "scene_name": resolved_scene_name,
        "quality": quality,
        "format": format,
        "save_last_frame": save_last_frame,
        "output_name": output_name,
        "command": command,
        "artifacts": artifacts,
        "log_tail": _trim_text(combined_output),
    }


@mcp.tool()
def list_recent_renders(limit: int = 10) -> list[dict[str, Any]]:
    """List the most recently modified rendered assets under manim-videos/media."""
    if limit < 1 or limit > 50:
        raise ToolError("limit must be between 1 and 50")

    media_root = MANIM_PROJECT_ROOT / "media"
    if not media_root.exists():
        return []

    candidates = []
    for path in media_root.rglob("*"):
        if path.suffix.lower() not in {".gif", ".mp4", ".png", ".webm"}:
            continue
        stat = path.stat()
        candidates.append(
            {
                "path": path.relative_to(MANIM_PROJECT_ROOT).as_posix(),
                "modified_unix": stat.st_mtime,
                "size_bytes": stat.st_size,
            }
        )

    candidates.sort(key=lambda item: item["modified_unix"], reverse=True)
    return candidates[:limit]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
