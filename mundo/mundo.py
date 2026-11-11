"""O mundo de uma fase: guarda os elementos e resolve as colisões."""

import pygame


class Mundo:

    def __init__(self, plataformas, barreiras, perigos, checkpoints, itens):
        self._plataformas = list(plataformas)
        self._barreiras = list(barreiras)
        self._perigos = list(perigos)
        self._checkpoints = list(checkpoints)
        self._itens = list(itens)

    # Leitura (tuplas: ninguém troca a lista por fora)

    @property
    def plataformas(self):
        return tuple(self._plataformas)

    @property
    def barreiras(self):
        return tuple(self._barreiras)

    @property
    def perigos(self):
        return tuple(self._perigos)

    @property
    def checkpoints(self):
        return tuple(self._checkpoints)

    @property
    def itens(self):
        return tuple(self._itens)

    def marcadores_checkpoint(self):
        """[(x, ativo)] usado pela barra de progresso do HUD."""
        return [(c.x, c.ativo) for c in self._checkpoints]

    # Ciclo de vida

    def atualizar(self, dt):
        for grupo in (self._perigos, self._checkpoints, self._itens):
            for elemento in grupo:
                elemento.atualizar(dt)

    def desenhar(self, tela, camera_x, camera_y):
        for grupo in (self._perigos, self._plataformas, self._barreiras,
                      self._checkpoints, self._itens):
            for elemento in grupo:
                elemento.desenhar(tela, camera_x, camera_y)

    # Colisões

    def bloqueia(self, rect):
        """True se o retângulo bate em alguma barreira (passos e tiros)."""
        return any(b.rect.colliderect(rect) for b in self._barreiras)

    def superficie_em(self, rect):
        """True se o retângulo toca uma plataforma ou barreira (as bombas
        explodem ao encostar em qualquer superfície)."""
        return any(
            s.rect.colliderect(rect)
            for s in self._plataformas + self._barreiras
        )

    @staticmethod
    def _expulsar(jogador, rect_barreira):
        """Empurra o jogador para o lado mais próximo da barreira."""
        if jogador.posx + jogador.largura / 2 < rect_barreira.centerx:
            jogador.posx = rect_barreira.left - jogador.largura
        else:
            jogador.posx = rect_barreira.right

    def expulsar_de_barreiras(self, jogador):
        for barreira in self._barreiras:
            if barreira.rect.colliderect(jogador.get_rect()):
                self._expulsar(jogador, barreira.rect)

    def resolver_jogador(self, jogador, x_antes, y_antes):
        """Chamado depois que o jogador se moveu neste quadro.

        1) eixo X: barreiras bloqueiam o passo;
        2) eixo Y: plataformas e barreiras seguram por cima; barreiras
           também bloqueiam a cabeçada.
        """
        # --- eixo X (usa a altura antiga para não confundir com o pouso)
        caixa = pygame.Rect(
            int(jogador.posx), int(y_antes),
            jogador.largura, jogador.altura
        )

        for barreira in self._barreiras:
            r = barreira.rect

            if not r.colliderect(caixa):
                continue

            if jogador.posx > x_antes:
                jogador.posx = r.left - jogador.largura
            elif jogador.posx < x_antes:
                jogador.posx = r.right
            else:
                self._expulsar(jogador, r)

            caixa.x = int(jogador.posx)

        # --- eixo Y
        pes_antes = y_antes + jogador.altura
        pes_agora = jogador.posy + jogador.altura
        esquerda = jogador.posx
        direita = jogador.posx + jogador.largura

        if jogador.velocidade_y >= 0:
            topo_escolhido = None

            for suporte in self._plataformas + self._barreiras:
                r = suporte.rect

                if direita <= r.left or esquerda >= r.right:
                    continue

                if pes_antes <= r.top + 1 and pes_agora >= r.top:
                    if topo_escolhido is None or r.top < topo_escolhido:
                        topo_escolhido = r.top

            if topo_escolhido is not None:
                jogador.posy = topo_escolhido - jogador.altura
                jogador.velocidade_y = 0
                jogador.no_chao = True

        else:
            for barreira in self._barreiras:
                r = barreira.rect

                if direita <= r.left or esquerda >= r.right:
                    continue

                if y_antes >= r.bottom - 1 and jogador.posy <= r.bottom:
                    jogador.posy = r.bottom
                    jogador.velocidade_y = 0
