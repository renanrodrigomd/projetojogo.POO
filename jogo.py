import pygame
from Player import Player
from Inimigos import Inimigo

def iniciar_jogo():

    ALTURA = 700
    LARGURA = 1230

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

        for tiro in jogador.tiros[:]:

            if tiro.get_rect().colliderect(adversario.get_rect()):

                tiro.ativo = False
                adversario.vivo = False

        tela.fill((20, 20, 20))

        jogador.desenhar(tela)
        adversario.desenhar(tela)

        pygame.display.update()
        
