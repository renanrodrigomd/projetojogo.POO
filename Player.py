from atirar import Tiro

import pygame

class Player:

    def __init__(self):

        self.posx = 100
        self.posy = 550

        self.largura = 40
        self.altura = 60
        self.tiros = []
        self.velocidade = 5

        self.velocidade_y = 0
        self.gravidade = 0.5
        self.forca_pulo = -12

        self.no_chao = True

        self.vida = 3

    def mover(self):

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.posx -= self.velocidade

        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.posx += self.velocidade

        if self.posx < 0:
            self.posx = 0

        if self.posx > 1200 - self.largura:
            self.posx = 1200 - self.largura

    def pular(self):

        teclas = pygame.key.get_pressed()

        if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP]) and self.no_chao:

            self.velocidade_y = self.forca_pulo
            self.no_chao = False

    def atualizar(self):

        self.velocidade_y += self.gravidade

        self.posy += self.velocidade_y

        if self.posy >= 550:

            self.posy = 550
            self.velocidade_y = 0
            self.no_chao = True

        for tiro in self.tiros[:]:
            tiro.atualizar()

            if not tiro.ativo:
                self.tiros.remove(tiro)
 
    def desenhar(self, tela):

        pygame.draw.rect(
            tela,
            (255, 167, 0),
            (
                self.posx,
                self.posy,
                self.largura,
                self.altura
            )
        )
        for tiro in self.tiros:
            tiro.desenhar(tela)
    
    def atirar(self):
        tiro = Tiro(
            self.posx + self.largura,
            self.posy + self.altura // 2
        )
        self.tiros.append(tiro)