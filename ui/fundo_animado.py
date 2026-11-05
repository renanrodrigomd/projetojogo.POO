"""Fundo com a cidade em ruínas rolando devagar (menus e telas finais)."""

import pygame

from cenario import carregar_imagens
from config import LARGURA, ALTURA


class FundoAnimado:
    VELOCIDADE = 22  # pixels por segundo

    def __init__(self, escurecimento=150):
        self._imagem, _ = carregar_imagens()
        self._deslocamento = 0.0

        self._veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self._veu.fill((6, 10, 18, escurecimento))

    def atualizar(self, dt):
        self._deslocamento = (
            self._deslocamento + self.VELOCIDADE * dt / 1000
        ) % self._imagem.get_width()

    def desenhar(self, tela):
        largura = self._imagem.get_width()
        x = -int(self._deslocamento)

        while x < LARGURA:
            tela.blit(self._imagem, (x, 0))
            x += largura

        tela.blit(self._veu, (0, 0))
