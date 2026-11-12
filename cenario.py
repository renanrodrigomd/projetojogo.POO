"""Cenário da fase: fundo com paralaxe, chão e portal de saída."""

import functools

import pygame

from caminhos import asset
from config import LARGURA, ALTURA, CHAO_Y
from ui.fontes import texto


@functools.lru_cache(maxsize=1)
def carregar_porta_saida():

    porta = pygame.image.load(
        asset("background", "PortadeSaida.png")
    ).convert_alpha()

    return pygame.transform.smoothscale(porta, (220,230))
def carregar_imagens():
    """Carrega e redimensiona as imagens uma única vez (cache)."""
    fundo = pygame.image.load(
        asset("background", "Backgroundjogo.png")
    ).convert()
    fundo = pygame.transform.smoothscale(
        fundo, (int(fundo.get_width() * 0.95), int(fundo.get_height() * 0.95))
    )

   
    chao = pygame.image.load(
        asset("background", "chaojogo.png")
    ).convert_alpha()
    chao = pygame.transform.smoothscale(
        chao, (int(chao.get_width() * 0.50), int(chao.get_height() * 0.50))
    )

    return fundo, chao


class Cenario:
    FATOR_PARALAXE = 0.35

    def __init__(self):
        self._fundo, self._chao = carregar_imagens()
        self._porta_saida = carregar_porta_saida()

    def desenhar_fundo(self, tela, camera_x, camera_y):
        largura_fundo = self._fundo.get_width()
        deslocamento = int(camera_x * self.FATOR_PARALAXE)
        inicio_x = -(deslocamento % largura_fundo) - largura_fundo

        for x in range(inicio_x, LARGURA + largura_fundo, largura_fundo):
            tela.blit(self._fundo, (x, -camera_y))

    def desenhar_chao(self, tela, camera_x, camera_y):
        # Parte inferior (abaixo do chão)
        pygame.draw.rect(
            tela, (22, 25, 31),
            (0, CHAO_Y + 150 - camera_y, LARGURA, ALTURA)
        )

        # Chão repetido na horizontal
        largura_chao = self._chao.get_width()
        inicio_x = -(int(camera_x) % largura_chao)

        for x in range(inicio_x - largura_chao,
                       LARGURA + largura_chao, largura_chao):
            tela.blit(self._chao, (x, CHAO_Y - 75 - camera_y))

    def desenhar(self, tela, camera_x, camera_y):
        self.desenhar_fundo(tela, camera_x, camera_y)
        self.desenhar_chao(tela, camera_x, camera_y)

    def desenhar_saida(self, tela, camera_x, final, liberada):
        """Portal de saída. Fica azul quando a área está limpa e
        vermelho enquanto ainda há robôs vivos."""
        largura = self._porta_saida.get_width()
        altura = self._porta_saida.get_height()

        x = int(final - camera_x - largura / 2)
        y = int(CHAO_Y - altura + 5)

        if x > LARGURA or x + largura < 0:
           return

        tela.blit(self._porta_saida, (x, y))

        cor = (100, 235, 150) if liberada else (245, 105, 95)

        estado = "SAÍDA LIBERADA" if liberada else "ÁREA BLOQUEADA"

        texto(
            tela, estado, 16, cor,
            (x + largura // 2, y - 18),
            centralizado=True
       )