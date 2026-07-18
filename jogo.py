import pygame
from Player import Player
from Inimigos import Inimigo
#roda o jogo
def iniciar_jogo():
#tamanho da tela
    ALTURA = 700
    LARGURA = 1230
#desenha a tela
    tela = pygame.display.set_mode((LARGURA, ALTURA))
#chama o jogador e o adversário
    jogador = Player()
    adversario = Inimigo(400, 550)
#chama o relógio
    relogio = pygame.time.Clock()
#tudo funcionando
    rodando = True
#se estiver rodando, execute:
    while rodando:
#controla a velocidade do jogo
        relogio.tick(60)
#verifique todos os eventos e processe um por um
        for evento in pygame.event.get():
#fecha o jogo
            if evento.type == pygame.QUIT:
                rodando = False
#se mexer no teclado, faça os botões funcionarem
            if evento.type == pygame.KEYDOWN:
#atira no "r"
                if evento.key == pygame.K_r:
                    jogador.atirar()

        jogador.mover()
        jogador.pular()
        jogador.atualizar()

        adversario.mover(jogador.posx)
        adversario.atualizar()
#se os tiros saírem da tela, eles somem
        for tiro in jogador.tiros[:]:

            if tiro.get_rect().colliderect(adversario.get_rect()):

                tiro.ativo = False
                adversario.vivo = False
#preenche a cor da tela
        tela.fill((20, 20, 20))
#desenha o player e os inimigos na tela
        jogador.desenhar(tela)
        adversario.desenhar(tela)
#mostra na tela tudo o que foi desenhado
        pygame.display.update()
        
