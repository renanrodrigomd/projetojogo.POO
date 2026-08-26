import pygame
import math


class Tiro:

    def __init__(self, x, y, dx, dy):
        self.posx = x
        self.posy = y

        tamanho = math.sqrt(
            dx * dx + dy * dy
        )

        self.dx = dx / tamanho
        self.dy = dy / tamanho

        self.velocidade = 8
        self.ativo = True

    def atualizar(self):

        self.posx += self.dx * self.velocidade
        self.posy += self.dy * self.velocidade

        if (
            self.posx < -20
            or self.posx > 10000
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

    def desenhar(self, tela, camera_x = 0, camera_y = 0):

        pygame.draw.circle(
            tela,
            (255, 255, 0),
            (
                int(self.posx - camera_x),
                int(self.posy - camera_y)
            ),
            5
        )


class Missil(Tiro):

    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy)

        # O RPG é maior e mais lento que um tiro comum.
        self.velocidade = 7
        self.tamanho = 12
        self.explodiu = False

    def get_rect(self):

        return pygame.Rect(
            self.posx - self.tamanho,
            self.posy - self.tamanho,
            self.tamanho * 2,
            self.tamanho * 2
        )

    def desenhar(self, tela):

        pygame.draw.circle(
            tela,
            (40, 150, 40),
            (
                int(self.posx),
                int(self.posy)
            ),
            self.tamanho
        )