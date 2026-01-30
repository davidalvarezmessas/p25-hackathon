print("hello le hackaton")

import random

class Loup:
    def __init__(self, x, y, taille_grille):
        self.x = x
        self.y = y
        self.taille_grille = taille_grille
        self.energie = 40
        self.age = 0
        self.vivant = True

    def se_deplacer(self):
        if self.vivant == False :
            return
        deplacement = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(deplacement)
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < self.taille_grille and 0 <= new_y < self.taille_grille:
            self.x = new_x
            self.y = new_y

        self.energie -= 2
        self.age += 1

        if self.energie <= 0:
            self.vivant = False
        if self.age >= 40:
            self.vivant = False    

