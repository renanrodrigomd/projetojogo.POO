"""HUD da partida (visual futurista, mais limpo e com mais área livre)."""

import math

import pygame

from caminhos import asset
from config import (
    LARGURA, ALTURA, CHAO_Y, COR_PAINEL, COR_BORDA, COR_PERIGO, COR_CIANO,
    COR_DESTAQUE, COR_TEXTO, COR_TEXTO_SUAVE, COR_OK
)
from ui.fontes import texto


def desenhar_barra(tela, x, y, largura, altura, valor, maximo, cor):
    """Barra simples (usada nas barras de vida dos inimigos)."""
    pygame.draw.rect(tela, (20, 22, 28), (x, y, largura, altura),
                     border_radius=5)

    preenchimento = max(0, min(1, valor / maximo)) if maximo else 0

    pygame.draw.rect(tela, cor, (x, y, int(largura * preenchimento), altura),
                     border_radius=5)
    pygame.draw.rect(tela, (210, 215, 225), (x, y, largura, altura), 2,
                     border_radius=5)


def _painel(tela, retangulo):
    pygame.draw.rect(tela, COR_PAINEL, retangulo, border_radius=12)
    pygame.draw.rect(tela, COR_BORDA, retangulo, 2, border_radius=12)


class Hud:

    def __init__(self):
        self._retrato = self._carregar_retrato()

    @staticmethod
    def _carregar_retrato():
        """Usa assets/ui/retrato_gepeto.png se existir (sprite futura)."""
        caminho = asset("ui", "retrato_gepeto.png")

        if caminho.exists():
            imagem = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.smoothscale(imagem, (62, 62))

        return None

    def desenhar(self, tela, jogador, inimigos, pontuacao, fase, tempo,
                 camera_x, checkpoints=(), combo=None):
        vivos = sum(1 for inimigo in inimigos if inimigo.vivo)

        self._painel_jogador(tela, jogador)
        self._painel_tempo(tela, fase, tempo)
        self._painel_pontos(tela, pontuacao, vivos)
        self._barra_progresso(tela, jogador, fase, checkpoints)
        self._objetivo(tela, jogador, fase, vivos, camera_x, tempo)
        self._combo(tela, combo)
        self._armas_e_dash(tela, jogador)

    # Blocos do HUD

    def _combo(self, tela, combo):
        """Medidor de combo (só aparece com 2 abates seguidos ou mais)."""
        if combo is None or not combo.ativo:
            return

        texto(tela, f"COMBO  x{combo.multiplicador}", 22, COR_DESTAQUE,
              (LARGURA - 18, 112), direita=True)
        desenhar_barra(tela, LARGURA - 218, 142, 200, 8,
                       combo.fracao_restante, 1, COR_DESTAQUE)

    def _armas_e_dash(self, tela, jogador):
        """Armas (com munição) e recarga do dash, no canto inferior."""
        base_y = ALTURA - 76
        _painel(tela, pygame.Rect(18, base_y, 436, 60))

        for i, arma in enumerate(jogador.armas):
            ativo = i == jogador.indice_arma
            slot = pygame.Rect(28 + i * 148, base_y + 10, 140, 40)

            pygame.draw.rect(tela, (20, 34, 50) if ativo else (14, 18, 26),
                             slot, border_radius=8)
            pygame.draw.rect(tela, COR_CIANO if ativo else COR_BORDA, slot, 2,
                             border_radius=8)

            cor = COR_TEXTO if arma.disponivel else (90, 98, 112)
            municao = ("INF" if arma.infinita
                       else f"{arma.municao}/{arma.MUNICAO_MAX}")

            texto(tela, str(i + 1), 12, COR_TEXTO_SUAVE,
                  (slot.x + 8, slot.y + 5))
            texto(tela, arma.NOME, 13, cor, (slot.x + 22, slot.y + 4))
            texto(tela, municao, 16, cor, (slot.x + 22, slot.y + 20))

        # Dash
        pronto = jogador.dash_pronto
        texto(tela, "DASH  (SHIFT)", 12,
              COR_CIANO if pronto else COR_TEXTO_SUAVE, (332, base_y + 12))
        desenhar_barra(tela, 332, base_y + 32, 110, 12, jogador.dash_fracao,
                       1, COR_CIANO if pronto else (70, 96, 124))

    def _painel_jogador(self, tela, jogador):
        _painel(tela, pygame.Rect(18, 14, 330, 78))

        # Retrato (espaço reservado para a sprite do Gepeto)
        moldura = pygame.Rect(27, 22, 62, 62)

        if self._retrato:
            tela.blit(self._retrato, moldura)
        else:
            pygame.draw.rect(tela, (20, 34, 50), moldura, border_radius=8)
            texto(tela, "G", 34, COR_CIANO, moldura.center, True)

        pygame.draw.rect(tela, COR_CIANO, moldura, 2, border_radius=8)

        texto(tela, "GEPETO", 18, COR_TEXTO, (104, 24))
        texto(tela, "ENERGIA", 12, COR_TEXTO_SUAVE, (104, 68))

        if jogador.escudo_ativo:
            texto(tela, f"ESCUDO {jogador.escudo_restante:.1f}s", 14,
                  COR_CIANO, (260, 26))

        # Vida em módulos de energia
        for i in range(jogador.vida_max):
            celula = pygame.Rect(104 + i * 44, 46, 38, 16)

            if i < jogador.vida:
                pygame.draw.rect(tela, COR_PERIGO, celula, border_radius=4)
                pygame.draw.rect(tela, (255, 150, 150),
                                 (celula.x + 3, celula.y + 3,
                                  celula.width - 6, 3), border_radius=2)
            else:
                pygame.draw.rect(tela, (28, 32, 42), celula, border_radius=4)

            pygame.draw.rect(tela, (210, 215, 225), celula, 2,
                             border_radius=4)

    def _painel_tempo(self, tela, fase, tempo):
        _painel(tela, pygame.Rect(LARGURA // 2 - 120, 14, 240, 78))

        minutos = int(tempo) // 60
        segundos = int(tempo) % 60

        texto(tela, f"{minutos:02d}:{segundos:02d}", 32, COR_TEXTO,
              (LARGURA // 2, 44), True)
        texto(tela, f"FASE {fase.numero}  •  {fase.nome.upper()}", 12,
              COR_CIANO, (LARGURA // 2, 74), True)

    def _painel_pontos(self, tela, pontuacao, vivos):
        _painel(tela, pygame.Rect(LARGURA - 348, 14, 330, 78))

        texto(tela, "PONTOS", 12, COR_TEXTO_SUAVE, (LARGURA - 328, 24))
        texto(tela, f"{pontuacao:04d}", 30, COR_DESTAQUE,
              (LARGURA - 328, 42))

        texto(tela, "ROBÔS", 12, COR_TEXTO_SUAVE, (LARGURA - 130, 24))
        cor = COR_OK if vivos == 0 else COR_TEXTO
        texto(tela, str(vivos), 30, cor, (LARGURA - 130, 42))

    def _barra_progresso(self, tela, jogador, fase, checkpoints):
        x, y, largura, altura = 18, 102, LARGURA - 36, 6

        progresso = max(0.0, min(1.0, jogador.posx / fase.final))

        pygame.draw.rect(tela, (20, 24, 32), (x, y, largura, altura),
                         border_radius=3)
        pygame.draw.rect(tela, COR_CIANO,
                         (x, y, int(largura * progresso), altura),
                         border_radius=3)

        # Checkpoints (verde = já ativado)
        for cp_x, ativo in checkpoints:
            marca_x = x + int(largura * min(1.0, cp_x / fase.final))
            pygame.draw.rect(
                tela, COR_OK if ativo else (95, 106, 128),
                (marca_x - 1, y - 4, 3, 14)
            )

        # Marcador do jogador e bandeira da saída
        marcador_x = x + int(largura * progresso)
        pygame.draw.circle(tela, (255, 255, 255), (marcador_x, y + 3), 6)
        pygame.draw.circle(tela, COR_CIANO, (marcador_x, y + 3), 6, 2)
        pygame.draw.rect(tela, COR_DESTAQUE, (x + largura - 3, y - 5, 4, 16),
                         border_radius=2)

    def _objetivo(self, tela, jogador, fase, vivos, camera_x, tempo):
        if vivos:
            texto(tela, f"ELIMINE OS ROBÔS  •  FALTAM {vivos}", 14,
                  COR_TEXTO_SUAVE, (24, 118))
            return

        if jogador.posx >= fase.final:
            return

        # Área limpa: mensagem piscando + seta apontando para a saída
        pulso = 0.5 + 0.5 * math.sin(tempo * 6)

        texto(tela, "ÁREA LIMPA  •  SAÍDA LIBERADA", 20, COR_OK,
              (LARGURA // 2, 140), True, alfa=140 + 115 * pulso)

        if fase.final - camera_x > LARGURA - 60:
            ponta = LARGURA - 24 - int(6 * pulso)
            meio = CHAO_Y - 230

            pygame.draw.polygon(
                tela, COR_OK,
                [(ponta, meio), (ponta - 26, meio - 20), (ponta - 26, meio + 20)]
            )
