"""Classe base de todas as telas (HERANÇA + POLIMORFISMO).

Menu, créditos, jogo, pausa, vitória e derrota herdam de Tela e
implementam eventos/atualizar/desenhar. O Gerenciador chama os mesmos
métodos em qualquer tela sem saber qual ela é.
"""

from abc import ABC, abstractmethod


class Tela(ABC):
    # Se True, a tela de baixo continua sendo desenhada por trás.
    transparente = False

    def __init__(self, gerenciador):
        self._gerenciador = gerenciador

    @property
    def gerenciador(self):
        return self._gerenciador

    def ao_entrar(self):
        """Gancho opcional chamado quando a tela passa a ser exibida."""

    @abstractmethod
    def eventos(self, evento):
        """Trata um evento do pygame."""

    def atualizar(self, dt):
        """Lógica por quadro (dt em milissegundos)."""

    @abstractmethod
    def desenhar(self, superficie):
        """Desenha a tela."""
