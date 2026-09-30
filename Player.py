import pygame

from caminhos import asset
from Personagem import Personagem


class Player(Personagem):

    def __init__(self, x=100, y=550, chao_y=610, largura_mapa=10000):
        super().__init__(x, y)

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

        self.cooldown_tiro = 500
        self.largura_mapa = largura_mapa

        self.frames_andando = {
            "d": self._carregar_frames(
                "player",
                "Jogadorspriteandandodireita.png"
            ),
            "a": self._carregar_frames(
                "player",
                "jogadorandandoesquerda.png"
            )
        }

        self.frames_pulando = {
            "d": self._carregar_frames(
                "player",
                "jogadorpulandodireita.png"
            ),
            "a": self._carregar_frames(
                "player",
                "jogadorpulandoesquerda.png"
            )
        }

        self.frame_atual = 0
        self.tempo_ultimo_frame = pygame.time.get_ticks()
        self.velocidade_animacao = 80
        self.movendo = False

    def receber_dano(self):
        if self.invulneravel:
            return

        self.vida -= 1
        self.invulneravel = True
        self.tempo_invulnerabilidade = pygame.time.get_ticks()

    def _carregar_frames(self, pasta, nome):
        sprite_sheet = pygame.image.load(
            asset(pasta, nome)
        ).convert_alpha()

        quantidade_frames = 12
        largura_frame = sprite_sheet.get_width() / quantidade_frames
        frames = []

        for i in range(quantidade_frames):
            x_inicio = round(i * largura_frame)
            x_fim = round((i + 1) * largura_frame)

            frame = sprite_sheet.subsurface(
                (
                    x_inicio,
                    0,
                    x_fim - x_inicio,
                    sprite_sheet.get_height()
                )
            ).copy()

            altura = 85

            largura = max(
                1,
                round(
                    frame.get_width()
                    * altura
                    / frame.get_height()
                )
            )

            frame = pygame.transform.smoothscale(
                frame,
                (largura, altura)
            )

            frames.append(frame)

        return frames

    def mover(self):
        teclas = pygame.key.get_pressed()

        esquerda = (
            teclas[pygame.K_a]
            or teclas[pygame.K_LEFT]
        )

        direita = (
            teclas[pygame.K_d]
            or teclas[pygame.K_RIGHT]
        )

        cima = (
            teclas[pygame.K_w]
            or teclas[pygame.K_UP]
        )

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
            min(
                self.posx,
                self.largura_mapa - self.largura
            )
        )

    def pular(self):
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_SPACE] and self.no_chao:
            self.velocidade_y = self.forca_pulo
            self.no_chao = False

    def atualizar(self):
        if self.invulneravel:
            tempo_atual = pygame.time.get_ticks()

            if tempo_atual - self.tempo_invulnerabilidade >= 1000:
                self.invulneravel = False

        self.velocidade_y += self.gravidade
        self.posy += self.velocidade_y

        if self.posy + self.altura >= self.chao_y:
            self.posy = self.chao_y - self.altura
            self.velocidade_y = 0
            self.no_chao = True

        else:
            self.no_chao = False

        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_frame >= self.velocidade_animacao:
            self.frame_atual = (
                self.frame_atual + 1
            ) % 12

            self.tempo_ultimo_frame = agora

        self.atualizar_tiros()

    def desenhar(self, tela, camera_x=0, camera_y=0):

        if self.invulneravel:
            tempo_atual = pygame.time.get_ticks()

            if (tempo_atual // 100) % 2 == 0:
                return

        if self.no_chao:

            if self.movendo:
                frames = self.frames_andando[
                    self.ultima_horizontal
                ]

                frame = frames[self.frame_atual]

            else:
                frame = self.frames_andando[
                    self.ultima_horizontal
                ][0]

        else:
            frames = self.frames_pulando[
                self.ultima_horizontal
            ]

            frame = frames[self.frame_atual]

        rect = frame.get_rect(
            bottomleft=(
                int(self.posx - camera_x),
                int(self.posy + self.altura - camera_y)
            )
        )

        tela.blit(frame, rect)

        for tiro in self.tiros:
            tiro.desenhar(
                tela,
                camera_x,
                camera_y
            )