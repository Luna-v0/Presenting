"""Refresh de NumPy: o array que está por baixo do pandas.

Cenas:
    NpIntro_01_Array  UMA cena só: o array nasce em linha, dobra em matriz com
                      reshape, é vetorizado, recebe broadcasting, vira máscara
                      booleana e colapsa por axis. As MESMAS células atravessam
                      tudo: elas se movem, nunca somem e voltam.
    NpIntro_02_Dtype      um dtype para o array inteiro; NaN é float e promove
    NpIntro_03_Aleatorio  default_rng, as quatro chamadas mais usadas, e a semente
    NpIntro_04_Algebra    produto matricial e a regra das formas, transposta, solve
    NpIntro_05_Recap      as peças juntas

O `draw` de cada cena é só o ROTEIRO: uma lista de métodos com o nome do que
acontece na tela. Para mudar a ordem, mexa no roteiro; para mudar um beat, mexa
no método.

Os valores são os do NumPy de verdade, conferidos antes de animar.

Render & present (NpIntro_05_Recap é a última: segura o conteúdo no fim):
    uv run manim-slides render scenes/numpy_intro.py \\
        NpIntro_01_Array NpIntro_02_Dtype NpIntro_03_Aleatorio \\
        NpIntro_04_Algebra NpIntro_05_Recap \\
        -q h --disable_caching
    uv run manim-slides present NpIntro_01_Array NpIntro_02_Dtype \\
        NpIntro_03_Aleatorio NpIntro_04_Algebra NpIntro_05_Recap

Note: re-renders precisam de --disable_caching.
"""

import numpy as np

from manim import (
    BLACK,
    DOWN,
    ORIGIN,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    FadeTransform,
    Indicate,
    Rectangle,
    Text,
    Transform,
    VGroup,
    Write,
)
from manim_beamer.slides import SlideShow
from manim_beamer.slides.base import BeamerSlide

FRAME_WIDTH = 14.222222

# ── Paleta (a mesma do pandas_intro) ─────────────────────────────────────────
PY_BLUE = "#3776AB"
BEAMER_GREEN = "#007f5f"
DESTAQUE = "#e07a5f"
VERMELHO = "#c0392b"
CINZA = "#8a8a8a"
SERIF = "TeX Gyre Termes"
MONO = "Noto Sans Mono"

CEL_FILL = "#ffffff"
CEL_AZUL = "#e8eef5"
CEL_VERDE = "#e3f3ec"
CEL_ROSA = "#fbe9e4"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def text(s, font_size=30, weight="NORMAL", color=BLACK, font=SERIF):
    return Text(s, font=font, color=color, font_size=font_size, weight=weight)


def mono(s, font_size=24, color=BLACK, weight="NORMAL"):
    return Text(s, font=MONO, color=color, font_size=font_size, weight=weight)


def limitar(mob, largura_max):
    if mob.width > largura_max:
        mob.scale_to_fit_width(largura_max)
    return mob


def titulo(txt):
    """Título beamer feito à mão: a cena 01 troca de título várias vezes, e um
    Transform entre dois destes substitui o corte entre cenas."""
    t = text(txt, font_size=60, weight="BOLD")
    if t.width > 12.5:
        t.scale_to_fit_width(12.5)
    return t.to_edge(UP, buff=0.4)


def code_block(linhas, font_size=22, fill="#f6f8fa", stroke="#cccccc"):
    codigo = Text("\n".join(linhas), font=MONO, color=BLACK,
                  font_size=font_size, line_spacing=0.6)
    box = Rectangle(width=codigo.width + 0.8, height=codigo.height + 0.55,
                    color=stroke, fill_color=fill, fill_opacity=1.0, stroke_width=2)
    codigo.move_to(box.get_center())
    return VGroup(box, codigo)


LARG, ALT = 1.0, 0.66


def celula(valor, fill=CEL_FILL, font_size=24, color=BLACK):
    box = Rectangle(width=LARG, height=ALT, color=CINZA,
                    fill_color=fill, fill_opacity=1.0, stroke_width=1.5)
    txt = mono(str(valor), font_size=font_size, color=color)
    if txt.width > LARG - 0.18:
        txt.scale_to_fit_width(LARG - 0.18)
    txt.move_to(box.get_center())
    return VGroup(box, txt)


