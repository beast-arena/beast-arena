# -*- coding: utf-8 -*-
"""
$Id: NikolaisBeast.py 511 2012-05-20 09:17:37Z nkr $
"""
import string
class NikolaisBeast(object):
    """artificial intelligence of my beast"""

    def __init__(self):
        """constructor"""
        self.environment = None
        self.smallEnvironment = []
        self.savePlaces = []
        self.sprintCooldown = 0
        self.whiteListedMoves = (0, 2, 4, 6, 7, 8, 10, 11, 12, 13, 14, 16,
                                 17, 18, 20, 22, 24, '?')
        self.bigEnvironmentMoves = (0, 2, 4, 10, 14, 20, 22, 24)
    
    def bewegen(self, energy, environment, worldPast):
        """
        old/wrong method --> will be deleted soon
        """
        params = string.join((str(energy), environment, str(worldPast)), ';')
        return self.bewege(params)
     
    def bewege(self, paramString):
        """
        main method where the beast decides to which destination it moves
        @param paramString String which is given by Game/Server which contains energy, environment and worldPast
        @return String destination of the beast
        """
        if self.initialWork(paramString):
            return
        dest = self.checkSmallEnvironment()
        
        #checks if there are some weak opponents in the bigEnvironment, but 
        #only if dest is not already a place where a weak opponent sits
        if self.environment[dest] not in ('<', '=', '?'):   
            for tmpDest in self.bigEnvironmentMoves:
                if self.environment[tmpDest] in ('=', '<', '?') and \
                    self.sprintCooldown == 0 and tmpDest in self.savePlaces:
                    dest = tmpDest
                    self.sprintCooldown = 4
                    
        if dest not in self.savePlaces:
            dest = self.getSaveDest() 
            
        if dest in self.whiteListedMoves:
            return dest
        else:
            return 12
            
    def initialWork(self, paramString):
        """
        splits the params into energy, environment and the world
        calculates the save places, fills self.smallEnvironment and
        decrements the sprintcounter if not zero
        @param paramString String which is given from Game/Server to the beast according to its viewing range
        """
        params = paramString.split(';', 2)
        if len(params[0]) > 0:
            energy = int(params[0])
        else:
            energy = 0
        self.environment = params[1]
        worldLastTenRounds = params[2].rstrip(';')
        if self.environment == 'Ende' or self.environment == '':
            return True
            
        self.checkOpponents() 
        self.setSmallEnvironment()
        if self.sprintCooldown > 0:
            self.sprintCooldown -= 1
          
    def checkOpponents(self):
        """
        sets self.savePlaces to a list with save destinations
        """
        opponents = []
        saveMoves = []
        saveDests = []
        dangerousDests = []
        for move in range(25):
            saveMoves.append(move)
            opponents.append(None)
            if self.environment[move] == '>':
                opponents.insert(move, move) 
        for opp in range(25):
            if opponents[opp] != None:               
                dangerousDests = DangerousDestinations().getDangerousDests(opp)
            for i in range(25):
                if i in dangerousDests and saveMoves[i] != None:
                    saveMoves[i] = None        
        for i in range(25):
            if saveMoves[i] != None and i in self.whiteListedMoves:
                saveDests.append(i)
        self.savePlaces = saveDests
        
    def getSaveDest(self):
        """
        gets called if there is no place with food or weak opponents
        @todo this is the place for hunting food or opponents
        @return save destination 
        """
        bigSavePlace = -1
        diagonalSavePlace = -1
        for savePlace in self.savePlaces:
            if self.smallEnvironment[savePlace] != -1:
                if savePlace in (7, 11, 13, 17):
                    return savePlace
                else:
                    diagonalSavePlace = savePlace
            elif self.sprintCooldown == 0:
                bigSavePlace = savePlace
        if diagonalSavePlace == -1:
            return bigSavePlace
        return diagonalSavePlace

    def setSmallEnvironment(self):
        """fills self.smallEnvironment with destinations where you don't 
        have to sprint (6,7,8,11,12,13,16,17,18)"""
        self.smallEnvironment = []
        for i in range(25):
            if i in (6, 7, 8, 11, 12, 13, 16, 17, 18):
                self.smallEnvironment.append(self.environment[i])
            else:
                self.smallEnvironment.append(-1)

    def checkSmallEnvironment(self):
        """
        checks if there are usefull destinations in self.smallEnvironment 
        which contains food or weak opponents
        prefers straight moves, not diagonal
        @return possible destination of the beast
        """
        foodDestHorizontal = -1
        foodDestDiagonal = -1
        for savePlace in self.savePlaces:
            dest = self.smallEnvironment[savePlace]
            if dest != -1:          
                if '=' == dest and dest:
                    return savePlace
                elif '<' == dest:
                    return savePlace
                elif '?' == dest:
                    return savePlace
                elif '*' == dest:
                    if savePlace in (7, 11, 13, 17):
                        foodDestHorizontal = savePlace
                    else:
                        foodDestDiagonal = savePlace
        if foodDestHorizontal == -1:
            return foodDestDiagonal
        return foodDestHorizontal
  
