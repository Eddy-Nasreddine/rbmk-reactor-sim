import math
import random
from array import array
import pygame

class Explosion:
    GRAPHITE_COLORS = [(35, 35, 35), (55, 55, 55), (75, 75, 75)]
    FUEL_COLORS = [(0, 71, 171), (169, 169, 169)]
    EMBER_COLORS = [(255, 140, 0), (255, 90, 0), (255, 200, 60), (220, 60, 0)]
    RUBBLE_COLORS = [(20, 16, 14), (45, 38, 34), (65, 56, 50), (85, 75, 68)]

    def __init__(self, core_rect, screen_size, nominal_power):
        self.core_rect = pygame.Rect(core_rect)
        self.screen_size = screen_size
        self.nominal_power = nominal_power

        self.active = False
        self.frame = 0
        self.peak_power = 0
        self.debris = []
        self.rods = []
        self.smoke = []
        self.embers = []

        self.FLASH_FRAMES = 40
        self.SHAKE_FRAMES = 80
        self.FIREBALL_FRAMES = 75
        self.FIREBALL_RADIUS = 520
        self.OVERLAY_FRAME = 100
        self.SMOKE_LIFE = 180

        self.crater_rect = pygame.Rect(0, 0, int(self.core_rect.width * 0.55), int(self.core_rect.height * 0.6))
        self.crater_rect.center = self.core_rect.center

        self.flash = pygame.Surface(screen_size).convert()
        self.flash.fill((255, 255, 240))

        self.fireball = self.build_fireball(280)
        self.glow_rect = self.crater_rect.inflate(160, 120)
        self.glow = self.build_glow()
        self.puffs = [self.build_puff(radius) for radius in range(8, 129, 8)]

        self.band = pygame.Surface((self.core_rect.width, 260), pygame.SRCALPHA)
        self.band.fill((0, 0, 0, 180))

        self.title_font = pygame.font.Font(None, 96)
        self.text_font = pygame.font.Font(None, 34)

        self.sound = self.build_sound()

    def build_fireball(self, radius):
        fireball = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        outer = (190, 40, 0, 110)
        inner = (255, 245, 200, 255)
        layers = 16
        for i in range(layers):
            t = i / (layers - 1)
            color = tuple(int(a + (b - a) * t) for a, b in zip(outer, inner))
            pygame.draw.circle(fireball, color, (radius, radius), int(radius * (1 - t * 0.85)))
        return fireball

    def build_glow(self):
        glow = pygame.Surface(self.glow_rect.size, pygame.SRCALPHA)
        for i in range(10):
            rect = glow.get_rect().inflate(-i * self.glow_rect.width // 11, -i * self.glow_rect.height // 11)
            pygame.draw.ellipse(glow, (255, 100 + i * 10, 0, 32), rect)
        return glow

    def build_puff(self, radius):
        puff = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for i in range(4):
            pygame.draw.circle(puff, (150, 145, 140, 40), (radius, radius), radius - i * radius // 5)
        return puff

    def build_sound(self):
        mixer = pygame.mixer.get_init()
        if not mixer:
            return None

        frequency, size, channels = mixer
        samples = []
        rumble = 0.0
        phase = 0.0

        for i in range(int(frequency * 3)):
            t = i / frequency
            noise = random.uniform(-1, 1)
            rumble += (noise - rumble) * 0.02
            phase += 2 * math.pi * (60 - 25 * min(t, 1)) / frequency

            crack = noise * math.exp(-t / 0.04)
            roar = rumble * 6 * math.exp(-t / 0.9)
            debris = noise * 0.12 * math.exp(-t / 0.7)
            thump = math.sin(phase) * math.exp(-t / 0.5)
            samples.append(0.5 * crack + roar + debris + 0.6 * thump)

        peak = max(abs(sample) for sample in samples)
        data = array("h", (int(sample / peak * 0.9 * 32767) for sample in samples for _ in range(channels)))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def random_point(self, rect):
        angle = random.uniform(0, math.pi * 2)
        distance = math.sqrt(random.random())
        return (
            rect.centerx + math.cos(angle) * distance * rect.width / 2,
            rect.centery + math.sin(angle) * distance * rect.height / 2
        )

    def trigger(self, rod_rects, peak_power, volume):
        self.active = True
        self.frame = 0
        self.peak_power = peak_power

        self.debris = []
        for _ in range(500):
            x, y = self.random_point(self.crater_rect.inflate(-self.crater_rect.width // 2, -self.crater_rect.height // 2))
            angle = math.atan2(y - self.core_rect.centery, x - self.core_rect.centerx) + random.uniform(-0.4, 0.4)
            speed = random.uniform(5, 28)
            kind = random.random()
            if kind < 0.45:
                size, color = random.randint(7, 14), random.choice(self.GRAPHITE_COLORS)
            elif kind < 0.7:
                size, color = random.randint(4, 8), random.choice(self.FUEL_COLORS)
            else:
                size, color = random.randint(3, 6), random.choice(self.EMBER_COLORS)
            self.debris.append([x, y, math.cos(angle) * speed, math.sin(angle) * speed - random.uniform(4, 10), size, color])

        self.rods = [[rect.copy(), tip.copy(), random.uniform(-3, 3), random.uniform(-38, -22)] for rect, tip in rod_rects]
        self.smoke = []
        self.embers = [tuple(map(int, self.random_point(self.crater_rect))) for _ in range(220)]
        self.embers += [tuple(map(int, self.random_point(self.core_rect))) for _ in range(80)]

        if self.sound and volume > 0:
            self.sound.set_volume(volume)
            self.sound.play()

    def scorch(self, surface):
        soot = pygame.Surface(self.core_rect.size, pygame.SRCALPHA)
        soot.fill((10, 6, 4, 200))
        surface.blit(soot, self.core_rect)

        pygame.draw.ellipse(surface, (25, 18, 15), self.crater_rect)
        for _ in range(500):
            position = tuple(map(int, self.random_point(self.crater_rect.inflate(80, 60))))
            pygame.draw.circle(surface, random.choice(self.RUBBLE_COLORS), position, random.randint(4, 13))
        for _ in range(250):
            position = tuple(map(int, self.random_point(self.core_rect)))
            pygame.draw.circle(surface, random.choice(self.RUBBLE_COLORS), position, random.randint(3, 8))

    def overlay_visible(self):
        return self.active and self.frame >= self.OVERLAY_FRAME

    def get_shake(self):
        if self.frame >= self.SHAKE_FRAMES:
            return (0, 0)
        amount = int(16 * (1 - self.frame / self.SHAKE_FRAMES))
        return (random.randint(-amount, amount), random.randint(-amount, amount))

    def update(self):
        self.frame += 1

        for piece in self.debris:
            piece[0] += piece[2]
            piece[1] += piece[3]
            piece[2] *= 0.99
            piece[3] += 0.45
        self.debris = [piece for piece in self.debris if piece[1] < self.screen_size[1] + 20 and -40 < piece[0] < self.screen_size[0] + 40]

        for rod in self.rods:
            rod[0].x += rod[2]
            rod[0].y += rod[3]
            rod[1].x = rod[0].x
            rod[1].y = rod[0].bottom
            rod[3] += 0.1
        self.rods = [rod for rod in self.rods if rod[1].bottom > 0]

        if self.frame > 15:
            x, y = self.random_point(self.crater_rect)
            self.smoke.append([x, min(y, self.crater_rect.centery), random.uniform(-0.3, 0.9), random.uniform(-2.0, -0.7), 16.0, 0])

        for puff in self.smoke:
            puff[0] += puff[2]
            puff[1] += puff[3]
            puff[4] = min(128.0, puff[4] + 0.6)
            puff[5] += 1
        self.smoke = [puff for puff in self.smoke if puff[5] < self.SMOKE_LIFE and puff[1] + puff[4] > 0]

    def draw(self, screen):
        self.glow.set_alpha(random.randint(170, 255))
        screen.blit(self.glow, self.glow_rect)

        for position in self.embers:
            if random.random() < 0.6:
                pygame.draw.circle(screen, random.choice(self.EMBER_COLORS), position, random.randint(2, 4))

        for x, y, dx, dy, radius, age in self.smoke:
            puff = self.puffs[min(len(self.puffs) - 1, int(radius) // 8 - 1)]
            puff.set_alpha(int(255 * (1 - age / self.SMOKE_LIFE)))
            screen.blit(puff, (x - radius, y - radius))

        if self.frame < self.FIREBALL_FRAMES:
            radius = int(self.FIREBALL_RADIUS * (1 - math.exp(-self.frame / 8)))
            if radius > 0:
                fireball = pygame.transform.scale(self.fireball, (radius * 2, radius * 2))
                fireball.set_alpha(int(255 * min(1, (self.FIREBALL_FRAMES - self.frame) / 45)))
                screen.blit(fireball, fireball.get_rect(center=self.core_rect.center))

        for x, y, dx, dy, size, color in self.debris:
            pygame.draw.rect(screen, color, (x, y, size, size))

        for rect, tip, dx, dy in self.rods:
            pygame.draw.rect(screen, (96, 96, 96), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            pygame.draw.rect(screen, (255, 255, 255), tip)
            pygame.draw.rect(screen, (0, 0, 0), tip, 2)

    def draw_overlay(self, screen):
        if self.frame < self.FLASH_FRAMES:
            self.flash.set_alpha(int(255 * (1 - self.frame / self.FLASH_FRAMES) ** 2))
            screen.blit(self.flash, (0, 0))

        if not self.overlay_visible():
            return

        band_rect = self.band.get_rect(center=(self.core_rect.centerx, self.core_rect.centery - 40))
        screen.blit(self.band, band_rect)

        lines = [
            (self.title_font, "REACTOR DESTROYED", (230, 40, 30)),
            (self.text_font, f"Peak power: {int(self.peak_power):,} MW ({self.peak_power / self.nominal_power:.0f}x normal)", (240, 240, 240)),
            (self.text_font, "Click Restart or press R to try again", (200, 200, 200))
        ]
        y = band_rect.top + 30
        for font, text, color in lines:
            label = font.render(text, True, color)
            screen.blit(label, label.get_rect(midtop=(self.core_rect.centerx, y)))
            y += label.get_height() + 18
