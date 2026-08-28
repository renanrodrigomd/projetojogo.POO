import pygame
import jogo


pygame.init()

LARGURA = 1200
ALTURA = 700

tela = pygame.display.set_mode(
    (LARGURA, ALTURA)
)

pygame.display.set_caption(
    "SmachTech: Invasion Robotics"
)

fonte = pygame.font.SysFont(
    None,
    50
)

# Desenho das imagens no lugar dos botões e desenha a imagem de fundo do menu

BG = pygame.image.load('assets/telasjogo/TelaFundo.png')
BG = pygame.transform.scale(BG, (1200, 700))

botao_jogar = pygame.image.load('assets/telasjogo/jogar.png').convert_alpha()

botao_ranking = pygame.image.load('assets/telasjogo/credito.png').convert_alpha()

botao_sair = pygame.image.load('assets/telasjogo/sair.png').convert_alpha()

botao_jogar_rect = botao_jogar.get_rect(topleft=(450, 220))

botao_ranking_rect = botao_ranking.get_rect(topleft=(450, 330))

botao_sair_rect = botao_sair.get_rect(topleft=(450, 440))

rodando = True
iniciar_jogo = False

# Laço principal do jogo.
while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if botao_jogar_rect.collidepoint(evento.pos):
                iniciar_jogo = True
                rodando = False

            if botao_sair_rect.collidepoint(evento.pos):
                rodando = False

    tela.blit(BG, (0, 0))
    
    tela.blit(
        botao_jogar,
        botao_jogar_rect
    )

    tela.blit(
        botao_ranking,
        botao_ranking_rect
    )

    tela.blit(
        botao_sair,
        botao_sair_rect
    )

    # Renderiza os textos dos botões.
   

    pygame.display.update()


# Só inicia a partida se o jogador tiver escolhido "Jogar".
if iniciar_jogo:
    jogo.iniciar_jogo()


pygame.quit()