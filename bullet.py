import random
import pygame
from math import sin, cos, radians


class Bullet:
    def __init__(self, screen_width: int, screen_height: int, x: int, y: int, angle: float, is_white: bool):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.angle = angle
        self.speed = 4
        self.is_white = is_white
        self.radius = 3
        self.time_alive = 0

    def keep_in_map(self):
        if self.x >= self.screen_width:
            self.x = -self.radius
        elif self.x + self.radius <= 0:
            self.x = self.screen_width

        if self.y >= self.screen_height:
            self.y = -self.radius
        elif self.y + self.radius <= 0:
            self.y = self.screen_height

    def update(self):
        self.x += -self.speed * sin(radians(self.angle))
        self.y += -self.speed * cos(radians(self.angle))
        self.keep_in_map()
        self.time_alive += 1

    def draw(self, screen: pygame.Surface):
        if self.is_white:
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius)
        else:
            pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.radius)
