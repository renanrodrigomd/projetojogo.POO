"""Fontes e texto com cache.

Para usar uma fonte própria (ex.: Orbitron, Rajdhani), coloque o arquivo
em assets/fontes/principal.ttf (ou .otf). Se não existir, o jogo usa a
primeira fonte disponível da lista FAMILIAS.
"""

import pygame

from caminhos import asset

FAMILIAS = "bahnschrift,segoeui,dejavusans,arial"

_FONTES = {}
_TEXTOS = {}
_LIMITE_TEXTOS = 400


def _arquivo_da_fonte():
    for nome in ("principal.ttf", "principal.otf"):
        caminho = asset("fontes", nome)
        if caminho.exists():
            return str(caminho)
    return None


def fonte(tamanho, negrito=True):
    chave = (tamanho, negrito)

    if chave not in _FONTES:
        arquivo = _arquivo_da_fonte()

        if arquivo:
            criada = pygame.font.Font(arquivo, tamanho)
            criada.set_bold(negrito)
        else:
            criada = pygame.font.SysFont(FAMILIAS, tamanho, bold=negrito)

        _FONTES[chave] = criada

    return _FONTES[chave]


def renderizar(mensagem, tamanho, cor, negrito=True):
    chave = (mensagem, tamanho, tuple(cor), negrito)

    if chave not in _TEXTOS:
        if len(_TEXTOS) >= _LIMITE_TEXTOS:
            _TEXTOS.clear()

        _TEXTOS[chave] = fonte(tamanho, negrito).render(mensagem, True, cor)

    return _TEXTOS[chave]


def texto(tela, mensagem, tamanho, cor, posicao,
          centralizado=False, negrito=True, alfa=255, direita=False):
    """Desenha texto. `direita=True` alinha a posição pela borda direita."""
    imagem = renderizar(mensagem, tamanho, cor, negrito)

    if alfa < 255:
        imagem = imagem.copy()
        imagem.set_alpha(max(0, int(alfa)))

    if centralizado:
        tela.blit(imagem, imagem.get_rect(center=posicao))
    elif direita:
        retangulo = imagem.get_rect()
        retangulo.x = posicao[0] - retangulo.width
        retangulo.y = posicao[1]
        tela.blit(imagem, retangulo)
    else:
        tela.blit(imagem, posicao)


def texto_espacado(tela, mensagem, tamanho, cor, centro, espaco=6,
                   negrito=False, alfa=255):
    """Texto com espaço extra entre as letras (visual futurista)."""
    letras = [renderizar(letra, tamanho, cor, negrito) for letra in mensagem]
    largura = sum(l.get_width() for l in letras) + espaco * (len(letras) - 1)

    x = centro[0] - largura // 2
    y = centro[1] - letras[0].get_height() // 2

    for letra in letras:
        if alfa < 255:
            letra = letra.copy()
            letra.set_alpha(int(alfa))
        tela.blit(letra, (x, y))
        x += letra.get_width() + espaco
