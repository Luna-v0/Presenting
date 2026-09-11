# python-pptx recipes

Everything here uses the documented API on the stock **Blank** layout. No XML
surgery: cloned layouts open fine in python-pptx and fail in PowerPoint.

## Setup

```python
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

GROUND, INK, MUTED = "E4DCC6", "232A24", "5F5A4B"
STRUCTURE_FILL, STRUCTURE_STROKE = "CFC6AE", "8C8470"
GREEN_TINT, GREEN_MID, GREEN_DARK = "CCE0C6", "3D6349", "1E3527"
YELLOW_TINT, YELLOW_MID, YELLOW_DARK = "F6E5A5", "A87F20", "55400E"

SERIF, MONO = "Times New Roman", "Courier New"
W, H = 13.3333, 7.5

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
```

## A slide on the ground colour

```python
def blank(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])   # 6 == Blank
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(GROUND)
    return slide
```

## Text

```python
def text(slide, left, top, width, height, body, *, size=28, colour=INK,
         bold=False, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
         font=SERIF):
    box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = anchor
    for i, line in enumerate(str(body).split("\n")):
        para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        para.alignment = align
        run = para.add_run()
        run.text = line
        run.font.size, run.font.name, run.font.bold = Pt(size), font, bold
        run.font.color.rgb = RGBColor.from_string(colour)
    return box
```

`add_textbox` does not auto-shrink, so respect the character budgets.

## Title and rule

The rule tracks the title's width so the pair reads as one object. A fixed-width
rule under a short title looks like a stray line.

```python
def title_with_rule(slide, heading):
    box = text(slide, 0.7, 0.35, W - 1.4, 0.9, heading, size=52, bold=True)
    # rough width estimate: Times New Roman averages ~0.5 em per character
    est = min(len(heading) * 52 * 0.5 / 72, W - 1.4)
    rule_w = min(max(est + 0.4, 2.0), W - 1.4)
    rule = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches((W - rule_w) / 2), Inches(1.3),
        Inches(rule_w), Pt(2))
    rule.fill.solid()
    rule.fill.fore_color.rgb = RGBColor.from_string(GREEN_MID)
    rule.line.fill.background()
    rule.shadow.inherit = False
    return box
```

## Footer

```python
def footer(slide, section, number):
    text(slide, 0.5, H - 0.62, 6.0, 0.35, section, size=22, colour=MUTED,
         align=PP_ALIGN.LEFT)
    text(slide, W - 1.3, H - 0.62, 0.8, 0.35, str(number), size=22,
         colour=MUTED, align=PP_ALIGN.RIGHT)
```

## Pictures — contain, never stretch

```python
def picture(slide, path, left, top, width, height):
    pic = slide.shapes.add_picture(path, Inches(left), Inches(top))
    scale = min(Inches(width) / pic.width, Inches(height) / pic.height)
    pic.width, pic.height = int(pic.width * scale), int(pic.height * scale)
    pic.left = int(Inches(left) + (Inches(width) - pic.width) / 2)
    pic.top = int(Inches(top) + (Inches(height) - pic.height) / 2)
    return pic
```

## An accent box

The fill carries its own dark text. Never a light font on a dark fill.

```python
def accent_box(slide, left, top, width, height, body, accent="green"):
    tint, dark = ((GREEN_TINT, GREEN_DARK) if accent == "green"
                  else (YELLOW_TINT, YELLOW_DARK))
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(tint)
    shape.line.color.rgb = RGBColor.from_string(
        GREEN_MID if accent == "green" else YELLOW_MID)
    shape.shadow.inherit = False
    frame = shape.text_frame
    frame.word_wrap = True
    run = frame.paragraphs[0].add_run()
    run.text = body
    run.font.size, run.font.name = Pt(28), SERIF
    run.font.color.rgb = RGBColor.from_string(dark)
    return shape
```

## Diagrams with native shapes

For a slides deck, drawing boxes and connectors with pptx shapes beats
embedding an image: they stay editable in PowerPoint afterwards.

```python
def node(slide, left, top, width, height, label, accent=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    fill, line, ink = STRUCTURE_FILL, STRUCTURE_STROKE, INK
    if accent == "green":
        fill, line, ink = GREEN_TINT, GREEN_MID, GREEN_DARK
    elif accent == "yellow":
        fill, line, ink = YELLOW_TINT, YELLOW_MID, YELLOW_DARK
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(fill)
    shape.line.color.rgb = RGBColor.from_string(line)
    shape.shadow.inherit = False
    run = shape.text_frame.paragraphs[0].add_run()
    run.text = label
    run.font.size, run.font.name = Pt(28), SERIF
    run.font.color.rgb = RGBColor.from_string(ink)
    return shape
```

Connect them with `add_connector` and `begin_connect` / `end_connect` so the
arrows stay attached when the user moves a box:

```python
from pptx.enum.shapes import MSO_CONNECTOR

conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, 0, 0, 0, 0)
conn.begin_connect(a, 2)     # 2 == bottom of shape a
conn.end_connect(b, 0)       # 0 == top of shape b
conn.line.color.rgb = RGBColor.from_string(STRUCTURE_STROKE)
```

`add_connector` gives a plain line — python-pptx exposes no arrowhead property.
Either accept that (with a left-to-right or top-to-bottom layout the direction
usually reads fine) or place an `MSO_SHAPE.RIGHT_ARROW` / `DOWN_ARROW` between
the boxes. Do not reach into the line XML for it; the value is not worth
reintroducing the habit that broke the template.

An arrow or leader must stop at the **edge** of what it points at, never run
into the middle of the label.

## Speaker notes

```python
slide.notes_slide.notes_text_frame.text = notes
```

Directives, from the claim and the note. Never sentences to read aloud, and
never the cue.

## Save and check

```python
prs.save("deck.pptx")

again = Presentation("deck.pptx")
print(len(again.slides), "slides")
```

Reopening proves it parses, nothing more. Ask the user to open it once in
PowerPoint or Google Slides.
