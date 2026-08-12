import pygame

from Player import Player
from Inimigos import (
    InimigoTerrestre,
    InimigoAereo,
    InimigoBlindado,
    InimigoExplosivo
)


def iniciar_jogo():

    ALTURA = 700
    LARGURA = 1200

    tela = pygame.display.set_mode(
        (LARGURA, ALTURA)
    )

    jogador = Player()

    inimigos = [
        InimigoTerrestre(700, 550)
    ]

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

        for inimigo in inimigos:

            if not inimigo.vivo:
                continue

            inimigo.mover(
                jogador.posx,
                jogador.posy
            )

            inimigo.olhar_player(
                jogador.posx,
                jogador.posy
            )

            inimigo.atualizar()

            if inimigo.pode_atacar(
                jogador.posx,
                jogador.posy
            ):
                inimigo.atirar()

        # Verifica os tiros do Player contra todos os inimigos.
        for tiro in jogador.tiros[:]:

            for inimigo in inimigos:

                if not inimigo.vivo:
                    continue

                if tiro.get_rect().colliderect(
                    inimigo.get_rect()
                ):

                    tiro.ativo = False

                    if isinstance(
                        inimigo,
                        InimigoExplosivo
                    ):
                        inimigo.receber_dano()

                    else:
                        inimigo.vida -= 1

                        if inimigo.vida <= 0:
                            inimigo.vivo = False

                    break

        # Verifica os ataques dos inimigos contra o Player.
        for inimigo in inimigos:

            for tiro in inimigo.tiros[:]:

                if tiro.get_rect().colliderect(
                    jogador.get_rect()
                ):

                    tiro.ativo = False
                    jogador.vida -= 1

        tela.fill(
            (20, 20, 20)
        )

        jogador.desenhar(tela)

        for inimigo in inimigos:
            inimigo.desenhar(tela)

        pygame.display.update()