class DangerousDestinations(object):
    """
    @class DangerousDestinations
    holds the dangerous destinations for every position of an opponent
    """    
    def __init__(self):
        """
        initializes self.dangerousDestinations
        """
        self.dangerousDestinations = \
            [[0, 1, 2, 5, 6 , 10, 12], #1
            [0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13], #2
            [1, 2, 3, 4, 6, 7, 8, 9, 12, 14], #2
            [1, 2, 3, 4, 6, 7, 8, 9, 11, 13], #3
            [2, 3, 4, 8, 9, 12, 14], #4
            [0, 1 , 5 , 6 , 7 , 10, 11, 15, 17], #5
            [0, 1, 2, 5, 6, 7, 8, 10, 11, 12, 16, 18], #6
            [1, 2, 3, 6, 7, 8, 11, 12, 13, 15, 19], #7
            [2, 3, 4, 6, 7, 8, 9, 12, 13, 14, 16, 18], #8
            [3, 4, 7, 8, 9, 13, 14, 17, 19], #9
            [0, 2, 5, 6, 7, 10, 11, 12, 15, 16, 20, 22], #10
            [1, 3, 5, 6, 7, 10, 11, 12, 13, 15, 16, 17, 21, 23], #11
            [],
            [1, 3, 7, 8, 9, 11, 12, 13, 14, 17, 18, 19, 21, 23], #13
            [2, 4, 8, 9, 12, 13, 14, 18, 19, 22, 24], #14
            [5, 7, 10, 11, 15, 16, 17, 20, 21], #15
            [6, 8, 10, 11, 12, 15, 16, 17, 18, 20, 21, 22], #16
            [5, 7, 9, 11, 12, 13, 15, 16, 17, 18, 19, 21, 22, 23], #17
            [6, 8, 12, 13, 14, 16, 17, 18, 19, 22, 24], #18
            [7, 9, 13, 14, 17, 18, 19, 23, 24], #19
            [10, 12, 15, 16, 20, 21, 22], #20
            [11, 13, 15, 16, 17, 20, 21, 22, 23], #21
            [10, 12, 14, 16, 17, 18, 20, 21, 22, 23, 24], #22
            [11, 13, 17, 18, 19, 21, 22, 23, 24], #23
            [12, 14, 18, 19, 22, 23, 24]] #24
                                              
    def getDangerousDests(self, opp):
        """
        @param opp opponent
        @return dangerous destinations for given opponent
        """
        return self.dangerousDestinations[int(opp)] 

def main():
    """
    test beasts intelligence
    """
    b = NikolaisBeast()
#    s = '0123456789abcdefghijklmn>'
#    print b.bewegen(30, s, None)
#    print b.checkOpponents()
#    d = DangerousDestinations()
#    print d.getDangerousDestinations(24)

    print b.bewege(';;;sfksfdd')

if __name__ == '__main__':
    main()
