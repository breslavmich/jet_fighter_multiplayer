# Michael Breslavsky - 12A
# 14.10.2022
# File: constants.py
# Description: Constants for the 'Jet Fighter' game.
import os
import pygame

BLACK_PLANE_IMG = os.path.join('images', 'black-jet.webp')
WHITE_PLANE_IMG = os.path.join('images', 'white-jet.webp')
LOADING_IMG = os.path.join('images', 'loading.gif')

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

SERVER_LISTEN_IP = "0.0.0.0"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8200

ROTATE_AMOUNT = 2.5

FPS = 20
SCREEN_COLOR = (130, 130, 130)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WHITE_CONTROLS = [pygame.K_LEFT, pygame.K_RIGHT]
BLACK_CONTROLS = [pygame.K_a, pygame.K_d]
