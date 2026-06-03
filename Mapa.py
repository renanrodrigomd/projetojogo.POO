import pygame

class mapa:
    def __init__(self):
        pygame.init()
        self.largura = 1200
        self.altura = 777

        self.tela = pygame.display.set_mode((self.largura, self.altura))