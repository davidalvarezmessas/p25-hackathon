print("hello le hackaton")

#Consignes : 
#moutons broutent l'herbe
#loups mangent les moutons
#herbe pousse aléatoirement sur la grille
#Grille taille n*n
#case : vide, herbe, un animal, herbe + un animal
#Mouton : énergie baisse à chaque tour, se déplace aléatoirement en priorité sur l'herbe, sur l'herbe mangent et gagnent de l'énergie
#si énergie > 50  : se reproduit, perd 20 d'énergie et crée un mouton avec 20 d'énergie sur une case adjacente
#si énergie = 0 ou age > limite : meurt
#loup : se déplace aléatoirement en priorité sur les cases avec des moutons, mange les moutons et gagne de l'énergie
#énergie > seuil : se reproduit, perd 20 d'énergie et crée un loup sur une case adjacente

import argparse

def parse_args():
    parser=argparse.ArgumentParser(description="Simulation d'écosystème avec moutons, loups et herbe.")
    parser.add_argument('-g', '--grid-size',type=int, default=30, help="Longueur de la grille")
    parser.add_argument('-s', '--initial-sheep',type=int, default=50, help="Nombre initial de moutons")
    parser.add_argument('-w', '--initial-wolves',type=int, default=10, help="Nombre initial de loups")
    parser.add_argument('-gc', '--initial-grass-coverage',type=int, default=0.3, help="Proportion initiale d'herbe")
    parser.add_argument('-se','--sheep-initial-energy',type=int, default=20, help="Énergie initiale des moutons")
    parser.add_argument('-we','--wolf-initial-energy',type=int, default=40, help="Énergie initiale des loups")
    parser.add_argument('-seg','--sheep-energy-from-grass',type=int,default=15, help="Énergie gagnée par les moutons en mangeant de l'herbe")
    parser.add_argument('-wes','--wolf-energy-from-sheep',type=int,default=35, help="Énergie gagnée par les loups en mangeant des moutons")
    parser.add_argument('-sel','-sheep-energy-loss-per-turn',type=int,default=1, help="Énergie perdue par les moutons à chaque tour")
    parser.add_argument('-wel','--wolf-energy-loss-per-turn',type=int,default=2, help="Énergie perdue par les loups à chaque tour")
    parser.add_argument('-sr','--sheep-reproduction-threshold',type=int,default=50, help="Seuil d'énergie pour la reproduction des moutons")
    parser.add_argument('-wr','--wolf-reproduction-threshold',type=int,default=80, help="Seuil d'énergie pour la reproduction des loups")
    parser.add_argument('-re','--reproduction-energy-cost',type=int,default=20,help="Coût en énergie pour la reproduction")
    parser.add_argument('-sa','--sheep-max-age',type=int,default=50, help="Durée de vie maximale des moutons (en années)")
    parser.add_argument('-wa','--wolf-max-age',type=int,default=40, help="Durée de vie maximale des loups (en années)")
    parser.add_argument('-gp','--grass-growth-probability',type=float,default=0.08, help="Taux de croissance de l'herbe par tour")
    parser.add_argument('-t','--max-turns',type=int,default=500, help="Nombre maximum de tours de la simulation")
    return parser.parse_args()
#config initiale
GRID_SIZE = 30
INITIAL_SHEEP= 50
INITIAL_WOLVES=10
INITIAL_GRASS_COVERAGE=0.3

#énergie
SHEEP_INITIAL_ENERGY = 20
WOLF_INITIAL_ENERGY = 40
SHEEP_ENERGY_FROM_GRASS = 15
WOLF_ENERGY_FROM_SHEEP = 35
SHEEP_ENERGY_LOSS_PER_TURN = 1
WOLF_ENERGY_LOSS_PER_TURN = 2

#age
SHEEP_MAX_AGE = 50
WOLF_MAX_AGE = 40

#reproduction
SHEEP_REPRODUCTION_THRESHOLD=50
WOLF_REPRODUCTION_THRESHOLD=80
REPRODUCTION_ENERGY_COST=20

#herbe
GRASS_GROWTH_PROBABILITY=0.08
GRASS_REGROWTH_TIME=7

#simulation
MAX_TURNS=500



class Mouton(Grid):
    def __init__(self, position, energie, age):
        self.position = position
        self.energie = energie
        self.age = age
    def mort(self):
        return self.energie <= 0 or self.age > SHEEP_MAX_AGE
    def reproduire(self):
        if self.energie >= SHEEP_REPRODUCTION_THRESHOLD:
            self.energie -= REPRODUCTION_ENERGY_COST
            return Mouton(Grid.radjacent(self.position), SHEEP_INITIAL_ENERGY, 0)
        return None
    def manger(self):
        if Grid.has_grass(self.position):
            self.energie += SHEEP_ENERGY_FROM_GRASS
            Grid.remove_grass(self.position)
    def deplacer(self):
        (x,y)= self.position
        if Grid.has_grass((x+1,y)):
            self.position = (x+1,y)
        elif Grid.has_grass((x-1,y)):
            self.position = (x-1,y)
        elif Grid.has_grass((x,y+1)):
            self.position = (x,y+1)
        elif Grid.has_grass((x,y-1)):
            self.position = (x,y-1)
        else:
        self.position = Grid.radjacent(self.position)



    


import random

class Loup(Grid):
    def __init__(self, position, energie, age, taille_grille):
        self.position = position 
        
        self.energie = energie
        self.age = age
        self.vivant = True

    def se_deplacer(self):
        if self.vivant == False :
            return
        (x,y) = self.position 
        x = self.position[0]
        y = self.position[1]
        deplacement = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(deplacement)
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            self.x = new_x
            self.y = new_y

        self.energie -= WOLF_ENERGY_LOSS_PER_TURN
        self.age += 1

        if self.energie <= 0:
            self.vivant = False
        if self.age >= WOLF_MAX_AGE:
            self.vivant = False   

    def reproduire(self):
        if self.energie >= WOLF_REPRODUCTION_THRESHOLD :
            self.energie -= REPRODUCTION_ENERGY_COST 
            return Loup(Grid.radjacent(self.position), WOLF_INITIAL_ENERGY, 0)

    



