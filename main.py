import numpy as np
import random
import argparse
import pygame
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Simulation d'écosystème.")
    parser.add_argument('-g', '--grid_size', type=int, default=30)
    parser.add_argument('-s', '--initial_sheep', type=int, default=50)
    parser.add_argument('-w', '--initial_wolves', type=int, default=10)
    parser.add_argument('-gc', '--initial_grass_coverage', type=float, default=0.2)
    parser.add_argument('-se', '--sheep_initial_energy', type=int, default=20)
    parser.add_argument('-we', '--wolf_initial_energy', type=int, default=40)
    parser.add_argument('-seg', '--sheep_energy_from_grass', type=int, default=15)
    parser.add_argument('-wes', '--wolf_energy_from_sheep', type=int, default=35)
    parser.add_argument('-sel', '--sheep_energy_loss_per_turn', type=int, default=1)
    parser.add_argument('-wel', '--wolf_energy_loss_per_turn', type=int, default=2)
    parser.add_argument('-srt', '--sheep_reproduction_threshold', type=int, default=50)
    parser.add_argument('-wrt', '--wolf_reproduction_threshold', type=int, default=80)
    parser.add_argument('-rec', '--reproduction_energy_cost', type=int, default=20)
    parser.add_argument('-sma', '--sheep_max_age', type=int, default=50)
    parser.add_argument('-wma', '--wolf_max_age', type=int, default=40)
    parser.add_argument('-ggp', '--grass_growth_probability', type=float, default=0.05)
    parser.add_argument('-mt', '--max_turns', type=int, default=1000)
    return parser.parse_args()

class Grid:
    def __init__(self, size):
        self.size = size
        self.cells = [[{'grass': False, 'sheep': False, 'wolf': False} for _ in range(size)] for _ in range(size)]
    
    def radjacent(self, position):
        x, y = position
        adj = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if not self.cells[nx][ny]['sheep'] and not self.cells[nx][ny]['wolf']:
                    adj.append((nx, ny))
        return random.choice(adj) if adj else position

    def list_without_grass(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if not self.cells[x][y]['grass']]
    
    def list_without_sheep(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if not self.cells[x][y]['sheep']]

    def list_without_wolf(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if not self.cells[x][y]['wolf']]
        
    def has_grass(self, pos): return self.cells[pos[0]][pos[1]]['grass']
    def has_sheep(self, pos): return self.cells[pos[0]][pos[1]]['sheep']
    def has_wolf(self, pos): return self.cells[pos[0]][pos[1]]['wolf']
    def remove_grass(self, pos): self.cells[pos[0]][pos[1]]['grass'] = False
    def remove_sheep(self, pos): self.cells[pos[0]][pos[1]]['sheep'] = False
    def remove_wolf(self, pos): self.cells[pos[0]][pos[1]]['wolf'] = False
    def add_grass(self, pos): self.cells[pos[0]][pos[1]]['grass'] = True
    def add_sheep(self, pos): self.cells[pos[0]][pos[1]]['sheep'] = True
    def add_wolf(self, pos): self.cells[pos[0]][pos[1]]['wolf'] = True

class Mouton:
    """Classe représentant un mouton dans l'écosystème."""
    def __init__(self, position, energie, age):
        self.position = position
        self.energie = energie
        self.age = age

    def mort(self,args):
        """Vérifie si le mouton est mort."""
        return self.energie <= 0 or self.age > args.sheep_max_age
    
    def reproduire(self,grid,args):
        """Fait reproduire le mouton s'il a assez d'énergie."""
        if self.energie >= args.sheep_reproduction_threshold:
            self.energie -= args.reproduction_energy_cost
            new_pos = grid.radjacent(self.position)
            if new_pos != self.position:
                return Mouton(new_pos, args.sheep_initial_energy, 0)
        return None
    
    def manger(self,grid,args):
        """Fait manger le mouton s'il y a de l'herbe à sa position."""
        if grid.has_grass(self.position):
            self.energie += args.sheep_energy_from_grass
            grid.remove_grass(self.position)
            return (self.position,1)
        
    def deplacer(self, grid):
        x, y = self.position
        targets = []
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < grid.size and 0 <= ny < grid.size and grid.has_grass((nx, ny)):
                targets.append((nx, ny))
        
        new_pos = random.choice(targets) if targets else grid.radjacent(self.position)
        grid.remove_sheep(self.position)
        self.position = new_pos
        grid.add_sheep(self.position)

