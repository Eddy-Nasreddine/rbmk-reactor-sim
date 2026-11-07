import pygame

class Moderator(pygame.sprite.Sprite):
    def __init__(self, x, y, width=10, height=890):
        super().__init__()

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
