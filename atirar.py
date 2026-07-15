import pygame


class Tiro:
    def __init__(self, x, y, velocidade=10):
        self.x = x
        self.y = y
        self.velocidade = velocidade
        self.ativo = True

    def atualizar(self):
        self.x += self.velocidade

        # Exemplo: desativa quando sai da tela
        if self.x > 800:
            self.ativo = False

    def desenhar(self, tela):
        import pygame
        pygame.draw.circle(tela, (255, 255, 0), (self.x, self.y), 5)