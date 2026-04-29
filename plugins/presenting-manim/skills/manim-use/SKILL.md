---
name: manim-use
description: Use when the user wants to inspect, render, or reason about Manim scenes in this repository. Load this before using the repo-local `presenting-manim` MCP tools so the workflow stays consistent with the current project layout and render strategy.
---

# Manim Use

This repo uses Manim as the active presentation workflow.

## Scope

- Active project: `manim-videos/`
- Preferred scene location for new work: `manim-videos/scenes/`
- Archived Motion Canvas work: `old/motion-canvas/`

Do not edit `old/motion-canvas/` unless the user explicitly asks.

## Required Workflow

1. Start with `project_summary` to confirm the active Manim project root and recent render outputs.
2. Use `list_scenes` before rendering unless the target file and scene class are already explicit.
3. Prefer low-quality renders first with `render_scene(..., quality="low")`.
4. Use `read_source` when you need to inspect a scene before editing or debugging.
5. Use `list_recent_renders` after a render if you need the newest artifacts quickly.

## Guardrails

- Keep edits inside `manim-videos/` unless the task is specifically about the plugin or skills.
- Treat `main.py` and `rule_to_python.py` as older experiments. If a render failure only affects those files, do not assume the environment is broken.
- When validating the setup itself, prefer `scenes/title_card.py:TitleCard` because it is meant to be a known-good smoke test.
