import numpy as np
import random
import argparse
import pygame
wolf_img = pygame.image.load("loup.jpeg")
sheep_img = pygame.image.load("mouton.jpeg")
wolf_img = pygame.transform.scale(wolf_img, (24, 24))
sheep_img = pygame.transform.scale(sheep_img, (20, 20))


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
    parser = argparse.ArgumentParser(description="Simulation d'écosystème avec moutons, loups et herbe.")
    parser.add_argument('-g', '--grid_size', type=int, default=30, help="Longueur de la grille")
    parser.add_argument('-s', '--initial_sheep', type=int, default=50, help="Nombre initial de moutons")
    parser.add_argument('-w', '--initial_wolves', type=int, default=10, help="Nombre initial de loups")
    parser.add_argument('-gc', '--initial_grass_coverage', type=float, default=0.3, help="Proportion initiale d'herbe")
    parser.add_argument('-se', '--sheep_initial_energy', type=int, default=20, help="Énergie initiale des moutons")
    parser.add_argument('-we', '--wolf_initial_energy', type=int, default=40, help="Énergie initiale des loups")
    parser.add_argument('-seg', '--sheep_energy_from_grass', type=int, default=15, help="Énergie gagnée par les moutons en mangeant de l'herbe")
    parser.add_argument('-wes', '--wolf_energy_from_sheep', type=int, default=35, help="Énergie gagnée par les loups en mangeant des moutons")
    parser.add_argument('-sel', '--sheep_energy_loss_per_turn', type=int, default=1, help="Énergie perdue par les moutons à chaque tour")
    parser.add_argument('-wel', '--wolf_energy_loss_per_turn', type=int, default=2, help="Énergie perdue par les loups à chaque tour")
    parser.add_argument('-srt', '--sheep_reproduction_threshold', type=int, default=50, help="Seuil d'énergie pour la reproduction des moutons")
    parser.add_argument('-wrt', '--wolf_reproduction_threshold', type=int, default=80, help="Seuil d'énergie pour la reproduction des loups")
    parser.add_argument('-rec', '--reproduction_energy_cost', type=int, default=20, help="Coût en énergie pour la reproduction")
    parser.add_argument('-sma', '--sheep_max_age', type=int, default=50, help="Durée de vie maximale des moutons")
    parser.add_argument('-wma', '--wolf_max_age', type=int, default=40, help="Durée de vie maximale des loups")
    parser.add_argument('-ggp', '--grass_growth_probability', type=float, default=0.08, help="Taux de croissance de l'herbe par tour")
    parser.add_argument('-mt', '--max_turns', type=int, default=500, help="Nombre maximum de tours de la simulation")
    return parser.parse_args()


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
    
    def list_without_sheep(self):
        positions=[]
        for x in range(self.size):
            for y in range(self.size):
                if not self.cells[x][y]['sheep']:
                    positions.append((x,y))
        return positions
    
    def list_without_wolf(self):
        positions=[]
        for x in range(self.size):
            for y in range(self.size):
                if not self.cells[x][y]['wolf']:
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
class Mouton:
    def __init__(self, position, energie, age):
        self.position = position
        self.energie = energie
        self.age = age
    def mort(self,args):
        return self.energie <= 0 or self.age > args.sheep_max_age
    def reproduire(self,grid,args):
        if self.energie >= args.sheep_reproduction_threshold:
            self.energie -= args.reproduction_energy_cost
            newposition = grid.radjacent(self.position)
            return Mouton(newposition, args.sheep_initial_energy, 0)
        return None
    def manger(self,grid,args):
        if grid.has_grass(self.position):
            self.energie += args.sheep_energy_from_grass
            grid.remove_grass(self.position)
    def deplacer(self, grid):
        (x, y) = self.position
        size = grid.size
        # Détermine la nouvelle position
        if x + 1 < size and grid.has_grass((x + 1, y)):
            new_pos = (x + 1, y)
        elif x - 1 >= 0 and grid.has_grass((x - 1, y)):
            new_pos = (x - 1, y)
        elif y + 1 < size and grid.has_grass((x, y + 1)):
            new_pos = (x, y + 1)
        elif y - 1 >= 0 and grid.has_grass((x, y - 1)):
            new_pos = (x, y - 1)
        else:
            new_pos = grid.radjacent(self.position)
        # Mise à jour de la grille
        grid.remove_sheep(self.position)
        self.position = new_pos
        grid.add_sheep(self.position)

    def draw(self, screen) : 
        rect = self.wolf_img.get_rect(self.position)
        screen.blit(self.wolf_img, rect) 

