---
name: manim-create-scene
description: Use when the user wants a new Manim scene, a new presentation segment, or a storyboard turned into animation code in this repository. Create or extend scenes under `manim-videos/scenes/` and validate them through the repo-local Manim MCP server.
---

# Create Manim Scene

Load [manim-use](../manim-use/SKILL.md) first.

## Workflow

1. Put new scene files under `manim-videos/scenes/` unless the user names another target.
2. Keep scene class names explicit and stable. One primary scene per file is preferred for easier rendering.
3. Start with a minimal renderable version before adding polish.
4. Render drafts at low quality after meaningful edits.
5. Only move to higher quality once the structure, pacing, and layout are stable.

## Implementation Notes

- Prefer simple Manim primitives and clear sequencing over dense one-shot transforms.
- Use comments sparingly and only where animation intent would otherwise be hard to infer.
- Keep helper functions in the same file unless they are reused across scenes.
- Reuse assets already in the repo when possible.

## Validation

- First pass: `render_scene` with `quality="low"`
- Follow-up: inspect the output path from the tool result and iterate
- Only use a higher render quality when the user asks or when the scene is close to final
