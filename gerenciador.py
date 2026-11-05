"""Gerenciador de telas (máquina de estados com pilha).

Só existe UM loop no jogo inteiro. A tela do topo da pilha recebe os
eventos e é atualizada; telas transparentes (ex.: pausa) deixam a tela
de baixo ser desenhada por trás.
"""

import pygame

from config import FPS, LARGURA, ALTURA


class Gerenciador:

    def __init__(self, superficie):
        self._superficie = superficie
        self._pilha = []
        self._rodando = True
        self._relogio = pygame.time.Clock()

        # Transição (fade): 0 = nenhuma, +1 = escurecendo, -1 = clareando
        self._fade_direcao = 0
        self._fade_valor = 0.0
        self._tela_pendente = None
        self._veu = pygame.Surface((LARGURA, ALTURA))
        self._veu.fill((0, 0, 0))

    @property
    def superficie(self):
        return self._superficie

    @property
    def rodando(self):
        return self._rodando and bool(self._pilha)

    @property
    def em_transicao(self):
        return self._fade_direcao != 0

    def trocar(self, tela, fade=False):
        """Descarta todas as telas e passa a mostrar só a nova.

        Com fade=True a tela atual escurece, a troca acontece e a nova
        tela clareia. Durante o fade os eventos são ignorados."""
        if fade and self._pilha and not self.em_transicao:
            self._tela_pendente = tela
            self._fade_direcao = 1
            self._fade_valor = 0.0
        elif not self.em_transicao:
            self._aplicar_troca(tela)

    def _aplicar_troca(self, tela):
        self._pilha.clear()
        self._pilha.append(tela)
        tela.ao_entrar()

    def empilhar(self, tela):
        """Coloca uma tela por cima da atual (a de baixo fica parada)."""
        self._pilha.append(tela)
        tela.ao_entrar()

    def desempilhar(self):
        if len(self._pilha) > 1:
            self._pilha.pop()

    def sair(self):
        self._rodando = False

    def passo(self, dt, eventos):
        """Um quadro do jogo. Separado do loop para poder ser testado."""
        for evento in eventos:
            if evento.type == pygame.QUIT:
                self.sair()
                return

            if self._fade_direcao == 1:
                continue  # escurecendo: ignora entradas

            self._pilha[-1].eventos(evento)

            if not self.rodando:
                return

        if self._fade_direcao != 1:
            self._pilha[-1].atualizar(dt)

        self._avancar_fade(dt)
        self._desenhar()

    DURACAO_FADE = 220  # ms para escurecer e o mesmo para clarear

    def _avancar_fade(self, dt):
        if self._fade_direcao == 0:
            return

        self._fade_valor += self._fade_direcao * dt / self.DURACAO_FADE

        if self._fade_direcao == 1 and self._fade_valor >= 1:
            self._fade_valor = 1.0
            self._aplicar_troca(self._tela_pendente)
            self._tela_pendente = None
            self._fade_direcao = -1

        elif self._fade_direcao == -1 and self._fade_valor <= 0:
            self._fade_valor = 0.0
            self._fade_direcao = 0

    def _desenhar(self):
        inicio = len(self._pilha) - 1

        while inicio > 0 and self._pilha[inicio].transparente:
            inicio -= 1

        for tela in self._pilha[inicio:]:
            tela.desenhar(self._superficie)

        if self._fade_direcao != 0:
            self._veu.set_alpha(int(255 * self._fade_valor))
            self._superficie.blit(self._veu, (0, 0))

        pygame.display.flip()

    def executar(self):
        while self.rodando:
            dt = self._relogio.tick(FPS)
            self.passo(dt, pygame.event.get())
