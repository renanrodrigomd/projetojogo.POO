"""Tela da partida (antigo iniciar_jogo do jogo.py, agora em classe)."""

import math

import pygame

from camera import Camera
from cenario import Cenario
from config import LARGURA, ALTURA, CHAO_Y, COR_PERIGO, COR_DESTAQUE
from fases import FASES
from Player import Player
from resumo import ResumoPartida
from telas.tela_base import Tela
from ui.efeitos import TextosFlutuantes, Vinheta, Tremor
from ui.hud import Hud, desenhar_barra


class TelaJogo(Tela):

    DURACAO_IMPACTO = 180
    BONUS_SEM_DANO = 200

    def __init__(self, gerenciador, indice_fase=0, pontuacao_inicial=0):
        super().__init__(gerenciador)

        self._indice_fase = indice_fase
        self._fase = FASES[indice_fase]
        self._pontuacao_inicial = pontuacao_inicial
        self._pontuacao = pontuacao_inicial
        self._tempo = 0.0  # só avança enquanto esta tela está ativa

        self._cenario = Cenario()
        self._hud = Hud()
        self._camera = Camera(self._fase.largura, ALTURA, LARGURA, ALTURA)

        self._jogador = Player(
            x=100, y=CHAO_Y - 60, chao_y=CHAO_Y,
            largura_mapa=self._fase.largura
        )
        self._inimigos = self._fase.criar_inimigos()
        self._impactos = []

        # Efeitos visuais
        self._textos = TextosFlutuantes()
        self._vinheta = Vinheta()
        self._tremor = Tremor()

        # Estatísticas para as telas finais
        self._total_inimigos = len(self._inimigos)
        self._derrotados = 0
        self._dano_sofrido = 0
        self._progresso_max = 0.0
        self._causa = "Desconhecida"
        self._dica = "Fique em movimento e atire primeiro."

    # Leitura (ENCAPSULAMENTO: o resto do jogo não mexe nos atributos)

    @property
    def indice_fase(self):
        return self._indice_fase

    @property
    def pontuacao_inicial(self):
        return self._pontuacao_inicial

    @property
    def pontuacao(self):
        return self._pontuacao

    @property
    def tempo(self):
        return self._tempo

    # Eventos

    def eventos(self, evento):
        if evento.type != pygame.KEYDOWN:
            return

        if evento.key == pygame.K_k:
            self._jogador.atirar()

        elif evento.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
            if self._jogador.no_chao:
                self._jogador.velocidade_y = self._jogador.forca_pulo
                self._jogador.no_chao = False

        elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
            from telas.pausa import Pausa
            self.gerenciador.empilhar(Pausa(self.gerenciador, self))

    # Lógica

    def atualizar(self, dt):
        self._tempo += dt / 1000

        jogador = self._jogador

        jogador.mover()
        jogador.atualizar()
        self._camera.atualizar_camera(jogador)

        self._atualizar_inimigos()
        self._tiros_do_jogador()
        self._tiros_dos_inimigos()

        self._textos.atualizar(dt)
        self._vinheta.atualizar(dt)
        self._tremor.atualizar(dt)

        self._progresso_max = max(
            self._progresso_max, min(1.0, jogador.posx / self._fase.final)
        )

        if not jogador.esta_vivo:
            from telas.fim_de_jogo import TelaDerrota
            self.gerenciador.trocar(
                TelaDerrota(self.gerenciador, self._criar_resumo()),
                fade=True
            )
            return

        if jogador.posx >= self._fase.final and self._robos_vivos() == 0:
            from telas.fim_de_jogo import TelaVitoria

            bonus = self.BONUS_SEM_DANO if self._dano_sofrido == 0 else 0
            self._pontuacao += bonus

            resumo = self._criar_resumo(
                estrelas=self._fase.estrelas(self._tempo), bonus=bonus
            )
            self.gerenciador.trocar(
                TelaVitoria(self.gerenciador, resumo), fade=True
            )

    def _criar_resumo(self, estrelas=0, bonus=0):
        return ResumoPartida(
            indice_fase=self._indice_fase,
            pontuacao_inicial=self._pontuacao_inicial,
            pontuacao=self._pontuacao,
            tempo=self._tempo,
            derrotados=self._derrotados,
            total_inimigos=self._total_inimigos,
            progresso=self._progresso_max,
            dano_sofrido=self._dano_sofrido,
            causa=self._causa,
            dica=self._dica,
            estrelas=estrelas,
            bonus=bonus,
        )

    def _ferir_jogador(self, inimigo, motivo):
        """Aplica dano ao jogador e dispara os efeitos. True se acertou."""
        jogador = self._jogador
        vida_antes = jogador.vida

        jogador.receber_dano()

        if jogador.vida >= vida_antes:
            return False  # estava invulnerável

        self._dano_sofrido += 1
        self._causa = f"{motivo} {inimigo.NOME}"
        self._dica = inimigo.DICA

        self._textos.adicionar(
            jogador.posx + jogador.largura / 2, jogador.posy - 10,
            "-1", COR_PERIGO
        )
        self._vinheta.disparar()
        self._tremor.disparar(250, 7)

        return True

    def _robos_vivos(self):
        return sum(1 for inimigo in self._inimigos if inimigo.vivo)

    def _atualizar_inimigos(self):
        jogador = self._jogador

        for inimigo in self._inimigos:
            if not inimigo.vivo:
                continue

            inimigo.mover(jogador.posx, jogador.posy)
            inimigo.olhar_player(jogador.posx, jogador.posy)
            inimigo.atualizar()

            if inimigo.pode_atacar(jogador.posx, jogador.posy):
                inimigo.atirar()

            # Colisão física com o jogador
            if inimigo.get_rect().colliderect(jogador.get_rect()):
                if self._ferir_jogador(inimigo, "Contato com"):
                    if inimigo.posx > jogador.posx:
                        jogador.posx -= 55
                    else:
                        jogador.posx += 55

    def _tiros_do_jogador(self):
        for tiro in self._jogador.tiros[:]:
            for inimigo in self._inimigos:
                if not inimigo.vivo:
                    continue

                if tiro.get_rect().colliderect(inimigo.get_rect()):
                    impacto = tiro.criar_impacto()
                    self._impactos.append(
                        [impacto[0], impacto[1], pygame.time.get_ticks()]
                    )

                    # POLIMORFISMO: cada tipo de inimigo reage ao dano
                    # do seu jeito (o Explosivo sai correndo, por ex.).
                    inimigo.receber_dano()

                    if not inimigo.vivo:
                        self._pontuacao += 100
                        self._derrotados += 1
                        self._textos.adicionar(
                            inimigo.posx + inimigo.largura / 2,
                            inimigo.posy - 20, "+100", COR_DESTAQUE
                        )

                    break

    def _tiros_dos_inimigos(self):
        jogador = self._jogador

        for inimigo in self._inimigos:
            for tiro in inimigo.tiros[:]:
                if tiro.get_rect().colliderect(jogador.get_rect()):
                    tiro.ativo = False
                    self._ferir_jogador(inimigo, "Disparo de")

    # Desenho

    def desenhar(self, superficie):
        cam = self._camera

        # O tremor desloca só o mundo; o HUD fica parado.
        tremor_x, tremor_y = self._tremor.deslocamento()
        cam_x = cam.x + tremor_x
        cam_y = max(0, cam.y + tremor_y)

        self._cenario.desenhar(superficie, cam_x, cam_y)
        self._cenario.desenhar_saida(
            superficie, cam_x, self._fase.final, self._robos_vivos() == 0
        )

        for inimigo in self._inimigos:
            inimigo.desenhar(superficie, cam_x, cam_y)

            if inimigo.vivo:
                desenhar_barra(
                    superficie,
                    int(inimigo.posx - cam_x),
                    int(inimigo.posy - cam_y - 12),
                    int(inimigo.largura), 6,
                    inimigo.vida, inimigo.vida_max, (80, 220, 110)
                )

        self._jogador.desenhar(superficie, cam_x, cam_y)
        self._desenhar_impactos(superficie, cam_x, cam_y)
        self._textos.desenhar(superficie, cam_x, cam_y)

        self._vinheta.desenhar(superficie)

        self._hud.desenhar(
            superficie, self._jogador, self._inimigos,
            self._pontuacao, self._fase, self._tempo, cam.x
        )

    def _desenhar_impactos(self, superficie, cam_x, cam_y):
        agora = pygame.time.get_ticks()

        for impacto in self._impactos[:]:
            x, y, inicio = impacto
            decorrido = agora - inicio

            if decorrido >= self.DURACAO_IMPACTO:
                self._impactos.remove(impacto)
                continue

            progresso = decorrido / self.DURACAO_IMPACTO
            tela_x = int(x - cam_x)
            tela_y = int(y - cam_y)

            # Anel de energia em expansão
            pygame.draw.circle(superficie, (255, 170, 55), (tela_x, tela_y),
                               int(3 + progresso * 15), 2)

            # Clarão central
            if progresso < 0.35:
                pygame.draw.circle(
                    superficie, (255, 240, 190), (tela_x, tela_y),
                    max(1, int(5 * (1 - progresso / 0.35)))
                )

            # Faíscas
            for angulo in range(0, 360, 45):
                rad = math.radians(angulo)
                dist_final = 5 + progresso * 20
                dist_inicial = max(0, dist_final - 7)

                pygame.draw.line(
                    superficie, (255, 210, 100),
                    (int(tela_x + math.cos(rad) * dist_inicial),
                     int(tela_y + math.sin(rad) * dist_inicial)),
                    (int(tela_x + math.cos(rad) * dist_final),
                     int(tela_y + math.sin(rad) * dist_final)),
                    2
                )
