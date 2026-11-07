import pygame

class Water:
    surfaces = {}

    def __init__(self, x, y, size=26):
        self.size = size
        self.x = x
        self.y = y

        self.rect = pygame.Rect(
            x - self.size / 2,
            y - self.size / 2,
            self.size,
            self.size
        )

        self.heat = 0.0
        self.is_voided = False
        self.is_drained = False

        self.VOID_THRESHOLD = 80.0
        self.RECONDENSE_THRESHOLD = 60.0
        self.HEAT_PER_ABSORB = 5.0
        self.HEAT_PER_PASSAGE = 0.5

        self.LIGHT_BLUE = (204, 229, 255)
        self.DARK_RED = (255, 102, 102)

        self.color = self.get_color()
        self.drawn_color = None

    def heat_from_passage(self):
        if self.is_voided:
            return

        self.heat = min(100.0, self.heat + self.HEAT_PER_PASSAGE)
        if self.heat >= self.VOID_THRESHOLD:
            self.is_voided = True

    def absorb(self):
        if self.is_voided:
            return False

        self.heat = min(100.0, self.heat + self.HEAT_PER_ABSORB)
        if self.heat >= self.VOID_THRESHOLD:
            self.is_voided = True
        return True

    def update(self, cool_rate):
        self.heat = max(0.0, self.heat - cool_rate * 0.2)

        if self.is_voided and self.heat <= self.RECONDENSE_THRESHOLD:
            self.is_voided = False

        self.color = self.get_color()

    def drain(self):
        self.is_drained = True
        self.heat = 0.0
        self.is_voided = False
        self.color = self.get_color()

    def fill(self):
        self.is_drained = False
        self.heat = 0.0
        self.is_voided = False
        self.color = self.get_color()

    def get_color(self):
        if self.is_voided or self.is_drained:
            return None

        t = self.heat / 100.0
        r, g, b = self.LIGHT_BLUE
        red_r, red_g, red_b = self.DARK_RED
        return (
            int(r + (red_r - r) * t),
            int(g + (red_g - g) * t),
            int(b + (red_b - b) * t)
        )

    def needs_redraw(self):
        return self.color != self.drawn_color

    def get_surface(self, color):
        key = (color, self.size)
        if key not in Water.surfaces:
            surface = pygame.Surface((self.size, self.size)).convert()
            surface.fill(color)
            Water.surfaces[key] = surface
        return Water.surfaces[key]

    def draw(self, screen):
        self.drawn_color = self.color
        if self.color:
            screen.blit(self.get_surface(self.color), self.rect)
