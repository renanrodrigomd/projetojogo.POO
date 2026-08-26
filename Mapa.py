import pygame
from Personagem import Personagem
#cria o objeto mapa
class mapa:
    def __init__(self):
        pygame.init()
        self.largura = 1200
        self.altura = 777
        self.altura_mapa = 777
        self.largura_mapa = 10000
      

        self.tela = pygame.display.set_mode((self.largura, self.altura))

   