
import math
import pygame

from Personagem import Personagem
from mecanicas.armas import Pistola, Espingarda


class Player(Personagem):
    # Dash: arrancada curta na horizontal, invulnerável, com recarga
    DASH_DURACAO = 160       # ms
    DASH_RECARGA = 1100      # ms (conta a partir do início do dash)
    DASH_VELOCIDADE = 14     # pixels por quadro

    # Pulo variável: soltar a tecla corta a subida
    VELOCIDADE_CORTE_PULO = -4.0

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

        self._vida_max = 3
        self._vida = self._vida_max
        self.invulneravel = False
        self.tempo_invulnerabilidade = 0
        self.duracao_invulnerabilidade = 1000
        self._escudo_restante = 0  # ms (conta só enquanto a partida roda)

        self.cooldown_tiro = 500
        self.largura_mapa = largura_mapa

        # Armas (a [0] é a pistola, sempre disponível; a [1] precisa de munição)
        self._armas = [Pistola(), Espingarda()]
        self._indice_arma = 0

        # Dash
        self._dash_restante = 0
        self._dash_recarga = 0
        self._dash_direcao = 1
        self._rastro_dash = []

        self.movendo = False
        self.tempo_animacao = 0
        self.velocidade_animacao = 100
        self.frame_atual = 0

    @property
    def vida(self):
        return self._vida

    @property
    def vida_max(self):
        return self._vida_max

    @property
    def esta_vivo(self):
        return self._vida > 0

    @property
    def escudo_ativo(self):
        return self._escudo_restante > 0

    @property
    def escudo_restante(self):
        """Segundos de escudo que ainda restam."""
        return self._escudo_restante / 1000

    def ativar_escudo(self, duracao_ms):
        self._escudo_restante = max(self._escudo_restante, duracao_ms)

    def atualizar_escudo(self, dt):
        self._escudo_restante = max(0, self._escudo_restante - dt)

    # ---- Armas

    @property
    def armas(self):
        return tuple(self._armas)

    @property
    def indice_arma(self):
        return self._indice_arma

    @property
    def arma_atual(self):
        return self._armas[self._indice_arma]

    @property
    def arma_especial(self):
        return self._armas[1]

    def selecionar_arma(self, indice):
        if 0 <= indice < len(self._armas) and self._armas[indice].disponivel:
            self._indice_arma = indice
            return True

        return False

    def trocar_arma(self, passo=1):
        """Passa para a próxima (passo=1) ou anterior (passo=-1) arma
        disponível. Devolve True se trocou."""
        total = len(self._armas)

        for k in range(1, total):
            indice = (self._indice_arma + passo * k) % total

            if self._armas[indice].disponivel:
                self._indice_arma = indice
                return True

        return False

    def adicionar_municao_especial(self, quantidade):
        """Devolve quantas balas entraram. Na primeira coleta, já equipa
        a espingarda para o jogador perceber a arma nova."""
        estava_sem = not self.arma_especial.disponivel
        ganho = self.arma_especial.adicionar_municao(quantidade)

        if estava_sem and ganho:
            self._indice_arma = 1

        return ganho

    def atirar(self):
        """Dispara a arma atual na direção da mira. True se atirou."""
        vetores = {
            "a": (-1, 0), "d": (1, 0),
            "aw": (-1, -1), "dw": (1, -1), "w": (0, -1),
        }

        dx, dy = vetores[self.direcao_olhar]
        x = self.posx + self.largura // 2
        y = self.posy + self.altura // 2

        novos = self.arma_atual.disparar(x, y, dx, dy)
        self.tiros.extend(novos)

        # Acabou a munição: volta para a pistola
        if not self.arma_atual.disponivel:
            self._indice_arma = 0

        return bool(novos)

    # ---- Dash

    @property
    def esta_dashando(self):
        return self._dash_restante > 0

    @property
    def dash_pronto(self):
        return self._dash_recarga <= 0

    @property
    def dash_fracao(self):
        """0.0 = acabou de usar, 1.0 = pronto de novo."""
        return 1 - self._dash_recarga / self.DASH_RECARGA

    @property
    def rastro_dash(self):
        return tuple(self._rastro_dash)

    def iniciar_dash(self):
        if not self.dash_pronto:
            return False

        teclas = pygame.key.get_pressed()
        esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]
        direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT]

        if esquerda and not direita:
            self._dash_direcao = -1
        elif direita and not esquerda:
            self._dash_direcao = 1
        else:
            self._dash_direcao = -1 if self.ultima_horizontal == "a" else 1

        self._dash_restante = self.DASH_DURACAO
        self._dash_recarga = self.DASH_RECARGA
        return True

    def cortar_pulo(self):
        """Soltar a tecla de pulo no meio da subida encurta o salto."""
        if self.velocidade_y < self.VELOCIDADE_CORTE_PULO:
            self.velocidade_y = self.VELOCIDADE_CORTE_PULO

    def atualizar_timers(self, dt):
        """Escudo, dash e recarga das armas (dt em ms; pausa-seguro)."""
        self.atualizar_escudo(dt)

        self._dash_restante = max(0, self._dash_restante - dt)
        self._dash_recarga = max(0, self._dash_recarga - dt)

        for arma in self._armas:
            arma.atualizar(dt)

        # Rastro visual do dash
        if self.esta_dashando:
            self._rastro_dash.append((self.posx, self.posy))
            del self._rastro_dash[:-5]
        elif self._rastro_dash:
            self._rastro_dash.pop(0)

    def restaurar_vida(self):
        self._vida = self._vida_max
        self.invulneravel = False

    def curar(self, quantidade=1):
        self._vida = min(self._vida_max, self._vida + quantidade)

    def receber_dano(self):
        if self.invulneravel or self.escudo_ativo or self.esta_dashando:
            return

        self._vida = max(0, self._vida - 1)
        self.invulneravel = True
        self.tempo_invulnerabilidade = pygame.time.get_ticks()

    def mover(self):
        if self.esta_dashando:
            self.posx += self._dash_direcao * self.DASH_VELOCIDADE
            self.movendo = True
            self.ultima_horizontal = "d" if self._dash_direcao > 0 else "a"
            self.direcao_olhar = self.ultima_horizontal
            self.posx = max(0, min(self.posx, self.largura_mapa - self.largura))
            return

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

        # Física do salto e da queda (o dash flutua em linha reta).
        if self.esta_dashando:
            self.velocidade_y = 0
        else:
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
