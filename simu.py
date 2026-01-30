import pygame
import sys

#wolf_img = pygame.image.load("loup.jpeg")
#wolf_img = pygame.transform.scale(wolf_img, (50, 50))  # taille 50x50 pixels


#sheep_img = pygame.image.load("mouton.jpeg")
#sheep_img = pygame.transform.scale(sheep_img, (50, 50))  # taille 50x50 pixels


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
    
    #rect = wolf_img.get_rect(center=(WIDTH//2, HEIGHT//2))
    #screen.blit(wolf_img, rect) 

    #rect = sheep_img.get_rect(center=(WIDTH//3, HEIGHT//3))
    #screen.blit(sheep_img, rect) 
    pygame.display.flip()


pygame.quit()
sys.exit()