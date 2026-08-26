import pygame
from tiros import Tiro


class Personagem:

    def __init__(self, x, y):
        self.posx = x
        self.posy = y

        self.largura = 40
        self.altura = 60

        self.direcao_olhar = "d"

        self.tiros = []

        # O cooldown é definido em milissegundos.
        self.cooldown_tiro = 500
        self.ultimo_tiro = 0

    def atirar(self):
        agora = pygame.time.get_ticks()

        if agora - self.ultimo_tiro < self.cooldown_tiro:
            return

        self.ultimo_tiro = agora

        vetores = {
            "a": (-1, 0),
            "d": (1, 0),
            "aw": (-1, -1),
            "dw": (1, -1),
            "w": (0, -1)
        }

        dx, dy = vetores[self.direcao_olhar]

        x = self.posx + self.largura // 2
        y = self.posy + self.altura // 2

        tiro = Tiro(x, y, dx, dy)

        self.tiros.append(tiro)

    def atualizar_tiros(self):
        for tiro in self.tiros[:]:
            tiro.atualizar()

            if not tiro.ativo:
                self.tiros.remove(tiro)

    def get_rect(self):
        return pygame.Rect(
            self.posx,
            self.posy,
            self.largura,
            self.altura
        )