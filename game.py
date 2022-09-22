import pygame
from constants import BLACK_PLANE_IMG, WHITE_PLANE_IMG
from jet import Jet


class Game:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.turn = 0
        self.image_black = None
        self.image_white = None
        self.planes = []
        self.load_images()
        self.initialise_jets()

    def load_images(self) -> None:
        self.image_black = pygame.image.load(BLACK_PLANE_IMG)
        self.image_white = pygame.image.load(WHITE_PLANE_IMG)

    def initialise_jets(self, positions: list = None) -> None:
        if not positions or len(positions) < 4:
            self.planes[0] = Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                 plane_image=self.image_white, is_white=True)
            self.planes[1] = Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                 plane_image=self.image_black, is_white=False)
        else:
            self.planes[0] = Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                 plane_image=self.image_white, is_white=True, x=positions[0], y=positions[1])
            self.planes[1] = Jet(screen_width=self.screen_width, screen_height=self.screen_height,
                                 plane_image=self.image_black, is_white=False, x=positions[2], y=positions[3])
