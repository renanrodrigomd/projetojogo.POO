"""Destroços caindo no fundo (decoração com paralaxe).

Três camadas de profundidade: as de trás são pequenas, lentas e claras
(neblina); as da frente são maiores, rápidas e escuras. Ao tocar o solo
de cada camada, o fragmento levanta uma nuvem de poeira e reaparece lá
em cima. As camadas seguem a câmera em velocidades diferentes.
"""

import math
import random
from collections import namedtuple

import pygame

from config import LARGURA

Camada = namedtuple(
    "Camada", "paralaxe quantidade raio velocidade cor realce solo"
)


class _Fragmento:
    __slots__ = ("camada", "x", "y", "vy", "raio", "forma",
                 "rot", "vrot", "solo")


class _Poeira:
    __slots__ = ("x", "y", "paralaxe", "raio", "idade")


class Destrocos:
    DURACAO_POEIRA = 650  # ms
    MARGEM = 80

    CAMADAS = (
        # paralaxe, qtd, raio, velocidade px/s, cor, realce, solo (y)
        Camada(0.15, 14, (2, 4), (60, 100), (92, 102, 130), (128, 138, 166), (440, 475)),
        Camada(0.35, 12, (4, 8), (110, 170), (62, 70, 94), (98, 108, 136), (475, 510)),
        Camada(0.60, 8, (8, 15), (190, 280), (36, 42, 60), (84, 94, 120), (510, 534)),
    )

    def __init__(self, intensidade=1.0, semente=None):
        self._rng = random.Random(semente)
        self._fragmentos = []
        self._poeiras = []

        for camada in self.CAMADAS:
            quantidade = max(1, round(camada.quantidade * intensidade))

            for _ in range(quantidade):
                self._fragmentos.append(self._novo(camada, inicial=True))

    @property
    def quantidade(self):
        return len(self._fragmentos)

    def _novo(self, camada, inicial=False):
        rng = self._rng
        f = _Fragmento()

        f.camada = camada
        f.x = rng.uniform(0, LARGURA + 2 * self.MARGEM)
        f.solo = rng.uniform(*camada.solo)
        f.y = rng.uniform(-20, f.solo) if inicial else rng.uniform(-80, -10)
        f.vy = rng.uniform(*camada.velocidade)
        f.raio = rng.uniform(*camada.raio)
        f.rot = rng.uniform(0, math.tau)
        f.vrot = rng.uniform(-2.5, 2.5)

        pontos = rng.randint(5, 7)
        angulos = sorted(rng.uniform(0, math.tau) for _ in range(pontos))
        f.forma = [(a, rng.uniform(0.55, 1.0)) for a in angulos]

        return f

    def atualizar(self, dt):
        segundos = dt / 1000

        for i, f in enumerate(self._fragmentos):
            f.y += f.vy * segundos
            f.rot += f.vrot * segundos

            if f.y >= f.solo:
                self._levantar_poeira(f)
                self._fragmentos[i] = self._novo(f.camada)

        for poeira in self._poeiras:
            poeira.idade += dt

        self._poeiras = [
            p for p in self._poeiras if p.idade < self.DURACAO_POEIRA
        ]

    def _levantar_poeira(self, fragmento):
        poeira = _Poeira()
        poeira.x = fragmento.x
        poeira.y = fragmento.solo
        poeira.paralaxe = fragmento.camada.paralaxe
        poeira.raio = fragmento.raio
        poeira.idade = 0
        self._poeiras.append(poeira)

    def _tela_x(self, x, paralaxe, camera_x):
        largura = LARGURA + 2 * self.MARGEM
        return (x - camera_x * paralaxe) % largura - self.MARGEM

    def desenhar(self, tela, camera_x):
        for poeira in self._poeiras:
            self._desenhar_poeira(tela, poeira, camera_x)

        for f in self._fragmentos:
            self._desenhar_fragmento(tela, f, camera_x)

    def _desenhar_fragmento(self, tela, f, camera_x):
        px = self._tela_x(f.x, f.camada.paralaxe, camera_x)

        # rastro curto nas camadas da frente
        if f.camada.paralaxe >= 0.35:
            pygame.draw.line(
                tela, f.camada.cor,
                (px, f.y - f.raio - 16 * f.camada.paralaxe * 2),
                (px, f.y - f.raio), 1
            )

        pontos = [
            (px + math.cos(a + f.rot) * f.raio * k,
             f.y + math.sin(a + f.rot) * f.raio * k * 0.85)
            for a, k in f.forma
        ]

        pygame.draw.polygon(tela, f.camada.cor, pontos)

        if f.raio >= 6:
            pygame.draw.polygon(tela, f.camada.realce, pontos, 1)

    def _desenhar_poeira(self, tela, poeira, camera_x):
        progresso = poeira.idade / self.DURACAO_POEIRA
        px = self._tela_x(poeira.x, poeira.paralaxe, camera_x)

        raio = int(poeira.raio * (0.8 + progresso * 2.6)) + 2
        y = int(poeira.y - progresso * 10)

        # a cor se confunde com o fundo conforme a poeira some
        cor = (
            int(150 - 80 * progresso),
            int(156 - 76 * progresso),
            int(176 - 70 * progresso),
        )

        pygame.draw.circle(tela, cor, (int(px - raio * 0.6), y), raio, 1)
        pygame.draw.circle(tela, cor, (int(px + raio * 0.6), y), raio, 1)
