import pygame

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 22)
        self.text = text

        self.base_color = (45, 90, 160)
        self.hover_color = (65, 115, 190)
        self.press_color = (30, 65, 125)
        self.text_color = (255, 255, 255)
        self.border_color = (20, 40, 80)

        self.is_hovered = False
        self.is_pressed = False

        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_pressed = self.is_hovered and mouse_pressed

    def holding(self):
        self.update()
        return self.is_pressed

    def draw(self, screen):
        self.update()

        if self.is_pressed:
            color = self.press_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.base_color

        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=6)
        screen.blit(self.text_surface, self.text_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)
