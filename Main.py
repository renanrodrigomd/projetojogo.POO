"""Ponto de entrada do jogo: python Main.py"""

import pygame

from config import LARGURA, ALTURA, TITULO
from gerenciador import Gerenciador
from telas.menu import MenuPrincipal


def main():
    pygame.init()

    superficie = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption(TITULO)

    gerenciador = Gerenciador(superficie)
    gerenciador.trocar(MenuPrincipal(gerenciador))
    gerenciador.executar()

    pygame.quit()


if __name__ == "__main__":
    main()
