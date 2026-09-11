"""A backup slide: any other layout, marked as backup in the footer.

Demotion, not deletion, is how the review loop resolves "cool, but it doesn't
fit the story" (plan §6.3). That only works if a demoted beat still renders and
is still visibly *theirs*.

The mark is a word in the footer, not a graphic. An earlier version drew a
stripe down the left margin — the only place a mark could go without colliding
with a centered claim or a wide figure — and the first person to see it asked
why there was a bar on the slide. A mark nobody reads as a mark is just a stray
line. The footer already carries secondary status in muted, it never collides
with content, and it can hold the actual word.
"""

from __future__ import annotations

from .base import Content, Layout, register


@register
class Backup(Layout):
    name = "backup"
    chrome = "full"
    #: delegates, so it accepts whatever the wrapped layout accepts
    accepts = tuple(
        f.name for f in Content.__dataclass_fields__.values() if f.name != "extra"
    )
    requires = ()
    slots: dict = {}
    text_slots = ()

    def build(self, content: Content, *, target: str = "manim"):
        from .base import get_layout

        inner_name = content.backup_of or "claim-above-figure"
        inner = get_layout(inner_name)
        inner_content = Content(**{
            k: v for k, v in vars(content).items() if k != "backup_of"
        })
        built = inner.build(inner_content, target=target)
        built.layout = f"{self.name}({inner_name})"
        return built

    def active_slots(self, content: Content) -> set[str]:
        from .base import get_layout

        inner = get_layout(content.backup_of or "claim-above-figure")
        return inner.active_slots(content)
