"""Definição das fases (várias fases curtas).

Cada Fase guarda só DADOS (tamanho, saída e lista de inimigos) e sabe
criar seus inimigos. Os atributos são privados e expostos como
propriedades somente leitura (ENCAPSULAMENTO). Na Etapa 3 a lista de
inimigos será lida de arquivo pelo spawn.py.
"""

from config import CHAO_Y
from Inimigos import (
    InimigoTerrestre,
    InimigoAereo,
    InimigoBlindado,
    InimigoExplosivo,
)


class Fase:

    def __init__(self, numero, nome, largura, final, inimigos,
                 tempo_tres_estrelas=30, tempo_duas_estrelas=45):
        if final >= largura:
            raise ValueError("A saída precisa ficar antes do fim do mapa.")

        self._numero = numero
        self._nome = nome
        self._largura = largura
        self._final = final
        self._especificacoes = tuple(inimigos)
        self._tempo_tres = tempo_tres_estrelas
        self._tempo_duas = tempo_duas_estrelas

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


# (classe, posição x, altura acima do chão — só importa para o aéreo)
FASES = [
    Fase(1, "Rua Destruída", 3600, 3300, [
        (InimigoTerrestre, 900, 70),
        (InimigoTerrestre, 1700, 70),
        (InimigoExplosivo, 2500, 60),
    ], tempo_tres_estrelas=30, tempo_duas_estrelas=45),
    Fase(2, "Ponte Central", 4600, 4300, [
        (InimigoTerrestre, 900, 70),
        (InimigoAereo, 1700, 220),
        (InimigoExplosivo, 2400, 60),
        (InimigoBlindado, 3400, 100),
    ], tempo_tres_estrelas=40, tempo_duas_estrelas=60),
    Fase(3, "Complexo Robótico", 5600, 5300, [
        (InimigoTerrestre, 800, 70),
        (InimigoExplosivo, 1600, 60),
        (InimigoAereo, 2400, 220),
        (InimigoTerrestre, 3200, 70),
        (InimigoBlindado, 4100, 100),
        (InimigoAereo, 4700, 240),
    ], tempo_tres_estrelas=55, tempo_duas_estrelas=80),
]
