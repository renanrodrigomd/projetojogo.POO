try:
    from caminhos import asset
except ImportError:
    asset = None

import math
import pygame

_sprite_cartucho = None
_cartucho_carregado = False


def carregar_cartucho():
    global _sprite_cartucho, _cartucho_carregado

    if _cartucho_carregado:
        return _sprite_cartucho

    _cartucho_carregado = True

    if asset is None:
        return None

    try:
        caminho = asset("player", "cartucho.png")
        imagem = pygame.image.load(caminho).convert()

        # Remove o preto sem percorrer pixel por pixel.
        imagem.set_colorkey((0, 0, 0))

        # Recorta a imagem usando operações nativas do Pygame.
        mascara = pygame.mask.from_surface(imagem)
        areas = mascara.get_bounding_rects()

        if not areas:
            return None

        area = areas[0].unionall(areas[1:])
        imagem = imagem.subsurface(area).copy()

        # Redimensiona e preserva o fundo transparente.
        imagem = pygame.transform.scale(imagem, (22, 8))
        imagem.set_colorkey((0, 0, 0))

        _sprite_cartucho = imagem

    except (FileNotFoundError, pygame.error, OSError):
        _sprite_cartucho = None

    return _sprite_cartucho




class Tiro:
    def __init__(self, x, y, dx, dy):
        self.posx = float(x)
        self.posy = float(y)

        magnitude = math.hypot(dx, dy)

        if magnitude == 0:
            dx, dy = 1, 0
            magnitude = 1

        self.dx = dx / magnitude
        self.dy = dy / magnitude

        self.velocidade = 8
        self.tempo_vida = 0
        self.duracao_efeito = 120
        self.ativo = True
        self.rastro = []

        self.sprite = None 

        

    def atualizar(self):
        if not self.ativo:
            return

        self.rastro.append((self.posx, self.posy))

        if len(self.rastro) > 5:
            self.rastro.pop(0)

        self.tempo_vida += 16
        self.posx += self.dx * self.velocidade
        self.posy += self.dy * self.velocidade

        if (
            self.posx < -20
            or self.posx > 10000
            or self.posy < -20
            or self.posy > 720
        ):
            self.ativo = False

    def get_rect(self):
        return pygame.Rect(
            round(self.posx - 5),
            round(self.posy - 5),
            10,
            10
        )

    def criar_impacto(self):
        self.ativo = False
        return self.posx, self.posy

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if not self.ativo:
            return

        x = round(self.posx - camera_x)
        y = round(self.posy - camera_y)

        if self.sprite is not None:
            angulo = math.degrees(math.atan2(self.dy, self.dx))

            imagem = pygame.transform.rotate(self.sprite, - angulo)

            retangulo = imagem.get_rect(center=(x,y))

            tela.blit(imagem, retangulo)
            return

        # Rastro dos disparos.
        for i, ponto in enumerate(self.rastro):
            px = round(ponto[0] - camera_x)
            py = round(ponto[1] - camera_y)

            raio = max(1, (i + 1) * 2 // max(1, len(self.rastro)))

            pygame.draw.circle(
                tela, (170, 155, 105), (px, py), raio
            )

        progresso = min(
            self.tempo_vida / self.duracao_efeito,
            1
        )

        tamanho = max(2, int(5 - progresso * 2))

        pygame.draw.circle(tela, (255, 175, 55), (x, y), tamanho + 2)
        pygame.draw.circle(tela, (255, 230, 130), (x, y), tamanho)
        pygame.draw.circle(tela, (255, 255, 235), (x, y), max(1, tamanho // 2))

class TiroPlayer(Tiro):

    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy)


        self.sprite = carregar_cartucho()

        # Calcula a rotação apenas uma vez por projétil.
        if self.sprite is not None:
            angulo = math.degrees(
                math.atan2(self.dy, self.dx)
            )

            self.sprite_rotacionada = pygame.transform.rotate(
                self.sprite, -angulo
            )
        else:
            self.sprite_rotacionada = None

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if not self.ativo:
            return

        if self.sprite_rotacionada is None:
            super().desenhar(tela, camera_x, camera_y)
            return

        x = round(self.posx - camera_x)
        y = round(self.posy - camera_y)

        retangulo = self.sprite_rotacionada.get_rect(
            center=(x, y)
        )

        tela.blit(self.sprite_rotacionada, retangulo)

class Missil(Tiro):
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy)

        self.velocidade = 7
        self.tamanho = 12
        self.explodiu = False
        self.sprite = None

        # A imagem é opcional. Sua ausência não impede o jogo de rodar.
        if asset is not None:
            try:
                caminho = asset("enemys", "Tiro.Tank.png")
                imagem = pygame.image.load(caminho).convert_alpha()

                area = imagem.get_bounding_rect()

                if area.width > 0 and area.height > 0:
                    imagem = imagem.subsurface(area).copy()

                self.sprite = pygame.transform.smoothscale(
                    imagem, (42, 21)
                )

            except (FileNotFoundError, pygame.error, OSError):
                self.sprite = None

    def get_rect(self):
        return pygame.Rect(
            round(self.posx - self.tamanho),
            round(self.posy - self.tamanho),
            self.tamanho * 2,
            self.tamanho * 2
        )

    def desenhar(self, tela, camera_x=0, camera_y=0):
        if not self.ativo:
            return

        x = round(self.posx - camera_x)
        y = round(self.posy - camera_y)

        angulo = math.degrees(math.atan2(self.dy, self.dx))

        if self.sprite is not None:
            imagem = pygame.transform.rotate(self.sprite, -angulo)
            retangulo = imagem.get_rect(center=(x, y))
            tela.blit(imagem, retangulo)
            return

        # Representação alternativa: chama e corpo do míssil.
        cauda_x = round(x - self.dx * 22)
        cauda_y = round(y - self.dy * 22)

        pygame.draw.line(
            tela, (255, 90, 35),
            (cauda_x, cauda_y), (x, y), 7
        )

        pygame.draw.line(
            tela, (255, 205, 90),
            (cauda_x, cauda_y), (x, y), 3
        )

        perpendicular_x = -self.dy * 5
        perpendicular_y = self.dx * 5

        ponta = (x + self.dx * 8, y + self.dy * 8)
        lado_1 = (
            round(x - self.dx * 7 + perpendicular_x),
            round(y - self.dy * 7 + perpendicular_y)
        )
        lado_2 = (
            round(x - self.dx * 7 - perpendicular_x),
            round(y - self.dy * 7 - perpendicular_y)
        )

        pygame.draw.polygon(
            tela, (255, 225, 150),
            [ponta, lado_1, lado_2]
        )

        # Pequeno brilho na parte traseira.
        pygame.draw.circle(
            tela, (255, 100, 45),
            (cauda_x, cauda_y), 4
        )