class Loup:
    def __init__(self, position, energie, age):
        self.position = position
        self.energie = energie
        self.age = age

    def deplacer(self, grid):
        (x, y) = self.position
        size = grid.size
        # Détermine la nouvelle position
        if x + 1 < size and grid.has_sheep((x + 1, y)):
            new_pos = (x + 1, y)
        elif x - 1 >= 0 and grid.has_sheep((x - 1, y)):
            new_pos = (x - 1, y)
        elif y + 1 < size and grid.has_sheep((x, y + 1)):
            new_pos = (x, y + 1)
        elif y - 1 >= 0 and grid.has_sheep((x, y - 1)):
            new_pos = (x, y - 1)
        else:
            new_pos = grid.radjacent(self.position)
        # Mise à jour de la grille
        grid.remove_wolf(self.position)
        self.position = new_pos
        grid.add_wolf(self.position)

    def mort(self, wolf_max_age):
        return self.energie <= 0 or self.age > wolf_max_age

    def reproduire(self, grid, wolf_reproduction_threshold, reproduction_energy_cost, wolf_initial_energy):
        if self.energie >= wolf_reproduction_threshold:
            self.energie -= reproduction_energy_cost
            newposition = grid.radjacent(self.position)
            grid.add_wolf(newposition)
            return Loup(newposition, wolf_initial_energy, 0)

    def chasser(self, grid, args):
        (x, y) = self.position
        size = grid.size
        if x + 1 < size and grid.has_sheep((x + 1, y)):
            grid.remove_sheep((x + 1, y))
            self.energie += args.wolf_energy_from_sheep
        if x - 1 >= 0 and grid.has_sheep((x - 1, y)):
            grid.remove_sheep((x - 1, y))
            self.energie += args.wolf_energy_from_sheep
        if y + 1 < size and grid.has_sheep((x, y + 1)):
            grid.remove_sheep((x, y + 1))
            self.energie += args.wolf_energy_from_sheep
        if y - 1 >= 0 and grid.has_sheep((x, y - 1)):
            grid.remove_sheep((x, y - 1))
            self.energie += args.wolf_energy_from_sheep

    def draw(self, screen) : 
        rect = self.wolf_img.get_rect(self.position)
        screen.blit(self.wolf_img, rect)   
    


#classe pour le comportement de l'herbe, sa présence et sa position
class Grass:
    def __init__(self, position):
        self.position = position
        self.presence = 1  # 1 si l'herbe est présente, 0 sinon

    def pousse_aleatoire(self, grid, growth_probability):
        """Fait pousser de l'herbe aléatoirement sur la grille."""
        positions_sans_herbe = grid.list_without_grass()
        if positions_sans_herbe:
            position = random.choice(positions_sans_herbe)
            if random.random() < growth_probability:
                grid.add_grass(position)

