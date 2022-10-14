# Michael Breslavsky - 12A
# 14.10.2022
# File: game.py
# Description: A game object for the 'Jet Fighter' game. Object is used both for the server and the client.
import pygame
from constants import BLACK_PLANE_IMG, WHITE_PLANE_IMG, SCREEN_COLOR, FPS, WHITE, BLACK
from jet import Jet


class Game:
    def __init__(self, screen_width: int, screen_height: int, plane_positions: list = None):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.planes = []
        self.initialise_jets(plane_positions)
        self.score_0 = 0
        self.score_1 = 0
        self.screen = None
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.hits = []

    def initialise_jets(self, positions: list = None) -> None:
        """Initialising the 'jet' objects for the game"""
        image_black = pygame.image.load(BLACK_PLANE_IMG)
        image_white = pygame.image.load(WHITE_PLANE_IMG)
        if len(self.planes) != 0:
            return
        if not positions or len(positions) < 4:
            self.planes.append(Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                   plane_image=image_white, is_white=True))
            self.planes.append(Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                   plane_image=image_black, is_white=False))
        else:
            self.planes.append(Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                   plane_image=image_white, is_white=True, x=positions[0], y=positions[1]))
            self.planes.append(Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                   plane_image=image_black, is_white=False, x=positions[2], y=positions[3]))

    def initialise_window(self):
        """Creating initial game window"""
        screen_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(screen_size)
        self.screen.fill(SCREEN_COLOR)

    def draw(self):
        """Drawing all elements on the screen"""
        self.screen.fill(SCREEN_COLOR)
        for jet in self.planes:
            jet.draw(self.screen)
        text1 = self.font.render(str(self.score_0), True, WHITE)
        text1_rect = text1.get_rect()
        text1_rect.center = (int(self.screen_width / 4), int(self.screen_height / 7))
        text2 = self.font.render(str(self.score_1), True, BLACK)
        text2_rect = text2.get_rect()
        text2_rect.center = (int(3 * self.screen_width / 4), int(self.screen_height / 7))
        self.screen.blit(text1, text1_rect)
        self.screen.blit(text2, text2_rect)
        pygame.display.flip()
        self.clock.tick(FPS)

    def get_init_data(self):
        """Returning a dictionary with the initial game data"""
        return {'width': self.screen_width,
                'height': self.screen_height,
                'planes_pos': [self.planes[0].x, self.planes[0].y, self.planes[1].x, self.planes[1].y]}

    def update(self):
        """Updating the game"""
        for i in range(len(self.planes)):
            plane = self.planes[i]
            plane.update(self.planes[1 - i].bullets, self.hits)  # Updating each airplane

    def up_to_date_game_data(self):
        """Returning the current game data"""
        description_dict = {
            'score_0': self.score_0,
            'score_1': self.score_1,
        }
        planes = [plane.to_dict() for plane in self.planes]
        description_dict['planes'] = planes
        return description_dict
