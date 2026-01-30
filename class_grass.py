import numpy as np 
import random



class Grass():
    def __init__(self, presence, x, y):
        self.presence = presence
        self.x = x
        self.y = y 

    # CHANGER EN FONCTION DU CODE DE LA GRILLE 
    def __pousse_aléatoire__(self,GRASS_GROWTH_PROBABILITY):
        x = np.random.radnt(0,100)
        y = np.random.radnt(0,100)
        
        self.x = x
        self.y = y 
        if self.presence == 0
            self.presence = np.random.binomial(1, GRASS_GROWTH_PROBABILITY)

    
        

    

    


    

        

