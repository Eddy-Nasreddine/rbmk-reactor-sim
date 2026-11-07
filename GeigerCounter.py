import math
import random
from array import array
import pygame

class GeigerCounter:
    def __init__(self, max_clicks=12, variants=6, frame_time=1 / 60, amplitude=0.7, volume=0.5):
        self.sounds = []
        self.volume = volume

        mixer = pygame.mixer.get_init()
        if not mixer:
            return

        self.frequency, size, self.channels = mixer
        self.amplitude = amplitude
        self.frame_samples = int(self.frequency * frame_time)
        self.click_samples = int(self.frequency * 0.008)

        for count in range(1, max_clicks + 1):
            self.sounds.append([self.build_sound(count) for _ in range(variants)])

    def build_click(self):
        ring_pitch = random.uniform(3000, 4500)
        body_pitch = random.uniform(900, 1300)
        samples = []

        for i in range(self.click_samples):
            t = i / self.frequency
            impulse = 1.0 if i < 2 else 0.0
            noise = random.uniform(-1, 1) * math.exp(-t / 0.0003)
            ring = math.sin(2 * math.pi * ring_pitch * t) * math.exp(-t / 0.001)
            body = math.sin(2 * math.pi * body_pitch * t) * math.exp(-t / 0.0025)
            samples.append(0.4 * impulse + 0.3 * noise + 0.4 * ring + 0.25 * body)

        peak = max(abs(sample) for sample in samples)
        return [sample / peak for sample in samples]

    def build_sound(self, count):
        mix = [0.0] * (self.frame_samples + self.click_samples)

        for _ in range(count):
            start = random.randrange(self.frame_samples)
            strength = random.uniform(0.6, 1.0)
            for i, sample in enumerate(self.build_click()):
                mix[start + i] += sample * strength

        peak = max(1.0, max(abs(sample) for sample in mix))
        data = array("h", (int(sample / peak * self.amplitude * 32767) for sample in mix for _ in range(self.channels)))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def click(self, count):
        if count <= 0 or self.volume <= 0 or not self.sounds:
            return

        sound = random.choice(self.sounds[min(count, len(self.sounds)) - 1])
        sound.set_volume(self.volume)
        sound.play()
