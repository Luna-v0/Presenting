"""Refresh de pandas: o que é DataFrame, Series e índice.

Cenas:
    PdIntro_01_Tabela  DataFrame -> Series -> índice -> consulta, TUDO numa cena
                       só, porque é sempre a MESMA tabela na tela: entre um
                       assunto e o outro muda o título, não o conteúdo
    PdIntro_02_Merge   juntar duas tabelas pela chave; how decide quem sobrevive
    PdIntro_03_Melt    largo x longo, com melt e pivot
    PdIntro_04_Recap   as peças juntas

Por que a 01 é uma cena longa: o manim-slides corta entre cenas, então dois
SlideShows seguidos obrigam a tabela a sumir e voltar. Mantendo os quatro
assuntos numa cena só, a tabela nunca sai da tela: o título é que se
transforma. (Mesmo truque do python_intro.py com a linha do tempo.)

O deck prefere Transform a FadeOut+FadeIn: o que já está na tela vira o próximo
estado, em vez de sumir e voltar. Só sai de cena o que o pandas de fato descarta.

Cada conceito aparece com o código que o produz ao lado.

Os valores mostrados são os do pandas de verdade: o filtro `valor > 1000`
sobra as linhas 0, 3 e 4, de propósito, para o buraco no índice ficar visível.

Render & present (PdIntro_04_Recap é a última: segura o conteúdo no fim):
    uv run manim-slides render scenes/pandas_intro.py \\
        PdIntro_01_Tabela PdIntro_02_Merge PdIntro_03_Melt PdIntro_04_Recap \\
        -q h --disable_caching
    uv run manim-slides present \\
        PdIntro_01_Tabela PdIntro_02_Merge PdIntro_03_Melt PdIntro_04_Recap

Note: re-renders precisam de --disable_caching (mesma pegadinha do python_intro).
"""

import numpy as np

from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    FadeTransform,
    Indicate,
    Rectangle,
    ReplacementTransform,
    Text,
    Transform,
    VGroup,
    Write,
)
from manim_beamer.slides import SlideShow
from manim_beamer.slides.base import BeamerSlide

# Default 16:9 camera frame (MovingCameraScene). x in [-7.11, 7.11], y in [-4, 4].
FRAME_WIDTH = 14.222222

# ── Paleta (fundo branco, como o resto do repo) ──────────────────────────────
PY_BLUE = "#3776AB"
PY_YELLOW = "#FFD343"
BEAMER_GREEN = "#007f5f"
DESTAQUE = "#e07a5f"
CINZA = "#8a8a8a"
SERIF = "TeX Gyre Termes"
MONO = "Noto Sans Mono"

CAB_FILL = "#e8eef5"
IDX_FILL = "#f0f0f0"
CEL_FILL = "#ffffff"

# ── Os dados (batem com o pandas: conferidos antes de animar) ────────────────
COLUNAS = ["vendedor", "produto", "valor", "status"]
LARGURAS = [2.0, 2.1, 1.5, 2.0]
LINHAS = [
    ["Ana", "notebook", "3200.0", "aprovada"],
    ["Ana", "cadeira", "890.0", "aprovada"],
    ["Bruno", "mouse", "150.0", "aprovada"],
    ["Bruno", "mesa", "1200.0", "pendente"],
    ["Carla", "monitor", "1450.0", "aprovada"],
]
MASCARA = [True, False, False, True, True]          # valor > 1000
SOBRAM = [0, 3, 4]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def text(s, font_size=30, weight="NORMAL", color=BLACK, font=SERIF):
    return Text(s, font=font, color=color, font_size=font_size, weight=weight)


def mono(s, font_size=24, color=BLACK, weight="NORMAL"):
    return Text(s, font=MONO, color=color, font_size=font_size, weight=weight)


def code_block(lines, font_size=22, fill="#f6f8fa", stroke="#cccccc"):
    """Painel de código monoespaçado. Um Text multilinha só, para o Pango
    preservar a indentação."""
    code = Text("\n".join(lines), font=MONO, color=BLACK,
                font_size=font_size, line_spacing=0.6)
    box = Rectangle(width=code.width + 0.8, height=code.height + 0.55,
                    color=stroke, fill_color=fill, fill_opacity=1.0, stroke_width=2)
    code.move_to(box.get_center())
    return VGroup(box, code)


def limitar(mob, largura_max):
    """Encolhe o mobject se ele passar da largura pedida. Evita texto cortado
    na borda: o frame vai de -7.11 a 7.11."""
    if mob.width > largura_max:
        mob.scale_to_fit_width(largura_max)
    return mob


