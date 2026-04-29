import {
  makeScene2D,
  Code,
  Txt,
  remove,
  insert,
  LezerHighlighter,
  View2D,
  vector2Signal,
  word,
} from "@motion-canvas/2d";
import {
  createRef,
  waitFor,
  loop,
  cancel,
  useRandom,
} from "@motion-canvas/core";
import { HighlightStyle } from "@codemirror/language";
import { parser } from "@lezer/python";
import { tags as t } from "@lezer/highlight";

const MyStyle = HighlightStyle.define([
  //change the  [ ] colors and the classNames to a darker color
  { tag: t.keyword, color: "#0000aa" },
  { tag: t.string, color: "#aa5500" },
  { tag: t.number, color: "#008800" },
  { tag: t.comment, color: "#888888", fontStyle: "italic" },
  { tag: t.function(t.variableName), color: "#0055aa" },
  { tag: t.className, color: "#2c2c8c" }, // Darker tone
  { tag: t.list, color: "#2f4f4f" }, // Dark slate gray
  { tag: t.variableName, color: "#333333" },
  { tag: t.operator, color: "#000000" },
  { tag: t.bracket, color: "#000000" },
  { tag: t.meta, color: "#555555" },
]);

Code.defaultHighlighter = new LezerHighlighter(parser, MyStyle);

// hello world?

export default function* rewardCode(view: View2D) {
  const code = createRef<Code>();
  const random = useRandom();

  function naturalPause(i: number): number {
    // Suaviza a digitação com uma curva senoidal leve
    return 0.02 + 0.02 * Math.sin(i * 0.7 + random.nextFloat(0, Math.PI));
  }

  view.fill("#fff");

  view.add(
    <Code ref={code} code="" fontSize={30} y={0} width={800} fill="#000" />,
  );
  // Typing function (word-by-word)
  function* typeCodeLine(codeLine: string) {
    let current_line = 0;
    let current_column = 0;

    // find max line in codeLine
    let max_size = -1;
    const lines = codeLine.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.length > max_size) {
        max_size = line.length;
      }
    }

    let result = "";
    for (let i = 0; i < max_size + 10; i++) {
      result += " ";
    }
    yield* code().code.insert([0, 0], result, 0);
    for (let i = 0; i < codeLine.length; i++) {
      const char = codeLine[i];

      if (char === "\n") {
        yield* code().code.remove(
          [
            [current_line, current_column],
            [current_line, current_column + 2],
          ],
          0,
        );
        current_line++;
        current_column = 0;
      }

      // Insert the next character plus a cursor (in-place swap)
      yield* code().code.insert(
        [current_line, current_column],
        char + "\u2063|",
        0.0,
      );

      // Remove the cursor
      yield* code().code.remove(
        [
          [current_line, current_column + 1],
          [current_line, current_column + 3],
        ],
        0.0,
      );

      yield* waitFor(char === "\t" || char === "\n" ? 0.1 : naturalPause(i));
      current_column++;
    }
    yield* code().code.remove(
      [
        [current_line, current_column],
        [current_line, current_column + 2],
      ],
      0,
    );
  }

  //   // Typing multiple lines
  //   yield* typeCodeLine(`
  // def R(s_t, a_t, s_next):
  //     # Já sei vou otimizar para
  //     # sempre andar no meio da pista
  //
  //     if s_t.distancia_pista > 0: return 0
  //     else: return 1`);
  //   yield* waitFor(1);
  // clear
  yield* code().code(
    `
def p_S(regras):
    """
    S : numero '+' S
      | numero '-' S
      | numero '*' S
      | numero '/' S
      | numero
    """

    if len(regras) == 2:
        regras[0] = regras[1]
        return

    if regras[2] == "+":
        regras[0] = regras[1] + regras[3]

    elif regras[2] == "-":
        regras[0] = regras[1] - regras[3]
    elif regras[2] == "*":
        regras[0] = regras[1] * regras[3]
    elif regras[2] == "/":
        if regras[3] == 0:
            raise ZeroDivisionError("Divisão por zero")
        regras[0] = regras[1] / regras[3]

def p_error(p):
    print("Erro de sintaxe " + str(p))

    ...`,
    2,
  );

  yield* waitFor(2);

  yield* code().code(
    `


class MyParser(Parser):
    debugfile = "parser.out"
    tokens = MyLexer.tokens

    def error(self, t):
        print(f"Syntax error at '{t.value}'")

    @_('numero "+" S','numero "-" S', 'numero "*" S', 'numero "/" S', "numero")
    def S(self, p):
        if len(p) == 1:
            return p.numero
        elif len(p) == 3:
            if p[1] == "+":
                return p.numero + p.S
            elif p[1] == "-":
                return p.numero - p.S
            elif p[1] == "*":
                return p.numero * p.S
            elif p[1] == "/":
                return p.numero / p.S

    ...`,
    2,
  );
  yield* waitFor(5);
}
