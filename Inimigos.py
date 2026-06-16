import pygame

class Inimigo:

    def __init__(self, x, y):

        self.posx = 1000
        self.posy = 550

        self.largura = 40
        self.altura = 60

        self.velocidade = 4

        self.limite_esquerda = x - 100
        self.limite_direita = x + 100

        self.vida = 2

    def mover(self, player_x):
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
    
     
    def atualizar(self):
        self.limite_esquerda = self.posx - 4
        self.limite_direita = self.posx + 1

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