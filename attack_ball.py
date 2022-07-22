from pit import pitagoras
import pygame

class AttackBall():
    def __init__(self,window,destinations,pointer,function,y=0,x=0):
        self.surface = pygame.image.load("damage.png")
        self.width = self.surface.get_rect().width
        self.height = self.surface.get_rect().height

        self.pointer = pointer

        self.window = window
        self.x = x
        self.y = y
        self.angle = 0

        self.acceleration = 2300
        self.speed = 0
        self.max_speed = 7000
        
        self.function = function

        self.destinations = destinations
        self.vector = [0,0]
        self.next_destination()
    
    def main(self):
        if self.speed < self.max_speed:
            self.speed += self.acceleration * self.window.delta_time()

        if pitagoras([self.x,self.y],self.destinations[0]) < self.speed * self.window.delta_time():
            self.end()
        
        self.x += self.speed * self.window.delta_time() * self.vector[0]
        self.y += self.speed * self.window.delta_time() * self.vector[1]

        self.draw()

    def draw(self):
        self.window.get_screen().blit(self.rotate(),(self.x,self.y))

    def rotate(self):
        self.angle += 3
        
        surface = pygame.Surface((self.width,self.height), pygame.SRCALPHA, 32)
        surface.convert_alpha()
        surface.blit(self.surface,(0,0))
        surface = pygame.transform.rotate(surface, self.angle)

        return surface
    
    def next_destination(self):
        self.vector = [0,0]
        dist = pitagoras([self.x,self.y],self.destinations[0])
        if dist != 0:
            self.vector[0] = (- self.x + self.destinations[0][0])/dist
            self.vector[1] = (- self.y + self.destinations[0][1])/dist

    def end(self):
        self.speed = 0
        self.x = self.destinations[0][0]
        self.y = self.destinations[0][1]

        if len(self.destinations) > 1:
            self.destinations.pop(0)
            self.next_destination()
            return

        if self.function != None:
            self.function()

        for attack in range(len(self.pointer)):
            if self.pointer[attack] == self:
                self.pointer.pop(attack)
                break