def titulo(txt):
    """Um título no estilo beamer, posicionado no topo.

    Feito à mão (em vez de `make_title`) porque a cena 01 troca de título
    várias vezes: um Transform entre dois destes é o que substitui o corte
    entre cenas.
    """
    t = text(txt, font_size=60, weight="BOLD")
    if t.width > 12.5:
        t.scale_to_fit_width(12.5)
    return t.to_edge(UP, buff=0.4)


def celula(conteudo, largura, altura, fill, font_size=22, weight="NORMAL",
           color=BLACK, font=MONO):
    box = Rectangle(width=largura, height=altura, color=CINZA,
                    fill_color=fill, fill_opacity=1.0, stroke_width=1.5)
    if conteudo == "":
        return VGroup(box)
    txt = Text(conteudo, font=font, color=color, font_size=font_size, weight=weight)
    if txt.width > largura - 0.2:
        txt.scale_to_fit_width(largura - 0.2)
    txt.move_to(box.get_center())
    return VGroup(box, txt)


class Tabela(VGroup):
    """Uma tabela de DataFrame, com acesso a coluna, linha e índice.

    Guarda as partes separadas para dar para destacar uma coluna inteira, uma
    linha inteira ou só a faixa do índice.
    """

    ALTURA = 0.58
    LARG_IDX = 0.85

    def __init__(self, colunas=COLUNAS, linhas=LINHAS, larguras=LARGURAS,
                 indices=None, font_size=22, larg_idx=None, nome_indice=""):
        super().__init__()
        self.colunas = list(colunas)
        self.larguras = list(larguras)
        self.indices = list(range(len(linhas))) if indices is None else list(indices)
        self.LARG_IDX = self.LARG_IDX if larg_idx is None else larg_idx

        self.canto = celula(nome_indice, self.LARG_IDX, self.ALTURA, IDX_FILL,
                            font_size=font_size, weight="BOLD", color=CINZA)
        self.cabecalho = VGroup(*[
            celula(nome, larg, self.ALTURA, CAB_FILL, font_size=font_size,
                   weight="BOLD", color=PY_BLUE)
            for nome, larg in zip(self.colunas, self.larguras)
        ])
        self.rotulos = VGroup(*[
            celula(str(r), self.LARG_IDX, self.ALTURA, IDX_FILL,
                   font_size=font_size, weight="BOLD", color=CINZA)
            for r in self.indices
        ])
        self.corpo = VGroup(*[
            VGroup(*[
                celula(valor, larg, self.ALTURA, CEL_FILL, font_size=font_size)
                for valor, larg in zip(linha, self.larguras)
            ])
            for linha in linhas
        ])

        # posicionamento: canto ancora tudo
        self.canto.move_to(ORIGIN)
        x = self.canto.get_right()[0]
        for cel, larg in zip(self.cabecalho, self.larguras):
            cel.move_to([x + larg / 2, self.canto.get_center()[1], 0])
            x += larg

        for i, (rot, linha) in enumerate(zip(self.rotulos, self.corpo)):
            y = self.canto.get_center()[1] - (i + 1) * self.ALTURA
            rot.move_to([self.canto.get_center()[0], y, 0])
            x = self.canto.get_right()[0]
            for cel, larg in zip(linha, self.larguras):
                cel.move_to([x + larg / 2, y, 0])
                x += larg

        self.add(self.canto, self.cabecalho, self.rotulos, self.corpo)
        self.move_to(ORIGIN)

    def coluna(self, j):
        """Cabeçalho + todas as células daquela coluna."""
        return VGroup(self.cabecalho[j], *[linha[j] for linha in self.corpo])

    def linha(self, i):
        """Rótulo do índice + todas as células daquela linha."""
        return VGroup(self.rotulos[i], *self.corpo[i])

    def faixa_indice(self):
        return VGroup(self.canto, *self.rotulos)


def serie_vertical(rotulos, valores, font_size=22, largura_idx=1.6, largura_val=1.9):
    """Uma Series como o pandas imprime: rótulo à esquerda, valor à direita.

    É o mesmo desenho venha ela de uma coluna ou de uma linha, e é justamente
    esse o ponto.
    """
    linhas = VGroup()
    for rot, val in zip(rotulos, valores):
        r = celula(str(rot), largura_idx, Tabela.ALTURA, IDX_FILL,
                   font_size=font_size, weight="BOLD", color=CINZA)
        v = celula(str(val), largura_val, Tabela.ALTURA, CEL_FILL, font_size=font_size)
        v.next_to(r, RIGHT, buff=0)
        linhas.add(VGroup(r, v))
    linhas.arrange(DOWN, buff=0)
    return linhas


