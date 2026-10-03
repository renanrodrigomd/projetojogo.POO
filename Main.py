import pygame

import jogo

from caminhos import asset


pygame.init()

LARGURA = 1200
ALTURA = 700

tela = pygame.display.set_mode(
    (LARGURA, ALTURA)
)

pygame.display.set_caption(
    "SmachTech: Invasion Robotics"
)


# Fundo

BG = pygame.image.load(
    asset(
        "telasjogo",
        "TelaFundo.png"
    )
).convert()

BG = pygame.transform.smoothscale(
    BG,
    (LARGURA, ALTURA)
)


# Botões

botao_jogar = pygame.image.load(
    asset(
        "telasjogo",
        "jogar.png"
    )
).convert_alpha()

botao_creditos = pygame.image.load(
    asset(
        "telasjogo",
        "credito.png"
    )
).convert_alpha()

botao_sair = pygame.image.load(
    asset(
        "telasjogo",
        "sair.png"
    )
).convert_alpha()


botao_jogar_rect = botao_jogar.get_rect(
    center=(LARGURA // 2, 255)
)

botao_creditos_rect = botao_creditos.get_rect(
    center=(LARGURA // 2, 355)
)

botao_sair_rect = botao_sair.get_rect(
    center=(LARGURA // 2, 455)
)


fonte = pygame.font.SysFont(
    "arial",
    22,
    bold=True
)


def desenhar_botao(
    tela,
    imagem,
    rect,
    mouse_pos
):
    # Efeito quando o mouse passa por cima

    if rect.collidepoint(mouse_pos):

        imagem_hover = pygame.transform.smoothscale(
            imagem,
            (
                int(imagem.get_width() * 1.05),
                int(imagem.get_height() * 1.05)
            )
        )

        rect_hover = imagem_hover.get_rect(
            center=rect.center
        )

        tela.blit(
            imagem_hover,
            rect_hover
        )

    else:

        tela.blit(
            imagem,
            rect
        )


def tela_creditos():

    esperando = True
    relogio = pygame.time.Clock()

    while esperando:

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                return False

            if (
                evento.type == pygame.KEYDOWN
                and evento.key in (
                    pygame.K_ESCAPE,
                    pygame.K_BACKSPACE
                )
            ):
                esperando = False

        tela.blit(
            BG,
            (0, 0)
        )

        # Painel

        painel = pygame.Surface(
            (650, 430),
            pygame.SRCALPHA
        )

        painel.fill(
            (8, 12, 20, 235)
        )

        tela.blit(
            painel,
            (275, 125)
        )

        fonte_titulo = pygame.font.SysFont(
            "arial",
            42,
            bold=True
        )

        fonte_texto = pygame.font.SysFont(
            "arial",
            24
        )

        titulo = fonte_titulo.render(
            "SMACHTECH",
            True,
            (105, 210, 255)
        )

        tela.blit(
            titulo,
            titulo.get_rect(
                center=(600, 180)
            )
        )

        subtitulo = fonte_texto.render(
            "Invasion Robotics",
            True,
            (225, 230, 240)
        )

        tela.blit(
            subtitulo,
            subtitulo.get_rect(
                center=(600, 220)
            )
        )

        nomes = [
            "Desenvolvedores",
            "Renan Rodrigo Medeiros Dantas",
            "Gustavo Medeiros Lucena",
            "Juan Oliveira Fonseca",
        ]

        for i, nome in enumerate(nomes):

            if i == 0:
                cor = (255, 215, 100)
            else:
                cor = (225, 230, 240)

            imagem = fonte_texto.render(
                nome,
                True,
                cor
            )

            tela.blit(
                imagem,
                imagem.get_rect(
                    center=(
                        600,
                        285 + i * 38
                    )
                )
            )

        ajuda = fonte.render(
            "ESC / BACKSPACE  •  voltar",
            True,
            (170, 180, 195)
        )

        tela.blit(
            ajuda,
            ajuda.get_rect(
                center=(600, 500)
            )
        )

        pygame.display.flip()

        relogio.tick(60)

    return True


# Menu principal

rodando = True

while rodando:

    mouse_pos = pygame.mouse.get_pos()

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
        ):

            # Jogar

            if botao_jogar_rect.collidepoint(
                evento.pos
            ):

                jogo.iniciar_jogo()

            # Créditos

            elif botao_creditos_rect.collidepoint(
                evento.pos
            ):

                if not tela_creditos():
                    rodando = False

            # Sair

            elif botao_sair_rect.collidepoint(
                evento.pos
            ):

                rodando = False

    # Fundo

    tela.blit(
        BG,
        (0, 0)
    )

    # Escurecimento leve

    camada = pygame.Surface(
        (LARGURA, ALTURA),
        pygame.SRCALPHA
    )

    camada.fill(
        (0, 0, 0, 45)
    )

    tela.blit(
        camada,
        (0, 0)
    )

    # Botões

    desenhar_botao(
        tela,
        botao_jogar,
        botao_jogar_rect,
        mouse_pos
    )

    desenhar_botao(
        tela,
        botao_creditos,
        botao_creditos_rect,
        mouse_pos
    )

    desenhar_botao(
        tela,
        botao_sair,
        botao_sair_rect,
        mouse_pos
    )

    pygame.display.flip()


pygame.quit()