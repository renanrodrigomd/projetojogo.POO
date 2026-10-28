
import math
import pygame
from tiros import Tiro, Missil


class Inimigo:
    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        self.posx = float(x)
        self.posy = float(y)
        self.largura = 40
        self.altura = 60

        self.chao_y = chao_y
        self.largura_mapa = largura_mapa

        self.vivo = True
        self.vida = 2
        self.velocidade = 3
        self.alcance_ataque = 500
        self.cooldown_tiro = 2000
        self.ultimo_tiro = 0

        self.angulo_olhar = 0
        self.tiros = []

    def get_rect(self):
        return pygame.Rect(
            round(self.posx),
            round(self.posy),
            self.largura,
            self.altura
        )

    def olhar_player(self, player_x, player_y):
        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        dx = player_x - centro_x
        dy = player_y - centro_y

        if dx != 0 or dy != 0:
            angulo = math.degrees(math.atan2(dy, dx))
            passo = 360 / 16
            self.angulo_olhar = round(angulo / passo) * passo
            self.angulo_olhar %= 360

    def pode_atacar(self, player_x, player_y):
        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        distancia = math.hypot(
            player_x - centro_x,
            player_y - centro_y
        )

        return distancia <= self.alcance_ataque

    def mover(self, player_x, player_y):
        pass

    def atirar(self):
        if not self.vivo:
            return

        agora = pygame.time.get_ticks()

        if agora - self.ultimo_tiro < self.cooldown_tiro:
            return

        self.ultimo_tiro = agora

        radianos = math.radians(self.angulo_olhar)
        dx = math.cos(radianos)
        dy = math.sin(radianos)

        x = self.posx + self.largura / 2
        y = self.posy + self.altura / 2

        self.tiros.append(Tiro(x, y, dx, dy))

    def receber_dano(self):
        if not self.vivo:
            return

        self.vida -= 1

        if self.vida <= 0:
            self.vivo = False

    def atualizar_tiros(self):
        for tiro in self.tiros[:]:
            tiro.atualizar()

            if not tiro.ativo:
                self.tiros.remove(tiro)

    def atualizar(self):
        self.atualizar_tiros()

    def _desenhar_tiros(self, tela, camera_x, camera_y):
        for tiro in self.tiros:
            tiro.desenhar(tela, camera_x, camera_y)

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            ret = self.get_rect()
            ret.move_ip(-camera_x, -camera_y)

            pygame.draw.rect(tela, (180, 55, 55), ret, border_radius=5)
            pygame.draw.rect(tela, (255, 190, 100), ret, 2, border_radius=5)

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoTerrestre(Inimigo):
    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 56
        self.altura = 70
        self.vida = 2
        self.velocidade = 3
        self.alcance_ataque = 420
        self.cooldown_tiro = 1800

        self.posy = self.chao_y - self.altura

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        distancia = player_x - (self.posx + self.largura / 2)

        if abs(distancia) > self.alcance_ataque * 0.65:
            direcao = 1 if distancia > 0 else -1
            self.posx += direcao * self.velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = self.chao_y - self.altura

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            # Pernas mecânicas
            pygame.draw.rect(tela, (75, 86, 99), (x + 9, y + 48, 13, 19))
            pygame.draw.rect(tela, (75, 86, 99), (x + 34, y + 48, 13, 19))

            # Corpo e cabeça
            pygame.draw.rect(
                tela, (126, 145, 160),
                (x + 5, y + 18, 46, 34), border_radius=5
            )
            pygame.draw.rect(
                tela, (190, 202, 211),
                (x + 9, y + 4, 38, 26), border_radius=5
            )

            # Visor
            pygame.draw.rect(
                tela, (30, 42, 53),
                (x + 13, y + 11, 30, 11), border_radius=3
            )
            pygame.draw.circle(tela, (255, 220, 65), (x + 21, y + 16), 3)
            pygame.draw.circle(tela, (255, 220, 65), (x + 35, y + 16), 3)

            # Detalhes do corpo
            pygame.draw.rect(tela, (45, 55, 67), (x + 18, y + 34, 20, 8))
            pygame.draw.line(tela, (255, 180, 55), (x + 20, y + 38), (x + 36, y + 38), 2)

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoAereo(Inimigo):
    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 70
        self.altura = 50
        self.vida = 2
        self.velocidade = 2
        self.alcance_ataque = 500
        self.cooldown_tiro = 1600

        self.distancia_minima = 230
        self.distancia_vertical = 120
        self.altura_minima = 40
        self.altura_maxima = chao_y - 100

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        dx = player_x - centro_x
        dy = player_y - centro_y

        # Aproxima-se até alcançar a distância de combate.
        if abs(dx) > self.distancia_minima:
            self.posx += self.velocidade if dx > 0 else -self.velocidade

        # Ajusta a altitude para acompanhar o jogador.
        if abs(dy) > self.distancia_vertical:
            self.posy += self.velocidade if dy > 0 else -self.velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = max(
            self.altura_minima,
            min(self.posy, self.altura_maxima)
        )

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            # Asas
            pygame.draw.polygon(
                tela, (66, 115, 139),
                [(x + 8, y + 20), (x - 2, y + 9),
                 (x + 21, y + 17), (x + 24, y + 32)]
            )
            pygame.draw.polygon(
                tela, (66, 115, 139),
                [(x + 62, y + 20), (x + 72, y + 9),
                 (x + 49, y + 17), (x + 46, y + 32)]
            )

            # Corpo do drone
            pygame.draw.ellipse(
                tela, (117, 157, 176),
                (x + 15, y + 8, 40, 34)
            )
            pygame.draw.ellipse(
                tela, (205, 226, 235),
                (x + 23, y + 12, 24, 17)
            )

            # Sensor e propulsores
            pygame.draw.circle(tela, (35, 50, 64), (x + 35, y + 21), 7)
            pygame.draw.circle(tela, (60, 225, 255), (x + 35, y + 21), 4)
            pygame.draw.circle(tela, (60, 225, 255), (x + 8, y + 11), 4)
            pygame.draw.circle(tela, (60, 225, 255), (x + 62, y + 11), 4)

            pygame.draw.line(
                tela, (60, 225, 255),
                (x + 35, y + 42), (x + 35, y + 49), 3
            )

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoBlindado(Inimigo):
    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 110
        self.altura = 75
        self.vida = 8
        self.velocidade = 1.2
        self.alcance_ataque = 600
        self.cooldown_tiro = 2800

        self.posy = self.chao_y - self.altura
        self.tempo_ultimo_frame = pygame.time.get_ticks()
        self.frame_atual = 0
        self.velocidade_animacao = 150
        self.andando = False

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        distancia = player_x - (self.posx + self.largura / 2)
        self.andando = abs(distancia) > self.alcance_ataque

        if self.andando:
            self.posx += self.velocidade if distancia > 0 else -self.velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = self.chao_y - self.altura

    def atualizar_animacao(self):
        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_frame >= self.velocidade_animacao:
            self.frame_atual = (self.frame_atual + 1) % 2
            self.tempo_ultimo_frame = agora

    def atualizar(self):
        self.atualizar_animacao()
        self.atualizar_tiros()

    def atirar(self):
        if not self.vivo:
            return

        agora = pygame.time.get_ticks()

        if agora - self.ultimo_tiro < self.cooldown_tiro:
            return

        self.ultimo_tiro = agora

        radianos = math.radians(self.angulo_olhar)
        dx = math.cos(radianos)
        dy = math.sin(radianos)

        x = self.posx + self.largura / 2
        y = self.posy + self.altura / 2

        self.tiros.append(Missil(x, y, dx, dy))

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            # Esteiras
            pygame.draw.rect(
                tela, (37, 43, 50),
                (x + 4, y + 49, 102, 22), border_radius=7
            )

            for roda_x in range(x + 15, x + 101, 17):
                pygame.draw.circle(tela, (115, 126, 135), (roda_x, y + 60), 6)
                pygame.draw.circle(tela, (45, 51, 58), (roda_x, y + 60), 3)

            # Blindagem
            pygame.draw.polygon(
                tela, (87, 105, 119),
                [(x + 7, y + 49), (x + 14, y + 26),
                 (x + 39, y + 17), (x + 84, y + 17),
                 (x + 101, y + 34), (x + 105, y + 49)]
            )

            pygame.draw.rect(
                tela, (145, 160, 171),
                (x + 30, y + 10, 38, 22), border_radius=4
            )

            # Canhão
            pygame.draw.rect(
                tela, (177, 188, 197),
                (x + 57, y + 15, 43, 8), border_radius=2
            )

            # Luz de alerta
            cor_luz = (255, 100, 55) if self.frame_atual == 0 else (255, 190, 55)
            pygame.draw.circle(tela, cor_luz, (x + 43, y + 21), 5)

            # Placas de blindagem
            pygame.draw.line(
                tela, (222, 170, 65),
                (x + 20, y + 36), (x + 91, y + 36), 3
            )

            barra_largura = 90
            vida_atual = max(0, min(self.vida, 8))
            pygame.draw.rect(tela, (55, 55, 55), (x + 10, y - 9, barra_largura, 5))
            pygame.draw.rect(
                tela, (235, 75, 65),
                (x + 10, y - 9, barra_largura * vida_atual / 8, 5)
            )

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoExplosivo(Inimigo):
    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 56
        self.altura = 70
        self.vida = 2

        self.velocidade = 1
        self.velocidade_correndo = 6
        self.alcance_ataque = 90

        self.correndo = False
        self.explodiu = False
        self.raio_explosao = 80

        self.posy = self.chao_y - self.altura

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        centro_x = self.posx + self.largura / 2
        distancia = player_x - centro_x

        velocidade = (
            self.velocidade_correndo
            if self.correndo
            else self.velocidade
        )

        if distancia != 0:
            self.posx += velocidade if distancia > 0 else -velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = self.chao_y - self.altura

    def atirar(self):
        # Este inimigo persegue o jogador em vez de disparar projéteis.
        return

    def receber_dano(self):
        if not self.vivo:
            return

        self.vida -= 1
        self.correndo = True

        if self.vida <= 0:
            self.vivo = False
            self.explodiu = True

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            centro = (x + self.largura // 2, y + self.altura // 2)

            # Efeito pulsante quando o robô começa a correr.
            if self.correndo:
                pulso = int(pygame.time.get_ticks() / 70) % 8
                pygame.draw.circle(
                    tela, (255, 80, 45),
                    centro, 36 + pulso, 3
                )

            # Pernas
            pygame.draw.rect(tela, (90, 58, 48), (x + 8, y + 48, 13, 18))
            pygame.draw.rect(tela, (90, 58, 48), (x + 35, y + 48, 13, 18))

            # Corpo danificado
            pygame.draw.polygon(
                tela, (176, 71, 43),
                [(x + 9, y + 24), (x + 17, y + 12),
                 (x + 39, y + 12), (x + 49, y + 26),
                 (x + 45, y + 52), (x + 12, y + 52)]
            )

            pygame.draw.rect(
                tela, (235, 110, 58),
                (x + 13, y + 7, 30, 23), border_radius=4
            )

            cor_sensor = (255, 70, 45) if self.correndo else (255, 210, 70)
            pygame.draw.circle(tela, cor_sensor, (x + 22, y + 17), 4)
            pygame.draw.circle(tela, cor_sensor, (x + 35, y + 17), 4)

            # Núcleo de energia
            pygame.draw.circle(tela, (70, 36, 30), (x + 28, y + 39), 9)
            pygame.draw.circle(tela, (255, 165, 60), (x + 28, y + 39), 5)

            if self.correndo:
                pygame.draw.line(tela, (255, 230, 120), (x + 25, y + 35), (x + 31, y + 43), 2)
                pygame.draw.line(tela, (255, 230, 120), (x + 31, y + 35), (x + 25, y + 43), 2)

        self._desenhar_tiros(tela, camera_x, camera_y)
