"""Fase: dados de uma fase (tamanho, saída, inimigos e elementos do mapa).

Os atributos são privados e expostos como propriedades somente leitura
(ENCAPSULAMENTO). As fases são lidas de assets/fases/*.json pelo spawn.py.
"""

from config import CHAO_Y
from mundo.mundo import Mundo


class Fase:
    CATEGORIAS = ("plataformas", "barreiras", "perigos", "checkpoints", "itens")

    def __init__(self, numero, nome, largura, final, inimigos,
                 tempo_tres_estrelas=30, tempo_duas_estrelas=45,
                 elementos=None, intensidade_destrocos=1.0):
        if final >= largura:
            raise ValueError("A saída precisa ficar antes do fim do mapa.")

        self._numero = numero
        self._nome = nome
        self._largura = largura
        self._final = final
        self._especificacoes = tuple(inimigos)
        self._tempo_tres = tempo_tres_estrelas
        self._tempo_duas = tempo_duas_estrelas
        self._intensidade_destrocos = intensidade_destrocos

        elementos = elementos or {}
        self._elementos = {
            categoria: tuple(elementos.get(categoria, ()))
            for categoria in self.CATEGORIAS
        }

    @property
    def numero(self):
        return self._numero

    @property
    def nome(self):
        return self._nome

    @property
    def largura(self):
        return self._largura

    @property
    def final(self):
        return self._final

    @property
    def tempo_tres_estrelas(self):
        return self._tempo_tres

    @property
    def tempo_duas_estrelas(self):
        return self._tempo_duas

    @property
    def intensidade_destrocos(self):
        return self._intensidade_destrocos

    def estrelas(self, tempo):
        """1 a 3 estrelas conforme o tempo (metas ajustáveis por fase)."""
        if tempo <= self._tempo_tres:
            return 3
        if tempo <= self._tempo_duas:
            return 2
        return 1

    def criar_inimigos(self):
        """Cria instâncias novas a cada chamada (POLIMORFISMO: todas as
        classes filhas são construídas e usadas do mesmo jeito)."""
        return [
            classe(x, CHAO_Y - altura_voo, CHAO_Y, self._largura)
            for classe, x, altura_voo in self._especificacoes
        ]

    def criar_mundo(self):
        """Cria elementos novos (estado limpo) a cada chamada."""
        def construir(categoria):
            return [
                classe.de_dados(dados)
                for classe, dados in self._elementos[categoria]
            ]

        return Mundo(
            construir("plataformas"), construir("barreiras"),
            construir("perigos"), construir("checkpoints"),
            construir("itens"),
        )
