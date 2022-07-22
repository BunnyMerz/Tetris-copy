import pygame
from PPlay import window

class Square():
    def __init__(self, color, size=32, x=0, y=0, solid=0, style=0):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.surface = pygame.Surface((size,size))
        self.surface.fill(color)

        padding = 2
        color_difference = 20 * style # Negative = darker, Positive = lighter
        if color_difference != 0:
            surface_top = pygame.Surface((size-padding,size-padding))
            different_color = []

            if color_difference > 0:
                func = min
                m = 255
            else:
                func = max
                m = 0

            for c in color:
                different_color.append(func(m,c + color_difference))
            print(color_difference,color,different_color)
            surface_top.fill(different_color)
            self.surface.blit(surface_top,(padding/2,padding/2))

        self.solid = solid

    def draw(self):
        # rect = pygame.Rect(self.x, self.y,10,10)
        window.Window.get_screen().blit(self.surface, (self.x,self.y))