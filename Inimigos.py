
import math
import pygame
from tiros import Tiro, Missil
from mecanicas.explosao import Bomba


class Inimigo:
    NOME = "Robô"
    VOA = False  # True para os que ignoram barreiras do chão
    EXPLODE_AO_TOCAR = False  # True: detona em vez de causar dano de contato
    DICA = "Fique em movimento e atire primeiro."

    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        self.posx = float(x)
        self.posy = float(y)
        self.largura = 40
        self.altura = 60

        self.chao_y = chao_y
        self.largura_mapa = largura_mapa

        self.vivo = True
        self._vida = 0
        self._vida_max = 0
        self.vida = 2
        self.velocidade = 3
        self.alcance_ataque = 500
        self.cooldown_tiro = 2000
        self.ultimo_tiro = 0

        self.angulo_olhar = 0
        self.tiros = []
        self.bombas = []

    @property
    def explosao_pendente(self):
        """True quando o robô acabou de explodir e a partida ainda precisa
        criar a explosão. Só o Explosivo sobrescreve."""
        return False

    def marcar_explosao_tratada(self):
        pass

    def receber_tiro(self, tiro):
        """Chamado quando um tiro do jogador acerta este robô.
        Devolve True se o dano valeu, False se o tiro foi bloqueado.
        Cada tipo de robô pode reagir de um jeito (POLIMORFISMO)."""
        self.receber_dano()
        return True

    @property
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, valor):
        # Nunca fica negativa; a primeira vez que a vida é definida
        # (ou aumentada) vira a vida máxima usada nas barras do HUD.
        self._vida = max(0, valor)
        self._vida_max = max(self._vida_max, self._vida)

        if self._vida == 0:
            self.vivo = False

    @property
    def vida_max(self):
        return self._vida_max

    def get_rect(self):
        return pygame.Rect(
            round(self.posx),
            round(self.posy),
            self.largura,
            self.altura
        )

    def olhar_player(self, player_x, player_y):
        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        dx = player_x - centro_x
        dy = player_y - centro_y

        if dx != 0 or dy != 0:
            angulo = math.degrees(math.atan2(dy, dx))
            passo = 360 / 16
            self.angulo_olhar = round(angulo / passo) * passo
            self.angulo_olhar %= 360

    def pode_atacar(self, player_x, player_y):
        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        distancia = math.hypot(
            player_x - centro_x,
            player_y - centro_y
        )

        return distancia <= self.alcance_ataque

    def mover(self, player_x, player_y):
        pass

    def atirar(self):
        if not self.vivo:
            return

        agora = pygame.time.get_ticks()

        if agora - self.ultimo_tiro < self.cooldown_tiro:
            return

        self.ultimo_tiro = agora

        radianos = math.radians(self.angulo_olhar)
        dx = math.cos(radianos)
        dy = math.sin(radianos)

        x = self.posx + self.largura / 2
        y = self.posy + self.altura / 2

        self.tiros.append(Tiro(x, y, dx, dy))

    def receber_dano(self):
        self.vida -= 1

        if self.vida <= 0:
            self.vivo = False
            self.limpar_tiros()

    def limpar_tiros(self):
    
        for tiro in self.tiros:
            tiro.ativo = False

        self.tiros.clear()
        self.bombas.clear()

    def atualizar_tiros(self):
        if not self.vivo:
            self.limpar_tiros()
            return

        for tiro in self.tiros[:]:
            tiro.atualizar()

            if not tiro.ativo:
                self.tiros.remove(tiro)

    def atualizar(self):
        self.atualizar_tiros()

        for bomba in self.bombas:
            bomba.atualizar()

    def _desenhar_tiros(self, tela, camera_x, camera_y):
        if not self.vivo:
            return

        for tiro in self.tiros:
            if tiro.ativo:
                tiro.desenhar(tela, camera_x, camera_y)

        for bomba in self.bombas:
            bomba.desenhar(tela, camera_x, camera_y)

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            ret = self.get_rect()
            ret.move_ip(-camera_x, -camera_y)

            pygame.draw.rect(tela, (180, 55, 55), ret, border_radius=5)
            pygame.draw.rect(tela, (255, 190, 100), ret, 2, border_radius=5)

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoTerrestre(Inimigo):
    NOME = "Robô Terrestre"
    DICA = "Robôs terrestres atiram de longe: pule os disparos e avance."

    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 56
        self.altura = 70
        self.vida = 2
        self.velocidade = 3
        self.alcance_ataque = 420
        self.cooldown_tiro = 1800

        self.posy = self.chao_y - self.altura

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        distancia = player_x - (self.posx + self.largura / 2)

        if abs(distancia) > self.alcance_ataque * 0.65:
            direcao = 1 if distancia > 0 else -1
            self.posx += direcao * self.velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = self.chao_y - self.altura

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            # Pernas mecânicas
            pygame.draw.rect(tela, (75, 86, 99), (x + 9, y + 48, 13, 19))
            pygame.draw.rect(tela, (75, 86, 99), (x + 34, y + 48, 13, 19))

            # Corpo e cabeça
            pygame.draw.rect(
                tela, (126, 145, 160),
                (x + 5, y + 18, 46, 34), border_radius=5
            )
            pygame.draw.rect(
                tela, (190, 202, 211),
                (x + 9, y + 4, 38, 26), border_radius=5
            )

            # Visor
            pygame.draw.rect(
                tela, (30, 42, 53),
                (x + 13, y + 11, 30, 11), border_radius=3
            )
            pygame.draw.circle(tela, (255, 220, 65), (x + 21, y + 16), 3)
            pygame.draw.circle(tela, (255, 220, 65), (x + 35, y + 16), 3)

            # Detalhes do corpo
            pygame.draw.rect(tela, (45, 55, 67), (x + 18, y + 34, 20, 8))
            pygame.draw.line(tela, (255, 180, 55), (x + 20, y + 38), (x + 36, y + 38), 2)

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoAereo(Inimigo):
    VOA = True
    NOME = "Drone Aéreo"
    DICA = "Drones atacam de cima: segure W ou ↑ para atirar para cima."

    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 70
        self.altura = 50
        self.vida = 2
        self.velocidade = 2
        self.alcance_ataque = 500
        self.cooldown_tiro = 1600

        self.distancia_minima = 230
        self.distancia_vertical = 120
        self.altura_minima = 40
        self.altura_maxima = chao_y - 100

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        centro_x = self.posx + self.largura / 2
        centro_y = self.posy + self.altura / 2

        dx = player_x - centro_x
        dy = player_y - centro_y

        # Aproxima-se até alcançar a distância de combate.
        if abs(dx) > self.distancia_minima:
            self.posx += self.velocidade if dx > 0 else -self.velocidade

        # Ajusta a altitude para acompanhar o jogador.
        if abs(dy) > self.distancia_vertical:
            self.posy += self.velocidade if dy > 0 else -self.velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = max(
            self.altura_minima,
            min(self.posy, self.altura_maxima)
        )

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            # Asas
            pygame.draw.polygon(
                tela, (66, 115, 139),
                [(x + 8, y + 20), (x - 2, y + 9),
                 (x + 21, y + 17), (x + 24, y + 32)]
            )
            pygame.draw.polygon(
                tela, (66, 115, 139),
                [(x + 62, y + 20), (x + 72, y + 9),
                 (x + 49, y + 17), (x + 46, y + 32)]
            )

            # Corpo do drone
            pygame.draw.ellipse(
                tela, (117, 157, 176),
                (x + 15, y + 8, 40, 34)
            )
            pygame.draw.ellipse(
                tela, (205, 226, 235),
                (x + 23, y + 12, 24, 17)
            )

            # Sensor e propulsores
            pygame.draw.circle(tela, (35, 50, 64), (x + 35, y + 21), 7)
            pygame.draw.circle(tela, (60, 225, 255), (x + 35, y + 21), 4)
            pygame.draw.circle(tela, (60, 225, 255), (x + 8, y + 11), 4)
            pygame.draw.circle(tela, (60, 225, 255), (x + 62, y + 11), 4)

            pygame.draw.line(
                tela, (60, 225, 255),
                (x + 35, y + 42), (x + 35, y + 49), 3
            )

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoBlindado(Inimigo):
    NOME = "Robô Blindado"
    DICA = "O blindado aguenta 8 tiros: recue e atire de longe."

    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 110
        self.altura = 75
        self.vida = 8
        self.velocidade = 1.2
        self.alcance_ataque = 600
        self.cooldown_tiro = 2800

        self.posy = self.chao_y - self.altura
        self.tempo_ultimo_frame = pygame.time.get_ticks()
        self.frame_atual = 0
        self.velocidade_animacao = 150
        self.andando = False

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        distancia = player_x - (self.posx + self.largura / 2)
        self.andando = abs(distancia) > self.alcance_ataque

        if self.andando:
            self.posx += self.velocidade if distancia > 0 else -self.velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = self.chao_y - self.altura

    def atualizar_animacao(self):
        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_frame >= self.velocidade_animacao:
            self.frame_atual = (self.frame_atual + 1) % 2
            self.tempo_ultimo_frame = agora

    def atualizar(self):
        self.atualizar_animacao()
        self.atualizar_tiros()

    def atirar(self):
        if not self.vivo:
            return

        agora = pygame.time.get_ticks()

        if agora - self.ultimo_tiro < self.cooldown_tiro:
            return

        self.ultimo_tiro = agora

        radianos = math.radians(self.angulo_olhar)
        dx = math.cos(radianos)
        dy = math.sin(radianos)

        x = self.posx + self.largura / 2
        y = self.posy + self.altura / 2

        self.tiros.append(Missil(x, y, dx, dy))

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            # Esteiras
            pygame.draw.rect(
                tela, (37, 43, 50),
                (x + 4, y + 49, 102, 22), border_radius=7
            )

            for roda_x in range(x + 15, x + 101, 17):
                pygame.draw.circle(tela, (115, 126, 135), (roda_x, y + 60), 6)
                pygame.draw.circle(tela, (45, 51, 58), (roda_x, y + 60), 3)

            # Blindagem
            pygame.draw.polygon(
                tela, (87, 105, 119),
                [(x + 7, y + 49), (x + 14, y + 26),
                 (x + 39, y + 17), (x + 84, y + 17),
                 (x + 101, y + 34), (x + 105, y + 49)]
            )

            pygame.draw.rect(
                tela, (145, 160, 171),
                (x + 30, y + 10, 38, 22), border_radius=4
            )

            # Canhão
            pygame.draw.rect(
                tela, (177, 188, 197),
                (x + 57, y + 15, 43, 8), border_radius=2
            )

            # Luz de alerta
            cor_luz = (255, 100, 55) if self.frame_atual == 0 else (255, 190, 55)
            pygame.draw.circle(tela, cor_luz, (x + 43, y + 21), 5)

            # Placas de blindagem
            pygame.draw.line(
                tela, (222, 170, 65),
                (x + 20, y + 36), (x + 91, y + 36), 3
            )

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoExplosivo(Inimigo):
    EXPLODE_AO_TOCAR = True
    NOME = "Robô Explosivo"
    DICA = "O explosivo corre quando atingido: derrube-o à distância."

    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 56
        self.altura = 70
        self.vida = 2

        self.velocidade = 1
        self.velocidade_correndo = 6
        self.alcance_ataque = 90

        self.correndo = False
        self.explodiu = False
        self._explosao_tratada = False
        self.raio_explosao = 80

        self.posy = self.chao_y - self.altura

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        centro_x = self.posx + self.largura / 2
        distancia = player_x - centro_x

        velocidade = (
            self.velocidade_correndo
            if self.correndo
            else self.velocidade
        )

        if distancia != 0:
            self.posx += velocidade if distancia > 0 else -velocidade

        self.posx = max(
            0,
            min(self.posx, self.largura_mapa - self.largura)
        )

        self.posy = self.chao_y - self.altura

    def atirar(self):
        # Este inimigo persegue o jogador em vez de disparar projéteis.
        return

    @property
    def explosao_pendente(self):
        return self.explodiu and not self._explosao_tratada

    def marcar_explosao_tratada(self):
        self._explosao_tratada = True

    def detonar(self):
        """Autodestruição ao encostar no jogador."""
        if not self.vivo:
            return

        self.vida = 0
        self.explodiu = True
        self.limpar_tiros()

    def receber_dano(self):
        if not self.vivo:
            return

        self.vida -= 1
        self.correndo = True

        if self.vida <= 0:
            self.vivo = False
            self.limpar_tiros()
            self.explodiu = True

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            centro = (x + self.largura // 2, y + self.altura // 2)

            # Efeito pulsante quando o robô começa a correr.
            if self.correndo:
                pulso = int(pygame.time.get_ticks() / 70) % 8
                pygame.draw.circle(
                    tela, (255, 80, 45),
                    centro, 36 + pulso, 3
                )

            # Pernas
            pygame.draw.rect(tela, (90, 58, 48), (x + 8, y + 48, 13, 18))
            pygame.draw.rect(tela, (90, 58, 48), (x + 35, y + 48, 13, 18))

            # Corpo danificado
            pygame.draw.polygon(
                tela, (176, 71, 43),
                [(x + 9, y + 24), (x + 17, y + 12),
                 (x + 39, y + 12), (x + 49, y + 26),
                 (x + 45, y + 52), (x + 12, y + 52)]
            )

            pygame.draw.rect(
                tela, (235, 110, 58),
                (x + 13, y + 7, 30, 23), border_radius=4
            )

            cor_sensor = (255, 70, 45) if self.correndo else (255, 210, 70)
            pygame.draw.circle(tela, cor_sensor, (x + 22, y + 17), 4)
            pygame.draw.circle(tela, cor_sensor, (x + 35, y + 17), 4)

            # Núcleo de energia
            pygame.draw.circle(tela, (70, 36, 30), (x + 28, y + 39), 9)
            pygame.draw.circle(tela, (255, 165, 60), (x + 28, y + 39), 5)

            if self.correndo:
                pygame.draw.line(tela, (255, 230, 120), (x + 25, y + 35), (x + 31, y + 43), 2)
                pygame.draw.line(tela, (255, 230, 120), (x + 31, y + 35), (x + 25, y + 43), 2)

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoEscudeiro(Inimigo):
    """Robô de chão com um escudo na frente.

    O escudo bloqueia tiros que vêm de frente. Para derrotá-lo é preciso
    pegá-lo pelas costas (o dash atravessa o robô!), atirar de cima ou
    usar uma explosão. Ele demora um pouco para virar para o jogador.
    """
    NOME = "Robô Escudeiro"
    DICA = "O escudo barra tiros de frente: use o dash para passar por ele e atire pelas costas."

    TEMPO_VIRAR = 650   # ms até virar para o outro lado
    TEMPO_FLASH = 140   # ms que o escudo brilha ao bloquear

    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 60
        self.altura = 72
        self.vida = 3
        self.velocidade = 1.6
        self.alcance_ataque = 0

        self._lado = 1            # +1: escudo voltado para a direita
        self._orientado = False   # vira para o jogador no primeiro quadro
        self._tempo_virar = 0
        self._flash_ate = 0

        self.posy = self.chao_y - self.altura

    @property
    def lado(self):
        return self._lado

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        distancia = player_x - (self.posx + self.largura / 2)
        lado_desejado = 1 if distancia > 0 else -1

        if not self._orientado:
            self._lado = lado_desejado
            self._orientado = True

        # Só vira depois de o jogador ficar do outro lado por um tempo
        if lado_desejado != self._lado:
            self._tempo_virar += 16
            if self._tempo_virar >= self.TEMPO_VIRAR:
                self._lado = lado_desejado
                self._tempo_virar = 0
        else:
            self._tempo_virar = 0

        self.posx += self._lado * self.velocidade
        self.posx = max(0, min(self.posx, self.largura_mapa - self.largura))
        self.posy = self.chao_y - self.altura

    def atirar(self):
        # Ataca só por contato.
        return

    def receber_tiro(self, tiro):
        # O escudo barra tiros que se movem em direção à sua face.
        if tiro.dx * self._lado < -0.3:
            self._flash_ate = pygame.time.get_ticks() + self.TEMPO_FLASH
            return False

        self.receber_dano()
        return True

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)
            lado = self._lado

            # Pernas
            pygame.draw.rect(tela, (52, 60, 72), (x + 10, y + 52, 15, 20))
            pygame.draw.rect(tela, (52, 60, 72), (x + 35, y + 52, 15, 20))

            # Corpo
            pygame.draw.polygon(
                tela, (78, 92, 112),
                [(x + 8, y + 26), (x + 16, y + 12), (x + 44, y + 12),
                 (x + 52, y + 28), (x + 48, y + 56), (x + 12, y + 56)]
            )
            pygame.draw.rect(tela, (112, 130, 152),
                             (x + 16, y + 6, 28, 22), border_radius=4)

            # Sensor voltado para o lado do escudo
            sensor_x = x + (36 if lado > 0 else 24)
            pygame.draw.circle(tela, (255, 190, 70), (sensor_x, y + 16), 4)

            # Aviso de que está virando
            if self._tempo_virar > 0:
                pygame.draw.circle(tela, (255, 220, 90),
                                   (x + self.largura // 2, y - 6), 4)

            # Escudo (brilha ao bloquear um tiro)
            brilhando = pygame.time.get_ticks() < self._flash_ate
            cor_escudo = (235, 250, 255) if brilhando else (90, 205, 255)
            placa_x = x + self.largura - 8 if lado > 0 else x - 4

            pygame.draw.rect(tela, (22, 44, 62),
                             (placa_x, y + 6, 12, 62), border_radius=5)
            pygame.draw.rect(tela, cor_escudo,
                             (placa_x, y + 6, 12, 62), 3, border_radius=5)

            if brilhando:
                pygame.draw.circle(
                    tela, cor_escudo,
                    (placa_x + (12 if lado > 0 else 0), y + 37), 18, 2
                )

        self._desenhar_tiros(tela, camera_x, camera_y)


class InimigoBombardeiro(Inimigo):
    """Drone que cruza o céu sobre o jogador soltando bombas."""
    VOA = True
    NOME = "Drone Bombardeiro"
    DICA = "Bombardeiros soltam bombas ao passar por cima: saia de baixo ou derrube-os atirando para cima."

    ULTRAPASSAGEM = 320   # quanto passa do jogador antes de dar a volta
    JANELA_BOMBA = 30     # distância horizontal para soltar a bomba

    def __init__(self, x, y, chao_y=610, largura_mapa=10000):
        super().__init__(x, y, chao_y, largura_mapa)

        self.largura = 78
        self.altura = 40
        self.vida = 2
        self.velocidade = 2.6
        self.alcance_ataque = 0
        self.cooldown_bomba = 2300

        self._direcao = 0
        self._ultima_bomba = 0

    def mover(self, player_x, player_y):
        if not self.vivo:
            return

        centro_x = self.posx + self.largura / 2

        if self._direcao == 0:
            self._direcao = 1 if player_x >= centro_x else -1

        # Dá a volta depois de passar do jogador
        if self._direcao > 0 and centro_x > player_x + self.ULTRAPASSAGEM:
            self._direcao = -1
        elif self._direcao < 0 and centro_x < player_x - self.ULTRAPASSAGEM:
            self._direcao = 1

        self.posx += self._direcao * self.velocidade

        # Bate na borda do mapa: inverte
        limite = self.largura_mapa - self.largura
        if self.posx <= 0 or self.posx >= limite:
            self.posx = max(0, min(self.posx, limite))
            self._direcao = -self._direcao

        if abs(player_x - (self.posx + self.largura / 2)) <= self.JANELA_BOMBA:
            self._soltar_bomba()

    def atirar(self):
        # Não atira: só solta bombas (dentro de mover).
        return

    def _soltar_bomba(self):
        agora = pygame.time.get_ticks()

        if agora - self._ultima_bomba < self.cooldown_bomba:
            return

        self._ultima_bomba = agora
        self.bombas.append(Bomba(
            self.posx + self.largura / 2, self.posy + self.altura, self
        ))

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if self.vivo:
            x = round(self.posx - camera_x)
            y = round(self.posy - camera_y)

            # Asas
            pygame.draw.polygon(
                tela, (60, 52, 74),
                [(x, y + 14), (x + 22, y + 6), (x + 22, y + 22)]
            )
            pygame.draw.polygon(
                tela, (60, 52, 74),
                [(x + self.largura, y + 14), (x + self.largura - 22, y + 6),
                 (x + self.largura - 22, y + 22)]
            )

            # Corpo
            corpo = pygame.Rect(x + 14, y + 4, self.largura - 28, 24)
            pygame.draw.rect(tela, (92, 82, 112), corpo, border_radius=10)
            pygame.draw.rect(tela, (150, 136, 176), corpo, 2, border_radius=10)

            # Compartimento da bomba (acende quando está pronto para soltar)
            pronta = (pygame.time.get_ticks() - self._ultima_bomba
                      >= self.cooldown_bomba)
            cor_baia = (255, 90, 60) if pronta else (70, 62, 84)
            pygame.draw.rect(tela, cor_baia,
                             (x + self.largura // 2 - 9, y + 26, 18, 10),
                             border_radius=3)

            # Luz de posição piscando
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                pygame.draw.circle(tela, (255, 220, 90),
                                   (x + self.largura // 2, y + 8), 3)

        self._desenhar_tiros(tela, camera_x, camera_y)
