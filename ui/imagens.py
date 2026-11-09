"""Imagens das telas (menu, vitória e derrota).

As três são ilustrações com FUNDO PRETO, feitas para serem somadas ao
que está atrás com pygame.BLEND_ADD: o preto não soma nada (fica
"transparente") e o brilho do desenho aparece por cima.
"""

import functools

import pygame

from caminhos import asset
from config import LARGURA, ALTURA

# Quanto de "quase preto" ainda conta como fundo ao recortar o desenho
LIMIAR_PRETO = 14


def _recortar_conteudo(imagem, limiar=LIMIAR_PRETO):
    """Recorta a imagem no menor retângulo que contém o desenho.

    Tudo que é (quase) preto é considerado fundo. Se algo der errado, a
    imagem inteira é devolvida e o jogo continua funcionando.
    """
    try:
        fundo = pygame.mask.from_threshold(
            imagem, (0, 0, 0), (limiar, limiar, limiar, 255)
        )
        fundo.invert()  # agora a máscara marca o desenho, não o fundo

        areas = fundo.get_bounding_rects()

        if not areas:
            return imagem

        area = areas[0].unionall(areas[1:])
        return imagem.subsurface(area).copy()

    except (pygame.error, ValueError, TypeError, AttributeError):
        return imagem


@functools.lru_cache(maxsize=None)
def titulo_recortado(nome_arquivo, altura):
    """Título (GAME OVER, WIN...) sem as margens pretas, com a altura
    pedida e a proporção original. Cacheado."""
    imagem = pygame.image.load(asset("telasjogo", nome_arquivo)).convert()
    imagem = _recortar_conteudo(imagem)

    largura = max(1, round(imagem.get_width() * altura / imagem.get_height()))

    return pygame.transform.smoothscale(imagem, (largura, altura))


@functools.lru_cache(maxsize=None)
def moldura_de_tela(nome_arquivo):
    """Ilustração em tela cheia ("cover"): preenche a janela toda sem
    distorcer, cortando o excesso das bordas. Cacheada."""
    imagem = pygame.image.load(asset("telasjogo", nome_arquivo)).convert()

    escala = max(LARGURA / imagem.get_width(), ALTURA / imagem.get_height())
    nova = pygame.transform.smoothscale(
        imagem,
        (round(imagem.get_width() * escala),
         round(imagem.get_height() * escala))
    )

    resultado = pygame.Surface((LARGURA, ALTURA))
    resultado.blit(
        nova,
        ((LARGURA - nova.get_width()) // 2, (ALTURA - nova.get_height()) // 2)
    )

    return resultado
