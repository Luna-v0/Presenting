---
name: render-manim
description: Use to compile a screenplay into manim-slides scenes and render, present, or export them — "render the deck", "let me see it", "export the HTML", "present it". Also the way to produce the self-contained HTML the user watches back, which is how judgement gets into the revision loop. Load manim-use first for the MCP render tooling.
---

# Render (manim)

Load [manim-use](../manim-use/SKILL.md) first.

Screenplay → scenes via `presenting_lib.compile` → `manim-slides`.

## Compile

```bash
cd manim-videos
uv run python -c "
from presenting_lib.compile import compile_deck
path, findings = compile_deck('decks/<slug>/screenplay.md',
                              'decks/<slug>/out/<slug>_scenes.py')
print(path)
[print(f) for f in findings]
"
```

The generated module is **thin on purpose**: it declares which beats belong to
which scene and nothing else. All positioning lives in `presenting_lib/layouts`.
If you find yourself wanting to hand-edit the generated file, the change belongs
in the screenplay or the library — the file is overwritten on every compile, and
it carries a header saying so.

Compilation refuses to proceed on errors. The common ones:

- `SlotOverflow` — text does not fit at or above the legibility floor. Cut it in
  the screenplay. The message names the slot, the length and the budget.
- accent used while `accents.*.meaning` is unassigned — decide the meanings, or
  drop the accent.
- a discussion or activity beat the genre does not allow.

## Render at 2K. Always.

```bash
cd manim-videos
uv run manim-slides render decks/<slug>/out/<slug>_scenes.py <Scene> ... -qp
```

`-qp` is 2560x1440 at 60fps, and it is what every deck ships at — the generated
module's header says so. A deck gets shown on a projector or a large display and
`-ql` text is visibly soft there, so a low-quality render is never the thing you
hand over, however convenient it was to make.

Other flags exist — `-ql` 480p15, `-qh` 1080p60, `-qk` 4K — and `-ql` is
legitimate for one thing only: a fast structural check while a screenplay is
still moving, where you want to know whether a layout overflows rather than what
it looks like. The moment you are showing the user anything, or exporting,
re-render at `-qp`.

`--disable_caching` is needed after any library change; per-scene caching makes
reruns cheap otherwise.

Clear the media tree once after a library change, then drop the flag. Keeping it
on breaks chunked rendering: a scene's config file is only written when the whole
scene finishes, so if you are rendering under a wall-clock limit and a single 2K
scene needs longer than one chunk, `--disable_caching` throws away its partial
work and that scene can never complete no matter how many chunks you run. With
caching on, each chunk resumes mid-scene.

`-qh` does not work: manim-slides' own parser takes the `h` as its `-h` help
flag, so it prints usage and **exits 0** — every scene reports success and nothing
is written. Use `--quality h`. `-ql`, `-qm` and `-qp` are unaffected.

**Photos are downscaled automatically at compile.** manim resamples every source
pixel of an `ImageMobject` on every frame and does not care that the image is drawn
at a fraction of its size. A 2551px-wide PNG inside a `FadeIn` measured at 8.8
seconds *per frame*; the same photo at 1600px ran at 18.8 frames per second — about
170x. So `compile_deck` (and `scripts/preflight.py`) run
`presenting_lib.assets.normalize_images` first: any image in `assets/raw/` whose
long edge exceeds 1600px is downscaled in place, with the untouched original moved
to `assets/raw/_full/`. Screenplay paths keep working; each resize is reported as a
`note` finding. Drop full-resolution photos straight into `assets/raw/` — the
compile handles the rest. Still size a render *estimate* by its image pixels, not
its beat count.

At `-qp` the reversed-animation pass costs about 25-30s *per slide*, on top of
the animation render — a seven-slide scene spends three to four minutes in
concatenation alone. Budget for it rather than concluding the render has hung.

**Budget the time.** 2K at 60fps is ~36x the pixel throughput of `-ql`, and a
full uncached two-deck render measured at a few hours on this machine. Start it
in the background, tell the user roughly how long it will be, and do something
else — do not sit and poll it, and do not quietly downgrade to `-ql` because it
is taking a while. If you need a fast look at a layout mid-iteration, render the
*one scene* you changed at `-ql`, not the deck.

## Fixing one section: render only that section

When the user is iterating on a specific section or animation, never re-render
the deck. The compiler emits **one scene class per section** — the names are in
the generated module's header (`decks/<slug>/out/<slug>_scenes.py`), of the form
`<Slug>_<NN>_<SectionName>`. Render exactly the scene(s) holding the beats being
worked on:

```bash
uv run manim-slides render decks/<slug>/out/<slug>_scenes.py <TheOneScene> -ql
uv run manim-slides present <TheOneScene>
```

Then **tell the user where the part lives**: which scene class, which beat ids
it contains, and the path to the rendered output — so their next instruction
can name the beat instead of describing the slide.

**If even the focused render's ETA is too long, optimize the cost instead of
waiting it out.** The usual culprit is an image (check `assets/raw/` for
anything the normalizer missed — GIFs, videos, `assets/built/`), a `raw` beat
doing heavy work, or `--disable_caching` left on from an earlier library
change. Find which it is, shrink it, then render. A long wait accepted silently
becomes the cost of every iteration after it.

## Present

```bash
uv run manim-slides present <Scene> ...
```

`→`/`Space` next, `←` previous, `R` replay, `F` fullscreen, `Esc` quit.

## Export the HTML — this one is load-bearing

```bash
uv run manim-slides convert --one-file --offline --use-template identity/out/revealjs.html \\
    -ctransition="'fade'" -cbackground_transition="'fade'" \\
    -ctransition_speed="'fast'" \\
    <Scene> ... <slug>.html
```

`fade` replaces reveal.js's default hard cut between slides, and `fast` keeps it
short: during a crossfade both videos are on screen and the incoming one is
already playing, so a slow fade lets the audience glimpse the next animation
starting before the current slide has cleared. **Keep the inner
quotes**: manim-slides pastes the value into the reveal.js config verbatim, so
`-ctransition=fade` emits a bare JavaScript identifier, `Reveal.initialize`
throws, and the deck does not open at all.

One file, no sidecar directory — `--one-file --offline` embeds the videos and
pulls in the remote assets, so it survives being copied to a laptop with no
network. Open it in any browser; same keys, no Python on the host. **This is how the deck
gets watched back, and watching it back is how the user forms judgement about
whether the talk works.** Produce it after every meaningful render, and say
where it is. Then hand off to `deck-review`.

## Scene splits

The compiler makes one scene per section, and splits further at:

- a **raw** beat — it gets its own scene class, either aliasing an existing
  scene (`raw.scene: module:Class`) or carrying inline code;
- a **`scene_type: 3d`** boundary — manim-beamer's `MovingCameraScene` runner
  cannot host a `ThreeDScene`, which `ft_v2` already worked around by hand.

Scene names appear in the generated header. They change if sections are renamed,
so re-read the header rather than reusing an old command line.

## Known-good smoke tests

If something looks broken at the environment level rather than the deck level:

```bash
uv run manim scenes/title_card.py TitleCard -ql
uv run manim-slides render scenes/beamer_demo.py \
    BeamerDemoPart1 BowlDescent3D BeamerDemoPart2 -ql
```

Those are unrelated to the library. If they fail, the problem is the install.
