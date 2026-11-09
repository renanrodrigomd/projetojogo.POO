"""Fundo com a cidade em ruínas rolando devagar (menus e telas finais)."""

import pygame

from cenario import carregar_imagens
from config import LARGURA, ALTURA
from mundo.destrocos import Destrocos


class FundoAnimado:
    VELOCIDADE = 22  # pixels por segundo

    def __init__(self, escurecimento=150, destrocos_acima_do_veu=False):
        self._imagem, _ = carregar_imagens()
        self._deslocamento = 0.0
        self._destrocos_acima = destrocos_acima_do_veu
        self._destrocos = Destrocos(0.8, semente=7)

        self._veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self._veu.fill((6, 10, 18, escurecimento))

    def atualizar(self, dt):
        self._destrocos.atualizar(dt)
        self._deslocamento = (
            self._deslocamento + self.VELOCIDADE * dt / 1000
        ) % self._imagem.get_width()

    def desenhar(self, tela):
        largura = self._imagem.get_width()
        x = -int(self._deslocamento)

        while x < LARGURA:
            tela.blit(self._imagem, (x, 0))
            x += largura

        # Com o véu muito escuro, os destroços vão por cima dele para
        # continuarem visíveis (usado no menu).
        if self._destrocos_acima:
            tela.blit(self._veu, (0, 0))
            self._destrocos.desenhar(tela, self._deslocamento / 0.35)
        else:
            self._destrocos.desenhar(tela, self._deslocamento / 0.35)
            tela.blit(self._veu, (0, 0))
