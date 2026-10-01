import pygame
import math

from caminhos import asset

class Tiro:

    def __init__(self, x, y, dx, dy):
        self.posx = x
        self.posy = y

        self.tempo_vida = 0
        self.duracao_efeito = 120

        tamanho = math.sqrt(dx * dx + dy * dy)

        self.dx = dx / tamanho
        self.dy = dy / tamanho

        self.velocidade = 8
        self.ativo = True

        self.rastro = []

    def atualizar(self):
        self.rastro.append((self.posx, self.posy))

        self.tempo_vida += 16

        if len(self.rastro) > 5:
            self.rastro.pop(0)

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

    def criar_impacto(self):
        self.ativo = False
        return (self.posx, self.posy)

    def desenhar(self, tela, camera_x=0, camera_y=0):

        x = int(self.posx - camera_x)
        y = int(self.posy - camera_y)

        progresso = min(
            self.tempo_vida / self.duracao_efeito,
            1
        )

        # Começa grande e diminui rapidamente
        tamanho = int(9 - progresso * 6)

        if tamanho < 2:
            tamanho = 2

        # Pequeno rastro atrás do tiro
        rastro = int(8 - progresso * 7)

        if rastro > 1:
            inicio_x = int(
                x - self.dx * rastro
            )

            inicio_y = int(
                y - self.dy * rastro
            )

            pygame.draw.line(
                tela,
                (190, 190, 190),
                (inicio_x, inicio_y),
                (x, y),
                max(1, tamanho // 2)
            )

        # Impacto inicial
        if progresso < 0.25:

            impacto = int(
                12 * (1 - progresso / 0.25)
            )

            pygame.draw.circle(
                tela,
                (255, 190, 80),
                (x, y),
                impacto
            )

        # Corpo principal
        pygame.draw.circle(
            tela,
            (255, 220, 120),
            (x, y),
            tamanho
        )

        # Núcleo
        pygame.draw.circle(
            tela,
            (255, 255, 255),
            (x, y),
            max(1, tamanho // 2)
        )


class Missil(Tiro):

    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy)

        self.velocidade = 7
        self.tamanho = 12
        self.explodiu = False

        self.sprite = pygame.image.load(asset("enemys", "Tiro.Tank.png")).convert_alpha()

        area =  self.sprite.get_bounding_rect()

        if area.width > 0 and area.height > 0:
            self.sprite =self.sprite.subsurface(area).copy()

        #Tamanho do Projetil no mapa
        self.sprite = pygame.transform.smoothscale(self.sprite, (60,30))

    def get_rect(self):
        return pygame.Rect(
            self.posx - self.tamanho,
            self.posy - self.tamanho,
            self.tamanho * 2,
            self.tamanho * 2
        )

    def desenhar(self, tela, camera_x=0, camera_y=0):

        angulo = math.degrees(math.atan2(self.dy, self.dx))

        sprite = pygame.transform.rotate(self.sprite, -angulo)
        
        rect = sprite.get_rect(
            center=(
                int(self.posx - camera_x),
                int(self.posy - camera_y)
            )
        )

        tela.blit(sprite, rect)
        
