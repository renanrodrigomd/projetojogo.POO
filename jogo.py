import pygame

from caminhos import asset
from camera import Camera
from Player import Player
from Inimigos import (
    InimigoTerrestre,
    InimigoAereo,
    InimigoBlindado,
    InimigoExplosivo
)


LARGURA = 1200
ALTURA = 700
LARGURA_MAPA = 10000
CHAO_Y = 610
FINAL_FASE = 9500


def texto(tela, mensagem, tamanho, cor, posicao, centralizado=False):

    fonte = pygame.font.SysFont(
        "arial",
        tamanho,
        bold=True
    )

    imagem = fonte.render(
        mensagem,
        True,
        cor
    )

    if centralizado:

        rect = imagem.get_rect(
            center=posicao
        )

        tela.blit(
            imagem,
            rect
        )

    else:

        tela.blit(
            imagem,
            posicao
        )


def desenhar_barra(
    tela,
    x,
    y,
    largura,
    altura,
    valor,
    maximo,
    cor
):

    pygame.draw.rect(
        tela,
        (20, 22, 28),
        (x, y, largura, altura),
        border_radius=5
    )

    preenchimento = max(
        0,
        min(
            1,
            valor / maximo
        )
    )

    pygame.draw.rect(
        tela,
        cor,
        (
            x,
            y,
            int(largura * preenchimento),
            altura
        ),
        border_radius=5
    )

    pygame.draw.rect(
        tela,
        (210, 215, 225),
        (x, y, largura, altura),
        2,
        border_radius=5
    )


def desenhar_hud(
    tela,
    jogador,
    inimigos,
    pontuacao,
    fase,
    tempo
):

    vivos = sum(
        1
        for inimigo in inimigos
        if inimigo.vivo
    )

    # Painel superior

    pygame.draw.rect(
        tela,
        (12, 16, 24),
        (18, 15, 1164, 82),
        border_radius=14
    )

    pygame.draw.rect(
        tela,
        (50, 58, 75),
        (18, 15, 1164, 82),
        2,
        border_radius=14
    )

    # Jogador

    texto(
        tela,
        "GEPETO",
        21,
        (220, 225, 235),
        (35, 25)
    )

    desenhar_barra(
        tela,
        35,
        53,
        180,
        16,
        jogador.vida,
        3,
        (220, 70, 75)
    )

    texto(
        tela,
        f"{jogador.vida}/3",
        16,
        (245, 245, 245),
        (103, 52)
    )

    # Fase

    texto(
        tela,
        f"FASE {fase}",
        20,
        (105, 205, 255),
        (250, 27)
    )

    # Pontuação

    texto(
        tela,
        f"PONTOS  {pontuacao:04d}",
        20,
        (255, 215, 95),
        (400, 27)
    )

    # Inimigos

    texto(
        tela,
        f"ROBÔS  {vivos}",
        20,
        (220, 225, 235),
        (625, 27)
    )

    # Tempo

    minutos = int(tempo) // 60
    segundos = int(tempo) % 60

    texto(
        tela,
        f"{minutos:02d}:{segundos:02d}",
        20,
        (220, 225, 235),
        (850, 27)
    )

    # Objetivo

    if vivos:

        objetivo = "ELIMINE OS ROBÔS E AVANCE ATÉ A SAÍDA"

    else:

        objetivo = "ÁREA LIMPA! A SAÍDA ESTÁ LIBERADA"

    texto(
        tela,
        objetivo,
        16,
        (165, 175, 190),
        (250, 57)
    )


def desenhar_saida(tela, camera_x):

    x = FINAL_FASE - camera_x

    if -100 < x < LARGURA + 100:

        # Estrutura da saída

        pygame.draw.rect(
            tela,
            (15, 25, 35),
            (
                x,
                CHAO_Y - 155,
                95,
                155
            ),
            border_radius=12
        )

        pygame.draw.rect(
            tela,
            (80, 210, 255),
            (
                x + 8,
                CHAO_Y - 147,
                79,
                147
            ),
            4,
            border_radius=10
        )

        # Linhas internas

        for i in range(4):

            yy = CHAO_Y - 125 + i * 30

            pygame.draw.line(
                tela,
                (80, 210, 255),
                (x + 20, yy),
                (x + 75, yy),
                3
            )

        texto(
            tela,
            "SAÍDA",
            18,
            (150, 230, 255),
            (x + 47, CHAO_Y - 180),
            centralizado=True
        )


