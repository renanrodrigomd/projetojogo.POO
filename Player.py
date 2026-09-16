import pygame
import math

from Personagem import Personagem


class Player(Personagem):

    def __init__(self, x=100, y=550, chao_y=610, largura_mapa=10000):
        super().__init__(x, y)

        self.ultima_horizontal = "d"
        self.velocidade = 5

        self.velocidade_y = 0
        self.gravidade = 0.5
        self.forca_pulo = -12

        self.no_chao = False
        self.chao_y = chao_y

        self.vida = 3
        self.cooldown_tiro = 500
        self.largura_mapa = largura_mapa

    def mover(self):
        teclas = pygame.key.get_pressed()

        esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]
        direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT]

        cima = teclas[pygame.K_w] or teclas[pygame.K_UP]

        # Usa elif para impedir que esquerda e direita sejam
        # aplicadas ao mesmo tempo.
        if esquerda and not direita:
            self.posx -= self.velocidade
            self.ultima_horizontal = "a"
        elif direita and not esquerda:
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

        # Limites horizontais do mapa.
        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

    def pular(self):
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_SPACE] and self.no_chao:
            self.velocidade_y = self.forca_pulo
            self.no_chao = False

    def atualizar(self):
        # Gravidade.
        self.velocidade_y += self.gravidade
        self.posy += self.velocidade_y

        # Chão: a parte inferior do personagem fica exatamente
        # sobre a superfície do chão.
        if self.posy + self.altura >= self.chao_y:
            self.posy = self.chao_y - self.altura
            self.velocidade_y = 0
            self.no_chao = True
        else:
            self.no_chao = False

        self.atualizar_tiros()

    def desenhar(self, tela, camera_x=0, camera_y=0):
        tela_x = self.posx - camera_x
        tela_y = self.posy - camera_y

        pygame.draw.rect(
            tela,
            (255, 167, 0),
            (tela_x, tela_y, self.largura, self.altura)
        )

        vetores = {
            "a": (-1, 0),
            "d": (1, 0),
            "aw": (-1, -1),
            "dw": (1, -1),
            "w": (0, -1)
        }

        dx, dy = vetores[self.direcao_olhar]

        tamanho = math.sqrt(dx * dx + dy * dy)
        dx /= tamanho
        dy /= tamanho

        comprimento = 120

        inicio = (
            tela_x + self.largura // 2,
            tela_y + self.altura // 2
        )

        fim = (
            inicio[0] + dx * comprimento,
            inicio[1] + dy * comprimento
        )

        pygame.draw.line(tela, (255, 0, 0), inicio, fim, 3)

        for tiro in self.tiros:
            tiro.desenhar(tela, camera_x, camera_y)
