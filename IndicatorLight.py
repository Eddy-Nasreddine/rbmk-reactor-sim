import pygame

class IndicatorLight:
    def __init__(self, x, y, radius, on_color=(80, 220, 80), off_color=(90, 90, 90)):
        self.x = x
        self.y = y
        self.radius = radius
        self.on_color = on_color
        self.off_color = off_color
        self.glow_color = tuple(min(255, c + 60) for c in on_color)

        self.bezel_color = (60, 60, 60)
        self.bezel_highlight = (150, 150, 150)

    def draw(self, screen, is_on):
        center = (self.x, self.y)
        pygame.draw.circle(screen, self.bezel_color, center, self.radius + 4)
        pygame.draw.circle(screen, self.bezel_highlight, center, self.radius + 4, 2)

        color = self.on_color if is_on else self.off_color
        pygame.draw.circle(screen, color, center, self.radius)

        if is_on:
            pygame.draw.circle(screen, self.glow_color, center, max(1, self.radius - 4))
