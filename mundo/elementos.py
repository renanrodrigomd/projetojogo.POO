"""Elementos do mapa: plataformas, barreiras, perigos, checkpoints e itens.

POO aplicada:
  * ElementoMundo é abstrata e define o contrato (de_dados, _desenhar).
  * Plataforma, Barreira, Perigo, Checkpoint e Item HERDAM dela.
  * Perigo e Item são abstratas: PocaEnergia/PilarEletrico e
    KitVida/Escudo/RelogioTempo as especializam (POLIMORFISMO: o jogo
    trata todo Perigo e todo Item do mesmo jeito).
  * Estado interno (_coletado, _ativo, _tempo) só muda por métodos.

Tudo é desenhado por código; quando as sprites chegarem, basta trocar o
conteúdo de cada método _desenhar.
"""

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

import pygame

from config import LARGURA, CHAO_Y, COR_CIANO, COR_DESTAQUE, COR_OK, COR_PERIGO


class ElementoMundo(ABC):
    MARGEM_VISIVEL = 90

    def __init__(self, x, y, largura, altura):
        self._rect = pygame.Rect(int(x), int(y), int(largura), int(altura))

    @property
    def rect(self):
        return self._rect

    @classmethod
    @abstractmethod
    def de_dados(cls, dados):
        """Cria o elemento a partir de um dicionário do arquivo da fase."""

    def atualizar(self, dt):
        """Animações/ciclos internos (dt em ms)."""

    def visivel(self, camera_x):
        return (
            self._rect.right > camera_x - self.MARGEM_VISIVEL
            and self._rect.left < camera_x + LARGURA + self.MARGEM_VISIVEL
        )

    def desenhar(self, tela, camera_x, camera_y):
        if self.visivel(camera_x):
            self._desenhar(
                tela, self._rect.move(-int(camera_x), -int(camera_y))
            )

    @abstractmethod
    def _desenhar(self, tela, r):
        """Desenho do elemento. `r` já está em coordenadas de tela."""


# ----------------------------------------------------------------------
# Estrutura: plataformas e barreiras
# ----------------------------------------------------------------------

class Plataforma(ElementoMundo):
    """Plataforma que se atravessa por baixo e se pisa por cima."""

    ESPESSURA = 16

    def __init__(self, x, y, largura):
        super().__init__(x, y, largura, self.ESPESSURA)

    @classmethod
    def de_dados(cls, dados):
        return cls(dados["x"], dados["y"], dados["largura"])

    def _desenhar(self, tela, r):
        pygame.draw.rect(tela, (30, 38, 52), r, border_radius=4)
        pygame.draw.rect(tela, (62, 74, 96), r, 2, border_radius=4)
        pygame.draw.line(tela, COR_CIANO,
                         (r.left + 5, r.top + 2), (r.right - 5, r.top + 2), 2)

        for x in range(r.left + 16, r.right - 8, 34):
            pygame.draw.circle(tela, (92, 106, 130), (x, r.top + 10), 2)


