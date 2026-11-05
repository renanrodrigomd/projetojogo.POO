"""Carregamento de imagens sem distorcer a proporção."""

import functools

import pygame

from caminhos import asset
from config import LARGURA, ALTURA


def encaixar(imagem, tamanho, fundo=(0, 0, 0)):
    """Redimensiona mantendo a proporção e centraliza sobre um fundo.

    As imagens de menu/vitória/derrota têm fundo preto, então as faixas
    laterais ficam invisíveis. Antes elas eram esticadas e distorcidas.
    """
    largura, altura = tamanho
    escala = min(largura / imagem.get_width(), altura / imagem.get_height())

    nova = pygame.transform.smoothscale(
        imagem,
        (int(imagem.get_width() * escala), int(imagem.get_height() * escala))
    )

    resultado = pygame.Surface(tamanho)
    resultado.fill(fundo)
    resultado.blit(nova, nova.get_rect(center=(largura // 2, altura // 2)))

    return resultado


@functools.lru_cache(maxsize=None)
def fundo_de_tela(nome_arquivo):
    """Imagem da pasta telasjogo já encaixada na janela (cacheada)."""
    imagem = pygame.image.load(asset("telasjogo", nome_arquivo)).convert()
    return encaixar(imagem, (LARGURA, ALTURA))


@functools.lru_cache(maxsize=None)
def botao(nome_arquivo):
    return pygame.image.load(
        asset("telasjogo", nome_arquivo)
    ).convert_alpha()


@functools.lru_cache(maxsize=None)
def titulo_pixel_art(nome_arquivo, altura):
    """Imagem de título com altura fixa, ampliada SEM suavizar (mantém
    o pixel art nítido). O fundo preto some ao desenhar com BLEND_ADD."""
    imagem = pygame.image.load(asset("telasjogo", nome_arquivo)).convert()
    largura = int(imagem.get_width() * altura / imagem.get_height())

    return pygame.transform.scale(imagem, (largura, altura))
