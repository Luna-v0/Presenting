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
    <Code ref={code} code="" fontSize={60} y={0} x={100} width={800} fill="#000" />,
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

    if s_t.distancia_centro_pista > 0.1: return 0
    else: return 1`);
  yield* waitFor(2.5);
  // clear
  yield* code().code(
    `
def R(s_t, a_t, s_next):
    # Vou otimizar para sempre
    # andar no meio da pista e andar

    if s_t.distancia_centro_pista > 0.1 or 
       s_t.velocidade==0: return 0
    else: return 1`,
    2,
  );
  yield* waitFor(2.5);

  // Zoom out to fit the large code block
  yield* code().scale(0.3, 1);

  yield* code().code(
    `
def R(s_t, a_t, s_next):
    r = 0.0

    # Parâmetros de referência
    centro_bonus = max(0, 1 - abs(s_t.distancia_centro_pista * 5))  # decai exponencialmente conforme distancia
    velocidade_bonus = math.tanh(s_t.velocidade * 2)  # saturação suave
    estabilidade = 1.0 / (1.0 + abs(s_t.angulo_pista - a_t.angulo) * 2)  # estabilidade de direção
    suavidade_acao = 1.0 - abs(a_t.aceleracao - a_t.steering_angle) * 0.1  # penaliza ações bruscas
    penalidade_saida_pista = 1 if s_next.fora_da_pista else 0
    penalidade_brilhante = (s_t.velocidade**2) * abs(s_t.distancia_centro_pista) * random.uniform(0.5, 1.5)

    # Termos não-lineares e absurdamente compostos
    fator_complexo = math.sin(s_t.velocidade * math.pi) * math.exp(-abs(s_t.distancia_centro_pista) * 3)
    fator_caos = math.cos(a_t.steering_angle * 5) * random.uniform(0.9, 1.1)
    fator_inercia = (1 - math.tanh(abs(s_t.velocidade - s_next.velocidade))) * 0.5

    # Combinação arbitrária de tudo isso
    base_reward = (
        2 * centro_bonus
        + 3 * velocidade_bonus
        + 0.5 * estabilidade
        + suavidade_acao
        + fator_complexo
        + fator_caos
        + fator_inercia
        - penalidade_brilhante * 0.05
    )

    # Penalização por comportamento ruim
    if s_t.distancia_centro_pista > 0.1 or s_t.velocidade == 0:
        r = base_reward * 0.1  # quase sem recompensa
    else:
        r = base_reward

    # Reduz drasticamente se sair da pista
    if penalidade_saida_pista:
        r *= -10

    # Pequeno ruído para simular imprevisibilidade do ambiente
    r += random.uniform(-0.05, 0.05)

    # Escalonamento e limite
    r = max(-10, min(r, 10))

    return float(r)`,2
  );
    yield* waitFor(2.5);
}