class Barreira(ElementoMundo):
    """Obstáculo sólido: bloqueia passos e tiros e dá para subir nele."""

    # estilo: (largura, altura) padrão
    ESTILOS = {
        "caixa": (56, 56),
        "carro": (150, 64),
        "concreto": (90, 80),
    }

    def __init__(self, x, largura, altura, estilo="caixa", y=CHAO_Y):
        if estilo not in self.ESTILOS:
            raise ValueError(
                f"estilo '{estilo}' inválido (use: {', '.join(self.ESTILOS)})"
            )

        super().__init__(x, y - altura, largura, altura)
        self._estilo = estilo

    @property
    def estilo(self):
        return self._estilo

    @classmethod
    def de_dados(cls, dados):
        estilo = dados.get("estilo", "caixa")
        largura_padrao, altura_padrao = cls.ESTILOS.get(estilo, (56, 56))

        return cls(
            dados["x"],
            dados.get("largura", largura_padrao),
            dados.get("altura", altura_padrao),
            estilo,
            dados.get("y", CHAO_Y),
        )

    def _desenhar(self, tela, r):
        if self._estilo == "carro":
            self._desenhar_carro(tela, r)
        elif self._estilo == "concreto":
            self._desenhar_concreto(tela, r)
        else:
            self._desenhar_caixa(tela, r)

    @staticmethod
    def _desenhar_caixa(tela, r):
        pygame.draw.rect(tela, (62, 76, 94), r, border_radius=3)
        pygame.draw.rect(tela, (34, 42, 54), r, 3, border_radius=3)

        # faixa de alerta no topo
        for x in range(r.left + 3, r.right - 10, 14):
            pygame.draw.rect(tela, COR_DESTAQUE, (x, r.top + 5, 7, 6))

        for y in range(r.top + 20, r.bottom - 6, 14):
            pygame.draw.line(tela, (44, 54, 68),
                             (r.left + 5, y), (r.right - 5, y), 2)

        for cx, cy in ((r.left + 6, r.bottom - 6), (r.right - 6, r.bottom - 6)):
            pygame.draw.circle(tela, (110, 124, 146), (cx, cy), 2)

    @staticmethod
    def _desenhar_concreto(tela, r):
        pygame.draw.rect(tela, (92, 97, 106), r, border_radius=2)
        pygame.draw.rect(tela, (56, 60, 68), r, 3, border_radius=2)

        # rachaduras
        pygame.draw.lines(tela, (58, 62, 70), False, [
            (r.left + r.width * 0.3, r.top + 4),
            (r.left + r.width * 0.45, r.top + r.height * 0.4),
            (r.left + r.width * 0.35, r.top + r.height * 0.7),
        ], 2)

        # vergalhões expostos no topo
        for k in (0.2, 0.55, 0.8):
            x = int(r.left + r.width * k)
            pygame.draw.line(tela, (130, 84, 60),
                             (x, r.top), (x + 3, r.top - 12), 2)

    @staticmethod
    def _desenhar_carro(tela, r):
        w, h = r.width, r.height
        x, y = r.left, r.top

        # cabine
        pygame.draw.polygon(tela, (58, 66, 80), [
            (x + w * 0.22, y + h * 0.40), (x + w * 0.34, y + h * 0.05),
            (x + w * 0.68, y + h * 0.05), (x + w * 0.82, y + h * 0.40),
        ])
        pygame.draw.polygon(tela, (26, 34, 48), [
            (x + w * 0.30, y + h * 0.38), (x + w * 0.38, y + h * 0.14),
            (x + w * 0.64, y + h * 0.14), (x + w * 0.74, y + h * 0.38),
        ])

        # carroceria
        corpo = pygame.Rect(x, y + int(h * 0.38), w, int(h * 0.46))
        pygame.draw.rect(tela, (98, 92, 94), corpo, border_radius=6)
        pygame.draw.rect(tela, (54, 50, 54), corpo, 3, border_radius=6)
        pygame.draw.line(tela, (130, 84, 60),
                         (x + w * 0.5, y + h * 0.44),
                         (x + w * 0.66, y + h * 0.6), 3)

        # rodas
        for k in (0.22, 0.78):
            centro = (int(x + w * k), int(y + h * 0.86))
            pygame.draw.circle(tela, (24, 26, 32), centro, int(h * 0.16))
            pygame.draw.circle(tela, (90, 96, 108), centro, int(h * 0.07))


# ----------------------------------------------------------------------
# Perigos
# ----------------------------------------------------------------------

class Perigo(ElementoMundo, ABC):
    """Tudo que machuca o jogador ao encostar."""

    NOME = "Perigo"
    DICA = "Observe o cenário antes de avançar."

    @property
    @abstractmethod
    def perigoso(self):
        """True quando está causando dano agora."""

    def reacao(self, jogador):
        """O que acontece com o jogador depois de ser ferido."""


