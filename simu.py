import pygame
import sys

pygame.init()

# Fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Écosystème")

clock = pygame.time.Clock()
FPS = 60

# Boucle principale
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))  # fond sombre

    pygame.display.flip()

pygame.quit()
sys.exit()