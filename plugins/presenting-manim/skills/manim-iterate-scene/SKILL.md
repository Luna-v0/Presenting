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
4. Re-render **only the scene being fixed**, at low quality, after each
   meaningful fix — never the whole file or deck. Tell the user which scene
   class and file you touched and where the rendered output landed, so they
   can point at the exact part next time.
5. If even the single-scene render is slow, do not wait it out — find the cost
   and shrink it first. The usual culprit is an oversized `ImageMobject`
   source (anything over ~1600px on the long edge; deck assets are normalized
   at compile, but hand-written scenes load images directly), or caching
   disabled when it no longer needs to be.
6. If a legacy file fails but `scenes/title_card.py:TitleCard` still renders, treat the issue as scene-specific rather than an environment problem.

## Common Cases

- API drift in older scene code against the current Manim release
- Overlapping text or poor spacing
- Animations that are hard to read because too much changes at once
- Scene files with multiple classes where the intended target was ambiguous

## Guardrails

- Do not rewrite a scene from scratch unless the user asks or the existing version is irreparably broken.
- Preserve presentation intent even when modernizing old API usage.
