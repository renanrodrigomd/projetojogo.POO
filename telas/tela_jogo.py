"""Tela da partida (antigo iniciar_jogo do jogo.py, agora em classe)."""

import math

import pygame

from camera import Camera
from cenario import Cenario
from config import LARGURA, ALTURA, CHAO_Y, COR_PERIGO, COR_DESTAQUE, \
    COR_OK, COR_CIANO
from fases import FASES
from Player import Player
from mundo.destrocos import Destrocos
from resumo import ResumoPartida, EstadoCheckpoint
from telas.tela_base import Tela
from ui.efeitos import TextosFlutuantes, Vinheta, Tremor
from ui.hud import Hud, desenhar_barra


class TelaJogo(Tela):

    DURACAO_IMPACTO = 180
    BONUS_SEM_DANO = 200
    PENALIDADE_CHECKPOINT = 5  # segundos somados ao continuar

    def __init__(self, gerenciador, indice_fase=0, pontuacao_inicial=0,
                 checkpoint=None):
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

        self._mundo = self._fase.criar_mundo()
        self._destrocos = Destrocos(self._fase.intensidade_destrocos)
        self._checkpoint = checkpoint

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

        if checkpoint is not None:
            self._restaurar(checkpoint)

    def _restaurar(self, estado):
        """Volta ao ponto do checkpoint com a vida cheia."""
        self._jogador.posx = estado.x - self._jogador.largura / 2
        self._jogador.restaurar_vida()

        self._tempo = estado.tempo + self.PENALIDADE_CHECKPOINT
        self._pontuacao = estado.pontuacao
        self._dano_sofrido = estado.dano_sofrido
        self._derrotados = len(estado.mortos)
        self._progresso_max = min(1.0, estado.x / self._fase.final)

        for i in estado.mortos:
            self._inimigos[i].vida = 0

        for i in estado.itens:
            self._mundo.itens[i].marcar_coletado()

        for i in estado.checkpoints:
            self._mundo.checkpoints[i].ativar()

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

        x_antes, y_antes = jogador.posx, jogador.posy

        jogador.mover()
        jogador.atualizar()
        jogador.atualizar_escudo(dt)
        self._mundo.resolver_jogador(jogador, x_antes, y_antes)
        self._camera.atualizar_camera(jogador)

        self._mundo.atualizar(dt)
        self._destrocos.atualizar(dt)

        self._atualizar_inimigos()
        self._processar_mundo()
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
            checkpoint=self._checkpoint,
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

            x_antes = inimigo.posx
            inimigo.mover(jogador.posx, jogador.posy)

            # Barreiras bloqueiam os robôs de chão (drones passam por cima)
            if not inimigo.VOA and self._mundo.bloqueia(inimigo.get_rect()):
                inimigo.posx = x_antes

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

                    self._mundo.expulsar_de_barreiras(jogador)

    def _processar_mundo(self):
        """Perigos, checkpoints e itens."""
        jogador = self._jogador
        corpo = jogador.get_rect()

        # Perigos (POLIMORFISMO: poça, pilar... todos são Perigo)
        for perigo in self._mundo.perigos:
            if perigo.perigoso and perigo.rect.colliderect(corpo):
                if self._ferir_jogador(perigo, "Contato com"):
                    perigo.reacao(jogador)
                    self._mundo.expulsar_de_barreiras(jogador)

        # Checkpoints
        for checkpoint in self._mundo.checkpoints:
            if not checkpoint.ativo and checkpoint.rect.colliderect(corpo):
                checkpoint.ativar()
                self._checkpoint = self._criar_estado_checkpoint(checkpoint)
                self._textos.adicionar(
                    checkpoint.x, CHAO_Y - 150, "CHECKPOINT", COR_OK, 1200
                )

        # Itens
        for item in self._mundo.itens:
            if (not item.coletado
                    and item.rect.colliderect(corpo)
                    and item.pode_coletar(jogador)):
                item.marcar_coletado()
                resultado = item.aplicar(jogador)

                self._pontuacao += resultado.pontos
                self._tempo = max(0.0, self._tempo - resultado.tempo_removido)
                self._textos.adicionar(
                    item.rect.centerx, item.rect.top - 10,
                    resultado.mensagem, resultado.cor, 1000
                )

    def _criar_estado_checkpoint(self, checkpoint):
        mundo = self._mundo

        return EstadoCheckpoint(
            x=checkpoint.x,
            pontuacao=self._pontuacao,
            tempo=self._tempo,
            dano_sofrido=self._dano_sofrido,
            mortos=tuple(
                i for i, inimigo in enumerate(self._inimigos)
                if not inimigo.vivo
            ),
            itens=tuple(
                i for i, item in enumerate(mundo.itens) if item.coletado
            ),
            checkpoints=tuple(
                i for i, c in enumerate(mundo.checkpoints) if c.ativo
            ),
        )

    def _tiros_do_jogador(self):
        for tiro in self._jogador.tiros[:]:
            # Barreiras seguram os tiros
            if tiro.ativo and self._mundo.bloqueia(tiro.get_rect()):
                impacto = tiro.criar_impacto()
                self._impactos.append(
                    [impacto[0], impacto[1], pygame.time.get_ticks()]
                )
                continue

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
            # Robôs mortos não podem causar dano: seus tiros somem.
            if not inimigo.vivo:
                inimigo.limpar_tiros()
                continue

            for tiro in inimigo.tiros[:]:
                if not tiro.ativo:
                    continue

                if self._mundo.bloqueia(tiro.get_rect()):
                    tiro.ativo = False
                    continue

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

        self._cenario.desenhar_fundo(superficie, cam_x, cam_y)
        self._destrocos.desenhar(superficie, cam_x)
        self._cenario.desenhar_chao(superficie, cam_x, cam_y)
        self._cenario.desenhar_saida(
            superficie, cam_x, self._fase.final, self._robos_vivos() == 0
        )
        self._mundo.desenhar(superficie, cam_x, cam_y)

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
        self._desenhar_escudo(superficie, cam_x, cam_y)
        self._desenhar_impactos(superficie, cam_x, cam_y)
        self._textos.desenhar(superficie, cam_x, cam_y)

        self._vinheta.desenhar(superficie)

        self._hud.desenhar(
            superficie, self._jogador, self._inimigos,
            self._pontuacao, self._fase, self._tempo, cam.x,
            self._mundo.marcadores_checkpoint()
        )

    def _desenhar_escudo(self, superficie, cam_x, cam_y):
        jogador = self._jogador

        if not jogador.escudo_ativo:
            return

        # Pisca nos últimos 1,5 s para avisar que vai acabar
        if jogador.escudo_restante < 1.5 and (
                pygame.time.get_ticks() // 120) % 2 == 0:
            return

        centro = (int(jogador.posx + jogador.largura / 2 - cam_x),
                  int(jogador.posy + jogador.altura / 2 - cam_y))
        pulso = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 140)

        pygame.draw.circle(superficie, COR_CIANO, centro,
                           int(42 + 3 * pulso), 3)
        pygame.draw.circle(superficie, (190, 240, 255), centro,
                           int(35 + 2 * pulso), 1)

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
