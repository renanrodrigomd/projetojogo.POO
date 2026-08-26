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
        self.camera_x = 0
        self.camera_y = 0

        self.tela = pygame.display.set_mode((self.largura, self.altura))

    def atualizar_camera(self, Jogador_x, jogador_y):
        self.camera_x = jogador_x - self.largura // 2
        self.camera_y = jogador_y - self.altura // 2

        if self.camera_x < 0:
            self.camera_x = 0

        if self.camera_x > self.largura_mapa - self.largura:
            self.camera_x = self.largura_mapa - self.largura

        if self.camera_y < 0:
            self.camera_y = 0


        if self.camera_y > self.altura_mapa - self.altura:
            self.camera_y = self.altura_mapa - self.altura
