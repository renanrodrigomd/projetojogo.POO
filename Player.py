import pygame
import math

from Personagem import Personagem


class Player(Personagem):

    def __init__(self):
        super().__init__(100, 550)

        self.ultima_horizontal = "d"

        self.velocidade = 5

        self.velocidade_y = 0
        self.gravidade = 0.5
        self.forca_pulo = -12

        self.no_chao = True

        self.vida = 3

        # O Player pode atirar a cada 0,3 segundo.
        self.cooldown_tiro = 300

    def mover(self):
        teclas = pygame.key.get_pressed()

        esquerda = (
            teclas[pygame.K_a]
            or teclas[pygame.K_LEFT]
        )

        direita = (
            teclas[pygame.K_d]
            or teclas[pygame.K_RIGHT]
        )

        cima = (
            teclas[pygame.K_w]
            or teclas[pygame.K_UP]
        )

        if esquerda:
            self.posx -= self.velocidade
            self.ultima_horizontal = "a"

        if direita:
            self.posx += self.velocidade
            self.ultima_horizontal = "d"

        if esquerda and cima:
            self.direcao_olhar = "aw"

        elif direita and cima:
            self.direcao_olhar = "dw"

        elif cima:
            self.direcao_olhar = "w"

        elif esquerda:
            self.direcao_olhar = "a"

        elif direita:
            self.direcao_olhar = "d"

        else:
            self.direcao_olhar = self.ultima_horizontal

        if self.posx < 0:
            self.posx = 0

        if self.posx > 1200 - self.largura:
            self.posx = 1200 - self.largura

    def pular(self):
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_SPACE] and self.no_chao:
            self.velocidade_y = self.forca_pulo
            self.no_chao = False

    def atualizar(self):
        self.velocidade_y += self.gravidade
        self.posy += self.velocidade_y

        if self.posy >= 550:
            self.posy = 550
            self.velocidade_y = 0
            self.no_chao = True

        self.atualizar_tiros()

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

        vetores = {
            "a": (-1, 0),
            "d": (1, 0),
            "aw": (-1, -1),
            "dw": (1, -1),
            "w": (0, -1)
        }

        dx, dy = vetores[self.direcao_olhar]

        tamanho = math.sqrt(
            dx * dx + dy * dy
        )

        dx /= tamanho
        dy /= tamanho

        comprimento = 120

        inicio = (
            self.posx + self.largura // 2,
            self.posy + self.altura // 2
        )

        fim = (
            inicio[0] + dx * comprimento,
            inicio[1] + dy * comprimento
        )

        pygame.draw.line(
            tela,
            (255, 0, 0),
            inicio,
            fim,
            3
        )

        for tiro in self.tiros:
            tiro.desenhar(tela)