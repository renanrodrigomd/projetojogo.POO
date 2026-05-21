import pygame


class inimigos: #classe pai
  def __init__(self, x, y, velocidade = 2):
    self.y = y
    self.x = x
    self.velocidade = velocidade


  def perseguir(self,player):
    if self.x < player.posx:
      self.x += self.velocidade

    elif self.x > player.posx:
      self.x -= self.velocidade

  def desenhar(self, tela):
      
      pygame.draw.rect(tela,(234,109,0), (int(self.x), int(self.y), 40, 40))

    
class aereo(inimigos): #classe filha
 pass
class parado(inimigos): #classe filha
 pass
class terrestre(inimigos): #classe filha
  pass