def desenhar_cenario(
    tela,
    background,
    chao,
    camera_x,
    camera_y
):

    # Fundo repetido

    inicio_x = (
        -(camera_x % background.get_width())
        - background.get_width()
    )

    for x in range(
        inicio_x,
        LARGURA + background.get_width(),
        background.get_width()
    ):

        tela.blit(
            background,
            (x, -camera_y)
        )

    # Chão

    inicio_chao = (
        -(camera_x % chao.get_width())
        - chao.get_width()
    )

    for x in range(
        inicio_chao,
        LARGURA + chao.get_width(),
        chao.get_width()
    ):

        tela.blit(
            chao,
            (x, CHAO_Y - 20 - camera_y)
        )

    # Parte inferior

    pygame.draw.rect(
        tela,
        (22, 25, 31),
        (
            0,
            CHAO_Y + 150 - camera_y,
            LARGURA,
            ALTURA
        )
    )

    # Linha do chão

    pygame.draw.line(
        tela,
        (75, 85, 95),
        (0, CHAO_Y - camera_y),
        (LARGURA, CHAO_Y - camera_y),
        3
    )


def tela_derrota(tela):

    imagem = pygame.image.load(
        asset(
            "telasjogo",
            "Teladederrota.png"
        )
    ).convert()

    imagem = pygame.transform.smoothscale(
        imagem,
        tela.get_size()
    )

    tela.blit(
        imagem,
        (0, 0)
    )

    texto(
        tela,
        "ESC  •  voltar ao menu",
        20,
        (235, 235, 235),
        (LARGURA // 2, ALTURA - 35),
        True
    )

    pygame.display.flip()

    esperando = True
    relogio = pygame.time.Clock()

    while esperando:

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                return False

            if (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_ESCAPE
            ):
                esperando = False

        relogio.tick(60)

    return True


def tela_vitoria(tela, pontuacao, tempo):

    imagem = pygame.image.load(
        asset(
            "telasjogo",
            "Vitoria.png"
        )
    ).convert()

    imagem = pygame.transform.smoothscale(
        imagem,
        tela.get_size()
    )

    tela.blit(
        imagem,
        (0, 0)
    )

    texto(
        tela,
        f"PONTUAÇÃO  {pontuacao:04d}   •   TEMPO  {int(tempo)}s",
        24,
        (245, 245, 245),
        (LARGURA // 2, ALTURA - 75),
        True
    )

    texto(
        tela,
        "ESC  •  voltar ao menu",
        18,
        (210, 215, 225),
        (LARGURA // 2, ALTURA - 35),
        True
    )

    pygame.display.flip()

    esperando = True
    relogio = pygame.time.Clock()

    while esperando:

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                return False

            if (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_ESCAPE
            ):
                esperando = False

        relogio.tick(60)

    return True


def iniciar_jogo():

    tela = pygame.display.set_mode(
        (LARGURA, ALTURA)
    )

    pygame.display.set_caption(
        "SmachTech: Invasion Robotics"
    )

    # Fundo

    background_original = pygame.image.load(
        asset(
            "background",
            "Backgroundjogo.png"
        )
    ).convert()

    background = pygame.transform.smoothscale(
        background_original,
        (
            int(background_original.get_width() * 0.95),
            int(background_original.get_height() * 0.95)
        )
    )

    # Chão

    chao_original = pygame.image.load(
        asset(
            "background",
            "chaojogo.png"
        )
    ).convert_alpha()

    chao = pygame.transform.smoothscale(
        chao_original,
        (
            int(chao_original.get_width() * 0.50),
            int(chao_original.get_height() * 0.50)
        )
    )

    # Câmera

    cam = Camera(
        LARGURA_MAPA,
        ALTURA,
        LARGURA,
        ALTURA
    )

    # Jogador

    jogador = Player(
        x=100,
        y=CHAO_Y - 60,
        chao_y=CHAO_Y,
        largura_mapa=LARGURA_MAPA
    )

    # Inimigos

    inimigos = [

        InimigoTerrestre(
            900,
            CHAO_Y - 70,
            CHAO_Y,
            LARGURA_MAPA
        ),

        InimigoTerrestre(
            1700,
            CHAO_Y - 70,
            CHAO_Y,
            LARGURA_MAPA
        ),

        InimigoExplosivo(
            2500,
            CHAO_Y - 60
        ),

        InimigoAereo(
            3300,
            CHAO_Y - 220,
            CHAO_Y,
            LARGURA_MAPA
        ),

        InimigoBlindado(
            4500,
            CHAO_Y - 100,
            CHAO_Y,
            LARGURA_MAPA
        ),

        InimigoTerrestre(
            5700,
            CHAO_Y - 70,
            CHAO_Y,
            LARGURA_MAPA
        ),

        InimigoExplosivo(
            6900,
            CHAO_Y - 60
        ),

        InimigoAereo(
            7700,
            CHAO_Y - 240,
            CHAO_Y,
            LARGURA_MAPA
        ),

        InimigoBlindado(
            8500,
            CHAO_Y - 100,
            CHAO_Y,
            LARGURA_MAPA
        )
    ]

    # Variáveis

    pontuacao = 0
    fase = 1

    relogio = pygame.time.Clock()

    inicio_fase = pygame.time.get_ticks()

    impactos = []

    rodando = True

    # Loop principal

    while rodando:

        relogio.tick(60)

        tempo = (
            pygame.time.get_ticks()
            - inicio_fase
        ) / 1000

        # Eventos

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_k:
                    jogador.atirar()

                if evento.key in (
                    pygame.K_SPACE,
                    pygame.K_w,
                    pygame.K_UP
                ):

                    if jogador.no_chao:

                        jogador.velocidade_y = (
                            jogador.forca_pulo
                        )

                        jogador.no_chao = False

                if evento.key == pygame.K_ESCAPE:
                    return True

        # Atualiza jogador

        jogador.mover()
        jogador.atualizar()

        cam.atualizar_camera(jogador)

        # Atualiza inimigos

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

            # Colisão física com o jogador

            if inimigo.get_rect().colliderect(
                jogador.get_rect()
            ):

                vida_antes = jogador.vida

                jogador.receber_dano()

                if jogador.vida < vida_antes:

                    if inimigo.posx > jogador.posx:
                        jogador.posx -= 55
                    else:
                        jogador.posx += 55

        # Tiros do jogador

        for tiro in jogador.tiros[:]:

            for inimigo in inimigos:

                if not inimigo.vivo:
                    continue

                if tiro.get_rect().colliderect(
                    inimigo.get_rect()
                ):

                    impacto = tiro.criar_impacto()

                    impactos.append([
                        impacto[0],
                        impacto[1],
                        pygame.time.get_ticks()
                    ])

                    if isinstance(
                        inimigo,
                        InimigoExplosivo
                    ):

                        inimigo.receber_dano()

                    else:

                        inimigo.vida -= 1

                        if inimigo.vida <= 0:
                            inimigo.vivo = False

                    if not inimigo.vivo:
                        pontuacao += 100

                    break

        # Tiros dos inimigos

        for inimigo in inimigos:

            for tiro in inimigo.tiros[:]:

                if tiro.get_rect().colliderect(
                    jogador.get_rect()
                ):

                    tiro.ativo = False

                    jogador.receber_dano()

        # Derrota

        if jogador.vida <= 0:

            if not tela_derrota(tela):
                return False

            return True

        # Contagem de inimigos

        vivos = sum(
            1
            for inimigo in inimigos
            if inimigo.vivo
        )

        # Vitória

        if (
            jogador.posx >= FINAL_FASE
            and vivos == 0
        ):

            if not tela_vitoria(
                tela,
                pontuacao,
                tempo
            ):
                return False

            return True

        # Desenho

        desenhar_cenario(
            tela,
            background,
            chao,
            cam.x,
            cam.y
        )

        desenhar_saida(
            tela,
            cam.x
        )

        # Inimigos

        for inimigo in inimigos:

            inimigo.desenhar(
                tela,
                cam.x,
                cam.y
            )

            if inimigo.vivo:

                if isinstance(
                    inimigo,
                    InimigoBlindado
                ):
                    max_vida = 8
                else:
                    max_vida = 2

                barra_x = int(
                    inimigo.posx - cam.x
                )

                barra_y = int(
                    inimigo.posy
                    - cam.y
                    - 12
                )

                desenhar_barra(
                    tela,
                    barra_x,
                    barra_y,
                    int(inimigo.largura),
                    6,
                    inimigo.vida,
                    max_vida,
                    (80, 220, 110)
                )

        # Jogador

        jogador.desenhar(
            tela,
            cam.x,
            cam.y
        )

        # Efeitos de impacto

        agora = pygame.time.get_ticks()

        for impacto in impactos[:]:

            x, y, tempo_impacto = impacto

            decorrido = (
                agora - tempo_impacto
            )

            if decorrido >= 250:

                impactos.remove(
                    impacto
                )

                continue

            progresso = (
                decorrido / 250
            )

            raio = int(
                5 + progresso * 20
            )

            pygame.draw.circle(
                tela,
                (255, 190, 70),
                (
                    int(x - cam.x),
                    int(y - cam.y)
                ),
                raio,
                3
            )

        # HUD

        desenhar_hud(
            tela,
            jogador,
            inimigos,
            pontuacao,
            fase,
            tempo
        )

        pygame.display.flip()

    return True