import pygame
import math

from caminhos import asset

class Tiro:

    def __init__(self, x, y, dx, dy):
        self.posx = x
        self.posy = y

        tamanho = math.sqrt(dx * dx + dy * dy)

        self.dx = dx / tamanho
        self.dy = dy / tamanho

        self.velocidade = 8
        self.ativo = True

    def atualizar(self):
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

    def desenhar(self, tela, camera_x=0, camera_y=0):
        pygame.draw.circle(
            tela,
            (255, 255, 0),
            (
                int(self.posx - camera_x),
                int(self.posy - camera_y)
            ),
            5
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
        
