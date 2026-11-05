"""Resumo de uma partida, enviado da TelaJogo para as telas finais.

É imutável (frozen): depois de criado ninguém altera os números, o que
protege os dados (ENCAPSULAMENTO).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResumoPartida:
    indice_fase: int
    pontuacao_inicial: int
    pontuacao: int          # já inclui o bônus, se houver
    tempo: float
    derrotados: int
    total_inimigos: int
    progresso: float        # 0.0 a 1.0 (quanto da fase foi percorrido)
    dano_sofrido: int
    causa: str
    dica: str
    estrelas: int = 0
    bonus: int = 0

    @property
    def numero_fase(self):
        return self.indice_fase + 1

    @property
    def pontos_da_fase(self):
        return self.pontuacao - self.pontuacao_inicial
