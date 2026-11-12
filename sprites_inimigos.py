"""Quadros de animação dos inimigos (assets/enemys/frames/<conjunto>/NN.png).

As pastas são geradas a partir das folhas de sprites (veja
tools/preparar_inimigos.py). Aqui só carregamos, escalamos e guardamos em
cache. Se algo faltar, devolvemos uma tupla vazia e o inimigo usa o desenho
antigo feito com formas, então o jogo nunca trava por causa de imagem.
"""

import functools

import pygame

from caminhos import asset


@functools.lru_cache(maxsize=None)
def quadros(conjunto, altura=None, largura=None, pixel_art=False):
    """Quadros do conjunto escalados para `altura` OU `largura` (px),
    mantendo a proporção. Devolve () se não for possível carregar."""
    pasta = asset("enemys", "frames", conjunto)

    try:
        arquivos = sorted(pasta.glob("*.png"))
        if not arquivos:
            return ()

        escalar = pygame.transform.scale if pixel_art else pygame.transform.smoothscale
        resultado = []

        for arquivo in arquivos:
            img = pygame.image.load(arquivo).convert_alpha()

            if altura is not None:
                novo = (round(img.get_width() * altura / img.get_height()), altura)
            else:
                novo = (largura, round(img.get_height() * largura / img.get_width()))

            resultado.append(escalar(img, novo))

        return tuple(resultado)

    except (pygame.error, OSError):
        return ()


@functools.lru_cache(maxsize=None)
def quadros_espelhados(conjunto, altura=None, largura=None, pixel_art=False):
    """Os mesmos quadros virados na horizontal (para a outra direção)."""
    return tuple(
        pygame.transform.flip(q, True, False)
        for q in quadros(conjunto, altura, largura, pixel_art)
    )
