import pygame

class ControlRod(pygame.sprite.Sprite):
    def __init__(self, x, y, width=10, height=890, tip_height=150):
        super().__init__()

        self.x = x
        self.y = y

        self.width = width
        self.height = height
        self.tip_height = tip_height
        self.min_y = y - height - tip_height
        self.max_y = y

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

        self.tip_rect = pygame.Rect(
            self.x,
            self.y + self.height,
            self.width,
            self.tip_height
        )

        self.channel_rect = pygame.Rect(
            self.x,
            self.max_y,
            self.width,
            0
        )

        self.CHANNEL_WATER_COLOR = (204, 229, 255)
        self.set_y(y)

    def raise_rod(self, amount):
        self.set_y(self.y - amount)

    def lower_rod(self, amount):
        self.set_y(self.y + amount)

    def set_y(self, position):
        self.y = max(self.min_y, min(self.max_y, position))
        self.rect.y = self.y
        self.tip_rect.y = self.y + self.height

        channel_top = max(self.tip_rect.bottom, self.max_y)
        self.channel_rect.top = channel_top
        self.channel_rect.height = max(0, self.max_y + self.height - channel_top)

    def draw_channel(self, screen):
        pygame.draw.rect(screen, self.CHANNEL_WATER_COLOR, self.channel_rect)

    def draw(self, screen):
        pygame.draw.rect(screen, (96, 96, 96), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        pygame.draw.rect(screen, (255, 255, 255), self.tip_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.tip_rect, 2)
