# -*- coding: utf-8 -*-
"""
$Id: BeastAnalytics.py 511 2012-05-20 09:17:37Z nkr $
"""
from AnalyticBeastObject import AnalyticBeastObject
import os.path

class BeastAnalytics(object):
    """
    beast analytics class which holds every analyticbeastobject
    """
    
    def __init__(self):
        self.roundCounter = 1
        self.analyticBeastMap = {}
        self.beastObjectMap = {}

    def setBeastObjectMap(self, beastObjectMap):
        """
        @param beastObjectMap: beastList which is given by the game
        """
        self.beastObjectMap = beastObjectMap
        for beastObject in beastObjectMap.values():
            self.analyticBeastMap[beastObject.ID] = AnalyticBeastObject(beastObject.ID, beastObject)

    def nextRound(self):
        """
        is called every round for every beast
        """
        self.roundCounter += 1
        for analyticBeastObject in self.analyticBeastMap.values():
            if not analyticBeastObject.energyGainedThisRound:
                analyticBeastObject.roundsWithoutEnergyGain += 1
            analyticBeastObject.madeMoveThisRound = False
            analyticBeastObject.energyGainedThisRound = False

    def madeHorizontalMove(self, ID):
        """
        increment horizontal moves made by 1
        """
        self.analyticBeastMap[ID].horizontal += 1
        self.analyticBeastMap[ID].moveCosts += 2
        self.analyticBeastMap[ID].moves += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
            
    def madeDiagonalMove(self, ID):
        """
        increment diagonal moves made by 1
        """
        self.analyticBeastMap[ID].diagonal += 1
        self.analyticBeastMap[ID].moveCosts += 3
        self.analyticBeastMap[ID].moves += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
                
    def madeVerticalMove(self, ID):
        """
        increment vertical moves made by 1
        """
        self.analyticBeastMap[ID].vertical += 1
        self.analyticBeastMap[ID].moveCosts += 2
        self.analyticBeastMap[ID].moves += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
                
    def madeHorizontalSprintMove(self, ID):
        """
        increment horizontal sprint moves made by 1
        """
        self.analyticBeastMap[ID].sprintsHorizontal += 1
        self.analyticBeastMap[ID].sprints += 1
        self.analyticBeastMap[ID].moveCosts += 5
        self.analyticBeastMap[ID].moves += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
                
    def madeDiagonalSprintMove(self, ID):
        """
        increment diagonal sprint moves made by 1
        """
        self.analyticBeastMap[ID].sprintsDiagonal += 1
        self.analyticBeastMap[ID].sprints += 1
        self.analyticBeastMap[ID].moveCosts += 7
        self.analyticBeastMap[ID].moves += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
                
    def madeVerticalSprintMove(self, ID):
        """
        increment vertical sprint moves made by 1
        """
        self.analyticBeastMap[ID].sprintsVertical += 1
        self.analyticBeastMap[ID].sprints += 1
        self.analyticBeastMap[ID].moveCosts += 5
        self.analyticBeastMap[ID].moves += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
        
    def madeNotAllowedMove(self, ID):
        """
        increment not allowed moves made by 1
        """
        self.analyticBeastMap[ID].notAllowedMoves += 1
        self.analyticBeastMap[ID].moveCosts += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
        
    def stay(self, ID):
        """
        increment stays moves made by 1
        """
        self.analyticBeastMap[ID].stays += 1
        self.analyticBeastMap[ID].moveCosts += 1
        self.analyticBeastMap[ID].madeMoveThisRound = True
       
    def hide(self, ID):
        """
        increment hides moves made by 1
        """
        self.analyticBeastMap[ID].hides += 1
        self.analyticBeastMap[ID].moveCosts += 2
        self.analyticBeastMap[ID].madeMoveThisRound = True
        
    def devourFood(self, ID):
        """
        increases either food devourd or food rained on beast 
        weather move was made this round or not
        """
        if self.analyticBeastMap[ID].madeMoveThisRound:
            self.analyticBeastMap[ID].rainedFoodOnBeast += 1
            return
        self.analyticBeastMap[ID].foodConsumed += 1
        self.analyticBeastMap[ID].energyGainedThisRound = True
        
    def markAsDead(self, ID, energy):
        """
        marks beast as dead
        """
        self.analyticBeastMap[ID].energyBeforeDeath == energy
        self.analyticBeastMap[ID].diedAtRound == self.roundCounter
        
    def wonFight(self, ID, energy):
        """
        increments fights won by 1 and modifies energy variables involved
        """
        self.analyticBeastMap[ID].fightsWon += 1
        self.analyticBeastMap[ID].energyGainedThroughFights += energy
        self.analyticBeastMap[ID].energyGainedThisRound = True
        
    def getStatisticFile(self, ID):
        """
        generates output file containing beast statistics
        """
        if not self.analyticBeastMap.has_key(ID):
            return
        filename = 'Analytic_' + ID
        
        # If new game has started delete the old WorldMap file:
        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except OSError as exc:
                print 'Error occured while trying to delete file: ' + filename + ' - Err: ' + exc
        try:
            f = open(filename, 'a')
            f.write(self.getStatistic(ID))
            f.close()
        except IOError as exc:
            print 'Error occured while writing beast statistics to file: ', exc
      
    def getStatisticString(self,name,ID):
        """
        returns a formatted string for passing to clients after game
        """
        
        if not self.analyticBeastMap.has_key(ID):
            return ''
    
        s = name + \
        ':' + str(self.analyticBeastMap[ID].moves) + \
        ':' + str(self.analyticBeastMap[ID].vertical) + \
        ':' + str(self.analyticBeastMap[ID].horizontal) + \
        ':' + str(self.analyticBeastMap[ID].diagonal) + \
        ':' + str(self.analyticBeastMap[ID].sprints) + \
        ':' + str(self.analyticBeastMap[ID].sprintsVertical) + \
        ':' + str(self.analyticBeastMap[ID].sprintsHorizontal) + \
        ':' + str(self.analyticBeastMap[ID].sprintsDiagonal) + \
        ':' + str(self.analyticBeastMap[ID].notAllowedMoves) + \
        ':' + str(self.analyticBeastMap[ID].hides) + \
        ':' + str(self.analyticBeastMap[ID].stays) + \
        ':' + str(float(self.analyticBeastMap[ID].moveCosts)/float(self.analyticBeastMap[ID].moves))+\
        ':' + str(self.analyticBeastMap[ID].foodConsumed) + \
        ':' + str(self.analyticBeastMap[ID].fightsWon)
        
        return s
       
    def getStatistic(self,name, ID):
        """
        returns string containing current statistic for beast
        """      
        if not self.analyticBeastMap.has_key(ID):
            return
    
        #generating header        
        statistic = 'Statistic for Beast: ' \
        + name+ '\nType: ' + self.analyticBeastMap[ID].type + '\n'\
        '\nFIGHT DATA:\naverage energy gained per round with fights: ' + \
        (str(float(self.analyticBeastMap[ID].foodConsumed*5+self.analyticBeastMap[ID].energyGainedThroughFights)/float(self.analyticBeastMap[ID].moves)) \
        if self.analyticBeastMap[ID].moves > 0 else "0") + \
        '\n# of fights won: ' + str(self.analyticBeastMap[ID].fightsWon) + \
        '\naverage energy gained per fight: '
        if self.analyticBeastMap[ID].fightsWon != 0:
            statistic += str(float(self.analyticBeastMap[ID].energyGainedThroughFights)/float(self.analyticBeastMap[ID].fightsWon))
        else: statistic += '0'
        
        #generating moving data
        statistic += '\nMOVING DATA:' + \
        '\nmoves overall: ' + str(self.analyticBeastMap[ID].moves) + \
        '\nmove costs overall: ' + str(self.analyticBeastMap[ID].moveCosts) + \
        '\nvertical moves: ' + str(self.analyticBeastMap[ID].vertical) + \
        '\nhorizontal moves: ' + str(self.analyticBeastMap[ID].horizontal) + \
        '\ndiagonal moves: ' + str(self.analyticBeastMap[ID].diagonal) + \
        '\nvertical sprints: ' + str(self.analyticBeastMap[ID].sprintsVertical) + \
        '\nhorizontal sprints: ' + str(self.analyticBeastMap[ID].sprintsHorizontal) + \
        '\ndiagonal sprints: ' + str(self.analyticBeastMap[ID].sprintsDiagonal) + \
        '\nsprints: ' + str(self.analyticBeastMap[ID].sprints) + \
        '\nnot allowed moves: ' + str(self.analyticBeastMap[ID].notAllowedMoves) + \
        '\nhides: ' + str(self.analyticBeastMap[ID].hides) + \
        '\nstays: ' + str(self.analyticBeastMap[ID].stays) + '\n' + \
        '\nfood consumed: ' + str(self.analyticBeastMap[ID].foodConsumed) + \
        '\nfood rained on beast: ' + str(self.analyticBeastMap[ID].rainedFoodOnBeast) + \
        '\naverage moving cost: ' + (str(float(self.analyticBeastMap[ID].moveCosts)/float(self.analyticBeastMap[ID].moves)) \
                                     if self.analyticBeastMap[ID].moves > 0 else '0') + \
        '\naverage energy gained per round without fights: ' + (str(float(self.analyticBeastMap[ID].foodConsumed*5)/float(self.analyticBeastMap[ID].moves)) \
                                                                 if self.analyticBeastMap[ID].moves > 0 else '0')
        return statistic