class Simulation: #Classe qui gère la simulation tour par tour
    def __init__(self, grid, args):
        self.grid=grid
        self.steps_max=args.max_turns
        self.current_step=0
        self.sheep=[]
        self.wolves=[]
        
    def grid_init(self,args):
        #initialisation de l'herbe
        coverage=0
        while coverage < args.initial_grass_coverage: 
            x=random.randint(0,self.grid.size-1)
            y=random.randint(0,self.grid.size-1)
            if not self.grid.cells[x][y]['grass']:
                self.grid.add_grass((x,y))
                coverage += 1/self.grid.size**2
        for i in range(args.initial_sheep):
                position=random.choice(self.grid.list_without_sheep())
                new_sheep=Mouton(position,args.sheep_initial_energy,0)
                self.sheep.append(new_sheep)
                self.grid.add_sheep(position)
        for i in range(args.initial_wolves):
                position=random.choice(self.grid.list_without_wolf())
                new_wolf=Loup(position,args.wolf_initial_energy,0)
                self.wolves.append(new_wolf)
                self.grid.add_wolf(position)
        #initialisation des moutons

    def age(self):
        for sheep in self.sheep:
            sheep.age += 1
        for wolf in self.wolves:
            wolf.age += 1
    
    def grass_growth(self,args):
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                if not self.grid.cells[x][y]['grass']:
                    if random.random() < args.grass_growth_probability :  # Probabilité de croissance de l'herbe
                        self.grid.add_grass((x,y))
                                            
    def action_sheep(self,args):
         for sheep in self.sheep:
            sheep.deplacer(self.grid)
            sheep.manger(self.grid,args)
            sheep.energie -= args.sheep_energy_loss_per_turn
    
    def action_wolves(self, args):
        moutons_manges = set()
        for wolf in self.wolves:
            pos_mouton_mange = wolf.chasser(self.grid, args)
            if pos_mouton_mange is not None:
                moutons_manges.add(pos_mouton_mange)
            else:
                wolf.deplacer(self.grid)
            wolf.energie -= args.wolf_energy_loss_per_turn
        # Retirer les moutons mangés de la liste des moutons vivants
        self.sheep = [sheep for sheep in self.sheep if sheep.position not in moutons_manges]

    def remove_dead(self,args):
        self.sheep=[sheep for sheep in self.sheep if sheep.energie > 0 and sheep.age <= args.sheep_max_age]
        self.wolves=[wolf for wolf in self.wolves if wolf.energie > 0 and wolf.age <= args.wolf_max_age]

    def reproduce(self,args):
        new_sheep = []
        for sheep in self.sheep:
            baby_sheep = sheep.reproduire(self.grid, args)
            if baby_sheep is not None:
                new_sheep.append(baby_sheep)
        self.sheep = [s for s in self.sheep if s is not None]
        self.sheep.extend(new_sheep)

        new_wolves = []
        for wolf in self.wolves:
            baby_wolf = wolf.reproduire(
                self.grid,
                args.wolf_reproduction_threshold,
                args.reproduction_energy_cost,
                args.wolf_initial_energy
            )
            if baby_wolf is not None:
                new_wolves.append(baby_wolf)
        self.wolves = [w for w in self.wolves if w is not None]
        self.wolves.extend(new_wolves)

    #faire l'affichage
    def step(self,args):
        self.current_step+=1
        self.age()
        self.grass_growth(args)
        self.action_sheep(args)
        self.action_wolves(args)
        self.remove_dead(args)
        self.reproduce(args)
        #self.affichage()

    def run(self, args):
        try:
            while self.current_step < self.steps_max:
                if not self.sheep and not self.wolves:
                    print("Tous les moutons et loups sont morts. Arrêt de la simulation.")
                    break
                self.step(args)
        except KeyboardInterrupt:
            print("\nSimulation interrompue par l'utilisateur (Ctrl+C).")

    #DESSIN 
    def draw(self, screen):
        if self.presence == 1 :                 # on colorie que s'il y a de l'herbe
            pygame.draw.rect(screen, (50, 200, 50), (self.x, self.y))
    
    def draw(self, screen, cell_size, wolf_img, sheep_img):
    screen.fill((30, 30, 30))  # fond sombre

    # Dessiner l'herbe
    for x in range(self.grid.size):
        for y in range(self.grid.size):
            if self.grid.has_grass((x, y)):
                pygame.draw.rect(screen, (50, 200, 50),
                                 (x*cell_size, y*cell_size, cell_size, cell_size))

    # Dessiner les moutons
    for sheep in self.sheep:
        pos = sheep.position
        rect = sheep_img.get_rect(center=(pos[0]*cell_size + cell_size//2,
                                          pos[1]*cell_size + cell_size//2))
        screen.blit(sheep_img, rect)

    # Dessiner les loups
    for wolf in self.wolves:
        pos = wolf.position
        rect = wolf_img.get_rect(center=(pos[0]*cell_size + cell_size//2,
                                        pos[1]*cell_size + cell_size//2))
        screen.blit(wolf_img, rect)

    pygame.display.flip()


if __name__ == "__main__":
    args = parse_args()
    grid = Grid(args.grid_size)
    sim = Simulation(grid, args)
    sim.grid_init(args)
    print("Début de la simulation!")
    for step in range(args.max_turns):
        sim.step(args)
        nb_sheep = len(sim.sheep)
        nb_wolves = len(sim.wolves)
        print(f"Tour {step+1}: moutons = {nb_sheep}, loups = {nb_wolves}")
        if nb_sheep == 0 and nb_wolves == 0:
            print("Tous les animaux sont morts. Fin de la simulation.")
            break
    print("Simulation terminée.")