import pygame
import math

class player:
    def __init__(self, y, x):
        self.posy = y
        self.posx = x
        self.direção = 'd'

    def mover(self, direction):
        self.direção = direction

        if direction == "d":
           self.posx -= 2
        elif direction == "a":
           self.posx += 2
        elif direction == "space":
           self.posy -= 6



    def desenhar(self, tela):
        pygame.draw.rect(tela,(255,167,0), (int(self.posx), tela.get_height() -40, 40, 40))
