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



    