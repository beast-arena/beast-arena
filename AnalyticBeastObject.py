# -*- coding: utf-8 -*-

class AnalyticBeastObject(object):
    """
    main beast analytics class
    """

    def __init__(self, name, beastObject):
        self.name = name
        self.beastObject = beastObject
        self.type = beastObject.beast.__class__.__name__
        
        #OUTPUT variables
        #general Data
        self.energyAtGameEnd = 0
        self.diedAtRound = 0 #done
        self.rainedFoodOnBeast = 0 #done

        #fight Data
        self.fightsWon = 0 #done
        self.energyGainedThroughFights = 0 #done
        self.energyBeforeDeath = 0 #done
        self.avgEnergyGainedPerFight = 0
        
        #food Data
        self.foodConsumed = 0 #done
        self.avgEnergyPerMoveWithFights = 0 #with movingcosts
        self.avgEnergyPerMoveWithoutFights = 0 #with movingcosts     
        self.roundsWithoutEnergyGain = 0 #done
        self.energyGainedThisRound = False #done
        self.madeMoveThisRound = False #done
        
        #MOVING Data
        self.moves = 0 #done
        self.moveCosts = 0 #done
        
        self.hides = 0 #done
        self.stays = 0 #done
        self.sprintsHorizontal = 0 #done
        self.sprintsVertical = 0 #done
        self.sprintsDiagonal = 0 #done
        self.horizontal = 0 #done
        self.vertical = 0 #done
        self.diagonal = 0 #done
        self.avgMovingCost = 0
        self.sprints = 0 #done
        self.notAllowedMoves = 0 #done

