import pygame
import random
from Neutron import Neutron

class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=10):
        super().__init__()

        self.x = x
        self.y = y
        self.radius = radius
        self.color = (169, 169, 169)
        self.disabled = True
        self.is_xenon = False
        self.has_iodine = False
        self.rect = pygame.Rect(
            x - self.radius,
            y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        self.DECAY_CHANCE = 1 / 60000
        self.XENON_CHANCE = 1 / 20000
        self.XENON_DECAY_CHANCE = 1 / 10000
        self.BURNOUT_CHANCE = 0.6

    def draw(self, screen):
        if self.is_xenon:
            self.color = (64, 64, 64)
        elif self.disabled:
            self.color = (169, 169, 169)
        else:
            self.color = (0, 71, 171)
        pygame.draw.circle(
            screen,
            self.color,
            (self.x, self.y),
            self.radius
        )

    def refuel(self):
        self.disabled = False
        self.has_iodine = False

    def revert(self):
        self.is_xenon = False
        self.disabled = True

    def decay(self):
        return random.random() < self.DECAY_CHANCE

    def decay_to_xenon(self):
        if self.has_iodine and random.random() < self.XENON_CHANCE:
            self.is_xenon = True
            return True
        return False

    def xenon_decay(self):
        if random.random() < self.XENON_DECAY_CHANCE:
            self.revert()
            return True
        return False

    def burn_out(self):
        if random.random() < self.BURNOUT_CHANCE:
            self.revert()
            return True
        return False

    def hit(self):
        if self.disabled:
            return []

        self.disabled = True
        self.has_iodine = True
        return [
            Neutron(self.x, self.y),
            Neutron(self.x, self.y),
            Neutron(self.x, self.y)
        ]
