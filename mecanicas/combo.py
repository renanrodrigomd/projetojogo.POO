"""Combo: derrotar robôs em sequência multiplica os pontos e tira tempo.

Regras (ajustáveis nas constantes):
  * cada abate abre/renova uma janela de 3 s;
  * o multiplicador sobe a cada abate seguido, até x4;
  * a partir do 2º abate seguido, cada abate tira 1 s do cronômetro
    (o README prevê "eliminar inimigos em sequência reduz o tempo");
  * se a janela acabar, o combo zera.

O estado é privado e só muda por registrar_abate() e atualizar(dt);
a janela conta com dt, então congela na pausa.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoCombo:
    """O que a partida precisa aplicar depois de um abate."""
    contagem: int
    multiplicador: int
    pontos: int
    tempo_removido: float


class Combo:
    JANELA = 3000          # ms para encadear o próximo abate
    MULTIPLICADOR_MAX = 4
    PONTOS_BASE = 100
    BONUS_TEMPO = 1.0      # segundos removidos a partir do 2º abate

    def __init__(self):
        self._contagem = 0
        self._restante = 0
        self._maior = 0

    @property
    def contagem(self):
        return self._contagem

    @property
    def maior_combo(self):
        return self._maior

    @property
    def multiplicador(self):
        return max(1, min(self.MULTIPLICADOR_MAX, self._contagem))

    @property
    def ativo(self):
        """True quando há um combo de verdade (2 abates ou mais)."""
        return self._contagem >= 2 and self._restante > 0

    @property
    def fracao_restante(self):
        """1.0 logo após um abate; cai até 0.0 quando a janela acaba."""
        return self._restante / self.JANELA

    def registrar_abate(self):
        self._contagem += 1
        self._restante = self.JANELA
        self._maior = max(self._maior, self._contagem)

        multiplicador = self.multiplicador

        return ResultadoCombo(
            contagem=self._contagem,
            multiplicador=multiplicador,
            pontos=self.PONTOS_BASE * multiplicador,
            tempo_removido=self.BONUS_TEMPO if self._contagem >= 2 else 0.0,
        )

    def atualizar(self, dt):
        if self._restante <= 0:
            return

        self._restante = max(0, self._restante - dt)

        if self._restante == 0:
            self._contagem = 0