# ─────────────────────────────────────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────────────────────────────────────

class VisualSlide(BeamerSlide):
    """BeamerSlide com corpo inteiramente animado à mão."""

    def reset_camera(self, target_scene):
        target_scene.camera.frame.move_to(ORIGIN).set(width=FRAME_WIDTH)

    def make_title(self):
        title = self.title_text.copy()
        if title.width > 12.5:
            title.scale_to_fit_width(12.5)
        return title.to_edge(UP, buff=0.4)


# ─────────────────────────────────────────────────────────────────────────────
# 1: Uma cena só: DataFrame → Series → índice → consulta
#
# A tabela nasce no primeiro bloco e NÃO sai mais da tela. Entre um assunto e o
# outro, o que muda é o título (Transform) e o material de apoio de cada bloco.
# ─────────────────────────────────────────────────────────────────────────────

PRODUTOS = [l[1] for l in LINHAS]
MASCARA_TXT = ["True", "False", "False", "True", "True"]
SOBRAM = [0, 3, 4]


class TabelaSlide(VisualSlide):
    """DataFrame → Series → índice → consulta, numa cena só.

    O `draw` é só o ROTEIRO: cada beat da apresentação é um método com nome do
    que acontece na tela. Para mudar a ordem, mexa no roteiro; para mudar o que
    um beat faz, mexa no método. O estado que atravessa os beats (a tabela, o
    realce, o código, o título) mora em `self`.
    """

    def __init__(self):
        super().__init__(title="O DataFrame", subtitle=None)

    # ── o roteiro ────────────────────────────────────────────────────────────

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        self.ts = target_scene if target_scene is not None else self
        self.reset_camera(self.ts)

        self.abre_com_a_tabela()

        self.vira_a_cena_da_series()
        self.a_coluna_e_uma_series()
        self.a_linha_tambem_e_uma_series()

        self.vira_a_cena_do_indice()
        self.o_indice_e_rotulo_nao_posicao()
        self.coluna_produtos_vira_indice()
        self.enderecar_pelo_rotulo()
        self.o_numero_nao_endereca_mais_nada()

        self.vira_a_cena_da_consulta()
        self.a_mascara_booleana()
        self.o_filtro_e_os_rotulos_que_ficam()

    # ── bloco 1: o DataFrame ─────────────────────────────────────────────────

    def abre_com_a_tabela(self):
        ts = self.ts
        self.titulo_atual = titulo("O DataFrame")
        ts.play(Write(self.titulo_atual))
        ts.next_slide()

        self.codigo = code_block(['df = pd.read_csv("vendas.csv")'])
        self.codigo.move_to([0, 2.2, 0])
        ts.play(FadeIn(self.codigo))
        ts.next_slide()

        self.tabela = Tabela()
        self.tabela.move_to([0, -0.6, 0])
        ts.play(Create(self.tabela.canto), Create(self.tabela.cabecalho))
        ts.next_slide()

        for i in range(len(LINHAS)):
            ts.play(FadeIn(self.tabela.linha(i)), run_time=0.32)
        ts.next_slide()

        self.rotulo = text("isto é um DataFrame", font_size=32,
                           weight="BOLD", color=BEAMER_GREEN)
        self.rotulo.next_to(self.tabela, DOWN, buff=0.45)
        ts.play(Write(self.rotulo))
        ts.next_slide()

        self.legenda = text("uma tabela: linhas e colunas, com nome e rótulo",
                            font_size=24, color=CINZA)
        self.legenda.next_to(self.rotulo, DOWN, buff=0.25)
        ts.play(FadeIn(self.legenda))
        ts.next_slide()

    # ── bloco 2: a Series ────────────────────────────────────────────────────

    def vira_a_cena_da_series(self):
        """Só o título muda; a tabela ANDA para a esquerda em vez de piscar."""
        ts = self.ts
        ts.play(
            Transform(self.titulo_atual, titulo("A Series")),
            FadeOut(self.codigo), FadeOut(self.rotulo), FadeOut(self.legenda),
            self.tabela.animate.scale(0.84).move_to([-3.4, -0.4, 0]),
            run_time=1.3,
        )
        ts.next_slide()

    def a_coluna_e_uma_series(self):
        ts = self.ts
        self.codigo = code_block(['df["valor"]'])
        self.codigo.move_to([3.6, 2.4, 0])
        ts.play(FadeIn(self.codigo))

        col = self.tabela.coluna(2)
        self.realce = Rectangle(width=col.width + 0.12, height=col.height + 0.12,
                                color=DESTAQUE, stroke_width=4).move_to(col.get_center())
        self.realce.set_z_index(10)      # senão a tabela é redesenhada por cima
        ts.play(Create(self.realce))
        ts.next_slide()

        self.serie = serie_vertical([0, 1, 2, 3, 4], [l[2] for l in LINHAS])
        self.serie.scale(0.84).move_to([3.6, -0.3, 0])
        self.rodape = mono("Name: valor, dtype: float64", font_size=18, color=CINZA)
        self.rodape.next_to(self.serie, DOWN, buff=0.2)
        self.legenda = text("uma coluna é uma Series", font_size=28,
                            weight="BOLD", color=BEAMER_GREEN)
        self.legenda.next_to(self.serie, UP, buff=0.35)
        ts.play(FadeIn(self.serie, shift=RIGHT * 0.4), FadeIn(self.rodape))
        ts.next_slide()

        ts.play(Write(self.legenda))
        ts.next_slide()

    def a_linha_tambem_e_uma_series(self):
        """A mesma cena vira a da linha: tudo se transforma, nada pisca."""
        ts = self.ts
        lin = self.tabela.linha(2)

        # o FadeTransform SUBSTITUI o mobject em cena, então a variável tem de
        # apontar para o novo: senão o antigo fica na tela para sempre
        serie_linha = serie_vertical(COLUNAS, LINHAS[2]).scale(0.84).move_to([3.6, -0.3, 0])

        ts.play(
            Transform(self.codigo,
                      code_block(["df.loc[2]"]).move_to(self.codigo.get_center())),
            Transform(self.realce,
                      Rectangle(width=lin.width + 0.12, height=lin.height + 0.12,
                                color=DESTAQUE, stroke_width=4).move_to(lin.get_center())),
            FadeTransform(self.serie, serie_linha),
            Transform(self.rodape, mono("Name: 2, dtype: object", font_size=18,
                                        color=CINZA).move_to([3.6, -1.75, 0])),
            Transform(self.legenda, text("uma linha também é", font_size=28, weight="BOLD",
                                         color=BEAMER_GREEN).move_to(self.legenda.get_center())),
            run_time=1.3,
        )
        self.serie = serie_linha          # a partir daqui, é esta que está em cena
        ts.next_slide()

        self.nota = text("muda só quem é o índice:  os rótulos  →  os nomes das colunas",
                         font_size=24, color=CINZA)
        limitar(self.nota, 12.0)
        self.nota.to_edge(DOWN, buff=0.45)
        ts.play(FadeIn(self.nota))
        ts.next_slide()

    # ── bloco 3: o índice ────────────────────────────────────────────────────

    def vira_a_cena_do_indice(self):
        """A tabela anda na MESMA animação, então o realce tem de mirar onde a
        faixa VAI estar, não onde ela está agora."""
        ts = self.ts
        destino = np.array([-3.1, -0.3, 0.0])
        deslocamento = destino - self.tabela.get_center()
        faixa = self.tabela.faixa_indice()
        alvo_realce = Rectangle(width=faixa.width + 0.12, height=faixa.height + 0.12,
                                color=DESTAQUE, stroke_width=4)
        alvo_realce.move_to(faixa.get_center() + deslocamento)

        ts.play(
            Transform(self.titulo_atual, titulo("O índice")),
            FadeOut(self.serie), FadeOut(self.rodape), FadeOut(self.legenda),
            FadeOut(self.nota), FadeOut(self.codigo),
            Transform(self.realce, alvo_realce),
            self.tabela.animate.move_to(destino),
            run_time=1.3,
        )
        ts.play(*[Indicate(r, color=DESTAQUE) for r in self.tabela.rotulos])
        ts.next_slide()

    def o_indice_e_rotulo_nao_posicao(self):
        ts = self.ts
        self.codigo = code_block(["df.index"], font_size=22)
        saida = mono("RangeIndex(start=0, stop=5, step=1)", font_size=17, color=CINZA)
        limitar(self.codigo, 5.2)
        limitar(saida, 5.2)
        self.codigo.move_to([3.9, 1.9, 0])
        saida.next_to(self.codigo, DOWN, buff=0.25)
        ts.play(FadeIn(self.codigo), FadeIn(saida))
        ts.next_slide()

        self.nota = text("o índice é RÓTULO,\nnão posição", font_size=30,
                         weight="BOLD", color=BEAMER_GREEN)
        limitar(self.nota, 5.2)
        self.nota.move_to([3.9, 0.3, 0])
        ts.play(Write(self.nota))
        ts.next_slide()

        detalhe = text("aqui os dois coincidem.\nÉ coincidência, e vai acabar agora.",
                       font_size=22, color=CINZA)
        limitar(detalhe, 5.2)
        detalhe.next_to(self.nota, DOWN, buff=0.4)
        ts.play(FadeIn(detalhe))
        ts.next_slide()

        # a deixa emenda direto no set_index
        ts.play(Transform(self.codigo, limitar(code_block(
                    ['df = df.set_index("produto")'], font_size=20), 5.2
                ).move_to(self.codigo.get_center())),
                FadeOut(saida), FadeOut(detalhe))
        ts.next_slide()

    def coluna_produtos_vira_indice(self):
        """A coluna `produto` sobe, sai, e a tabela vira a de índice nomeado."""
        ts = self.ts
        nova = Tabela(
            colunas=["vendedor", "valor", "status"],
            linhas=[[l[0], l[2], l[3]] for l in LINHAS],
            larguras=[2.0, 1.5, 2.0],
            indices=PRODUTOS, larg_idx=2.2, nome_indice="produto",
        )
        nova.scale(0.84).move_to([-3.1, -0.3, 0])
        alvo_faixa = nova.faixa_indice()

        # Uma animação só: a tabela inteira MORFA na nova, e a coluna "produto"
        # atravessa a tela virando a faixa de índice. É esse morph que conta a
        # história do set_index: nada de FadeOut antes, que só duplicaria o
        # movimento (a coluna sairia e voltaria para refazer o caminho).
        ts.play(ReplacementTransform(self.tabela, nova),
                Transform(self.realce,
                          Rectangle(width=alvo_faixa.width + 0.12,
                                    height=alvo_faixa.height + 0.12,
                                    color=DESTAQUE, stroke_width=4
                                    ).move_to(alvo_faixa.get_center())),
                run_time=1.6)
        self.tabela = nova
        ts.next_slide()

        ts.play(Transform(self.nota, limitar(
            text("os rótulos agora\nsão nomes", font_size=30, weight="BOLD",
                 color=BEAMER_GREEN), 5.2).move_to(self.nota.get_center())))
        ts.next_slide()

    def enderecar_pelo_rotulo(self):
        ts = self.ts
        lin = self.tabela.linha(2)
        ts.play(Transform(self.codigo, limitar(code_block(['df.loc["mouse"]'],
                                                          font_size=20), 5.2
                                               ).move_to(self.codigo.get_center())),
                Transform(self.realce,
                          Rectangle(width=lin.width + 0.12, height=lin.height + 0.12,
                                    color=DESTAQUE, stroke_width=4).move_to(lin.get_center())))
        ts.next_slide()

    def o_numero_nao_endereca_mais_nada(self):
        """O KeyError, que é a prova de que rótulo não é posição."""
        ts = self.ts
        erro = mono("KeyError: 2", font_size=26, color="#c0392b", weight="BOLD")
        erro.move_to(self.nota.get_center())
        ts.play(Transform(self.codigo, limitar(code_block(["df.loc[2]"], font_size=20), 5.2
                                               ).move_to(self.codigo.get_center())),
                FadeTransform(self.nota, erro))
        ts.next_slide()

        prova = text("o 2 não é rótulo de nada:\nposição nunca foi o endereço",
                     font_size=22, color=CINZA)
        limitar(prova, 5.2)
        prova.next_to(erro, DOWN, buff=0.45)
        ts.play(FadeIn(prova))
        ts.next_slide()

        self.fecho = text(".loc fala de RÓTULO\n.iloc fala de POSIÇÃO", font_size=27,
                          weight="BOLD", color=BEAMER_GREEN)
        limitar(self.fecho, 5.2)
        self.fecho.move_to(erro.get_center())
        ts.play(Transform(self.codigo, limitar(code_block(["df.iloc[2]"], font_size=20), 5.2
                                               ).move_to(self.codigo.get_center())),
                FadeTransform(erro, self.fecho), FadeOut(prova),
                Indicate(self.tabela.linha(2), color=BEAMER_GREEN))
        ts.next_slide()

    # ── bloco 4: a consulta ──────────────────────────────────────────────────

    def vira_a_cena_da_consulta(self):
        ts = self.ts
        ts.play(
            Transform(self.titulo_atual, titulo("Uma consulta")),
            FadeOut(self.fecho), FadeOut(self.realce), FadeOut(self.codigo),
            self.tabela.animate.move_to([-3.1, -0.5, 0]),
            run_time=1.2,
        )
        ts.next_slide()

    def a_mascara_booleana(self):
        ts = self.ts
        self.codigo = code_block(['df["valor"] > 1000'], font_size=20)
        limitar(self.codigo, 5.2)
        self.codigo.move_to([3.9, 2.3, 0])
        ts.play(FadeIn(self.codigo))
        ts.next_slide()

        self.mascara = serie_vertical(PRODUTOS, MASCARA_TXT,
                                      largura_idx=2.2, largura_val=1.5)
        self.mascara.scale(0.84).move_to([3.9, -0.5, 0])
        self.titulo_m = mono("máscara booleana", font_size=20, color=CINZA)
        self.titulo_m.next_to(self.mascara, UP, buff=0.22)
        ts.play(FadeIn(self.titulo_m))
        for i, item in enumerate(self.mascara):
            ts.play(FadeIn(item), Indicate(self.tabela.corpo[i][1], color=DESTAQUE),
                    run_time=0.34)
        ts.next_slide()

        nota = text("não é True nem False: é outra coluna, do mesmo tamanho",
                    font_size=24, color=CINZA)
        limitar(nota, 12.0)
        nota.to_edge(DOWN, buff=0.4)
        ts.play(FadeIn(nota))
        ts.next_slide()

        ts.play(Transform(self.codigo, limitar(code_block(['df[df["valor"] > 1000]'],
                                                          font_size=20), 5.2
                                               ).move_to(self.codigo.get_center())),
                FadeOut(nota))
        ts.next_slide()

    def o_filtro_e_os_rotulos_que_ficam(self):
        """Aqui o FadeOut é o próprio significado: a linha foi descartada."""
        ts = self.ts
        fora = [i for i in range(len(LINHAS)) if i not in SOBRAM]
        ts.play(*[FadeOut(self.tabela.linha(i)) for i in fora],
                *[FadeOut(self.mascara[i]) for i in fora])
        ts.next_slide()

        for i in SOBRAM:
            ts.play(Indicate(self.tabela.rotulos[i], color=DESTAQUE, scale_factor=1.4),
                    run_time=0.4)
        ts.next_slide()

        # A máscara ficou com buracos onde as linhas saíram. Transformar aquilo
        # espalhado direto em texto fica feio: primeiro os sobreviventes se
        # juntam, e só então o bloco arrumado vira a frase.
        sobreviventes = VGroup(*[self.mascara[i] for i in SOBRAM])
        ts.play(FadeOut(self.titulo_m),
                sobreviventes.animate.arrange(DOWN, buff=0).move_to([3.9, 0.9, 0]),
                run_time=0.9)
        ts.next_slide()

        conclusao = text("notebook, mesa, monitor", font_size=30,
                         weight="BOLD", color=BEAMER_GREEN)
        limitar(conclusao, 5.2)
        conclusao.move_to([3.9, 0.9, 0])
        ts.play(FadeTransform(sobreviventes, conclusao), run_time=1.0)
        ts.next_slide()

        detalhe = text("os rótulos vieram junto.\nO que sobrou sabe de onde veio.",
                       font_size=22, color=CINZA)
        limitar(detalhe, 5.2)
        detalhe.next_to(conclusao, DOWN, buff=0.45)
        ts.play(FadeIn(detalhe))
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# 2: Juntar duas tabelas: merge
# ─────────────────────────────────────────────────────────────────────────────

