"""Menu principal, Como jogar e Créditos."""

import math

import pygame

from config import (
    LARGURA, ALTURA, COR_CIANO, COR_TEXTO, COR_DESTAQUE, COR_TEXTO_SUAVE,
    COR_PAINEL, COR_BORDA, COR_PERIGO, COR_OK, VERSAO
)
from telas.tela_base import Tela
from ui.botoes import BotaoTexto, MenuBotoes
from ui.fontes import texto, texto_espacado, renderizar
from ui.fundo_animado import FundoAnimado


class MenuPrincipal(Tela):

    def __init__(self, gerenciador):
        super().__init__(gerenciador)

        self._fundo = FundoAnimado(150)
        self._tempo = 0.0

        # Camada de brilho do título (cópia com transparência variável)
        self._brilho = renderizar("SMACHTECH", 96, COR_CIANO).copy()

        x = LARGURA // 2
        botoes = [
            BotaoTexto("JOGAR", (x, 330), 320, 52),
            BotaoTexto("COMO JOGAR", (x, 396), 320, 52),
            BotaoTexto("CRÉDITOS", (x, 462), 320, 52),
            BotaoTexto("SAIR", (x, 528), 320, 52),
        ]

        self._menu = MenuBotoes(
            botoes,
            [self._jogar, self._como_jogar, self._creditos, self._sair]
        )

    # Ações dos botões

    def _jogar(self):
        from telas.tela_jogo import TelaJogo
        self.gerenciador.trocar(TelaJogo(self.gerenciador, 0, 0), fade=True)

    def _como_jogar(self):
        self.gerenciador.empilhar(ComoJogar(self.gerenciador))

    def _creditos(self):
        self.gerenciador.empilhar(Creditos(self.gerenciador))

    def _sair(self):
        self.gerenciador.sair()

    # Tela

    def eventos(self, evento):
        self._menu.eventos(evento)

    def atualizar(self, dt):
        self._tempo += dt / 1000
        self._fundo.atualizar(dt)

    def desenhar(self, superficie):
        self._fundo.desenhar(superficie)

        pulso = 0.5 + 0.5 * math.sin(self._tempo * 2.2)

        # Brilho pulsante atrás do título
        self._brilho.set_alpha(int(40 + 70 * pulso))
        for deslocamento in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            superficie.blit(
                self._brilho,
                self._brilho.get_rect(
                    center=(LARGURA // 2 + deslocamento[0],
                            150 + deslocamento[1])
                )
            )

        texto(superficie, "SMACHTECH", 96, COR_CIANO, (LARGURA // 2, 150), True)
        texto_espacado(superficie, "INVASION ROBOTICS", 24, COR_TEXTO,
                       (LARGURA // 2, 218), espaco=10)

        pygame.draw.line(superficie, COR_CIANO,
                         (LARGURA // 2 - 190, 248), (LARGURA // 2 + 190, 248), 2)

        self._menu.desenhar(superficie)

        texto(superficie, "↑ ↓  navegar    ENTER  selecionar", 14,
              COR_TEXTO_SUAVE, (LARGURA // 2, ALTURA - 28), True)
        texto(superficie, VERSAO, 14, COR_TEXTO_SUAVE,
              (LARGURA - 20, ALTURA - 28), True)


class ComoJogar(Tela):
    """Explica controles e inimigos. Também abre pela pausa."""

    CONTROLES = [
        ("A / D   ou   ← / →", "Mover"),
        ("ESPAÇO   ou   W / ↑", "Pular"),
        ("K", "Atirar"),
        ("W / ↑  (segurando)", "Mirar para cima (também na diagonal)"),
        ("ESC   ou   P", "Pausar"),
    ]

    INIMIGOS = [
        ("Robô Terrestre", "Atira de longe. Pule os disparos.", COR_CIANO),
        ("Drone Aéreo", "Ataca de cima. Atire para cima.", (130, 190, 255)),
        ("Robô Blindado", "Aguenta 8 tiros. Atire de longe.", COR_DESTAQUE),
        ("Robô Explosivo", "Corre quando atingido. Derrube-o longe.", COR_PERIGO),
    ]

    def __init__(self, gerenciador):
        super().__init__(gerenciador)
        self._fundo = FundoAnimado(190)

    def eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (
            pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN
        ):
            self.gerenciador.desempilhar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.gerenciador.desempilhar()

    def atualizar(self, dt):
        self._fundo.atualizar(dt)

    def desenhar(self, superficie):
        self._fundo.desenhar(superficie)

        painel = pygame.Rect(150, 60, LARGURA - 300, ALTURA - 120)
        pygame.draw.rect(superficie, COR_PAINEL, painel, border_radius=16)
        pygame.draw.rect(superficie, COR_BORDA, painel, 2, border_radius=16)

        texto(superficie, "COMO JOGAR", 36, COR_CIANO, (LARGURA // 2, 105), True)
        texto(superficie, "Elimine todos os robôs e chegue à saída da fase.",
              17, COR_TEXTO_SUAVE, (LARGURA // 2, 145), True, negrito=False)

        texto(superficie, "CONTROLES", 16, COR_DESTAQUE, (190, 185))
        for i, (tecla, acao) in enumerate(self.CONTROLES):
            y = 218 + i * 34
            texto(superficie, tecla, 18, COR_TEXTO, (190, y))
            texto(superficie, acao, 18, COR_TEXTO_SUAVE, (520, y),
                  negrito=False)

        texto(superficie, "INIMIGOS", 16, COR_DESTAQUE, (190, 415))
        for i, (nome, descricao, cor) in enumerate(self.INIMIGOS):
            y = 448 + i * 32
            pygame.draw.circle(superficie, cor, (198, y + 10), 6)
            texto(superficie, nome, 18, COR_TEXTO, (216, y))
            texto(superficie, descricao, 18, COR_TEXTO_SUAVE, (470, y),
                  negrito=False)

        texto(superficie, "ESC  •  voltar", 15, COR_TEXTO_SUAVE,
              (LARGURA // 2, ALTURA - 82), True)


class Creditos(Tela):
    """Créditos com rolagem automática."""

    VELOCIDADE = 55  # pixels por segundo

    LINHAS = [
        ("SMACHTECH", 54, COR_CIANO),
        ("Invasion Robotics", 24, COR_TEXTO),
        ("", 40, COR_TEXTO),
        ("DESENVOLVEDORES", 18, COR_DESTAQUE),
        ("Renan Rodrigo Medeiros Dantas", 28, COR_TEXTO),
        ("Gustavo Medeiros Lucena", 28, COR_TEXTO),
        ("Juan Oliveira Fonseca", 28, COR_TEXTO),
        ("", 40, COR_TEXTO),
        ("PROJETO", 18, COR_DESTAQUE),
        ("Programação Orientada a Objetos", 24, COR_TEXTO),
        ("", 40, COR_TEXTO),
        ("FEITO COM", 18, COR_DESTAQUE),
        ("Python e Pygame", 24, COR_TEXTO),
        ("", 40, COR_TEXTO),
        ("Obrigado por jogar!", 26, COR_OK),
    ]

    ESPACO = 54

    def __init__(self, gerenciador):
        super().__init__(gerenciador)
        self._fundo = FundoAnimado(185)
        self._posicao = float(ALTURA)
        self._altura_total = len(self.LINHAS) * self.ESPACO

    def eventos(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (
            pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN
        ):
            self.gerenciador.desempilhar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.gerenciador.desempilhar()

    def atualizar(self, dt):
        self._fundo.atualizar(dt)

        velocidade = self.VELOCIDADE
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            velocidade *= 3  # segurar ESPAÇO acelera

        self._posicao -= velocidade * dt / 1000

        # Reinicia quando a última linha sai da tela
        if self._posicao < -self._altura_total:
            self._posicao = float(ALTURA)

    def desenhar(self, superficie):
        self._fundo.desenhar(superficie)

        for i, (mensagem, tamanho, cor) in enumerate(self.LINHAS):
            y = self._posicao + i * self.ESPACO

            if mensagem and -40 < y < ALTURA + 40:
                texto(superficie, mensagem, tamanho, cor,
                      (LARGURA // 2, y), True)

        texto(superficie, "ESC  •  voltar    ESPAÇO  •  acelerar", 14,
              COR_TEXTO_SUAVE, (LARGURA // 2, ALTURA - 24), True)
