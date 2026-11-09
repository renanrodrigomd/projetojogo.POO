"""Cenário da fase: fundo com paralaxe, chão e portal de saída."""

import functools

import pygame

from caminhos import asset
from config import LARGURA, ALTURA, CHAO_Y
from ui.fontes import texto


@functools.lru_cache(maxsize=1)
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
        x = final - camera_x

        if not (-100 < x < LARGURA + 100):
            return

        cor = (80, 210, 255) if liberada else (200, 90, 90)
        cor_texto = (150, 230, 255) if liberada else (240, 150, 150)

        pygame.draw.rect(
            tela, (15, 25, 35),
            (x, CHAO_Y - 155, 95, 155), border_radius=12
        )
        pygame.draw.rect(
            tela, cor,
            (x + 8, CHAO_Y - 147, 79, 147), 4, border_radius=10
        )

        for i in range(4):
            yy = CHAO_Y - 125 + i * 30
            pygame.draw.line(tela, cor, (x + 20, yy), (x + 75, yy), 3)

        texto(
            tela, "SAÍDA" if liberada else "BLOQUEADA", 18, cor_texto,
            (x + 47, CHAO_Y - 180), centralizado=True
        )
