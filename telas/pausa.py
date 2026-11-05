"""Tela de pausa (aparece POR CIMA da partida, que fica congelada)."""

import pygame

from config import LARGURA, ALTURA, COR_PAINEL, COR_BORDA, COR_CIANO, \
    COR_TEXTO_SUAVE
from telas.tela_base import Tela
from ui.botoes import BotaoTexto, MenuBotoes
from ui.fontes import texto


class Pausa(Tela):
    transparente = True

    def __init__(self, gerenciador, jogo):
        super().__init__(gerenciador)

        self._jogo = jogo

        self._veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self._veu.fill((0, 0, 0, 170))

        x = LARGURA // 2
        botoes = [
            BotaoTexto("CONTINUAR", (x, 305), 300),
            BotaoTexto("COMO JOGAR", (x, 368), 300),
            BotaoTexto("REINICIAR FASE", (x, 431), 300),
            BotaoTexto("MENU PRINCIPAL", (x, 494), 300),
        ]

        self._menu = MenuBotoes(
            botoes,
            [self._continuar, self._como_jogar, self._reiniciar, self._ir_menu]
        )

    def _continuar(self):
        self.gerenciador.desempilhar()

    def _como_jogar(self):
        from telas.menu import ComoJogar
        self.gerenciador.empilhar(ComoJogar(self.gerenciador))

    def _reiniciar(self):
        from telas.tela_jogo import TelaJogo
        self.gerenciador.trocar(TelaJogo(
            self.gerenciador, self._jogo.indice_fase,
            self._jogo.pontuacao_inicial
        ), fade=True)

    def _ir_menu(self):
        from telas.menu import MenuPrincipal
        self.gerenciador.trocar(MenuPrincipal(self.gerenciador), fade=True)

    def eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (
            pygame.K_ESCAPE, pygame.K_p
        ):
            self._continuar()
            return

        self._menu.eventos(evento)

    def desenhar(self, superficie):
        superficie.blit(self._veu, (0, 0))

        painel = pygame.Rect(LARGURA // 2 - 190, 175, 380, 370)
        pygame.draw.rect(superficie, COR_PAINEL, painel, border_radius=16)
        pygame.draw.rect(superficie, COR_BORDA, painel, 2, border_radius=16)

        texto(superficie, "PAUSA", 36, COR_CIANO, (LARGURA // 2, 235), True)
        self._menu.desenhar(superficie)

        texto(superficie, "ESC  •  continuar", 14, COR_TEXTO_SUAVE,
              (LARGURA // 2, 527), True)
