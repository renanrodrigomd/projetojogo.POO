import pygame
from Player import Player
from Inimigos import Inimigo

def iniciar_jogo():

    ALTURA = 800
    LARGURA = 1500

    tela = pygame.display.set_mode((LARGURA, ALTURA))

    jogador = Player()
    adversario = Inimigo(400, 550)

    relogio = pygame.time.Clock()

    rodando = True

    while rodando:

        relogio.tick(60)

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    jogador.atirar()

        jogador.mover()
        jogador.pular()
        jogador.atualizar()

        adversario.mover(jogador.posx)
        adversario.atualizar()

        tela.fill((20, 20, 20))

        jogador.desenhar(tela)
        adversario.desenhar(tela)

        pygame.display.update()
        
iniciar_jogo()