class Grade(VGroup):
    """Grade de células que guarda a lista PLANA delas.

    O truque da cena: o reshape não cria grade nova: são as MESMAS células
    andando para posições novas. Por isso `cels` é plana e `posicoes()` calcula
    para onde cada uma vai numa dada forma.
    """

    def __init__(self, valores, forma, centro=ORIGIN, fill=CEL_FILL):
        super().__init__()
        self.valores = list(valores)
        self.centro = np.array(centro, dtype=float)
        self.cels = [celula(v, fill=fill) for v in self.valores]
        self.add(*self.cels)
        self.aplicar(forma)

    def posicoes(self, forma, centro=None):
        linhas, colunas = forma
        centro = self.centro if centro is None else np.array(centro, dtype=float)
        largura, altura = colunas * LARG, linhas * ALT
        canto = centro + np.array([-largura / 2 + LARG / 2, altura / 2 - ALT / 2, 0.0])
        return [canto + np.array([(k % colunas) * LARG, -(k // colunas) * ALT, 0.0])
                for k in range(len(self.cels))]

    def aplicar(self, forma, centro=None):
        self.forma = forma
        if centro is not None:
            self.centro = np.array(centro, dtype=float)
        for cel, pos in zip(self.cels, self.posicoes(forma)):
            cel.move_to(pos)
        return self

    def em(self, i, j):
        return self.cels[i * self.forma[1] + j]

    def linha(self, i):
        colunas = self.forma[1]
        return VGroup(*self.cels[i * colunas:(i + 1) * colunas])

    def coluna(self, j):
        linhas, colunas = self.forma
        return VGroup(*[self.cels[i * colunas + j] for i in range(linhas)])


def trocar(cel, novo, fill=None, color=BLACK):
    """Troca o conteúdo de uma célula preservando a caixa e a posição."""
    alvo = celula(novo, fill=fill if fill is not None else CEL_FILL, color=color)
    alvo.move_to(cel.get_center())
    return Transform(cel, alvo)


class VisualSlide(BeamerSlide):
    def reset_camera(self, target_scene):
        target_scene.camera.frame.move_to(ORIGIN).set(width=FRAME_WIDTH)


# ─────────────────────────────────────────────────────────────────────────────
# 1: Uma cena só: o array, do reshape ao axis
# ─────────────────────────────────────────────────────────────────────────────

M = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
PLANO = [v for linha in M for v in linha]
DOBRO = [v * 2 for v in PLANO]
VETOR_B = [10, 20, 30, 40]
SOMADO = [v + VETOR_B[k % 4] for k, v in enumerate(PLANO)]
MASCARA = [v > 5 for v in PLANO]
SOMA_AXIS0 = [12, 15, 18, 21]
SOMA_AXIS1 = [6, 22, 38]

CENTRO = np.array([-2.6, -0.4, 0.0])


class ArraySlide(VisualSlide):
    """O array do NumPy, numa cena só."""

    def __init__(self):
        super().__init__(title="O array", subtitle=None)

    # ── o roteiro ────────────────────────────────────────────────────────────

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        self.ts = target_scene if target_scene is not None else self
        self.reset_camera(self.ts)

        self.nasce_em_linha()
        self.um_dtype_e_memoria_contigua()

        self.reshape_dobra_a_linha_em_matriz()

        self.vira_a_cena_da_vetorizacao()
        self.multiplicar_atinge_todo_mundo()

        self.vira_a_cena_do_broadcasting()
        o = self.a_linha_se_repete_para_baixo()

        self.vira_a_cena_da_mascara()
        self.comparar_devolve_booleanos()
        self.indexar_pela_mascara()

        self.vira_a_cena_do_axis()
        self.axis_zero_colapsa_as_linhas()
        self.axis_um_colapsa_as_colunas()

    # ── o array ──────────────────────────────────────────────────────────────

    def nasce_em_linha(self):
        ts = self.ts
        self.titulo_atual = titulo("O array")
        ts.play(Write(self.titulo_atual))
        ts.next_slide()

        self.codigo = code_block(["a = np.arange(12)"])
        self.codigo.move_to([0, 2.3, 0])
        ts.play(FadeIn(self.codigo))
        ts.next_slide()

        self.grade = Grade(PLANO, (1, 12), centro=[0, 0.2, 0])
        ts.play(FadeIn(self.grade, shift=DOWN * 0.3))
        ts.next_slide()

    def um_dtype_e_memoria_contigua(self):
        ts = self.ts
        self.nota = text("doze números, um tipo só, lado a lado na memória",
                         font_size=26, color=CINZA)
        limitar(self.nota, 12.0)
        self.nota.next_to(self.grade, DOWN, buff=0.6)
        ts.play(FadeIn(self.nota))
        ts.next_slide()

        forma = mono("a.shape  ->  (12,)", font_size=24, color=PY_BLUE)
        forma.next_to(self.nota, DOWN, buff=0.35)
        ts.play(Write(forma))
        self.forma_txt = forma
        ts.next_slide()

    # ── reshape ──────────────────────────────────────────────────────────────

    def reshape_dobra_a_linha_em_matriz(self):
        """As MESMAS células andam para a nova forma: a linha dobra em matriz."""
        ts = self.ts
        ts.play(Transform(self.codigo,
                          code_block(["m = a.reshape(3, 4)"]).move_to(self.codigo.get_center())),
                FadeOut(self.forma_txt))
        ts.next_slide()

        # A nota tem de sair do caminho na MESMA animação: ela está ancorada
        # embaixo da linha de 12, que é onde a matriz 3x4 vai pousar.
        alvo_nota = text("mesmos doze números, outra forma.\nNenhum dado foi copiado.",
                         font_size=26, color=CINZA)
        limitar(alvo_nota, 5.6)
        alvo_nota.move_to([3.9, 0.2, 0])

        alvos = self.grade.posicoes((3, 4), centro=CENTRO)
        ts.play(*[cel.animate.move_to(p) for cel, p in zip(self.grade.cels, alvos)],
                FadeTransform(self.nota, alvo_nota),
                run_time=1.6)
        self.grade.forma = (3, 4)
        self.grade.centro = CENTRO
        self.nota = alvo_nota
        ts.next_slide()

        forma = mono("m.shape  ->  (3, 4)", font_size=24, color=PY_BLUE)
        forma.next_to(self.nota, DOWN, buff=0.4)
        ts.play(Write(forma))
        self.forma_txt = forma
        ts.next_slide()

    # ── vetorização ──────────────────────────────────────────────────────────

    def vira_a_cena_da_vetorizacao(self):
        ts = self.ts
        ts.play(
            Transform(self.titulo_atual, titulo("Vetorização")),
            Transform(self.codigo, code_block(["m * 2"]).move_to(self.codigo.get_center())),
            FadeOut(self.nota), FadeOut(self.forma_txt),
            run_time=1.2,
        )
        ts.next_slide()

    def multiplicar_atinge_todo_mundo(self):
        """Sem for: as doze células mudam na mesma animação."""
        ts = self.ts
        ts.play(*[trocar(cel, v, fill=CEL_VERDE)
                  for cel, v in zip(self.grade.cels, DOBRO)], run_time=1.2)
        ts.next_slide()

        nota = text("nenhum `for`: a operação vale para o array inteiro,\n"
                    "e roda em código compilado", font_size=26, color=CINZA)
        limitar(nota, 5.6)
        nota.move_to([3.9, 0.2, 0])
        ts.play(FadeIn(nota))
        self.nota = nota
        ts.next_slide()

        # volta ao original para o próximo beat
        ts.play(*[trocar(cel, v) for cel, v in zip(self.grade.cels, PLANO)],
                run_time=0.9)
        ts.next_slide()

    # ── broadcasting ─────────────────────────────────────────────────────────

    def vira_a_cena_do_broadcasting(self):
        ts = self.ts
        ts.play(
            Transform(self.titulo_atual, titulo("Broadcasting")),
            Transform(self.codigo,
                      code_block(["m + np.array([10, 20, 30, 40])"], font_size=20)
                      .move_to(self.codigo.get_center())),
            FadeOut(self.nota),
            run_time=1.2,
        )
        ts.next_slide()

    def a_linha_se_repete_para_baixo(self):
        ts = self.ts
        vetor = Grade(VETOR_B, (1, 4), centro=CENTRO + np.array([0, 1.35, 0]),
                      fill=CEL_AZUL)
        ts.play(FadeIn(vetor, shift=DOWN * 0.25))
        ts.next_slide()

        # o vetor "desce" repetido sobre cada linha da matriz
        for i in range(3):
            copia = vetor.copy()
            ts.play(copia.animate.move_to(self.grade.linha(i).get_center()).set_opacity(0.45),
                    run_time=0.55)
            ts.play(*[trocar(self.grade.em(i, j), SOMADO[i * 4 + j], fill=CEL_VERDE)
                      for j in range(4)],
                    FadeOut(copia), run_time=0.55)
        ts.next_slide()

        nota = text("a forma menor se ESTICA para casar com a maior,\n"
                    "sem você repetir o vetor três vezes", font_size=26, color=CINZA)
        limitar(nota, 5.6)
        nota.move_to([3.9, 0.2, 0])
        ts.play(FadeIn(nota), FadeOut(vetor))
        self.nota = nota
        ts.next_slide()

        ts.play(*[trocar(cel, v) for cel, v in zip(self.grade.cels, PLANO)],
                run_time=0.9)
        ts.next_slide()

    # ── máscara ──────────────────────────────────────────────────────────────

    def vira_a_cena_da_mascara(self):
        ts = self.ts
        ts.play(
            Transform(self.titulo_atual, titulo("Máscara booleana")),
            Transform(self.codigo, code_block(["m > 5"]).move_to(self.codigo.get_center())),
            FadeOut(self.nota),
            run_time=1.2,
        )
        ts.next_slide()

    def comparar_devolve_booleanos(self):
        ts = self.ts
        ts.play(*[trocar(cel, "True" if b else "False",
                         fill=CEL_VERDE if b else CEL_ROSA)
                  for cel, b in zip(self.grade.cels, MASCARA)], run_time=1.2)
        ts.next_slide()

        nota = text("comparar NÃO devolve um booleano:\ndevolve um array de booleanos,\n"
                    "do mesmo tamanho", font_size=26, color=CINZA)
        limitar(nota, 5.6)
        nota.move_to([3.9, 0.2, 0])
        ts.play(FadeIn(nota))
        self.nota = nota
        ts.next_slide()

    def indexar_pela_mascara(self):
        ts = self.ts
        ts.play(Transform(self.codigo,
                          code_block(["m[m > 5]"]).move_to(self.codigo.get_center())))
        ts.next_slide()

        # Os False viram FANTASMA (opacidade baixa) em vez de sumir: assim eles
        # voltam inteiros no beat do axis, sem precisar recriar a grade.
        self.fora = [cel for cel, b in zip(self.grade.cels, MASCARA) if not b]
        dentro = [(cel, v) for cel, v, b in zip(self.grade.cels, PLANO, MASCARA) if b]
        ts.play(*[cel.animate.set_opacity(0.12) for cel in self.fora],
                *[trocar(cel, v, fill=CEL_VERDE) for cel, v in dentro], run_time=1.0)
        ts.next_slide()

        largura = len(dentro) * LARG
        canto = CENTRO + np.array([-largura / 2 + LARG / 2, -1.7, 0.0])
        ts.play(*[cel.animate.move_to(canto + np.array([k * LARG, 0.0, 0.0]))
                  for k, (cel, _) in enumerate(dentro)], run_time=1.1)
        ts.next_slide()

        alvo = text("sobra um array 1D só com os que passaram.\n"
                    "a forma da matriz se perde", font_size=26, color=CINZA)
        limitar(alvo, 5.6)
        alvo.move_to([3.9, 0.2, 0])
        ts.play(FadeTransform(self.nota, alvo))
        self.nota = alvo
        ts.next_slide()

    # ── axis ─────────────────────────────────────────────────────────────────

    def vira_a_cena_do_axis(self):
        """A matriz se REMONTA: os sobreviventes voltam ao lugar e os fantasmas
        reacendem. Nenhuma célula é destruída e recriada."""
        ts = self.ts
        alvos = self.grade.posicoes((3, 4))

        # ⚠️ duas animações no MESMO mobject dentro de um play se atropelam.
        # Por isso: mover e reacender numa cadeia `.animate` só, e restaurar os
        # valores num play separado.
        ts.play(
            Transform(self.titulo_atual, titulo("axis")),
            Transform(self.codigo,
                      code_block(["m.sum(axis=0)"]).move_to(self.codigo.get_center())),
            FadeOut(self.nota),
            *[cel.animate.set_opacity(1.0).move_to(p)
              for cel, p in zip(self.grade.cels, alvos)],
            run_time=1.2,
        )
        ts.play(*[trocar(cel, v) for cel, v in zip(self.grade.cels, PLANO)],
                run_time=0.7)
        ts.next_slide()

        nota = text("axis diz qual eixo DESAPARECE,\nnão qual sobra",
                    font_size=27, weight="BOLD", color=BEAMER_GREEN)
        limitar(nota, 5.6)
        nota.move_to([3.9, 1.2, 0])
        ts.play(Write(nota))
        self.nota = nota
        ts.next_slide()

    def axis_zero_colapsa_as_linhas(self):
        ts = self.ts
        resultado = Grade(SOMA_AXIS0, (1, 4),
                          centro=CENTRO + np.array([0, -1.5, 0]), fill=CEL_AZUL)
        # contorno que desliza, em vez de Indicate: que pintaria o PREENCHIMENTO
        # das células e viraria uma barra sólida
        col = self.grade.coluna(0)
        marca = Rectangle(width=col.width + 0.1, height=col.height + 0.1,
                          color=DESTAQUE, stroke_width=4).move_to(col.get_center())
        marca.set_z_index(10)
        ts.play(FadeIn(marca), run_time=0.25)
        for j in range(1, 4):
            alvo = self.grade.coluna(j)
            ts.play(marca.animate.move_to(alvo.get_center()), run_time=0.3)
        ts.play(FadeOut(marca), FadeIn(resultado, shift=DOWN * 0.2))
        self.res0 = resultado
        ts.next_slide()

        legenda = mono("(3, 4)  ->  (4,)", font_size=22, color=PY_BLUE)
        legenda.next_to(resultado, DOWN, buff=0.3)
        ts.play(Write(legenda))
        self.leg0 = legenda
        ts.next_slide()

    def axis_um_colapsa_as_colunas(self):
        ts = self.ts
        ts.play(Transform(self.codigo,
                          code_block(["m.sum(axis=1)"]).move_to(self.codigo.get_center())),
                FadeOut(self.res0), FadeOut(self.leg0))
        ts.next_slide()

        resultado = Grade(SOMA_AXIS1, (3, 1),
                          centro=CENTRO + np.array([3.0, 0, 0]), fill=CEL_AZUL)
        lin = self.grade.linha(0)
        marca = Rectangle(width=lin.width + 0.1, height=lin.height + 0.1,
                          color=DESTAQUE, stroke_width=4).move_to(lin.get_center())
        marca.set_z_index(10)
        ts.play(FadeIn(marca), run_time=0.25)
        for i in range(1, 3):
            alvo = self.grade.linha(i)
            ts.play(marca.animate.move_to(alvo.get_center()), run_time=0.3)
        ts.play(FadeOut(marca), FadeIn(resultado, shift=RIGHT * 0.2))
        ts.next_slide()

        legenda = mono("(3, 4)  ->  (3,)", font_size=22, color=PY_BLUE)
        legenda.next_to(resultado, DOWN, buff=0.3)
        ts.play(Write(legenda))
        ts.next_slide()

        fecho = text("axis=0 some com as LINHAS\naxis=1 some com as COLUNAS",
                     font_size=27, weight="BOLD", color=BEAMER_GREEN)
        limitar(fecho, 5.6)
        fecho.move_to(self.nota.get_center())
        ts.play(FadeTransform(self.nota, fecho))
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# 2: Um dtype só, e o NaN
# ─────────────────────────────────────────────────────────────────────────────

class DtypeSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Um tipo só", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        self.ts = target_scene if target_scene is not None else self
        self.reset_camera(self.ts)

        self.um_dtype_para_o_array_inteiro()
        self.o_nan_promove_o_array()
        self.o_nan_contamina_a_conta()

    def um_dtype_para_o_array_inteiro(self):
        ts = self.ts
        self.titulo_atual = titulo("Um tipo só")
        ts.play(Write(self.titulo_atual))
        ts.next_slide()

        self.grade = Grade([1, 2, 3], (1, 3), centro=[-3.4, 0.9, 0])
        self.codigo = code_block(["np.array([1, 2, 3])"])
        self.codigo.move_to([-3.4, 2.1, 0])
        tipo = mono("dtype: int64", font_size=24, color=PY_BLUE)
        tipo.next_to(self.grade, DOWN, buff=0.35)
        ts.play(FadeIn(self.codigo), FadeIn(self.grade), Write(tipo))
        self.tipo = tipo
        ts.next_slide()

        self.nota = text("um array tem UM dtype, para todos os elementos.\n"
                         "É isso que deixa a memória contígua, e a conta rápida.",
                         font_size=25, color=CINZA)
        limitar(self.nota, 12.0)
        self.nota.to_edge(DOWN, buff=0.7)
        ts.play(FadeIn(self.nota))
        ts.next_slide()

    def o_nan_promove_o_array(self):
        ts = self.ts
        codigo2 = code_block(["np.array([1, np.nan, 3])"])
        codigo2.move_to([3.4, 2.1, 0])
        grade2 = Grade(["1.0", "nan", "3.0"], (1, 3), centro=[3.4, 0.9, 0],
                       fill=CEL_ROSA)
        tipo2 = mono("dtype: float64", font_size=24, color=VERMELHO)
        tipo2.next_to(grade2, DOWN, buff=0.35)
        ts.play(FadeIn(codigo2), FadeIn(grade2), Write(tipo2))
        ts.next_slide()

        # a nota anterior VIRA esta; as duas juntas se sobrepunham
        alvo = text("NaN é um FLOAT. Um só já promove o array inteiro,\n"
                    "e é por isso que, no pandas, coluna de inteiros com nulo\n"
                    "vira float64.", font_size=25, color=CINZA)
        limitar(alvo, 12.0)
        alvo.to_edge(DOWN, buff=0.55)
        ts.play(FadeTransform(self.nota, alvo))
        self.nota = alvo
        ts.next_slide()

    def o_nan_contamina_a_conta(self):
        ts = self.ts
        alvo = text("e um único NaN contamina a conta inteira", font_size=27,
                    weight="BOLD", color=BEAMER_GREEN)
        limitar(alvo, 12.0)
        alvo.move_to(self.nota.get_center())
        ts.play(FadeTransform(self.nota, alvo))
        ts.next_slide()

        contas = code_block(['np.array([1., np.nan, 3.]).sum()   ->  nan',
                             'np.nansum([1., np.nan, 3.])        ->  4.0'], font_size=22)
        limitar(contas, 11.0)
        contas.move_to([0, -1.4, 0])
        ts.play(FadeIn(contas))
        ts.next_slide()

        fecho = text("a família nan* existe para isso", font_size=25, color=CINZA)
        fecho.next_to(contas, DOWN, buff=0.4)
        ts.play(FadeIn(fecho))
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# 3: Números aleatórios
# ─────────────────────────────────────────────────────────────────────────────

class AleatorioSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Números aleatórios", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        self.ts = target_scene if target_scene is not None else self
        self.reset_camera(self.ts)

        self.o_gerador_com_semente()
        self.as_quatro_que_voce_mais_usa()
        self.mesma_semente_mesmo_resultado()

    def o_gerador_com_semente(self):
        ts = self.ts
        self.titulo_atual = titulo("Números aleatórios")
        ts.play(Write(self.titulo_atual))
        ts.next_slide()

        self.codigo = code_block(["rng = np.random.default_rng(42)"])
        self.codigo.move_to([0, 2.3, 0])
        ts.play(FadeIn(self.codigo))
        ts.next_slide()

        self.grade = Grade(["0.774", "0.439", "0.859", "0.697"], (1, 4),
                           centro=[-2.4, -0.2, 0], fill=CEL_AZUL)
        self.rotulo = mono("rng.random(4)", font_size=22, color=CINZA)
        self.rotulo.next_to(self.grade, UP, buff=0.3)
        ts.play(FadeIn(self.grade), Write(self.rotulo))
        ts.next_slide()

        self.nota = text("floats entre 0 e 1", font_size=25, color=CINZA)
        limitar(self.nota, 5.4)
        self.nota.move_to([3.9, -0.2, 0])
        ts.play(FadeIn(self.nota))
        ts.next_slide()

    def as_quatro_que_voce_mais_usa(self):
        """Cada chamada TROCA os valores das mesmas células."""
        ts = self.ts
        passos = [
            ("rng.integers(1, 7, 5)", ["1", "5", "4", "3", "3"],
             "inteiros de 1 a 6:\no fim é exclusivo"),
            ("rng.normal(100, 15, 4)", ["104.6", "84.4", "111.3", "114.1"],
             "de uma normal,\nmédia 100 e desvio 15"),
            ('rng.choice(["loja", "site"],\n           5, p=[0.3, 0.7])',
             ["site", "site", "site", "site", "loja"],
             "sorteio com\nprobabilidade declarada"),
        ]
        for codigo_txt, valores, nota_txt in passos:
            nova = Grade(valores, (1, len(valores)), centro=[-2.4, -0.2, 0],
                         fill=CEL_AZUL)
            alvo_rot = mono(codigo_txt.split("\n")[0].strip(), font_size=22, color=CINZA)
            alvo_rot.next_to(nova, UP, buff=0.3)
            alvo_nota = text(nota_txt, font_size=25, color=CINZA)
            limitar(alvo_nota, 5.4)
            alvo_nota.move_to([3.9, -0.2, 0])

            ts.play(
                Transform(self.codigo, limitar(code_block(codigo_txt.split("\n"),
                                                          font_size=20), 8.0
                                               ).move_to(self.codigo.get_center())),
                FadeTransform(self.grade, nova),
                Transform(self.rotulo, alvo_rot),
                FadeTransform(self.nota, alvo_nota),
                run_time=1.0,
            )
            self.grade, self.nota = nova, alvo_nota
            ts.next_slide()

    def mesma_semente_mesmo_resultado(self):
        """O ponto que importa: reprodutibilidade."""
        ts = self.ts
        ts.play(
            Transform(self.codigo, limitar(code_block(
                ["np.random.default_rng(7).random(3)"], font_size=20), 8.0
            ).move_to(self.codigo.get_center())),
            FadeOut(self.grade), FadeOut(self.rotulo), FadeOut(self.nota),
            run_time=0.9,
        )
        ts.next_slide()

        a = Grade(["0.625", "0.897", "0.776"], (1, 3), centro=[-2.4, 0.2, 0],
                  fill=CEL_VERDE)
        b = Grade(["0.625", "0.897", "0.776"], (1, 3), centro=[-2.4, -0.7, 0],
                  fill=CEL_VERDE)
        rot = mono("duas execuções, semente 7", font_size=21, color=CINZA)
        rot.next_to(a, UP, buff=0.3)
        ts.play(FadeIn(a), Write(rot))
        ts.play(FadeIn(b))
        ts.next_slide()

        fecho = text("mesma semente,\nmesmos números.", font_size=28,
                     weight="BOLD", color=BEAMER_GREEN)
        limitar(fecho, 5.4)
        fecho.move_to([3.9, 0.2, 0])
        ts.play(Write(fecho))
        ts.next_slide()

        detalhe = text("sem semente, cada execução dá outro\n"
                       "resultado, e você não consegue\nreproduzir nem depurar.",
                       font_size=23, color=CINZA)
        limitar(detalhe, 5.4)
        detalhe.next_to(fecho, DOWN, buff=0.45)
        ts.play(FadeIn(detalhe))
        ts.next_slide()

        aviso = text("np.random.seed() é a API antiga.\nUse default_rng().",
                     font_size=23, color=VERMELHO)
        limitar(aviso, 11.0)
        aviso.to_edge(DOWN, buff=0.5)
        ts.play(FadeIn(aviso))
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# 4: Álgebra linear
# ─────────────────────────────────────────────────────────────────────────────

class AlgebraSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Álgebra linear", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        self.ts = target_scene if target_scene is not None else self
        self.reset_camera(self.ts)

        self.duas_matrizes()
        self.produto_matricial_e_a_regra_das_formas()
        self.quando_as_formas_nao_casam()
        self.transposta_gira_a_matriz()
        self.resolver_um_sistema()

    def duas_matrizes(self):
        ts = self.ts
        self.titulo_atual = titulo("Álgebra linear")
        ts.play(Write(self.titulo_atual))
        ts.next_slide()

        self.A = Grade([1, 2, 3, 4, 5, 6], (2, 3), centro=[-4.2, 0.1, 0])
        self.B = Grade([7, 8, 9, 10, 11, 12], (3, 2), centro=[-0.6, 0.1, 0],
                       fill=CEL_AZUL)
        rot_a = mono("A  (2, 3)", font_size=22, color=CINZA)
        rot_a.next_to(self.A, UP, buff=0.3)
        rot_b = mono("B  (3, 2)", font_size=22, color=CINZA)
        rot_b.next_to(self.B, UP, buff=0.3)
        ts.play(FadeIn(self.A), Write(rot_a))
        ts.play(FadeIn(self.B), Write(rot_b))
        self.rot_a, self.rot_b = rot_a, rot_b
        ts.next_slide()

    def produto_matricial_e_a_regra_das_formas(self):
        ts = self.ts
        self.codigo = code_block(["A @ B"])
        self.codigo.move_to([0, 2.4, 0])
        ts.play(FadeIn(self.codigo))
        ts.next_slide()

        regra = mono("(2, 3) @ (3, 2)  ->  (2, 2)", font_size=26, color=PY_BLUE)
        regra.to_edge(DOWN, buff=1.5)
        ts.play(Write(regra))
        ts.next_slide()

        interno = text("os de DENTRO têm de bater;\nos de FORA viram a forma do resultado",
                       font_size=24, color=CINZA)
        limitar(interno, 11.0)
        interno.next_to(regra, DOWN, buff=0.35)
        ts.play(FadeIn(interno))
        self.regra, self.interno = regra, interno
        ts.next_slide()

        self.R = Grade([58, 64, 139, 154], (2, 2), centro=[3.6, 0.1, 0],
                       fill=CEL_VERDE)
        rot_r = mono("(2, 2)", font_size=22, color=CINZA)
        rot_r.next_to(self.R, UP, buff=0.3)
        ts.play(FadeIn(self.R, shift=RIGHT * 0.3), Write(rot_r))
        self.rot_r = rot_r
        ts.next_slide()

    def quando_as_formas_nao_casam(self):
        ts = self.ts
        ts.play(Transform(self.codigo,
                          code_block(["B @ B"]).move_to(self.codigo.get_center())),
                FadeOut(self.R), FadeOut(self.rot_r))
        ts.next_slide()

        erro = mono("ValueError", font_size=30, color=VERMELHO, weight="BOLD")
        erro.move_to([3.6, 0.4, 0])
        alvo = mono("(3, 2) @ (3, 2)", font_size=26, color=VERMELHO)
        alvo.move_to(self.regra.get_center())
        ts.play(Write(erro), Transform(self.regra, alvo))
        ts.next_slide()

        porque = text("2 e 3 não batem:\no produto não existe", font_size=24,
                      color=CINZA)
        limitar(porque, 5.0)
        porque.next_to(erro, DOWN, buff=0.4)
        ts.play(FadeIn(porque))
        self.erro, self.porque = erro, porque
        ts.next_slide()

    def transposta_gira_a_matriz(self):
        """As mesmas células do A trocam de lugar: (i, j) vira (j, i)."""
        ts = self.ts
        ts.play(Transform(self.codigo,
                          code_block(["A.T"]).move_to(self.codigo.get_center())),
                FadeOut(self.erro), FadeOut(self.porque),
                FadeOut(self.B), FadeOut(self.rot_b),
                Transform(self.regra, mono("(2, 3)  ->  (3, 2)", font_size=26,
                                           color=PY_BLUE
                                           ).move_to(self.regra.get_center())),
                run_time=1.0)
        ts.next_slide()

        destinos = self.A.posicoes((3, 2))
        movimentos = []
        for k in range(6):
            i, j = divmod(k, 3)          # posição em A (2 linhas, 3 colunas)
            movimentos.append(self.A.cels[k].animate.move_to(destinos[j * 2 + i]))
        ts.play(*movimentos, run_time=1.4)
        self.A.forma = (3, 2)
        ts.play(Transform(self.rot_a, mono("A.T  (3, 2)", font_size=22, color=CINZA)
                          .move_to(self.rot_a.get_center())))
        ts.next_slide()

    def resolver_um_sistema(self):
        ts = self.ts
        ts.play(FadeOut(self.A), FadeOut(self.rot_a), FadeOut(self.regra),
                FadeOut(self.interno),
                Transform(self.codigo, limitar(code_block([
                    "M = np.array([[2, 1],",
                    "              [1, 3]])",
                    "b = np.array([7, 11])",
                    "np.linalg.solve(M, b)"], font_size=20), 6.0
                ).move_to([-3.6, 0.6, 0])),
                run_time=1.0)
        ts.next_slide()

        sistema = mono("2x +  y =  7\n x + 3y = 11", font_size=26, color=BLACK)
        sistema.move_to([-3.6, -1.9, 0])
        ts.play(Write(sistema))
        ts.next_slide()

        resposta = Grade(["2.0", "3.0"], (1, 2), centro=[3.4, 0.6, 0], fill=CEL_VERDE)
        rot = mono("x, y", font_size=22, color=CINZA)
        rot.next_to(resposta, UP, buff=0.3)
        ts.play(FadeIn(resposta), Write(rot))
        ts.next_slide()

        outras = code_block(["np.linalg.det(M)   ->  5.0",
                             "np.linalg.inv(M)   ->  a inversa",
                             "M @ solucao        ->  confere o resultado"], font_size=19)
        limitar(outras, 6.2)
        outras.move_to([3.4, -1.5, 0])
        ts.play(FadeIn(outras))
        ts.next_slide()

        fecho = text("solve é melhor que inv @ b:\nmais preciso e mais rápido.",
                     font_size=24, weight="BOLD", color=BEAMER_GREEN)
        limitar(fecho, 11.0)
        fecho.to_edge(DOWN, buff=0.45)
        ts.play(Write(fecho))
        ts.next_slide()

# ─────────────────────────────────────────────────────────────────────────────
# 5: Recap
# ─────────────────────────────────────────────────────────────────────────────

class RecapSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Quatro ideias", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(titulo("Quatro ideias")))
        ts.next_slide()

        itens = [
            ("um dtype", "memória contígua, e é daí que vem a velocidade", "a.dtype"),
            ("vetorização", "a operação vale para o array inteiro", "m * 2"),
            ("broadcasting", "a forma menor estica para casar", "m + [10, 20, 30, 40]"),
            ("axis", "diz qual eixo desaparece", "m.sum(axis=0)"),
        ]
        y = 1.7
        for nome, desc, cod in itens:
            rotulo = text(nome, font_size=30, weight="BOLD", color=PY_BLUE)
            corpo = text(desc, font_size=24, color=BLACK)
            cb = code_block([cod], font_size=19)

            rotulo.move_to([-5.6 + rotulo.width / 2, y, 0])
            corpo.move_to([-2.2 + corpo.width / 2, y, 0])
            limitar(cb, 4.2)
            cb.move_to([5.0, y, 0])

            ts.play(Write(rotulo), FadeIn(corpo), FadeIn(cb))
            ts.next_slide()
            y -= 1.15


# ─────────────────────────────────────────────────────────────────────────────
# Scene classes
# ─────────────────────────────────────────────────────────────────────────────

class EndHeldSlideShow(SlideShow):
    """SlideShow que termina segurando o conteúdo em vez de desaparecer."""

    def construct(self):
        for slide in self.slides:
            slide.draw(origin=None, scale=1.0, target_scene=self, animate=True)
        self.wait(1)


class NpIntro_01_Array(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[ArraySlide()], **kwargs)


class NpIntro_02_Dtype(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[DtypeSlide()], **kwargs)


class NpIntro_03_Aleatorio(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[AleatorioSlide()], **kwargs)


class NpIntro_04_Algebra(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[AlgebraSlide()], **kwargs)


class NpIntro_05_Recap(EndHeldSlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[RecapSlide()], **kwargs)