V_COLS = ["vendedor", "produto", "valor"]
V_LARG = [1.9, 2.0, 1.4]
V_LINHAS = [
    ["Ana", "notebook", "3200.0"],
    ["Ana", "cadeira", "890.0"],
    ["Bruno", "mouse", "150.0"],
    ["Carla", "monitor", "1450.0"],
]
REGIOES = [["Ana", "Sudeste"], ["Bruno", "Sul"], ["Diego", "Nordeste"]]


class MergeSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Juntar duas tabelas", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))

        vendas = Tabela(colunas=V_COLS, linhas=V_LINHAS, larguras=V_LARG)
        vendas.scale(0.8).move_to([-3.5, -0.3, 0])
        rot_v = mono("vendas", font_size=20, color=CINZA).next_to(vendas, UP, buff=0.2)

        vendedores = Tabela(colunas=["vendedor", "regiao"], linhas=REGIOES,
                            larguras=[1.9, 2.0])
        vendedores.scale(0.8).move_to([3.4, 0.2, 0])
        rot_d = mono("vendedores", font_size=20, color=CINZA).next_to(vendedores, UP, buff=0.2)

        ts.play(FadeIn(vendas), FadeIn(rot_v))
        ts.next_slide()
        ts.play(FadeIn(vendedores), FadeIn(rot_d))
        ts.next_slide()

        # ── a chave: a coluna que as duas têm ────────────────────────────────
        c1, c2 = vendas.coluna(0), vendedores.coluna(0)
        r1 = Rectangle(width=c1.width + 0.1, height=c1.height + 0.1,
                       color=DESTAQUE, stroke_width=4).move_to(c1.get_center())
        r2 = Rectangle(width=c2.width + 0.1, height=c2.height + 0.1,
                       color=DESTAQUE, stroke_width=4).move_to(c2.get_center())
        ts.play(Create(r1), Create(r2))

        chave = text("a chave: a coluna que as duas têm", font_size=25, color=CINZA)
        limitar(chave, 12.0)
        chave.to_edge(DOWN, buff=0.5)
        ts.play(FadeIn(chave))
        ts.next_slide()

        # ── o merge: a coluna regiao entra na esquerda ───────────────────────
        codigo = code_block(['vendas.merge(vendedores,',
                             '             on="vendedor", how="left")'], font_size=19)
        limitar(codigo, 5.0)
        codigo.move_to([0, 2.2, 0])
        ts.play(FadeIn(codigo), FadeOut(chave))
        ts.next_slide()

        juntas = Tabela(
            colunas=V_COLS + ["regiao"],
            linhas=[l + [r] for l, r in zip(V_LINHAS, ["Sudeste", "Sudeste", "Sul", "NaN"])],
            larguras=V_LARG + [2.0],
        )
        juntas.scale(0.8).move_to([-2.2, -0.3, 0])
        alvo_rot = mono("vendas", font_size=20, color=CINZA).next_to(juntas, UP, buff=0.2)
        ts.play(
            ReplacementTransform(vendas, juntas),
            Transform(rot_v, alvo_rot),
            FadeOut(r1), FadeOut(r2),
            vendedores.animate.scale(0.82).move_to([4.9, 0.2, 0]),
            rot_d.animate.scale(0.82).move_to([4.9, 1.35, 0]),
            run_time=1.4,
        )
        ts.next_slide()

        # ── quem não casou ───────────────────────────────────────────────────
        carla = Rectangle(width=juntas.linha(3).width + 0.1,
                          height=juntas.linha(3).height + 0.1,
                          color="#c0392b", stroke_width=4)
        carla.move_to(juntas.linha(3).get_center())
        nota = text("Carla não está na tabela da direita → NaN\n"
                    "Diego não está na da esquerda → ficou de fora",
                    font_size=23, color=CINZA)
        limitar(nota, 12.0)
        nota.to_edge(DOWN, buff=0.45)
        ts.play(Create(carla), FadeIn(nota))
        ts.next_slide()

        # ── how="inner" descarta ─────────────────────────────────────────────
        alvo_cod = code_block(['vendas.merge(vendedores,',
                               '             on="vendedor", how="inner")'], font_size=19)
        limitar(alvo_cod, 5.0)
        alvo_cod.move_to(codigo.get_center())
        ts.play(Transform(codigo, alvo_cod))
        ts.play(FadeOut(juntas.linha(3)), FadeOut(carla))
        ts.next_slide()

        fecho = text("a chave diz quem casa  ·  o how diz quem sobrevive",
                     font_size=27, weight="BOLD", color=BEAMER_GREEN)
        limitar(fecho, 12.0)
        fecho.move_to(nota.get_center())
        ts.play(FadeTransform(nota, fecho))
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# 3: Mudar a forma: melt
# ─────────────────────────────────────────────────────────────────────────────

