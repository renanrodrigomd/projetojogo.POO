from Mapa import mapa
import jogo
import pygame

pygame.init()
#tamanho da tela
LARGURA = 1200
ALTURA = 700
#desenha a tela com o título
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("SmachTech: Invasion Robotics")
#fonte da letra
fonte = pygame.font.SysFont(None, 50)
#botões funcionais
botao_jogar = pygame.Rect(450, 220, 300, 70)
botao_ranking = pygame.Rect(450, 330, 300, 70)
botao_sair = pygame.Rect(450, 440, 300, 70)
#tudo funcionando menos o jogo
rodando = True
iniciar_jogo = False
#se estiver rodando, execute:
while rodando:
#verifique todos os eventos e processe um por um
    for evento in pygame.event.get():
#fecha o jogo
        if evento.type == pygame.QUIT:
            rodando = False
#mouse funcionando
        if evento.type == pygame.MOUSEBUTTONDOWN:
#menu fecha, executa jogo.py
            if botao_jogar.collidepoint(evento.pos):
                iniciar_jogo = True
                rodando = False
#quebra o código
            if botao_sair.collidepoint(evento.pos):
                rodando = False
#preenche a cor da tela
    tela.fill((0, 0, 0))
#desenha os botões
    pygame.draw.rect(tela, (80, 80, 80), botao_jogar)
    pygame.draw.rect(tela, (80, 80, 80), botao_ranking)
    pygame.draw.rect(tela, (80, 80, 80), botao_sair)
#desenha os quadrados dos botões
    tela.blit(
        fonte.render("Jogar", True, (255, 255, 255)),
        (550, 240)
    )

    tela.blit(
        fonte.render("Ranking", True, (255, 255, 255)),
        (510, 350)
    )

    tela.blit(
        fonte.render("Sair", True, (255, 255, 255)),
        (560, 460)
    )
#mostra tudo o que foi desenhado
    pygame.display.update()
#se clicar em iniciar_jogo, executa o jogo.py
if iniciar_jogo:
    jogo.iniciar_jogo()
#encerra o pygame
pygame.quit()