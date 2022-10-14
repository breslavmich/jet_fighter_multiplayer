# Michael Breslavsky - 12A
# 14.10.2022
# File: jet.py
# Description: A jet object for the 'Jet Fighter' game. Object is used both for the server and the client.
import math
import random
import pygame
from math import sin, cos, radians
from bullet import Bullet


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    return rot_image, rot_rect


class Jet:
    def __init__(self, screen_width: int, screen_height: int, plane_image: pygame.Surface, is_white: bool,
                 x: int = None, y: int = None):
        self.x = x
        self.y = y
        if x is None:
            self.x = random.randint(0, screen_width)
        if y is None:
            self.y = random.randint(0, screen_height)
        self.image = plane_image

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.angle = 0
        self.speed = 3
        self.rotate_amount = 0

        self.bullets = []
        self.is_white = is_white

    def go_forward(self) -> None:
        """Updating the planes position to move forward"""
        self.x += -self.speed * sin(radians(self.angle))
        self.y += -self.speed * cos(radians(self.angle))

    def keep_in_map(self) -> None:
        """Keeping the jet in the bounds of the screen"""
        width, height = self.image.get_size()
        if self.x >= self.screen_width:
            self.x = -width
        elif self.x + width <= 0:
            self.x = self.screen_width

        if self.y >= self.screen_height:
            self.y = -height
        elif self.y + height <= 0:
            self.y = self.screen_height

    def draw(self, screen: pygame.Surface) -> None:
        """Drawing the jet on the screen"""
        rotated_image, rect = rot_center(self.image, self.angle)
        rect.x = self.x
        rect.y = self.y
        screen.blit(rotated_image, (self.x, self.y))
        self.draw_bullets(screen)

    def update(self, enemy_bullets: list, hits_list: list) -> None:
        """Updating the jet's parameters"""
        # Updating the position
        self.go_forward()
        self.keep_in_map()
        # Updating the angle
        if self.rotate_amount > 7:
            self.rotate_amount = 7
        elif self.rotate_amount < -7:
            self.rotate_amount = -7
        self.angle += self.rotate_amount

        # Updating all bullets
        for bullet in self.bullets:
            if bullet.time_alive > 200:
                self.bullets.remove(bullet)
            else:
                bullet.update()
        # Checking if plane was hit
        self.check_hits(enemy_bullets, hits_list)

    def check_hits(self, enemy_bullets: list, hits_list: list):
        """Checking if plane was hit"""
        for bullet in enemy_bullets:
            if math.dist((self.x + self.image.get_width() / 2, self.y + self.image.get_height() / 2),
                         (bullet.x, bullet.y)) < 13 + bullet.radius:
                # Checking if bullet hit the plane
                hits_list.append(bullet)
                enemy_bullets.remove(bullet)

    def shoot(self) -> None:
        """Shooting a bullet"""
        bullet = Bullet(self.screen_width, self.screen_height, int(self.x + self.image.get_width() / 2),
                        int(self.y + self.image.get_height() / 2), self.angle, self.is_white)  # Creating a bullet
        self.bullets.append(bullet)  # Adding bullet to the list

    def draw_bullets(self, screen: pygame.Surface) -> None:
        """Drawing all the bullets for the plane"""
        for bullet in self.bullets:
            bullet.draw(screen)

    def to_dict(self) -> dict:
        """Returning a description dictionary of the parameters of the plane to send to the client"""
        description = vars(self).copy()
        desc_bullets = []
        try:
            del description['image']
            del description['screen_width']
            del description['screen_height']
        except:
            pass
        for bullet in description['bullets']:
            desc_bullets.append(bullet.to_dict())
        description['bullets'] = desc_bullets
        return description

    def new_bullet_from_dict(self, description_dict: dict) -> None:
        """Creating a new bullet based on parameters from a dictionary"""
        new_bullet = Bullet(screen_width=description_dict['screen_width'],
                            screen_height=description_dict['screen_height'],
                            x=description_dict['x'],
                            y=description_dict['y'],
                            angle=description_dict['angle'],
                            is_white=description_dict['is_white'])
        self.bullets.append(new_bullet)

    def data_from_dict(self, description_dict: dict) -> None:
        """Updating a jet's parameters based on parameters from a dictionary"""
        self.x = description_dict['x']
        self.y = description_dict['y']

        self.angle = description_dict['angle']
        self.speed = description_dict['speed']
        self.rotate_amount = description_dict['rotate_amount']

        self.is_white = description_dict['is_white']
        self.bullets = []
        for i in range(len(description_dict['bullets'])):
            self.new_bullet_from_dict(description_dict['bullets'][i])
