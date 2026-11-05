"""Telas de vitória e derrota.

TelaFinal define o esqueleto (fundo, título animado, corpo e botões) e
as filhas só preenchem as partes que mudam (padrão Template Method):
  * herança: TelaDerrota e TelaVitoria herdam de TelaFinal
  * polimorfismo: cada uma desenha seu próprio corpo e tem suas opções
"""

import math
import random
from abc import abstractmethod

import pygame

from config import (
    LARGURA, ALTURA, COR_TEXTO, COR_TEXTO_SUAVE, COR_DESTAQUE, COR_PERIGO,
    COR_CIANO, COR_OK, COR_PAINEL, COR_BORDA
)
from fases import FASES
from recordes import Recordes
from telas.tela_base import Tela
from ui.botoes import BotaoTexto, MenuBotoes
from ui.fontes import texto
from ui.fundo_animado import FundoAnimado
from ui.imagens import titulo_pixel_art


def _formatar_tempo(segundos):
    return f"{int(segundos) // 60:02d}:{int(segundos) % 60:02d}"


class TelaFinal(Tela):
    IMAGEM = ""
    ALTURA_TITULO = 200
    Y_TITULO = 20
    GLITCH = False
    DURACAO_ENTRADA = 500   # ms para o título descer
    ATRASO_BOTOES = 450     # ms até aceitar Enter/clique (evita acidentes)

    def __init__(self, gerenciador, resumo):
        super().__init__(gerenciador)

        self._resumo = resumo
        self._t = 0  # milissegundos desde que a tela abriu

        self._fundo = FundoAnimado(200)
        self._titulo = titulo_pixel_art(self.IMAGEM, self.ALTURA_TITULO)

        opcoes = self._opcoes()
        passo = 270
        inicio = LARGURA // 2 - passo * (len(opcoes) - 1) // 2

        botoes = [
            BotaoTexto(rotulo, (inicio + i * passo, ALTURA - 50), 250, 46)
            for i, (rotulo, _) in enumerate(opcoes)
        ]

        self._menu = MenuBotoes(
            botoes, [acao for _, acao in opcoes], horizontal=True
        )

    @property
    def resumo(self):
        return self._resumo

    # Partes que cada tela filha define

    @abstractmethod
    def _opcoes(self):
        """Lista de (rótulo, ação)."""

    @abstractmethod
    def _desenhar_corpo(self, superficie):
        """Conteúdo entre o título e os botões."""

    # Ações comuns

    def _jogar_fase(self, indice, pontuacao_inicial):
        from telas.tela_jogo import TelaJogo
        self.gerenciador.trocar(
            TelaJogo(self.gerenciador, indice, pontuacao_inicial), fade=True
        )

    def _ir_menu(self):
        from telas.menu import MenuPrincipal
        self.gerenciador.trocar(MenuPrincipal(self.gerenciador), fade=True)

    def _sair(self):
        self.gerenciador.sair()

    # Tela

    def eventos(self, evento):
        if self._t < self.ATRASO_BOTOES:
            return

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._ir_menu()
            return

        self._menu.eventos(evento)

    def atualizar(self, dt):
        self._t += dt
        self._fundo.atualizar(dt)

    def desenhar(self, superficie):
        self._fundo.desenhar(superficie)
        self._desenhar_titulo(superficie)
        self._desenhar_corpo(superficie)

        if self._t >= self.ATRASO_BOTOES:
            self._menu.desenhar(superficie)

    # Título com entrada animada

    def _glitch_ativo(self):
        if not self.GLITCH:
            return False

        return (
            self.DURACAO_ENTRADA < self._t < self.DURACAO_ENTRADA + 450
            or (self._t > 1500 and self._t % 3200 < 140)
        )

    def _desenhar_titulo(self, superficie):
        progresso = min(1.0, self._t / self.DURACAO_ENTRADA)
        suavizado = 1 - (1 - progresso) ** 3  # desacelera ao chegar

        y = int(-self.ALTURA_TITULO
                + suavizado * (self.ALTURA_TITULO + self.Y_TITULO))
        x = LARGURA // 2 - self._titulo.get_width() // 2

        if self._glitch_ativo():
            faixas = 10
            altura_faixa = self.ALTURA_TITULO // faixas

            for i in range(faixas):
                desvio = random.randint(-16, 16) if random.random() < 0.6 else 0
                superficie.blit(
                    self._titulo, (x + desvio, y + i * altura_faixa),
                    pygame.Rect(0, i * altura_faixa,
                                self._titulo.get_width(), altura_faixa),
                    pygame.BLEND_ADD
                )
        else:
            superficie.blit(self._titulo, (x, y), None, pygame.BLEND_ADD)

    # Utilitários de desenho

    @staticmethod
    def _painel(superficie, retangulo):
        pygame.draw.rect(superficie, COR_PAINEL, retangulo, border_radius=14)
        pygame.draw.rect(superficie, COR_BORDA, retangulo, 2, border_radius=14)

    @staticmethod
    def _alfa_linha(t, inicio, duracao=200):
        """0 a 255 conforme a linha vai aparecendo."""
        return max(0, min(255, (t - inicio) * 255 / duracao))


