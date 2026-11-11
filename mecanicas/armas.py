"""Armas do jogador.

POO aplicada:
  * Arma é ABSTRATA e define o "molde" do disparo (padrão Template
    Method): disparar() confere recarga e munição e chama _criar_tiros(),
    que cada arma implementa do seu jeito.
  * Pistola e Espingarda HERDAM de Arma.
  * O Player usa qualquer arma do mesmo jeito (POLIMORFISMO).
  * Munição e recarga são privadas; só mudam por métodos (ENCAPSULAMENTO).

A recarga conta com dt (milissegundos de jogo), então não corre na pausa.
"""

import math
from abc import ABC, abstractmethod

from tiros import TiroPlayer


class TiroEspingarda(TiroPlayer):
    """Projétil da espingarda: mais rápido, mas de alcance curto."""

    ALCANCE_MS = 380

    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy)
        self.velocidade = 9

    def atualizar(self):
        super().atualizar()

        if self.tempo_vida >= self.ALCANCE_MS:
            self.ativo = False


class Arma(ABC):
    NOME = "Arma"
    RECARGA = 500           # ms entre disparos
    MUNICAO_MAX = None      # None = munição infinita

    def __init__(self, municao=None):
        self._municao = municao if self.MUNICAO_MAX is not None else None
        self._recarga = 0

    # Leitura

    @property
    def infinita(self):
        return self.MUNICAO_MAX is None

    @property
    def municao(self):
        return self._municao

    @property
    def disponivel(self):
        """Pode ser escolhida (tem munição ou é infinita)."""
        return self.infinita or self._municao > 0

    @property
    def pronta(self):
        return self._recarga <= 0 and self.disponivel

    # Ciclo de vida

    def atualizar(self, dt):
        self._recarga = max(0, self._recarga - dt)

    def adicionar_municao(self, quantidade):
        """Devolve quantas balas realmente entraram (0 se já está cheia)."""
        if self.infinita:
            return 0

        antes = self._municao
        self._municao = min(self.MUNICAO_MAX, self._municao + quantidade)
        return self._municao - antes

    def disparar(self, x, y, dx, dy):
        """Devolve a lista de tiros criados (vazia se não puder atirar)."""
        if not self.pronta:
            return []

        if not self.infinita:
            self._municao -= 1

        self._recarga = self.RECARGA
        return self._criar_tiros(x, y, dx, dy)

    @abstractmethod
    def _criar_tiros(self, x, y, dx, dy):
        """Cada arma decide quantos tiros e em que direções."""


class Pistola(Arma):
    NOME = "PISTOLA"
    RECARGA = 500

    def _criar_tiros(self, x, y, dx, dy):
        return [TiroPlayer(x, y, dx, dy)]


class Espingarda(Arma):
    NOME = "ESPINGARDA"
    RECARGA = 800
    MUNICAO_MAX = 12
    ABERTURA = (-16, 0, 16)   # graus de cada projétil em relação à mira

    def __init__(self, municao=0):
        super().__init__(municao)

    def _criar_tiros(self, x, y, dx, dy):
        base = math.atan2(dy, dx)

        return [
            TiroEspingarda(
                x, y,
                math.cos(base + math.radians(abertura)),
                math.sin(base + math.radians(abertura)),
            )
            for abertura in self.ABERTURA
        ]
