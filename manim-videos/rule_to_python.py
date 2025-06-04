from manim import DOWN, ORIGIN, UP, Code, MathTex, ReplacementTransform, Scene


class TexToPly(Scene):
    def construct(self):
        self.camera.background_color = "#ffffff"  # Set background color to white
        # 1. Create the LaTeX Mobject
        # You can use any LaTeX string here
        latex_string = r"S \longrightarrow digit + S \\ S \longrightarrow digit"
        latex_mobject = MathTex(latex_string, font_size=60, color="#000000")

        code_mobject = Code(
            "src-examples/test.py",
            background="rectangle",
            formatter_style="pastie",  # Light syntax highlighting style
            background_config={"stroke_color": "#000000", "fill_color": "#ffffff"},
            add_line_numbers=False,
            tab_width=4,
            paragraph_config={"font": "Monospace", "color": "#000000"},
        )
        self.play(latex_mobject.animate.move_to(ORIGIN))
        self.wait(0.5)

        # Ensure the code object is also ready at the transformation target
        code_mobject.move_to(ORIGIN)

        self.play(ReplacementTransform(latex_mobject, code_mobject))
        self.wait(3)


# To run this, save it as a .py file (e.g., morph_animation.py)
# and run in your terminal: manim -pql morph_animation.py LatexToCodeMorph
