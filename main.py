import numpy as np
import random
import argparse

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

#classe qui gère la grille 
class Grid:
    """Classe représentant la grille de l'écosystème."""
    def __init__(self, size):
        self.size=size
        self.cells=[[{'grass':False, 'sheep':False, 'wolf':False} for _ in range(size)] for _ in range(size)]
    
    def radjacent(self,position):
        """Renvoie une position adjacente aléatoire vide."""
        (x,y)= position
        adjacent_positions=[]
        if x>0:
            adjacent_positions.append((x-1,y))
        if x<self.size-1:
            adjacent_positions.append((x+1,y))
        if y>0:
            adjacent_positions.append((x,y-1))
        if y<self.size-1:
            adjacent_positions.append((x,y+1))
        for pos in adjacent_positions:
            if self.cells[pos[0]][pos[1]]['sheep'] or self.cells[pos[0]][pos[1]]['wolf']:
                adjacent_positions.remove(pos)
        return random.choice(adjacent_positions)
    
    def list_without_grass(self):
        """Renvoie une liste de positions sans herbe."""
        positions=[]
        for x in range(self.size):
            for y in range(self.size):
                if not self.cells[x][y]['grass']:
                    positions.append((x,y))
        return positions
        
    def has_grass(self,position):
        """Vérifie si une position contient de l'herbe."""
        (x,y)= position
        return self.cells[x][y]['grass']
    
    def has_sheep(self,position):
        """Vérifie si une position contient un mouton."""
        (x,y)= position
        return self.cells[x][y]['sheep']
    
    def has_wolf(self,position):
        """Vérifie si une position contient un loup."""
        (x,y)= position
        return self.cells[x][y]['wolf']
    
    def remove_grass(self,position):
        """Retire l'herbe d'une position."""
        (x,y)= position
        self.cells[x][y]['grass']=False

    def remove_sheep(self,position):
        """Retire un mouton d'une position."""
        (x,y)= position
        self.cells[x][y]['sheep']=False
    
    def remove_wolf(self,position):
        """Retire un loup d'une position."""
        (x,y)= position
        self.cells[x][y]['wolf']=False

    def add_grass(self,position):
        """Ajoute de l'herbe à une position."""
        (x,y)= position
        self.cells[x][y]['grass']=True

    def add_sheep(self,position):
        """Ajoute un mouton à une position."""
        (x,y)= position
        self.cells[x][y]['sheep']=True

    def add_wolf(self,position):
        """Ajoute un loup à une position."""
        (x,y)= position
        self.cells[x][y]['wolf']=True
    
#classe pour le comportement du mouton, son age, sa. position et son énergie 
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
            newposition = Grid.radjacent(self.position)
            Grid.add_sheep(newposition)
            return Mouton(newposition, SHEEP_INITIAL_ENERGY, 0)
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

#classe pour le comportement du loup, son age, sa position et son énergie
class Loup(Grid):
    def __init__(self, position, energie, age):
        self.position = position 
        
        self.energie = energie
        self.age = age
        self.vivant = True

    def deplacer(self):
        (x,y)= self.position
        if Grid.has_sheep((x+1,y)):
            self.position = (x+1,y)
        elif Grid.has_sheep((x-1,y)):
            self.position = (x-1,y)
        elif Grid.has_sheep((x,y+1)):
            self.position = (x,y+1)
        elif Grid.has_sheep((x,y-1)):
            self.position = (x,y-1)
        else:
            self.position = Grid.radjacent(self.position)
   
    def mort(self):
        return self.energie <= 0 or self.age > SHEEP_MAX_AGE
    
    def reproduire(self):
        if self.energie >= WOLF_REPRODUCTION_THRESHOLD :
            self.energie -= REPRODUCTION_ENERGY_COST 
            newposition = Grid.radjacent(self.position)
            Grid.add_wolf(newposition)
            return Loup(newposition, WOLF_INITIAL_ENERGY, 0)
        return None
    def chasser(self):
        (x,y) = self.position
        if Grid.has_sheep((x+1,y)):
            Grid.remove_sheep((x+1,y))
        if Grid.has_sheep((x-1,y)):  
            Grid.remove_sheep((x-1,y))      
        if Grid.has_sheep((x,y+1)):
            Grid.remove_sheep((x,y+1))   
        if Grid.has_sheep((x,y-1)): 
            Grid.remove_sheep((x,y-1))        
            
    


#classe pour le comportement de l'herbe, sa présence et sa position
class Grass():
    def __init__(self, presence, x, y):
        self.presence = presence
        self.x = x
        self.y = y 

    # CHANGER EN FONCTION DU CODE DE LA GRILLE 
    def __pousse_aléatoire__(self,GRASS_GROWTH_PROBABILITY):
        x = np.randlist(Grid.list_without_grass())
        y = np.random.radnt(0,100)
        
        self.x = x
        self.y = y 
        if self.presence == 0:
            self.presence = np.random.binomial(1, GRASS_GROWTH_PROBABILITY)
