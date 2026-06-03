import pygame

class Inimigo:

    def __init__(self, x, y):

        self.posx = x
        self.posy = y

        self.largura = 40
        self.altura = 40

        self.velocidade = 2

        self.limite_esquerda = x - 100
        self.limite_direita = x + 100

    def mover(self):

        self.posx += self.velocidade

        if self.posx >= self.limite_direita:
            self.velocidade *= -1

        if self.posx <= self.limite_esquerda:
            self.velocidade *= -1

    def desenhar(self, tela):

        pygame.draw.rect(
            tela,
            (255, 0, 0),
            (
                self.posx,
                self.posy,
                self.largura,
                self.altura
            )
        )