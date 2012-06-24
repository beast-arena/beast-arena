# -*- coding: utf-8 -*-

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
            self.analyticBeastMap[beastObject.name] = AnalyticBeastObject(beastObject.name, beastObject)

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

    def madeHorizontalMove(self, name):
        """
        increment horizontal moves made by 1
        """
        self.analyticBeastMap[name].horizontal += 1
        self.analyticBeastMap[name].moveCosts += 2
        self.analyticBeastMap[name].moves += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
            
    def madeDiagonalMove(self, name):
        """
        increment diagonal moves made by 1
        """
        self.analyticBeastMap[name].diagonal += 1
        self.analyticBeastMap[name].moveCosts += 3
        self.analyticBeastMap[name].moves += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
                
    def madeVerticalMove(self, name):
        """
        increment vertical moves made by 1
        """
        self.analyticBeastMap[name].vertical += 1
        self.analyticBeastMap[name].moveCosts += 2
        self.analyticBeastMap[name].moves += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
                
    def madeHorizontalSprintMove(self, name):
        """
        increment horizontal sprint moves made by 1
        """
        self.analyticBeastMap[name].sprintsHorizontal += 1
        self.analyticBeastMap[name].sprints += 1
        self.analyticBeastMap[name].moveCosts += 5
        self.analyticBeastMap[name].moves += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
                
    def madeDiagonalSprintMove(self, name):
        """
        increment diagonal sprint moves made by 1
        """
        self.analyticBeastMap[name].sprintsDiagonal += 1
        self.analyticBeastMap[name].sprints += 1
        self.analyticBeastMap[name].moveCosts += 7
        self.analyticBeastMap[name].moves += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
                
    def madeVerticalSprintMove(self, name):
        """
        increment vertical sprint moves made by 1
        """
        self.analyticBeastMap[name].sprintsVertical += 1
        self.analyticBeastMap[name].sprints += 1
        self.analyticBeastMap[name].moveCosts += 5
        self.analyticBeastMap[name].moves += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
        
    def madeNotAllowedMove(self, name):
        """
        increment not allowed moves made by 1
        """
        self.analyticBeastMap[name].notAllowedMoves += 1
        self.analyticBeastMap[name].moveCosts += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
        
    def stay(self, name):
        """
        increment stays moves made by 1
        """
        self.analyticBeastMap[name].stays += 1
        self.analyticBeastMap[name].moveCosts += 1
        self.analyticBeastMap[name].madeMoveThisRound = True
       
    def hide(self, name):
        """
        increment hides moves made by 1
        """
        self.analyticBeastMap[name].hides += 1
        self.analyticBeastMap[name].moveCosts += 2
        self.analyticBeastMap[name].madeMoveThisRound = True
        
    def devourFood(self, name):
        """
        increases either food devourd or food rained on beast 
        weather move was made this round or not
        """
        if self.analyticBeastMap[name].madeMoveThisRound:
            self.analyticBeastMap[name].rainedFoodOnBeast += 1
            return
        self.analyticBeastMap[name].foodConsumed += 1
        self.analyticBeastMap[name].energyGainedThisRound = True
        
    def markAsDead(self, name, energy):
        """
        marks beast as dead
        """
        self.analyticBeastMap[name].energyBeforeDeath == energy
        self.analyticBeastMap[name].diedAtRound == self.roundCounter
        
    def wonFight(self, name, energy):
        """
        increments fights won by 1 and modifies energy variables involved
        """
        self.analyticBeastMap[name].fightsWon += 1
        self.analyticBeastMap[name].energyGainedThroughFights += energy
        self.analyticBeastMap[name].energyGainedThisRound = True
        
    def getStatisticFile(self, name):
        """
        generates output file containing beast statistics
        """
        if not self.analyticBeastMap.has_key(name):
            return
        filename = 'Analytic_' + name
        
        # If new game has started delete the old WorldMap file:
        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except OSError as exc:
                print 'Error occured while trying to delete file: ' + filename + ' - Err: ' + exc
        try:
            f = open(filename, 'a')
            f.write(self.getStatistic(name))
            f.close()
        except IOError as exc:
            print 'Error occured while writing beast statistics to file: ', exc
         
    def getStatistic(self, name):
        """
        returns string containing current statistic for beast
        """      
        if not self.analyticBeastMap.has_key(name):
            return
    
        #generating header        
        statistic = ''
        statistic = 'Statistic for Beast: ' \
        + name + '\nType: ' + self.analyticBeastMap[name].type + '\n'\
        '\nFIGHT DATA:\naverage energy gained per round with fights: ' + \
        (str(float(self.analyticBeastMap[name].foodConsumed*5+self.analyticBeastMap[name].energyGainedThroughFights)/float(self.analyticBeastMap[name].moves)) \
        if self.analyticBeastMap[name].moves > 0 else "0") + \
        '\n# of fights won: ' + str(self.analyticBeastMap[name].fightsWon) + \
        '\naverage energy gained per fight: '
        if self.analyticBeastMap[name].fightsWon != 0:
            statistic += str(float(self.analyticBeastMap[name].energyGainedThroughFights)/float(self.analyticBeastMap[name].fightsWon))
        else: statistic += '0'
        
        #generating moving data
        statistic += '\nMOVING DATA:' + \
        '\nmoves overall: ' + str(self.analyticBeastMap[name].moves) + \
        '\nmove costs overall: ' + str(self.analyticBeastMap[name].moveCosts) + \
        '\nvertical moves: ' + str(self.analyticBeastMap[name].vertical) + \
        '\nhorizontal moves: ' + str(self.analyticBeastMap[name].horizontal) + \
        '\ndiagonal moves: ' + str(self.analyticBeastMap[name].diagonal) + \
        '\nvertical sprints: ' + str(self.analyticBeastMap[name].sprintsVertical) + \
        '\nhorizontal sprints: ' + str(self.analyticBeastMap[name].sprintsHorizontal) + \
        '\ndiagonal sprints: ' + str(self.analyticBeastMap[name].sprintsDiagonal) + \
        '\nsprints: ' + str(self.analyticBeastMap[name].sprints) + \
        '\nnot allowed moves: ' + str(self.analyticBeastMap[name].notAllowedMoves) + \
        '\nhides: ' + str(self.analyticBeastMap[name].hides) + \
        '\nstays: ' + str(self.analyticBeastMap[name].stays) + '\n' + \
        '\nfood consumed: ' + str(self.analyticBeastMap[name].foodConsumed) + \
        '\nfood rained on beast: ' + str(self.analyticBeastMap[name].rainedFoodOnBeast) + \
        '\naverage moving cost: ' + (str(float(self.analyticBeastMap[name].moveCosts)/float(self.analyticBeastMap[name].moves)) \
                                     if self.analyticBeastMap[name].moves > 0 else '0') + \
        '\naverage energy gained per round without fights: ' + (str(float(self.analyticBeastMap[name].foodConsumed*5)/float(self.analyticBeastMap[name].moves)) \
                                                                 if self.analyticBeastMap[name].moves > 0 else '0')
        return statistic

