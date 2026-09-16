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

def desenhar_hud(tela, jogador, inimigos, pontuacao, fase):
    fonte = pygame.font.Font(None, 32)
    fonte_pequena = pygame.font.Font(None, 26)

    inimigos_restantes = sum(
        1 for inimigo in inimigos
        if inimigo.vivo
    )

    # Fundo da HUD
    pygame.draw.rect(
        tela,
        (20, 20, 20),
        (15, 15, 1170, 75)
    )

    # Borda da HUD
    pygame.draw.rect(
        tela,
        (100, 100, 100),
        (15, 15, 1170, 75),
        2
    )

    # Vida
    texto_vida = fonte.render(
        f"VIDA: {jogador.vida}",
        True,
        (255, 255, 255)
    )

    tela.blit(
        texto_vida,
        (30, 28)
    )

    # Fase
    texto_fase = fonte.render(
        f"FASE: {fase}",
        True,
        (255, 255, 255)
    )

    tela.blit(
        texto_fase,
        (220, 28)
    )

    # Pontuação
    texto_pontuacao = fonte.render(
        f"PONTOS: {pontuacao}",
        True,
        (255, 255, 255)
    )

    tela.blit(
        texto_pontuacao,
        (400, 28)
    )

    # Inimigos restantes
    texto_inimigos = fonte.render(
        f"INIMIGOS: {inimigos_restantes}",
        True,
        (255, 255, 255)
    )

    tela.blit(
        texto_inimigos,
        (650, 28)
    )

    # Objetivo
    if inimigos_restantes > 0:
        objetivo = "OBJETIVO: Elimine todos os inimigos"
    else:
        objetivo = "OBJETIVO: Área limpa!"

    texto_objetivo = fonte_pequena.render(
        objetivo,
        True,
        (220, 220, 220)
    )

    tela.blit(
        texto_objetivo,
        (30, 62)
    )

def iniciar_jogo():

    LARGURA = 1200
    ALTURA = 700

    LARGURA_MAPA = 10000
    ALTURA_MAPA = 700

    # Altura da superfície do chão.
    CHAO_Y = 610

    tela = pygame.display.set_mode((LARGURA, ALTURA))

    #cria a sprite de fundo do mapa corretamente
    background_original = pygame.image.load(
        asset("background", "cidadeferrada.png")
    ).convert()

    #coincidencia da escala com o chao_y
    escala = CHAO_Y / (background_original.get_height() * 0.725)
    largura_fundo = max(1, int(background_original.get_width() * escala))
    altura_fundo = max(1, int(background_original.get_height() * escala))

    background = pygame.transform.smoothscale(
        background_original,
        (largura_fundo, altura_fundo)
    )

    cam = Camera(
        LARGURA_MAPA,
        ALTURA_MAPA,
        LARGURA,
        ALTURA
    )

    jogador = Player(
        x=100,
        y=CHAO_Y - 60,
        chao_y=CHAO_Y,
        largura_mapa=LARGURA_MAPA
    )

    inimigos = [
        InimigoTerrestre(700, CHAO_Y - 70, chao_y=CHAO_Y, largura_mapa=LARGURA_MAPA),
        InimigoBlindado(900, CHAO_Y - 100, chao_y=CHAO_Y, largura_mapa=LARGURA_MAPA),
        InimigoAereo(1100, CHAO_Y - 200, chao_y=CHAO_Y, largura_mapa=LARGURA_MAPA),
    ]

    pontuacao = 0
    fase = 1

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

                # Pulo por pressionamento, em vez de repetir
                # enquanto a tecla estiver sendo segurada.
                if evento.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    if jogador.no_chao:
                        jogador.velocidade_y = jogador.forca_pulo
                        jogador.no_chao = False

        jogador.mover()
        jogador.atualizar()

        cam.atualizar_camera(jogador)

        for inimigo in inimigos:

            if not inimigo.vivo:
                continue

            inimigo.mover(jogador.posx, jogador.posy)
            inimigo.olhar_player(jogador.posx, jogador.posy)
            inimigo.atualizar()

            if inimigo.pode_atacar(jogador.posx, jogador.posy):
                inimigo.atirar()

        # Tiros do Player contra inimigos.
        for tiro in jogador.tiros[:]:
            for inimigo in inimigos:

                if not inimigo.vivo:
                    continue

                if tiro.get_rect().colliderect(inimigo.get_rect()):
                    tiro.ativo = False

                    if isinstance(inimigo, InimigoExplosivo):
                        inimigo.receber_dano()

                        if not inimigo.vivo:
                            pontuacao += 100

                    else:
                        inimigo.vida -= 1

                        if inimigo.vida <= 0:
                            inimigo.vivo = False
                            pontuacao += 100

                    break

        # Tiros dos inimigos contra o Player.
        for inimigo in inimigos:
            for tiro in inimigo.tiros[:]:

                if tiro.get_rect().colliderect(jogador.get_rect()):
                    tiro.ativo = False
                    jogador.vida -= 1

        # repetição de sprite
        inicio_x = -(cam.x % background.get_width()) - background.get_width()

        for x in range(inicio_x, LARGURA + background.get_width(), background.get_width()):
            tela.blit(background, (x, -cam.y))

        # O chão é uma área jogável contínua, independentemente do fundo.
        pygame.draw.rect(
            tela,
            (45, 45, 45),
            (0, CHAO_Y - cam.y, LARGURA, ALTURA - CHAO_Y + cam.y)
        )

        # Linha superior do chão.
        pygame.draw.rect(
            tela,
            (25, 25, 25),
            (0, CHAO_Y - cam.y, LARGURA, 8)
        )

        jogador.desenhar(tela, cam.x, cam.y)

        for inimigo in inimigos:
            inimigo.desenhar(tela, cam.x, cam.y)

        desenhar_hud(
            tela,
            jogador,
            inimigos,
            pontuacao,
            fase
        )

        pygame.display.update()