---
name: manim-iterate-scene
description: Use when the user wants to debug, refine, or polish an existing Manim scene in this repository. This includes render failures, timing issues, layout fixes, and adapting older scene code to the currently installed Manim version.
---

# Iterate Manim Scene

Load [manim-use](../manim-use/SKILL.md) first.

## Workflow

1. Identify the target scene with `list_scenes`.
2. Inspect the relevant file with `read_source`.
3. Make the smallest change that addresses the current failure or visual issue.
4. Re-render at low quality after each meaningful fix.
5. If a legacy file fails but `scenes/title_card.py:TitleCard` still renders, treat the issue as scene-specific rather than an environment problem.

## Common Cases

- API drift in older scene code against the current Manim release
- Overlapping text or poor spacing
- Animations that are hard to read because too much changes at once
- Scene files with multiple classes where the intended target was ambiguous

## Guardrails

- Do not rewrite a scene from scratch unless the user asks or the existing version is irreparably broken.
- Preserve presentation intent even when modernizing old API usage.
