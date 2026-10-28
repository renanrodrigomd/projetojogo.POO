
import math
import pygame

from Personagem import Personagem


class Player(Personagem):
    def __init__(self, x=100, y=550, chao_y=610, largura_mapa=10000):
        super().__init__(x, y)

        self.largura = 40
        self.altura = 60

        self.ultima_horizontal = "d"
        self.velocidade = 5

        self.velocidade_y = 0
        self.gravidade = 0.5
        self.forca_pulo = -12

        self.no_chao = False
        self.chao_y = chao_y

        self.vida = 3
        self.invulneravel = False
        self.tempo_invulnerabilidade = 0
        self.duracao_invulnerabilidade = 1000

        self.cooldown_tiro = 500
        self.largura_mapa = largura_mapa

        self.movendo = False
        self.tempo_animacao = 0
        self.velocidade_animacao = 100
        self.frame_atual = 0

    def receber_dano(self):
        if self.invulneravel:
            return

        self.vida -= 1
        self.invulneravel = True
        self.tempo_invulnerabilidade = pygame.time.get_ticks()

    def mover(self):
        teclas = pygame.key.get_pressed()

        esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]
        direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT]
        cima = teclas[pygame.K_w] or teclas[pygame.K_UP]

        self.movendo = False

        if esquerda and not direita:
            self.posx -= self.velocidade
            self.ultima_horizontal = "a"
            self.movendo = True

        elif direita and not esquerda:
            self.posx += self.velocidade
            self.ultima_horizontal = "d"
            self.movendo = True

        if esquerda and cima:
            self.direcao_olhar = "aw"
        elif direita and cima:
            self.direcao_olhar = "dw"
        elif cima:
            self.direcao_olhar = "w"
        elif esquerda:
            self.direcao_olhar = "a"
        elif direita:
            self.direcao_olhar = "d"
        else:
            self.direcao_olhar = self.ultima_horizontal

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

    def pular(self):
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_SPACE] and self.no_chao:
            self.velocidade_y = self.forca_pulo
            self.no_chao = False

    def atualizar(self):
        agora = pygame.time.get_ticks()

        if self.invulneravel:
            if agora - self.tempo_invulnerabilidade >= self.duracao_invulnerabilidade:
                self.invulneravel = False

        # Física do salto e da queda.
        self.velocidade_y += self.gravidade
        self.posy += self.velocidade_y

        if self.posy + self.altura >= self.chao_y:
            self.posy = self.chao_y - self.altura
            self.velocidade_y = 0
            self.no_chao = True
        else:
            self.no_chao = False

        # Animação simples feita com formas do Pygame.
        if self.movendo and self.no_chao:
            if agora - self.tempo_animacao >= self.velocidade_animacao:
                self.frame_atual = (self.frame_atual + 1) % 2
                self.tempo_animacao = agora
        else:
            self.frame_atual = 0

        self.atualizar_tiros()

    def desenhar(self, tela, camera_x=0, camera_y=0):
        agora = pygame.time.get_ticks()

        # Pisca durante a invulnerabilidade, sem interromper o jogo.
        if self.invulneravel and (agora // 100) % 2 == 0:
            for tiro in self.tiros:
                tiro.desenhar(tela, camera_x, camera_y)
            return

        x = round(self.posx - camera_x)
        y = round(self.posy - camera_y)

        centro_x = x + self.largura // 2

        # Direção horizontal: direita ou esquerda.
        olhando_esquerda = self.direcao_olhar in ("a", "aw")
        olhando_cima = self.direcao_olhar in ("w", "aw", "dw")

        # Pernas: alternam para simular caminhada.
        deslocamento_perna = 0
        if self.movendo and self.no_chao:
            deslocamento_perna = 4 if self.frame_atual == 0 else -4

        cor_armadura = (65, 83, 105)
        cor_clara = (135, 157, 177)
        cor_detalhe = (245, 190, 65)

        pygame.draw.line(
            tela, cor_armadura,
            (centro_x - 8, y + 42),
            (centro_x - 10 - deslocamento_perna, y + 58),
            7
        )
        pygame.draw.line(
            tela, cor_armadura,
            (centro_x + 8, y + 42),
            (centro_x + 10 + deslocamento_perna, y + 58),
            7
        )

        # Botas.
        pygame.draw.rect(
            tela, (37, 43, 53),
            (centro_x - 17 - deslocamento_perna, y + 54, 12, 6),
            border_radius=2
        )
        pygame.draw.rect(
            tela, (37, 43, 53),
            (centro_x + 5 + deslocamento_perna, y + 54, 12, 6),
            border_radius=2
        )

        # Tronco.
        pygame.draw.rect(
            tela, cor_armadura,
            (centro_x - 13, y + 25, 26, 23),
            border_radius=5
        )
        pygame.draw.rect(
            tela, cor_clara,
            (centro_x - 9, y + 29, 18, 12),
            border_radius=3
        )
        pygame.draw.line(
            tela, cor_detalhe,
            (centro_x - 6, y + 35),
            (centro_x + 6, y + 35),
            3
        )

        # Braços.
        pygame.draw.line(
            tela, cor_armadura,
            (centro_x - 12, y + 29),
            (centro_x - 17, y + 42),
            6
        )
        pygame.draw.line(
            tela, cor_armadura,
            (centro_x + 12, y + 29),
            (centro_x + 17, y + 42),
            6
        )

        # Cabeça e visor.
        pygame.draw.rect(
            tela, cor_clara,
            (centro_x - 11, y + 5, 22, 21),
            border_radius=5
        )
        pygame.draw.rect(
            tela, (27, 38, 49),
            (centro_x - 8, y + 11, 16, 7),
            border_radius=2
        )

        visor_x = centro_x - 5 if olhando_esquerda else centro_x + 5
        pygame.draw.circle(
            tela, (70, 225, 255),
            (visor_x, y + 14), 2
        )

        # Antena.
        pygame.draw.line(
            tela, cor_armadura,
            (centro_x, y + 5),
            (centro_x, y),
            2
        )
        pygame.draw.circle(
            tela, cor_detalhe,
            (centro_x, y), 2
        )

        # Arma simples apontada na direção escolhida.
        vetores = {
            "a": (-1, 0),
            "d": (1, 0),
            "aw": (-1, -1),
            "dw": (1, -1),
            "w": (0, -1)
        }

        dx, dy = vetores.get(self.direcao_olhar, (1, 0))
        magnitude = math.hypot(dx, dy)
        dx /= magnitude
        dy /= magnitude

        origem = (centro_x, y + 34)
        ponta = (
            round(origem[0] + dx * 19),
            round(origem[1] + dy * 19)
        )

        pygame.draw.line(
            tela, (36, 43, 52), origem, ponta, 5
        )
        pygame.draw.circle(
            tela, cor_detalhe, ponta, 3
        )

        for tiro in self.tiros:
            tiro.desenhar(tela, camera_x, camera_y)
