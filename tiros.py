import pygame
import math


class Tiro:

    def __init__(self, x, y, dx, dy):
        self.posx = x
        self.posy = y

        # Normaliza a direção para manter a mesma velocidade
        # quando o tiro é diagonal.
        tamanho = math.sqrt(
            dx * dx + dy * dy
        )

        self.dx = dx / tamanho
        self.dy = dy / tamanho

        self.velocidade = 12
        self.ativo = True

    def atualizar(self):

        self.posx += self.dx * self.velocidade
        self.posy += self.dy * self.velocidade

        # Desativa o tiro quando ele sai da área da tela.
        if (
            self.posx < -20
            or self.posx > 1250
            or self.posy < -20
            or self.posy > 720
        ):
            self.ativo = False

    def get_rect(self):

        return pygame.Rect(
            self.posx - 5,
            self.posy - 5,
            10,
            10
        )

    def desenhar(self, tela):

        pygame.draw.circle(
            tela,
            (255, 255, 0),
            (
                int(self.posx),
                int(self.posy)
            ),
            5
        )