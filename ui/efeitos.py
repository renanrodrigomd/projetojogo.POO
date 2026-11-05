"""Efeitos visuais leves da partida: texto flutuante, vinheta e tremor."""

import random

import pygame

from config import LARGURA, ALTURA
from ui.fontes import texto


class _TextoFlutuante:
    def __init__(self, x, y, mensagem, cor, duracao):
        self.x = x
        self.y = y
        self.mensagem = mensagem
        self.cor = cor
        self.duracao = duracao
        self.idade = 0


class TextosFlutuantes:
    """Textos como "+100" e "-1" que sobem e somem."""

    SUBIDA = 45  # pixels percorridos durante a vida do texto

    def __init__(self):
        self._itens = []

    def adicionar(self, x, y, mensagem, cor, duracao=800):
        self._itens.append(_TextoFlutuante(x, y, mensagem, cor, duracao))

    def atualizar(self, dt):
        for item in self._itens:
            item.idade += dt

        self._itens = [i for i in self._itens if i.idade < i.duracao]

    def desenhar(self, tela, camera_x, camera_y):
        for item in self._itens:
            progresso = item.idade / item.duracao
            alfa = 255 * (1 - progresso) if progresso > 0.5 else 255

            texto(
                tela, item.mensagem, 26, item.cor,
                (item.x - camera_x, item.y - camera_y - progresso * self.SUBIDA),
                centralizado=True, alfa=alfa
            )


class Vinheta:
    """Bordas vermelhas que aparecem quando o jogador leva dano."""

    DURACAO = 450

    def __init__(self):
        self._imagem = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

        camadas = 14
        for i in range(camadas):
            alfa = int(150 * (1 - i / camadas) ** 2)
            pygame.draw.rect(
                self._imagem, (200, 20, 30, alfa),
                (i * 6, i * 6, LARGURA - i * 12, ALTURA - i * 12), 6
            )

        self._restante = 0

    def disparar(self):
        self._restante = self.DURACAO

    def atualizar(self, dt):
        self._restante = max(0, self._restante - dt)

    def desenhar(self, tela):
        if self._restante > 0:
            self._imagem.set_alpha(int(255 * self._restante / self.DURACAO))
            tela.blit(self._imagem, (0, 0))


class Tremor:
    """Tremor de câmera que diminui até parar."""

    def __init__(self):
        self._restante = 0
        self._duracao = 1
        self._forca = 0

    def disparar(self, duracao=250, forca=6):
        self._restante = duracao
        self._duracao = duracao
        self._forca = forca

    def atualizar(self, dt):
        self._restante = max(0, self._restante - dt)

    def deslocamento(self):
        if self._restante <= 0:
            return 0, 0

        forca = self._forca * self._restante / self._duracao
        return (random.uniform(-forca, forca), random.uniform(-forca, forca))
