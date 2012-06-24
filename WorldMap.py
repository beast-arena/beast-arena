# -*- coding: utf-8 -*-

from Config import Config
import math, numpy, random, string, re, os, logging

class WorldMap(object):
    """
    This class holds the world map as a numpy char array.
    It provides methods to randomly place beats and food items on the world map.
    Wrap-around is implemented.
    """
    def __init__(self, size, game):
        """
        Create a squarish WorldMap instance.
        @param size width and height of the world map
        @param game reference to the calling Game.Game
        """
        self.height = self.width = int(math.sqrt(size)) + 1
        self.world = numpy.chararray(shape=(self.width, self.height))
        self.world.fill('.')
        self.maxRecursion = 20 # max. recursion depth for placeFoodItem()
        self.beastObjectMap = game.beastObjectMap
        self.lastTenRounds = []
        self.game = game
        self.log = logging.getLogger('beast-arena-logging')

    def placeBeasts(self):
        """
        Place all beasts initially and randomly on the world map.
        Beasts are placed with guaranteed minimum distance to other beasts, 
        currently it is made sure that there is no other beast in the 5x5 
        environment of a beast.
        """
        for beastObject in self.beastObjectMap.values():
            while True:
                rndX = self.getRndX()
                rndY = self.getRndY()
                beastObject.setCoordinates(rndX, rndY)
                # check if 5x5 environment is empty:
                if self.getEnvironment(beastObject) == '.' * 25:
                    break
            self.world[rndX, rndY] = beastObject.name

    def getRndX(self):
        """
        Calculate a random x coordinate.
        @return random x coordinate as integer
        """
        return random.randint(0, self.width - 1)

    def getRndY(self):
        """
        Calculate a random y coordinate.
        @return random y coordinate as integer
        """
        return random.randint(0, self.height - 1)

    def placeFoodItem(self, initial=False):
        """
        Place a new food item randomly on the world map. 
        If the paramter 'initial' is 'True' then hitting a beast with a new food 
        item will be prevented (so that all beasts start the first round with the same energy).
        If 'initial' is 'False' or not mentioned a beast could be hit occasionally 
        by a food item. If that occurs, the energy of the food item will be added to the beast's energy.
        @param initial if 'true', no beast will be hit by the food item. 'False' by default.
        """
        rndX = self.getRndX()
        rndY = self.getRndY()
        if self.world[rndX, rndY] == '.':
            self.world[rndX, rndY] = '*'
        elif (self.world[rndX, rndY] == '*' or initial == True) and \
            (self.maxRecursion > 0):
            self.maxRecursion -= 1
            self.placeFoodItem(initial)
        else:
            for beastObject in self.beastObjectMap.values():
                if beastObject.name == self.world[rndX, rndY]:
                    beastObject.addEnergy(5)
        self.maxRecursion = 20 # maximum tries to place food

    def placeStartFood(self):
        """ 
        Initially place a calculated amount of food items on the world map.
        The amount depends on the number of beasts and a factor defined in 
        'startFoodItemsPerBeast' in beast_config) 
        """
        foodItems = Config.__getStartFoodItemsPerBeast__() * \
            len(self.beastObjectMap)
        i = 0    
        while i in range(foodItems):
            self.placeFoodItem(initial=True)
            i += 1
            
    def __str__ (self):
        """
        Generate a string representation of the world map.
        @return world map as string
        """
        return numpy.swapaxes(self.world, 0, 1).tostring()

    def getWrappedCoordinates(self, x, y):
        """ 
        Return the real position of the coordinates x and y within the world map
        as a dict (this implements the "wrap-around" of the world map).
        @return a dict with the keys 'x' and 'y', their values are integer numbers
        between 0 and 'the world's size - 1'.
        """
        if x > self.width - 1:
            x -= self.width
        elif x < 0:
            x += self.width
        if y > self.height - 1:
            y -= self.height
        elif y < 0:
            y += self.height
        return { 'x': x,
                 'y': y }

    def makeMove(self, oldX, oldY, newX, newY):
        """
        Update a beast's position to the new given coordinates
        and check if either food is eaten or a fight occurs.
        Finally update the beast position on the world map.
        @param oldX current x coordinate of the beast
        @param oldY current y coordinate of the beast
        @param newX desired x coordinate of the beast
        @param newY desired y coordinate of the beast
        """
        # if moved to an empty position
        if self.world[newX, newY] == ('.'):
            self.world[newX, newY] = self.world[oldX, oldY]
            self.world[oldX, oldY] = '.'
            return
        # if food is devoured
        elif self.world[newX, newY] == ('*'):
            self.beastObjectMap[self.world[oldX, oldY]].addEnergy(5)
            self.world[newX, newY] = self.world[oldX, oldY]
            self.world[oldX, oldY] = '.'
            return
        else: # a fight must take place
            attacker = self.beastObjectMap[self.world[oldX, oldY]]
            defender = self.beastObjectMap[self.world[newX, newY]]
            # if attacker wins
            if attacker.energy >= defender.energy:
                self.log.info('attacker ' +  str(attacker) + ' won against defender ' + str(defender))
                attacker.addEnergy(defender.energy)
                defender.setBeastAsDead()
                self.game.markDeadBeast(self.world[newX, newY])
                self.world[newX, newY] = self.world[oldX, oldY]
                self.world[oldX, oldY] = '.'
            # if defender wins
            else:
                self.log.info('defender ' + str(defender) + ' won against attacker ' + str(attacker))
                defender.addEnergy(attacker.energy)
                attacker.setBeastAsDead()
                self.game.markDeadBeast(self.world[oldX, oldY])
                self.world[oldX, oldY] = '.'
    
    def deleteBeastFromWorld(self, x, y):
        """
        marks the dead beast in the game and deletes it from the world
        @param x: X-Cord of the beast
        @param y: Y-Cord of the beast
        """
        self.game.markDeadBeast(self.world[x, y])
        self.world[x, y] = '.'

    def getEnvironment(self, beastObject):
        """
        Return the 5x5 environment of a given beast as a single line string.
        Foreign beasts are replaced by "<", ">" or "=" depending on their energy
        in comparison to our beast's energy. The postion of the own beast is
        always (2,2) in the matrix, or - as in the single line string - index 12
        (centered).
        @param beastObject the beastObject instance, whose environment should be returned
        @return 5x5 environment of the given beastObject as string
        """
        environment = numpy.chararray(shape=(5, 5))
        for j in range(5):
            for i in range(5):
                wrappedCoordinates = self.getWrappedCoordinates(
                    beastObject.x - 2 + i, beastObject.y - 2 + j)
                fieldContent = self.world[wrappedCoordinates['x'],
                            wrappedCoordinates['y']]
                if fieldContent in string.ascii_letters and \
                    not (j == 2 and i == 2): # do not modify our own beasts name
                    # if hidden flag is set, hide foreign beast's energy
                    if self.beastObjectMap[fieldContent].hidden:
                        fieldContent = '?'
                    else:
                        # replace the foreign beast's name by '<', '>' or '='
                        # depending on its energy in comparison to own beast's
                        # energy:
                        foreignBeastEnergy = \
                            self.beastObjectMap[fieldContent].energy
                        ownBeastEnergy = beastObject.energy
                        if foreignBeastEnergy == ownBeastEnergy:
                            fieldContent = '='
                        elif foreignBeastEnergy < ownBeastEnergy:
                            fieldContent = '<'
                        elif foreignBeastEnergy > ownBeastEnergy:
                            fieldContent = '>'
                environment[i, j] = fieldContent
        return numpy.swapaxes(environment, 0, 1).tostring()

    def insertWorldToLastTenRoundsAsString(self):
        """ 
        Insert the current world state into the list 'lastTenRounds' as String.
        Realized as a 'FiFo-Stack'.
        """
        if len(self.lastTenRounds) < 10:
            self.lastTenRounds.append(numpy.swapaxes(self.world, 0, 1).tostring())
        else:
            self.lastTenRounds.pop(0)
            self.lastTenRounds.append(numpy.swapaxes(self.world, 0, 1).tostring())

    def getStateTenRoundsBeforeAsString(self):
        """
        Return the state of the map ten rounds ago. If the game did not yet last
        at least ten rounds an empty string will be returned.
        @return the state of the map ten rounds ago
        """
        if len(self.lastTenRounds) < 10:
            return ''
        return self.lastTenRounds[0]
    
    def getLastTenRoundsAsString(self):
        """ 
        Return the world's states of the last ten rounds, stored in list 'lastTenRounds', as String.
        The particular states are separated by ';'.
        @return world states of the last 10 rounds as one string, each followed by a ';' (except the last one)
        """
        rounds = ''
        for r in self.lastTenRounds:
            rounds += r + ';'
        return rounds.rstrip(';')

    def writeWorldMaptoFile(self, filename, roundCount):
        """
        Write (append) the current world state to a file. The file will be deleted
        if the round count is 0. This method can be called several
        times during one game and the world states will be appended to the file.
        @param filename name of the file where the map should be saved
        @param roundCount the current round number
        """
        # If new game has started delete the old WorldMap file:
        if roundCount == 0 and os.path.isfile(filename):
            try:
                os.remove(filename)
            except OSError as exc:
                self.log.critical('Error occured while trying to delete file: ' + str(filename) \
                    + ' - Err: ' + str(exc))
        try:
            f = open(filename, 'a')
            wmstr = numpy.swapaxes(self.world, 0, 1).tostring()
            wmstr = re.sub("(.{" + str(self.width) + "})", "\\1\n", wmstr, \
                re.DOTALL)
            f.write('world state at round Nr.: ' + str(roundCount) + '\n')
            f.write(wmstr)
            f.close()
        except IOError as exc:
            self.log.critical('Error occured while writing world state to file: ' +  str(exc))
            
    def getSize(self):
        """
        Return the size of the world map in the format "<height>x<width>" as string.
        @return size of the world map
        """
        return str(self.height) + "x" + str(self.width)

