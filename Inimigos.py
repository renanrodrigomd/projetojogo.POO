import pygame
#cria a classe inimigo que pode ser abstrata
class Inimigo:

    def __init__(self, x, y):

        self.vivo = True

        self.posx = 1000
        self.posy = 550

        self.largura = 40
        self.altura = 60

        self.velocidade = 4

        self.limite_esquerda = x - 100
        self.limite_direita = x + 100

        self.vida = 5
#segue o player e para se chegar < 300 de distancia
    def mover(self, player_x):
        if not self.vivo:
            return
        distancia = player_x - self.posx
        if abs(distancia) > 300:
            if distancia > 0:
                self.posx += self.velocidade
            else:
                self.posx -= self.velocidade
        
        elif abs(distancia) < 300:
            if distancia < 300:
                self.posx -= self.velocidade
            else:
                self.posx += self.velocidade
#se o inimigo estiver vivo passa tais posições, se não ele desaparece
    def atualizar(self):
        if not self.vivo:
            return
        self.limite_esquerda = self.posx - 4
        self.limite_direita = self.posx + 1
#detecção de colisão
    def get_rect(self):
        return pygame.Rect(
            self.posx,
            self.posy,
            self.largura,
            self.altura
        )
#desenha o inimigo
    def desenhar(self, tela):

        if not self.vivo:
            return

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