class TelaDerrota(TelaFinal):
    IMAGEM = "Teladederrota.png"
    ALTURA_TITULO = 230
    Y_TITULO = 14
    GLITCH = True

    def _opcoes(self):
        r = self._resumo
        return [
            ("TENTAR NOVAMENTE", lambda: self._jogar_fase(
                r.indice_fase, r.pontuacao_inicial)),
            ("MENU PRINCIPAL", self._ir_menu),
            ("SAIR", self._sair),
        ]

    def _desenhar_corpo(self, superficie):
        r = self._resumo
        t = self._t

        painel = pygame.Rect(300, 258, 600, 306)
        self._painel(superficie, painel)

        linhas = [
            ("CAUSA", r.causa, COR_PERIGO),
            ("PROGRESSO", None, COR_TEXTO),
            ("TEMPO", _formatar_tempo(r.tempo), COR_TEXTO),
            ("ROBÔS DERROTADOS", f"{r.derrotados}/{r.total_inimigos}",
             COR_TEXTO),
            ("PONTOS", f"{r.pontuacao:04d}", COR_DESTAQUE),
        ]

        for i, (rotulo, valor, cor) in enumerate(linhas):
            y = 278 + i * 38
            alfa = self._alfa_linha(t, 600 + i * 140)

            if alfa <= 0:
                continue

            texto(superficie, rotulo, 14, COR_TEXTO_SUAVE, (330, y + 4),
                  alfa=alfa)

            if valor is not None:
                texto(superficie, valor, 20, cor, (570, y), alfa=alfa)
            else:
                self._barra_progresso(superficie, 570, y + 4, r.progresso, alfa)

        # Dica
        alfa = self._alfa_linha(t, 600 + 5 * 140)
        if alfa > 0:
            pygame.draw.line(superficie, COR_BORDA, (330, 488), (870, 488), 1)
            texto(superficie, "DICA", 13, COR_DESTAQUE, (330, 502), alfa=alfa)
            texto(superficie, r.dica, 16, COR_TEXTO, (330, 524),
                  negrito=False, alfa=alfa)

    @staticmethod
    def _barra_progresso(superficie, x, y, progresso, alfa):
        largura = 220

        pygame.draw.rect(superficie, (28, 32, 42), (x, y, largura, 14),
                         border_radius=6)
        pygame.draw.rect(superficie, COR_CIANO,
                         (x, y, int(largura * progresso), 14), border_radius=6)
        pygame.draw.rect(superficie, (210, 215, 225), (x, y, largura, 14), 2,
                         border_radius=6)

        texto(superficie, f"{int(progresso * 100)}%", 18, COR_TEXTO,
              (x + largura + 14, y - 5), alfa=alfa)