class PocaEnergia(Perigo):
    """Poça de energia no chão: é preciso pular por cima."""

    NOME = "Poça de energia"
    DICA = "Pule as poças de energia ou use as plataformas."
    ALTURA = 12

    def __init__(self, x, largura):
        super().__init__(x, CHAO_Y - self.ALTURA, largura, self.ALTURA)
        self._tempo = 0.0

    @classmethod
    def de_dados(cls, dados):
        return cls(dados["x"], dados["largura"])

    @property
    def perigoso(self):
        return True

    def atualizar(self, dt):
        self._tempo += dt

    def reacao(self, jogador):
        jogador.velocidade_y = -7   # pulinho para sair da poça
        jogador.no_chao = False

    def _desenhar(self, tela, r):
        poca = pygame.Rect(r.left, r.top - 4, r.width, 20)
        pygame.draw.ellipse(tela, (14, 86, 78), poca)
        pygame.draw.ellipse(tela, (40, 220, 180), poca.inflate(-10, -8))
        pygame.draw.ellipse(tela, (190, 255, 235), poca.inflate(-22, -14), 2)

        # bolhas de energia subindo
        for i in range(max(1, r.width // 46)):
            fase = (self._tempo / 700 + i * 0.37) % 1
            bx = r.left + 18 + (i * 46) % max(1, r.width - 30)
            by = r.top + 4 - int(fase * 22)
            pygame.draw.circle(tela, (150, 255, 225), (bx, by),
                               max(1, int(3 * (1 - fase))))


class PilarEletrico(Perigo):
    """Pilar que liga e desliga em ciclo. Pisca antes de ligar."""

    NOME = "Pilar elétrico"
    DICA = "Espere o pilar apagar: ele pisca antes de ligar."

    ALTURA = 96
    LARGURA = 26
    DESLIGADO = 1600
    AVISO = 400
    LIGADO = 1200

    def __init__(self, x, deslocamento=0):
        super().__init__(x, CHAO_Y - self.ALTURA, self.LARGURA, self.ALTURA)
        self._tempo = float(deslocamento)

    @classmethod
    def de_dados(cls, dados):
        return cls(dados["x"], dados.get("deslocamento", 0))

    @property
    def _ciclo(self):
        total = self.DESLIGADO + self.AVISO + self.LIGADO
        return self._tempo % total

    @property
    def em_aviso(self):
        return self.DESLIGADO <= self._ciclo < self.DESLIGADO + self.AVISO

    @property
    def perigoso(self):
        return self._ciclo >= self.DESLIGADO + self.AVISO

    def atualizar(self, dt):
        self._tempo += dt

    def reacao(self, jogador):
        # Empurra o jogador para longe do pilar
        if jogador.posx + jogador.largura / 2 < self._rect.centerx:
            jogador.posx -= 50
        else:
            jogador.posx += 50

        jogador.velocidade_y = -6
        jogador.no_chao = False

    def _desenhar(self, tela, r):
        centro_x = r.centerx

        # base e haste
        pygame.draw.rect(tela, (38, 44, 56),
                         (centro_x - 19, r.bottom - 14, 38, 14),
                         border_radius=3)
        pygame.draw.rect(tela, (70, 80, 98),
                         (centro_x - 5, r.top + 12, 10, r.height - 24))
        pygame.draw.rect(tela, (58, 66, 82),
                         (centro_x - 12, r.top, 24, 14), border_radius=3)

        if self.perigoso:
            pygame.draw.rect(tela, (20, 110, 150),
                             (centro_x - 13, r.top + 14, 26, r.height - 28))
            pygame.draw.rect(tela, (70, 205, 255),
                             (centro_x - 7, r.top + 14, 14, r.height - 28))
            pygame.draw.rect(tela, (235, 252, 255),
                             (centro_x - 2, r.top + 14, 4, r.height - 28))

            # raio irregular
            pontos = [(centro_x, r.top + 14)]
            for y in range(r.top + 30, r.bottom - 14, 16):
                pontos.append((centro_x + random.randint(-11, 11), y))
            pontos.append((centro_x, r.bottom - 14))
            pygame.draw.lines(tela, (255, 255, 255), False, pontos, 2)

        elif self.em_aviso:
            # faíscas piscando
            if int(self._tempo // 70) % 2 == 0:
                for _ in range(3):
                    y = random.randint(r.top + 16, r.bottom - 18)
                    pygame.draw.line(
                        tela, COR_CIANO,
                        (centro_x - 6, y), (centro_x + random.randint(2, 8), y + 5),
                        2
                    )
            pygame.draw.circle(tela, COR_DESTAQUE, (centro_x, r.top + 7), 4)


# ----------------------------------------------------------------------
# Checkpoint
# ----------------------------------------------------------------------

class Checkpoint(ElementoMundo):
    """Farol que salva o progresso quando o jogador encosta."""

    LARGURA = 36
    ALTURA = 120

    def __init__(self, x):
        super().__init__(x - self.LARGURA // 2, CHAO_Y - self.ALTURA,
                         self.LARGURA, self.ALTURA)
        self._ativo = False
        self._tempo = 0.0

    @classmethod
    def de_dados(cls, dados):
        return cls(dados["x"])

    @property
    def ativo(self):
        return self._ativo

    @property
    def x(self):
        return self._rect.centerx

    def ativar(self):
        self._ativo = True

    def atualizar(self, dt):
        self._tempo += dt

    def _desenhar(self, tela, r):
        cx = r.centerx

        pygame.draw.rect(tela, (40, 46, 58),
                         (cx - 16, r.bottom - 10, 32, 10), border_radius=3)
        pygame.draw.rect(tela, (90, 100, 118),
                         (cx - 3, r.top + 24, 6, r.height - 34))

        if self._ativo:
            cor, miolo = (80, 255, 170), (210, 255, 235)
            pulso = 0.5 + 0.5 * math.sin(self._tempo / 220)
            pygame.draw.circle(tela, (30, 120, 90), (cx, r.top + 16),
                               int(16 + 5 * pulso), 2)
        else:
            cor, miolo = (170, 70, 70), (230, 140, 140)

        pygame.draw.circle(tela, cor, (cx, r.top + 16), 11)
        pygame.draw.circle(tela, miolo, (cx - 3, r.top + 12), 4)


# ----------------------------------------------------------------------
# Itens
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class ResultadoItem:
    """O que a partida precisa fazer depois que um item é coletado."""
    mensagem: str
    cor: tuple
    tempo_removido: float = 0.0   # segundos tirados do cronômetro
    pontos: int = 50


class Item(ElementoMundo, ABC):
    TAMANHO = 30
    COR = COR_CIANO

    def __init__(self, x, y=CHAO_Y):
        # `y` é a superfície onde o item está apoiado (chão ou plataforma)
        super().__init__(x - self.TAMANHO // 2, y - self.TAMANHO - 22,
                         self.TAMANHO, self.TAMANHO)
        self._coletado = False
        self._tempo = 0.0

    @classmethod
    def de_dados(cls, dados):
        return cls(dados["x"], dados.get("y", CHAO_Y))

    @property
    def coletado(self):
        return self._coletado

    def marcar_coletado(self):
        self._coletado = True

    def atualizar(self, dt):
        self._tempo += dt

    def pode_coletar(self, jogador):
        return True

    @abstractmethod
    def aplicar(self, jogador):
        """Aplica o efeito ao jogador e devolve um ResultadoItem."""

    @abstractmethod
    def _icone(self, tela, centro):
        """Símbolo desenhado dentro do item."""

    def desenhar(self, tela, camera_x, camera_y):
        if self._coletado or not self.visivel(camera_x):
            return

        super().desenhar(tela, camera_x, camera_y)

    def _desenhar(self, tela, r):
        flutuar = int(4 * math.sin(self._tempo / 300))
        centro = (r.centerx, r.centery + flutuar)

        pulso = 0.5 + 0.5 * math.sin(self._tempo / 260)
        pygame.draw.circle(tela, self.COR, centro, int(22 + 3 * pulso), 1)

        losango = [
            (centro[0], centro[1] - 17), (centro[0] + 17, centro[1]),
            (centro[0], centro[1] + 17), (centro[0] - 17, centro[1]),
        ]
        pygame.draw.polygon(tela, (14, 20, 30), losango)
        pygame.draw.polygon(tela, self.COR, losango, 2)

        self._icone(tela, centro)


class KitVida(Item):
    COR = COR_PERIGO

    def pode_coletar(self, jogador):
        return jogador.vida < jogador.vida_max   # não gasta com vida cheia

    def aplicar(self, jogador):
        jogador.curar(1)
        return ResultadoItem("+1 ENERGIA", COR_OK)

    def _icone(self, tela, centro):
        x, y = centro
        pygame.draw.rect(tela, COR_PERIGO, (x - 3, y - 9, 6, 18))
        pygame.draw.rect(tela, COR_PERIGO, (x - 9, y - 3, 18, 6))


class Escudo(Item):
    COR = COR_CIANO
    DURACAO = 6000  # ms

    def aplicar(self, jogador):
        jogador.ativar_escudo(self.DURACAO)
        return ResultadoItem("ESCUDO!", COR_CIANO)

    def _icone(self, tela, centro):
        x, y = centro
        pygame.draw.polygon(tela, COR_CIANO, [
            (x - 8, y - 8), (x + 8, y - 8), (x + 8, y + 1),
            (x, y + 10), (x - 8, y + 1),
        ], 2)


class RelogioTempo(Item):
    COR = COR_DESTAQUE
    BONUS = 5  # segundos

    def aplicar(self, jogador):
        return ResultadoItem(f"-{self.BONUS}s", COR_DESTAQUE,
                             tempo_removido=self.BONUS)

    def _icone(self, tela, centro):
        x, y = centro
        pygame.draw.circle(tela, COR_DESTAQUE, (x, y), 9, 2)
        pygame.draw.line(tela, COR_DESTAQUE, (x, y), (x, y - 6), 2)
        pygame.draw.line(tela, COR_DESTAQUE, (x, y), (x + 5, y + 2), 2)
