from Mapa import mapa
import pygame

pygame.init()

LARGURA = 1200
ALTURA = 700

tela = pygame.display.set_mode((LARGURA, ALTURA))

pygame.display.set_caption(
    "SmachTech: Invasion Robotics"
)

fonte = pygame.font.SysFont(None, 50)

botao_jogar = pygame.Rect(450, 220, 300, 70)
botao_creditos = pygame.Rect(450, 330, 300, 70)
botao_sair = pygame.Rect(450, 440, 300, 70)

rodando = True

while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 0))

    pygame.draw.rect(tela, (80, 80, 80), botao_jogar)
    pygame.draw.rect(tela, (80, 80, 80), botao_creditos)
    pygame.draw.rect(tela, (80, 80, 80), botao_sair)

    tela.blit(
        fonte.render("Jogar", True, (255, 255, 255)),
        (550, 240)
    )

    tela.blit(
        fonte.render("Créditos", True, (255, 255, 255)),
        (510, 350)
    )

    tela.blit(
        fonte.render("Sair", True, (255, 255, 255)),
        (560, 460)
    )

    pygame.display.update()

pygame.quit()