class Loup:
    """Classe représentant un loup dans l'écosystème."""
    def __init__(self, position, energie, age):
        self.position, self.energie, self.age = position, energie, age

    def deplacer(self, grid):
        grid.remove_wolf(self.position)
        self.position = grid.radjacent(self.position)
        grid.add_wolf(self.position)

    def mort(self, max_age):
        return self.energie <= 0 or self.age > max_age

    def reproduire(self, grid, args):
        if self.energie >= args.wolf_reproduction_threshold:
            self.energie -= args.reproduction_energy_cost
            new_pos = grid.radjacent(self.position)
            if new_pos != self.position:
                return Loup(new_pos, args.wolf_initial_energy, 0)
        return None

    def chasser(self, grid, args):
        x, y = self.position
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < grid.size and 0 <= ny < grid.size and grid.has_sheep((nx, ny)):
                grid.remove_wolf(self.position)
                grid.remove_sheep((nx, ny))
                self.energie += args.wolf_energy_from_sheep
                self.position = (nx, ny)
                grid.add_wolf(self.position)
                return (nx, ny)
        return None

    def draw(self, screen) : 
        rect = self.wolf_img.get_rect(self.position)
        screen.blit(self.wolf_img, rect)   
    


#classe pour le comportement de l'herbe, sa présence et sa position
class Grass:
    """Classe représentant de l'herbe dans l'écosystème."""
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
    """Classe gérant la simulation de l'écosystème."""
    def __init__(self, grid, args):
        self.grid, self.args, self.current_step = grid, args, 0
        self.sheep, self.wolves = [], []

    def grid_init(self, args):
        # Herbe
        num_grass = int(args.initial_grass_coverage * (self.grid.size**2))
        for _ in range(num_grass):
            pos = (random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1))
            self.grid.add_grass(pos)
        # Moutons
        for _ in range(args.initial_sheep):
            pos = random.choice(self.grid.list_without_sheep())
            self.sheep.append(Mouton(pos, args.sheep_initial_energy, 0))
            self.grid.add_sheep(pos)
        # Loups
        for _ in range(args.initial_wolves):
            pos = random.choice(self.grid.list_without_wolf())
            self.wolves.append(Loup(pos, args.wolf_initial_energy, 0))
            self.grid.add_wolf(pos)

    def step(self):
        self.current_step += 1
        # 1. Age et Herbe
        for a in self.sheep + self.wolves: a.age += 1
        for _ in range(int(self.grid.size**2 * self.args.grass_growth_probability)):
            pos = (random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1))
            self.grid.add_grass(pos)

        # 2. Moutons
        for s in self.sheep:
            s.deplacer(self.grid)
            s.manger(self.grid, self.args)
            s.energie -= self.args.sheep_energy_loss_per_turn
        
        # 3. Loups
        eaten_pos = []
        for w in self.wolves:
            res = w.chasser(self.grid, self.args)
            if res: eaten_pos.append(res)
            else: w.deplacer(self.grid)
            w.energie -= self.args.wolf_energy_loss_per_turn
        
        self.sheep = [s for s in self.sheep if s.position not in eaten_pos]

        # 4. Mort et Reproduction
        self.sheep = [s for s in self.sheep if not s.mort(self.args)]
        self.wolves = [w for w in self.wolves if not w.mort(self.args.wolf_max_age)]
        
        new_s = [baby for s in self.sheep if (baby := s.reproduire(self.grid, self.args))]
        for b in new_s: self.grid.add_sheep(b.position)
        self.sheep.extend(new_s)

        new_w = [baby for w in self.wolves if (baby := w.reproduire(self.grid, self.args))]
        for b in new_w: self.grid.add_wolf(b.position)
        self.wolves.extend(new_w)

    #DESSIN 
    def draw_simulation(self, screen, cell_size, wolf_img, sheep_img):
        screen.fill((30, 30, 30))  # fond sombre

        # Dessiner l'herbe
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                if self.grid.has_grass((x, y)):
                    pygame.draw.rect(screen, (34, 139, 34), (x*cell_size, y*cell_size, cell_size-1, cell_size-1))
        for s in self.sheep:
            screen.blit(sheep_img, (s.position[0]*cell_size, s.position[1]*cell_size))
        for w in self.wolves:
            screen.blit(wolf_img, (w.position[0]*cell_size, w.position[1]*cell_size))

if __name__ == "__main__":
    args = parse_args()
    pygame.init()
    
    CELL_SIZE = 20
    screen = pygame.display.set_mode((args.grid_size * CELL_SIZE, args.grid_size * CELL_SIZE))
    pygame.display.set_caption("Simulation Vie Sauvage")
    
    # Chargement images avec fallback
    try:
        w_img = pygame.transform.scale(pygame.image.load("loup.jpeg"), (CELL_SIZE, CELL_SIZE))
        s_img = pygame.transform.scale(pygame.image.load("mouton.jpeg"), (CELL_SIZE, CELL_SIZE))
    except:
        w_img = pygame.Surface((CELL_SIZE, CELL_SIZE)); w_img.fill((255, 0, 0))
        s_img = pygame.Surface((CELL_SIZE, CELL_SIZE)); s_img.fill((255, 255, 255))

    grid = Grid(args.grid_size)
    sim = Simulation(grid, args)
    sim.grid_init(args)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
        
        if len(sim.sheep) > 0 or len(sim.wolves) > 0:
            sim.step()
        
        sim.draw_simulation(screen, CELL_SIZE, w_img, s_img)
        pygame.display.flip()
        clock.tick(10) # 10 tours par seconde
        
    pygame.quit()