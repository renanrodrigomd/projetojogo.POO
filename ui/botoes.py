"""Botões e menus navegáveis por teclado e mouse.

POO aplicada:
  * Botao é uma classe abstrata (contrato: area e desenhar).
  * BotaoImagem e BotaoTexto HERDAM de Botao.
  * MenuBotoes trata qualquer Botao do mesmo jeito (POLIMORFISMO).
  * Os atributos começam com "_" e são expostos por properties
    (ENCAPSULAMENTO).
"""

from abc import ABC, abstractmethod

import pygame

from config import (
    COR_PAINEL, COR_PAINEL_DESTAQUE, COR_BORDA, COR_CIANO,
    COR_TEXTO, COR_TEXTO_SUAVE
)
from ui.fontes import texto


class Botao(ABC):

    def __init__(self, rotulo, centro):
        self._rotulo = rotulo
        self._centro = centro
        self._selecionado = False

    @property
    def rotulo(self):
        return self._rotulo

    @property
    def selecionado(self):
        return self._selecionado

    @selecionado.setter
    def selecionado(self, valor):
        self._selecionado = bool(valor)

    @property
    @abstractmethod
    def area(self):
        """Retângulo usado para detectar o mouse."""

    def contem(self, posicao):
        return self.area.collidepoint(posicao)

    @abstractmethod
    def desenhar(self, tela):
        """Cada tipo de botão se desenha do seu jeito."""


class BotaoImagem(Botao):
    """Botão feito de um PNG (usado no menu principal)."""

    def __init__(self, rotulo, imagem, centro):
        super().__init__(rotulo, centro)

        self._imagem = imagem
        self._imagem_destaque = pygame.transform.smoothscale(
            imagem,
            (int(imagem.get_width() * 1.06), int(imagem.get_height() * 1.06))
        )

    @property
    def area(self):
        return self._imagem.get_rect(center=self._centro)

    def desenhar(self, tela):
        imagem = self._imagem_destaque if self._selecionado else self._imagem
        tela.blit(imagem, imagem.get_rect(center=self._centro))


class BotaoTexto(Botao):
    """Botão futurista desenhado por código (pausa, vitória, derrota)."""

    def __init__(self, rotulo, centro, largura=260, altura=48):
        super().__init__(rotulo, centro)
        self._largura = largura
        self._altura = altura

    @property
    def area(self):
        return pygame.Rect(
            self._centro[0] - self._largura // 2,
            self._centro[1] - self._altura // 2,
            self._largura,
            self._altura
        )

    def desenhar(self, tela):
        area = self.area

        if self._selecionado:
            fundo, borda, cor_texto = COR_PAINEL_DESTAQUE, COR_CIANO, COR_TEXTO
        else:
            fundo, borda, cor_texto = COR_PAINEL, COR_BORDA, COR_TEXTO_SUAVE

        pygame.draw.rect(tela, fundo, area, border_radius=8)
        pygame.draw.rect(tela, borda, area, 2, border_radius=8)

        if self._selecionado:
            # Marcador lateral que indica o botão ativo
            pygame.draw.rect(
                tela, COR_CIANO,
                (area.x + 8, area.y + 10, 4, area.height - 20),
                border_radius=2
            )

        texto(tela, self._rotulo, 20, cor_texto, area.center, True)


class MenuBotoes:
    """Controla seleção (teclado/mouse) e ação de uma lista de botões."""

    def __init__(self, botoes, acoes, horizontal=False):
        if len(botoes) != len(acoes):
            raise ValueError("Cada botão precisa de uma ação.")

        self._botoes = botoes
        self._acoes = acoes
        self._indice = 0

        if horizontal:
            self._teclas_anterior = (pygame.K_LEFT, pygame.K_a)
            self._teclas_proximo = (pygame.K_RIGHT, pygame.K_d)
        else:
            self._teclas_anterior = (pygame.K_UP, pygame.K_w)
            self._teclas_proximo = (pygame.K_DOWN, pygame.K_s)

        self._aplicar_selecao()

    def _aplicar_selecao(self):
        for i, botao in enumerate(self._botoes):
            botao.selecionado = (i == self._indice)

    def _selecionar(self, indice):
        self._indice = indice % len(self._botoes)
        self._aplicar_selecao()

    def eventos(self, evento):
        if evento.type == pygame.KEYDOWN:

            if evento.key in self._teclas_anterior:
                self._selecionar(self._indice - 1)

            elif evento.key in self._teclas_proximo:
                self._selecionar(self._indice + 1)

            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._acoes[self._indice]()

        elif evento.type == pygame.MOUSEMOTION:
            for i, botao in enumerate(self._botoes):
                if botao.contem(evento.pos):
                    self._selecionar(i)

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
        ):
            for i, botao in enumerate(self._botoes):
                if botao.contem(evento.pos):
                    self._selecionar(i)
                    self._acoes[i]()
                    return

    def desenhar(self, tela):
        for botao in self._botoes:
            botao.desenhar(tela)
