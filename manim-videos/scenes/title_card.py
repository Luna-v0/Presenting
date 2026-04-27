from manim import DOWN, FadeIn, FadeOut, Scene, Text, VGroup


class TitleCard(Scene):
    def construct(self):
        title = Text("Presenting with Manim", font_size=60)
        subtitle = Text("Repo-local MCP plus uv workflow", font_size=30)
        subtitle.next_to(title, DOWN, buff=0.35)

        stack = VGroup(title, subtitle)

        self.play(FadeIn(stack, shift=DOWN * 0.3))
        self.wait(1.0)
        self.play(FadeOut(stack))
