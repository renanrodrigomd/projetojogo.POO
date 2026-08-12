import pygame
import math

from Personagem import Personagem
from tiros import Tiro, Missil


class Inimigo(Personagem):

    def __init__(self, x, y):
        super().__init__(x, y)

        self.vivo = True
        self.vida = 2
        self.velocidade = 3

        self.alcance_ataque = 500
        self.cooldown_tiro = 2000

        # O inimigo usa ângulos em vez das 5 direções do Player.
        self.angulo_olhar = 0

    def mover(self, player_x, player_y):
        pass

    def olhar_player(self, player_x, player_y):
        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        distancia_x = player_x - centro_x
        distancia_y = player_y - centro_y

        # Calcula o ângulo real entre o inimigo e o Player.
        angulo = math.degrees(
            math.atan2(distancia_y, distancia_x)
        )

        # Converte o ângulo para um dos 16 raios disponíveis.
        passo = 360 / 16

        self.angulo_olhar = round(
            angulo / passo
        ) * passo

        self.angulo_olhar %= 360

    def pode_atacar(self, player_x, player_y):
        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        distancia = math.hypot(
            player_x - centro_x,
            player_y - centro_y
        )

        return distancia <= self.alcance_ataque

    def atirar(self):
        agora = pygame.time.get_ticks()

        if agora - self.ultimo_tiro < self.cooldown_tiro:
            return

        self.ultimo_tiro = agora

        radianos = math.radians(
            self.angulo_olhar
        )

        dx = math.cos(radianos)
        dy = math.sin(radianos)

        x = self.posx + self.largura // 2
        y = self.posy + self.altura // 2

        tiro = Tiro(
            x,
            y,
            dx,
            dy
        )

        self.tiros.append(tiro)

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

        radianos = math.radians(
            self.angulo_olhar
        )

        dx = math.cos(radianos)
        dy = math.sin(radianos)

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


class InimigoTerrestre(Inimigo):

    def __init__(self, x, y):
        super().__init__(x, y)

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        distancia = player_x - self.posx

        if abs(distancia) > self.alcance_ataque:

            if distancia > 0:
                self.posx += self.velocidade
            else:
                self.posx -= self.velocidade


class InimigoAereo(Inimigo):

    def __init__(self, x, y):
        super().__init__(x, y)

        self.vida = 2
        self.velocidade = 2

        # Distância horizontal que ele tenta manter do Player.
        self.distancia_minima = 250

        # Altura que ele tenta manter em relação ao Player.
        self.distancia_vertical = 180

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        distancia_x = player_x - centro_x
        distancia_y = player_y - centro_y

        # Mantém uma distância horizontal para não ficar
        # exatamente em cima do Player.
        if abs(distancia_x) > self.distancia_minima:

            if distancia_x > 0:
                self.posx += self.velocidade
            else:
                self.posx -= self.velocidade

        # Mantém uma distância vertical do Player.
        if abs(distancia_y) > self.distancia_vertical:

            if distancia_y > 0:
                self.posy += self.velocidade
            else:
                self.posy -= self.velocidade


class InimigoBlindado(Inimigo):

    def __init__(self, x, y):
        super().__init__(x, y)

        self.vida = 8
        self.velocidade = 1.5

        self.alcance_ataque = 600

        # O blindado dispara mais devagar.
        self.cooldown_tiro = 3000

    def atirar(self):
        agora = pygame.time.get_ticks()

        if agora - self.ultimo_tiro < self.cooldown_tiro:
            return

        self.ultimo_tiro = agora

        radianos = math.radians(
            self.angulo_olhar
        )

        dx = math.cos(radianos)
        dy = math.sin(radianos)

        x = self.posx + self.largura // 2
        y = self.posy + self.altura // 2

        missil = Missil(
            x,
            y,
            dx,
            dy
        )

        self.tiros.append(missil)


class InimigoExplosivo(Inimigo):

    def __init__(self, x, y):
        super().__init__(x, y)

        self.vida = 2

        # Começa devagar.
        self.velocidade = 1

        # Velocidade depois que leva o primeiro tiro.
        self.velocidade_correndo = 6

        self.correndo = False
        self.explodiu = False

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        # Depois de ser atingido, ele não para mais.
        velocidade = (
            self.velocidade_correndo
            if self.correndo
            else self.velocidade
        )

        distancia_x = player_x - self.posx

        if distancia_x > 0:
            self.posx += velocidade
        elif distancia_x < 0:
            self.posx -= velocidade

    def atirar(self):
        # O explosivo não possui ataque à distância.
        return

    def receber_dano(self):
        if not self.vivo:
            return

        self.vida -= 1

        # O primeiro tiro faz o inimigo correr.
        self.correndo = True

        if self.vida <= 0:
            self.vivo = False
            self.explodiu = True

    def desenhar(self, tela):
        if not self.vivo:
            return

        cor = (255, 120, 0) if self.correndo else (255, 200, 0)

        pygame.draw.rect(
            tela,
            cor,
            (
                self.posx,
                self.posy,
                self.largura,
                self.altura
            )
        )