LARGO_COLS = ["vendedor", "jan", "fev", "mar"]
LARGO = [["Ana", "4090", "3200", "2800"], ["Bruno", "150", "1200", "3100"]]
LONGO = [
    ["Ana", "jan", "4090"], ["Bruno", "jan", "150"],
    ["Ana", "fev", "3200"], ["Bruno", "fev", "1200"],
    ["Ana", "mar", "2800"], ["Bruno", "mar", "3100"],
]


class MeltSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Mudar a forma", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))

        largo = Tabela(colunas=LARGO_COLS, linhas=LARGO, larguras=[1.9, 1.4, 1.4, 1.4])
        largo.scale(0.9).move_to([-3.0, 0.72, 0])
        rot_l = mono("largo: bom de LER", font_size=20, color=CINZA)
        rot_l.next_to(largo, UP, buff=0.22)
        ts.play(FadeIn(largo), FadeIn(rot_l))
        ts.next_slide()

        # os meses são NOMES DE COLUNA
        meses = VGroup(largo.cabecalho[1], largo.cabecalho[2], largo.cabecalho[3])
        realce = Rectangle(width=meses.width + 0.1, height=meses.height + 0.1,
                           color=DESTAQUE, stroke_width=4).move_to(meses.get_center())
        nota = text("jan, fev e mar são NOMES DE COLUNA", font_size=24, color=CINZA)
        limitar(nota, 6.0)
        nota.move_to([3.6, 1.2, 0])
        ts.play(Create(realce), FadeIn(nota))
        ts.next_slide()

        codigo = code_block(['largo.melt(id_vars="vendedor",',
                             '           var_name="mes",',
                             '           value_name="valor")'], font_size=19)
        limitar(codigo, 6.2)
        codigo.move_to([3.6, -1.6, 0])
        ts.play(FadeIn(codigo))
        ts.next_slide()

        longo = Tabela(colunas=["vendedor", "mes", "valor"], linhas=LONGO,
                       larguras=[1.9, 1.4, 1.6])
        longo.scale(0.9).move_to([-3.0, -0.33, 0])
        alvo_rot = mono("longo: bom de CALCULAR", font_size=20, color=CINZA)
        alvo_rot.next_to(longo, UP, buff=0.22)
        alvo_nota = text("agora eles são VALOR\nda coluna 'mes'", font_size=24, color=CINZA)
        limitar(alvo_nota, 6.0)
        alvo_nota.move_to(nota.get_center())

        ts.play(FadeOut(realce), run_time=0.4)
        ts.play(ReplacementTransform(largo, longo),
                Transform(rot_l, alvo_rot),
                Transform(nota, alvo_nota),
                run_time=1.6)
        ts.next_slide()

        # ── e volta ──────────────────────────────────────────────────────────
        alvo_cod = code_block(['longo.pivot(index="vendedor",',
                               '            columns="mes",',
                               '            values="valor")'], font_size=19)
        limitar(alvo_cod, 6.2)
        alvo_cod.move_to(codigo.get_center())
        ts.play(Transform(codigo, alvo_cod))
        ts.next_slide()

        volta = Tabela(colunas=["fev", "jan", "mar"],
                       linhas=[["3200", "4090", "2800"], ["1200", "150", "3100"]],
                       larguras=[1.4, 1.4, 1.4],
                       indices=["Ana", "Bruno"], larg_idx=1.9, nome_indice="vendedor")
        volta.scale(0.9).move_to([-3.0, 0.72, 0])
        alvo_rot2 = mono("largo de novo", font_size=20, color=CINZA)
        alvo_rot2.next_to(volta, UP, buff=0.22)
        ts.play(ReplacementTransform(longo, volta), Transform(rot_l, alvo_rot2),
                run_time=1.4)
        ts.next_slide()

        fecho = text("mesmo dado, duas formas.\nGráfico e groupby querem o LONGO.",
                     font_size=26, weight="BOLD", color=BEAMER_GREEN)
        limitar(fecho, 6.0)
        fecho.move_to(nota.get_center())
        ts.play(FadeTransform(nota, fecho))
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# 4: Recap
# ─────────────────────────────────────────────────────────────────────────────

class RecapSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Três peças", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        itens = [
            ("DataFrame", "a tabela inteira", "df"),
            ("Series", "uma coluna, ou uma linha", 'df["valor"]'),
            ("índice", "o rótulo, que vem junto no filtro", "df.index"),
        ]
        y = 1.5
        for nome, desc, cod in itens:
            titulo = text(nome, font_size=32, weight="BOLD", color=PY_BLUE)
            corpo = text(desc, font_size=26, color=BLACK)
            cb = code_block([cod], font_size=20)

            titulo.move_to([-5.4, y, 0]).align_to([-5.4, y, 0], LEFT)
            corpo.next_to(titulo, RIGHT, buff=0.5)
            limitar(cb, 3.6)
            cb.move_to([5.0, y, 0])

            ts.play(Write(titulo), FadeIn(corpo), FadeIn(cb))
            ts.next_slide()
            y -= 1.5


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Scene classes: a ordem é a ordem da apresentação
# ─────────────────────────────────────────────────────────────────────────────

class EndHeldSlideShow(SlideShow):
    """SlideShow que termina segurando o conteúdo, em vez de desaparecer."""

    def construct(self):
        for slide in self.slides:
            slide.draw(origin=None, scale=1.0, target_scene=self, animate=True)
        self.wait(1)


class PdIntro_01_Tabela(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[TabelaSlide()], **kwargs)


class PdIntro_02_Merge(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[MergeSlide()], **kwargs)


class PdIntro_03_Melt(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[MeltSlide()], **kwargs)


class PdIntro_04_Recap(EndHeldSlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[RecapSlide()], **kwargs)
