import pygame
from Player import player

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
      
      pygame.draw.circle(tela,(234,109,0), (int(self.x), int(self.y), 40, 40))

    
class aereo:
   def __init__(self,x, velocidade):
     self.x = x
     self.x = velocidade
     
   def voar(self,player):
      distancia = abs( self.x - player.posx)


      if distancia <= 8:
         return
       

      if self.x < player.posx:
         self.x += self.velocidade
      elif self.x > player.posx:
         self.x -= self.velocidade
         

     
class parado: #classe filha
    def __init__(self):

     def parado(self):
      
      self.velocidade == 0
      
class terrestre(inimigos): #classe filha
  pass