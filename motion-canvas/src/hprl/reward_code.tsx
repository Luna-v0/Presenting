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
import { tags as t } from "@lezer/highlight";
import { HighlightStyle } from "@codemirror/language";
import { parser } from "@lezer/python";

Code.defaultHighlighter = new LezerHighlighter(parser);

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
    <Code ref={code} code="" fontSize={60} y={0} width={800} fill="#000" />,
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

  yield* waitFor(0.5);

  // Typing multiple lines
  yield* typeCodeLine(`
def R(s_t, a_t, s_next):
    # Já sei vou otimizar para
    # sempre andar no meio da pista

    if s_t.distancia_pista > 0: return 0
    else: return 1`);
  yield* waitFor(1);
  // clear
  yield* code().code(
    `
def R(s_t, a_t, s_next):
    # Vou otimizar para sempre
    # andar no meio da pista e andar

    if s_t.distancia_pista > 0 or 
       s_t.velocidade==0: return 0
    else: return 1`,
    2,
  );

  yield* waitFor(2);
}
