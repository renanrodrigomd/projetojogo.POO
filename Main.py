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

botao_jogar = pygame.Rect(
    450,
    220,
    300,
    70
)

botao_ranking = pygame.Rect(
    450,
    330,
    300,
    70
)

botao_sair = pygame.Rect(
    450,
    440,
    300,
    70
)

rodando = True
iniciar_jogo = False

# Laço principal do jogo.
while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if botao_jogar.collidepoint(evento.pos):
                iniciar_jogo = True
                rodando = False

            if botao_sair.collidepoint(evento.pos):
                rodando = False

    tela.fill((0, 0, 0))

    pygame.draw.rect(
        tela,
        (80, 80, 80),
        botao_jogar
    )

    pygame.draw.rect(
        tela,
        (80, 80, 80),
        botao_ranking
    )

    pygame.draw.rect(
        tela,
        (80, 80, 80),
        botao_sair
    )

    # Renderiza os textos dos botões.
    tela.blit(
        fonte.render(
            "Jogar",
            True,
            (255, 255, 255)
        ),
        (550, 240)
    )

    tela.blit(
        fonte.render(
            "Ranking",
            True,
            (255, 255, 255)
        ),
        (510, 350)
    )

    tela.blit(
        fonte.render(
            "Sair",
            True,
            (255, 255, 255)
        ),
        (560, 460)
    )

    pygame.display.update()


# Só inicia a partida se o jogador tiver escolhido "Jogar".
if iniciar_jogo:
    jogo.iniciar_jogo()


pygame.quit()