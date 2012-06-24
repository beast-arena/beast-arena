# -*- coding: utf-8 -*-

import random

class Beast(object):
    """ Basic Beast class (implements Random move "stragegy") """
        
    def __init__(self):
        self.environment = None
            
    def bewege(self, paramString):
        """
        calculates the destination where to move
        @param paramString string which is given by the server containing the 
        beasts energy, environment and the round ten rounds before
        @return destination move which is calculated by the client beast
        """
        # Just to give examples which param means what:
        params = paramString.split(';', 2)
        if len(params[0]) > 0:
            energy = int(params[0])
        else:
            energy = 0
        self.environment = params[1]
        worldLastTenRounds = params[2].rstrip(';')
        
        if energy > 0:
            whitelistedMoves = (0, 2, 4, 6, 7, 8, 10, 11, 12, 13, 14, 16, 17, 18, 20, 22, 24, '?')
            return random.choice(whitelistedMoves)
        else:
            return

