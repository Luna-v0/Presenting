from manim import (
    BLUE,
    DOWN,
    RED,
    UP,
    WHITE,
    YELLOW,
    Circle,
    Create,
    Graph,
    Scene,
    Text,
    Transform,
)

radius = 0.7


class ASTScene(Scene):
    def construct(self):
        # Define the graph nodes and edges (tree structure)
        nodes = ["E0", "E1", "T1", "plus", "T2"]
        edges = [("E0", "E1"), ("E0", "plus"), ("E0", "T2"), ("E1", "T1")]

        labels = {"E0": "E", "E1": "E", "T1": "int(1)", "plus": "+", "T2": "int(2)"}

        g = Graph(
            vertices=nodes,
            edges=edges,
            labels=labels,
            layout="tree",
            root_vertex="E0",
            vertex_config={
                "fill_color": BLUE,
                "E0": {"radius": radius},
                "E1": {"radius": radius},
                "T1": {"radius": radius},
                "plus": {"radius": radius},
                "T2": {"radius": radius},
            },
        )

        steps = [
            (0, "T1"),  # '1' → T1
            (0, "E1"),  # reduce T → E
            (1, "plus"),  # '+' → plus
            (2, "T2"),  # '2' → T2
            (2, "E0"),  # reduce E + T → E
        ]

        tokens = ["1", "+", "2"]
        input_text = Text(" ".join(tokens), font_size=36)
        input_text.to_edge(UP)

        self.play(Create(g))
        self.wait(1)
        for i, node_id in steps:
            # Highlight input token
            # Build colored string dynamically
            t2c = {
                tok: (YELLOW if idx == i else WHITE) for idx, tok in enumerate(tokens)
            }
            highlighted_input = Text(" ".join(tokens), font_size=36, t2c=t2c).move_to(
                input_text
            )
            self.play(Transform(input_text, highlighted_input))

            vertex_group = g.vertex_mobjects[node_id]
            circle = vertex_group[0]  # assuming Circle is first
            label = vertex_group[1]  # assuming Text is second

            # Highlight both properly
            self.play(
                circle.animate.set_fill(RED),  # Circle gets red
                label.animate.set_color(WHITE),  # Force text to stay visible
            )

            # Highlight graph node
            self.wait(0.3)

        self.wait()


# To run this, save it as a .py file (e.g., morph_animation.py)
# and run in your terminal: manim -pql morph_animation.py LatexToCodeMorph
