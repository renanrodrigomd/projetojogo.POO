import pygame

class camera:
    def __init__(self, largura_mapa, altura_mapa, largura_tela, altura_tela):
        self.x = 0
        self.y = 0

        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

        self.largura_tela = largura_tela
        self.altura_tela = altura_tela

    def atualizar_camera(self, jogador):
        self.x = jogador.rect.centerx - self.largura_tela // 2
        self.y = jogador.rect.centery - self.altura_tela // 2


        self.x = max(0, min(self.x, self.largura_mapa - self.largura_tela))
        self.y = max(0, min(self.y, self.altura_mapa - self.altura_tela))

    def aplicar(self, rect):
        return rect.move(-self.x, -self.y)