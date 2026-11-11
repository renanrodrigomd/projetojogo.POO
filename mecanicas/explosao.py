"""Explosões e bombas.

Explosao guarda a área de dano (círculo) e se desenha sozinha. Quem a
cria (robô explosivo, bomba do drone) só informa posição, raio e origem.
Bomba é o projétil que o Drone Bombardeiro solta.
"""

import math

import pygame


class Explosao:
    DURACAO = 520  # ms de animação

    def __init__(self, x, y, raio, origem, dano_jogador=1, dano_inimigos=2):
        self._x = x
        self._y = y
        self._raio = raio
        self._origem = origem
        self._dano_jogador = dano_jogador
        self._dano_inimigos = dano_inimigos
        self._idade = 0

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def raio(self):
        return self._raio

    @property
    def origem(self):
        """Quem causou a explosão (tem NOME e DICA, para a tela de derrota)."""
        return self._origem

    @property
    def dano_jogador(self):
        return self._dano_jogador

    @property
    def dano_inimigos(self):
        return self._dano_inimigos

    @property
    def terminou(self):
        return self._idade >= self.DURACAO

    def atualizar(self, dt):
        self._idade += dt

    def atinge(self, rect):
        """True se o círculo da explosão encosta no retângulo."""
        mais_perto_x = max(rect.left, min(self._x, rect.right))
        mais_perto_y = max(rect.top, min(self._y, rect.bottom))

        return math.hypot(
            self._x - mais_perto_x, self._y - mais_perto_y
        ) <= self._raio

    def desenhar(self, tela, camera_x, camera_y):
        if self.terminou:
            return

        p = self._idade / self.DURACAO
        cx = int(self._x - camera_x)
        cy = int(self._y - camera_y)

        # Bola de fogo: cresce rápido e escurece até virar fumaça
        raio_fogo = int(self._raio * (0.35 + 0.65 * math.sqrt(p)))
        cor_externa = (int(255 - 120 * p), int(110 - 60 * p), int(40 - 20 * p))
        cor_interna = (255, int(210 - 110 * p), int(110 - 80 * p))

        pygame.draw.circle(tela, cor_externa, (cx, cy), raio_fogo)
        pygame.draw.circle(tela, cor_interna, (cx, cy),
                           max(1, int(raio_fogo * (0.7 - 0.5 * p))))

        # Clarão branco no começo
        if p < 0.2:
            pygame.draw.circle(tela, (255, 255, 240), (cx, cy),
                               max(1, int(self._raio * (0.6 - 3 * p))))

        # Anel de choque
        pygame.draw.circle(
            tela, (255, 200, 120), (cx, cy),
            int(self._raio * (0.5 + 0.7 * p)), max(1, int(6 * (1 - p)))
        )

        # Faíscas
        for i in range(12):
            angulo = i * math.tau / 12 + 0.3
            comeco = self._raio * (0.5 + 0.6 * p)
            fim = comeco + 14 * (1 - p)

            pygame.draw.line(
                tela, (255, 220, 140),
                (cx + math.cos(angulo) * comeco, cy + math.sin(angulo) * comeco),
                (cx + math.cos(angulo) * fim, cy + math.sin(angulo) * fim), 2
            )


class Bomba:
    """Bomba que cai em linha reta e explode ao tocar em algo."""

    GRAVIDADE = 0.35
    VELOCIDADE_MAX = 9
    RAIO_EXPLOSAO = 58

    def __init__(self, x, y, origem):
        self.posx = float(x)
        self.posy = float(y)
        self.velocidade_y = 1.0
        self.origem = origem

    def atualizar(self):
        self.velocidade_y = min(
            self.VELOCIDADE_MAX, self.velocidade_y + self.GRAVIDADE
        )
        self.posy += self.velocidade_y

    def get_rect(self):
        return pygame.Rect(round(self.posx - 8), round(self.posy - 8), 16, 16)

    def explodir(self):
        """Bombas ferem o jogador, mas não os outros robôs."""
        return Explosao(
            self.posx, self.posy, self.RAIO_EXPLOSAO, self.origem,
            dano_jogador=1, dano_inimigos=0
        )

    def desenhar(self, tela, camera_x=0, camera_y=0):
        x = round(self.posx - camera_x)
        y = round(self.posy - camera_y)

        pygame.draw.circle(tela, (36, 40, 50), (x, y), 8)
        pygame.draw.circle(tela, (90, 100, 116), (x, y), 8, 2)
        pygame.draw.rect(tela, (90, 100, 116), (x - 2, y - 12, 4, 5))

        if (pygame.time.get_ticks() // 90) % 2 == 0:
            pygame.draw.circle(tela, (255, 70, 55), (x, y), 3)
