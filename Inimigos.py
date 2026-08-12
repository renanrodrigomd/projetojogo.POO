import pygame
import math

from Personagem import Personagem


class Inimigo(Personagem):

    def __init__(self, x, y):
        super().__init__(x, y)

        self.vivo = True
        self.vida = 2
        self.velocidade = 3

        # O inimigo começa a atacar quando o Player
        # estiver a até 300 pixels.
        self.alcance_ataque = 500

        # 1000 ms = 1 segundo.
        self.cooldown_tiro = 2000

    def mover(self, player_x):
        if not self.vivo:
            return

        distancia = player_x - self.posx

        if abs(distancia) > self.alcance_ataque:

            if distancia > 0:
                self.posx += self.velocidade

            else:
                self.posx -= self.velocidade

    def olhar_player(self, player_x, player_y):
        distancia_x = player_x - self.posx
        distancia_y = player_y - self.posy

        if distancia_x > 0:

            if distancia_y < -20:
                self.direcao_olhar = "dw"

            else:
                self.direcao_olhar = "d"

        else:

            if distancia_y < -20:
                self.direcao_olhar = "aw"

            else:
                self.direcao_olhar = "a"

        if abs(distancia_x) < 30 and distancia_y < 0:
            self.direcao_olhar = "w"

    def pode_atacar(self, player_x):
        distancia = abs(
            player_x - self.posx
        )

        return distancia <= self.alcance_ataque

    def atualizar(self):
        if not self.vivo:
            return

        self.atualizar_tiros()

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
            (0, 255, 0),
            inicio,
            fim,
            3
        )

        for tiro in self.tiros:
            tiro.desenhar(tela)