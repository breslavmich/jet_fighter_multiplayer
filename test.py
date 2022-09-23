import pygame
from jet import Jet

pygame.init()

ROTATE_AMOUNT = 2.5

size = (500, 500)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
img = pygame.image.load('images/black-jet.webp')
jet = Jet(500, 500, img, False)
finish = False
while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                jet.rotate_amount = -ROTATE_AMOUNT
            elif event.key == pygame.K_a:
                jet.rotate_amount = +ROTATE_AMOUNT
            elif event.key == pygame.K_SPACE:
                jet.shoot()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d or event.key == pygame.K_a:
                jet.rotate_amount = 0
    screen.fill((130, 130, 130))
    jet.update()
    jet.draw(screen)
    pygame.display.flip()
    clock.tick(30)
