import pygame
import random
import math

class Neutron(pygame.sprite.Sprite):
    FAST_COLOR = (255, 80, 80)
    THERMAL_COLOR = (238, 200, 200)
    images = {}

    def __init__(self, x, y, radius=5, speed=3):
        super().__init__()

        self.radius = radius
        self.x = x
        self.y = y
        self.thermal_n = False

        angle = random.uniform(0, math.pi * 2)

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.image = self.get_image(self.FAST_COLOR)
        self.rect = self.image.get_rect(center=(x, y))

    def get_image(self, color):
        key = (color, self.radius)
        if key not in Neutron.images:
            image = pygame.Surface((self.radius * 2, self.radius * 2)).convert()
            image.set_colorkey((0, 0, 0))
            pygame.draw.circle(image, color, (self.radius, self.radius), self.radius)
            Neutron.images[key] = image
        return Neutron.images[key]

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)

    def moderate(self, moderator_rect):
        self.thermal_n = True
        self.image = self.get_image(self.THERMAL_COLOR)
        speed = math.hypot(self.dx, self.dy) * 0.5
        angle = random.uniform(0, math.pi * 2)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        if self.dx > 0:
            self.x = moderator_rect.right + self.radius
        else:
            self.x = moderator_rect.left - self.radius
        self.rect.center = (self.x, self.y)
