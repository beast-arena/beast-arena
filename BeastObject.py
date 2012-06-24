# -*- coding: utf-8 -*-

from Config import Config
import logging

class BeastObject(object):
    """
    @class BeastObject
    creates an instance of a wrapped beast which can be handled by the server
    """
    def __init__(self, beast, name, beastAnalytics=None):
        self.name = name
        self.energy = 30
        self.beast = beast
        self.x = None
        self.y = None
        self.hidden = False
        self.sprintCooldown = 0
        self.beastAnalytics = beastAnalytics
        self.log = logging.getLogger('beast-arena-logging')
        self.alive = True

    def setCoordinates(self, x, y):
        """
        @brief called when position is initially set in WorldMap
        
        if a beast or food item appears on the world map this method
        is called from worldmap and sets the passed parameters for local x and y
        
        @param x int value which will be set for local x coordinate
        @param y int value which will be set for local y coordinate
        """
        self.x = x
        self.y = y
        
    def move(self, worldMap):
        """
        @brief does all essential operations for a beast object to move  
        
        calls 'bewege' on client beast, calculates moving-costs and finally 
        calls 'makeMove' in WorldMap to check of fights occur or food gets eaten and
        update position on worldMap
        """
        self.hidden = False
        whitelistedMoves = (0, 2, 4, 6, 7, 8, 10, 11, 12, 13, 14, 16, 17, 18, 20, 22, 24, '?')
        
        #necessary to prevent move-methods to be called of beasts killen in this ROUND
        if not self.alive:
            #send ten rounds before to beast when it's dead
            self.beast.bewege(';;' + worldMap.getStateTenRoundsBeforeAsString()+';')
            return
            
        destination = self.beast.bewege(str(self.energy) + ';' + worldMap.getEnvironment(self) + ';' + worldMap.getStateTenRoundsBeforeAsString()+';')
                
        if self.sprintCooldown > 0:
            self.sprintCooldown -= 1

        if destination != '?':
            try:
                destination = int(destination)
                if destination not in whitelistedMoves:
                    destination = 12 #beast needs to stay at current position
            except Exception: # if destination contains string/character
                destination = 12
        else:
            self.hidden = True
            
        # destinations where you can sprint
        if destination in (0, 2, 4, 10, 14, 20, 22, 24):
            if self.sprintCooldown == 0:
                self.sprintCooldown = 4
            else:    
                destination = 12 #can't sprint --> stays at old position

        if destination not in (12,'?'):
            destRow = destination / 5 - 2
            destCol = destination % 5 - 2  
            
            #Calculation the new cords incl. wrap around
            newX = worldMap.getWrappedCoordinates(self.x + (destCol), self.y + (destRow))['x']
            newY = worldMap.getWrappedCoordinates(self.x + (destCol), self.y + (destRow))['y']   
           
            #update Position in Worldmap if beast does not stay or hide
            worldMap.makeMove(self.x, self.y, newX, newY)
            self.x = newX
            self.y = newY

        #subtracts the energycosts if it has energy left 
        if self.energy > 0:
            self.energy -= Config.__getMovingCosts__(destination)
        
        # checks if a beast starved and delete it from the WorldMap
        if self.alive == True and self.energy <= 0:
            self.setBeastAsDead()
            worldMap.deleteBeastFromWorld(self.x, self.y)
                
        #Beast Analytics
        if self.beastAnalytics:
            if destination not in whitelistedMoves:
                self.beastAnalytics.madeNotAllowedMove(self.name)
            elif destination in (0, 4, 20, 24):
                self.beastAnalytics.madeDiagonalSprintMove(self.name)
            elif destination in (10, 14):
                self.beastAnalytics.madeHorizontalSprintMove(self.name)
            elif destination in (2, 22):
                self.beastAnalytics.madeVerticalSprintMove(self.name)
            elif destination in (11, 13):
                self.beastAnalytics.madeHorizontalMove(self.name)
            elif destination in (7, 17):
                self.beastAnalytics.madeVerticalMove(self.name)
            elif destination in (6, 8, 16, 18):
                self.beastAnalytics.madeDiagonalMove(self.name)
            elif destination == '?':
                self.beastAnalytics.hide(self.name)
    
    def setBeastAsDead(self):
        """
        sets the life to zero and sets the life-flag to False == Dead
        """
        self.alive = False
        self.energy = 0
                    
    def addEnergy(self, addEnergy):
        """
        @brief adds passed energy to self.energy of the BeastObject instance
        
        called from world map if a beast consume a food item, a food item drop 
        on a beasts head or a beast consume a smaller beast. the passed energy 
        will be added on the self.energy
        
        @param addEnergy int value of energy the beast will earn
        """
        #Beast Analytics
        if self.beastAnalytics:
            if addEnergy == 0:
                self.beastAnalytics.markAsDead(self.name, self.energy)
            elif addEnergy == 5:
                self.beastAnalytics.devourFood(self.name)
            elif addEnergy != 0 and addEnergy != 5:
                self.beastAnalytics.wonFight(self.name, addEnergy)
        
        #this is actually the important line ;)
        self.energy += addEnergy

    def __str__(self):
        '''
        @brief returns a string with name of the beast 
        
        called especially by the ranking list, to get the simple name of a beast       
        '''
        return self.name