class TelaVitoria(TelaFinal):
    IMAGEM = "Vitoria.png"
    ALTURA_TITULO = 190
    Y_TITULO = 14

    DURACAO_CONTAGEM = 1200
    INICIO_CONTAGEM = 500
    INTERVALO_ESTRELA = 450

    def __init__(self, gerenciador, resumo):
        self._novo_recorde = False
        self._recorde_anterior = None
        super().__init__(gerenciador, resumo)

    def ao_entrar(self):
        """Registra o resultado nos recordes (arquivo)."""
        r = self._resumo
        recordes = Recordes()

        self._recorde_anterior = recordes.melhor(r.numero_fase)
        self._novo_recorde = recordes.registrar(
            r.numero_fase, r.pontos_da_fase, r.tempo, r.estrelas
        )

    def _opcoes(self):
        r = self._resumo
        opcoes = []

        if r.indice_fase + 1 < len(FASES):
            opcoes.append(("PRÓXIMA FASE", lambda: self._jogar_fase(
                r.indice_fase + 1, r.pontuacao)))

        opcoes.append(("JOGAR DE NOVO", lambda: self._jogar_fase(
            r.indice_fase, r.pontuacao_inicial)))
        opcoes.append(("MENU PRINCIPAL", self._ir_menu))

        return opcoes

    @staticmethod
    def _pontos_estrela(centro, raio):
        pontos = []
        for i in range(10):
            angulo = -math.pi / 2 + i * math.pi / 5
            r = raio if i % 2 == 0 else raio * 0.45
            pontos.append((centro[0] + math.cos(angulo) * r,
                           centro[1] + math.sin(angulo) * r))
        return pontos

    def _desenhar_corpo(self, superficie):
        r = self._resumo
        t = self._t
        fase = FASES[r.indice_fase]

        # Estrelas acendendo uma a uma
        for i in range(3):
            centro = (LARGURA // 2 + (i - 1) * 110, 270)
            acesa = (i < r.estrelas
                     and t > self.INICIO_CONTAGEM + i * self.INTERVALO_ESTRELA)

            pontos = self._pontos_estrela(centro, 40)

            if acesa:
                pygame.draw.polygon(superficie, COR_DESTAQUE, pontos)
                pygame.draw.polygon(superficie, (255, 245, 200), pontos, 3)
            else:
                pygame.draw.polygon(superficie, (30, 36, 48), pontos)
                pygame.draw.polygon(superficie, COR_BORDA, pontos, 3)

        # Pontuação com contagem animada
        progresso = max(0.0, min(
            1.0, (t - self.INICIO_CONTAGEM) / self.DURACAO_CONTAGEM))
        mostrado = int(r.pontos_da_fase * (1 - (1 - progresso) ** 2))

        texto(superficie, "PONTOS", 14, COR_TEXTO_SUAVE, (LARGURA // 2, 332),
              True)
        texto(superficie, f"{mostrado:04d}", 50, COR_DESTAQUE,
              (LARGURA // 2, 372), True)

        if progresso >= 1:
            if self._novo_recorde:
                piscar = 160 + 95 * (0.5 + 0.5 * math.sin(t / 150))
                texto(superficie, "NOVO RECORDE!", 20, COR_OK,
                      (LARGURA // 2, 412), True, alfa=piscar)
            elif self._recorde_anterior:
                texto(superficie, f"RECORDE  {self._recorde_anterior['pontos']:04d}",
                      16, COR_TEXTO_SUAVE, (LARGURA // 2, 412), True)

        # Detalhes
        painel = pygame.Rect(300, 440, 600, 120)
        self._painel(superficie, painel)

        sem_dano = r.dano_sofrido == 0
        detalhes = [
            ("TEMPO", f"{_formatar_tempo(r.tempo)}   (3 estrelas até "
                      f"{fase.tempo_tres_estrelas}s)", COR_TEXTO, 330, 458),
            ("ROBÔS DERROTADOS", f"{r.derrotados}/{r.total_inimigos}",
             COR_TEXTO, 330, 508),
            ("DANO SOFRIDO", str(r.dano_sofrido),
             COR_OK if sem_dano else COR_TEXTO, 640, 508),
            ("BÔNUS SEM DANO", f"+{r.bonus}" if r.bonus else "—",
             COR_DESTAQUE if r.bonus else COR_TEXTO_SUAVE, 780, 508),
        ]

        for i, (rotulo, valor, cor, x, y) in enumerate(detalhes):
            alfa = self._alfa_linha(t, 900 + i * 150)

            if alfa > 0:
                texto(superficie, rotulo, 12, COR_TEXTO_SUAVE, (x, y),
                      alfa=alfa)
                texto(superficie, valor, 18, cor, (x, y + 16), alfa=alfa)
