import pygame

from Player import Player
from Inimigos import Inimigo


def iniciar_jogo():

    ALTURA = 700
    LARGURA = 1200

    tela = pygame.display.set_mode(
        (LARGURA, ALTURA)
    )

    jogador = Player()

    adversario = Inimigo(
        900,
        550
    )

    relogio = pygame.time.Clock()

    rodando = True

    while rodando:

        relogio.tick(60)

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_k:
                    jogador.atirar()

        jogador.mover()
        jogador.pular()
        jogador.atualizar()

        adversario.mover(
            jogador.posx
        )

        adversario.olhar_player(
            jogador.posx,
            jogador.posy
        )

        adversario.atualizar()

        if adversario.vivo:

            if adversario.pode_atacar(
                jogador.posx
            ):
                adversario.atirar()

        # Verifica se algum tiro do Player atingiu o inimigo.
        for tiro in jogador.tiros[:]:

            if (
                adversario.vivo
                and tiro.get_rect().colliderect(
                    adversario.get_rect()
                )
            ):

                tiro.ativo = False

                adversario.vida -= 1

                if adversario.vida <= 0:
                    adversario.vivo = False

        # Verifica se algum tiro do inimigo atingiu o Player.
        for tiro in adversario.tiros[:]:

            if tiro.get_rect().colliderect(
                jogador.get_rect()
            ):

                tiro.ativo = False

                jogador.vida -= 1

        tela.fill(
            (20, 20, 20)
        )

        jogador.desenhar(tela)
        adversario.desenhar(tela)

        pygame.display.update()