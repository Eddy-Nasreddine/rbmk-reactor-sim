import pygame

class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value, label="", decimals=3, suffix=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = 6
        self.handle_radius = 9

        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

        self.label = label
        self.decimals = decimals
        self.suffix = suffix
        self.font = pygame.font.Font(None, 22)
        self.dragging = False

        self.track_rect = pygame.Rect(x, y, width, self.height)
        self.label_text = None
        self.label_surface = None

    def _value_to_x(self):
        t = (self.value - self.min_value) / (self.max_value - self.min_value)
        return self.x + t * self.width

    def _x_to_value(self, mouse_x):
        t = (mouse_x - self.x) / self.width
        t = max(0.0, min(1.0, t))
        return self.min_value + t * (self.max_value - self.min_value)

    def _handle_center(self):
        return (int(self._value_to_x()), self.y + self.height // 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = pygame.Rect(0, 0, self.handle_radius * 2, self.handle_radius * 2)
            handle_rect.center = self._handle_center()

            if handle_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                self.dragging = True
                self.value = self._x_to_value(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.value = self._x_to_value(event.pos[0])

    def draw(self, screen):
        handle_center = self._handle_center()
        is_hovered = pygame.Vector2(pygame.mouse.get_pos()).distance_to(handle_center) <= self.handle_radius

        pygame.draw.rect(screen, (210, 210, 210), self.track_rect, border_radius=3)

        filled_rect = pygame.Rect(self.x, self.y, handle_center[0] - self.x, self.height)
        pygame.draw.rect(screen, (65, 115, 190), filled_rect, border_radius=3)

        handle_color = (65, 115, 190) if (is_hovered or self.dragging) else (50, 50, 50)
        pygame.draw.circle(screen, handle_color, handle_center, self.handle_radius)
        pygame.draw.circle(screen, (20, 40, 80), handle_center, self.handle_radius, 2)

        label_text = f"{self.label}: {self.value:.{self.decimals}f}{self.suffix}"
        if label_text != self.label_text:
            self.label_text = label_text
            self.label_surface = self.font.render(label_text, True, (0, 0, 0))
        screen.blit(self.label_surface, (self.x, self.y - 22))
