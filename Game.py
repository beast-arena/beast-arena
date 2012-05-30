#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id: Game.py 510 2012-05-17 22:43:51Z mli $
"""
from BeastObject import BeastObject
from WorldMap import WorldMap
from Config import Config
from BeastAnalytics import BeastAnalytics
from NikolaisBeast import NikolaisBeast
from SamysBeast import SamysBeast
from Team8Beast import Team8Beast
import string, random, time, threading, logging

class Game(threading.Thread):
    """ 
    global Game class
    here will be your beast registered and seated on WorldMap after it is 
    created (dependend on the umber of beasts)
    """   

    def __init__(self, getStatisticForBeast=None):
        """
        constructor --> initialising Variables
        @param getStatisticForBeast List: insert a tupel of chars ('a','b')
        """
        threading.Thread.__init__(self)
        self.server = None
        self.gui = None
        self.beastObjectMap = {}
        self.rankingList = []
        self.worldMap = None
        self.foodCounter = 0
        self.enableUrwidVisualisation = Config.__getUseUrwidVisualisation__()
        self.useNetworking = Config.__getUseNetworking__()
        self.startTimeMillis = time.time() + Config.__getStartInSeconds__()
        self.startTime = time.ctime(self.startTimeMillis)
        self.roundCounter = 0
        self.getStatisticForBeast = getStatisticForBeast
        self.useBeastAnalytics = True if(getStatisticForBeast) else False
        self.deadBeasts = 0
        self.urwidRoundDelay = Config.__getUrwidRoundDelay__() / 1000.0
        self.gameStarted = False
        self.gameFinished = False
        self.running = False
        self.log = logging.getLogger('beast-arena-logging')

        if self.enableUrwidVisualisation:
            self.useBeastAnalytics = True
            self.getStatisticForBeast = ''
        self.beastAnalytics = BeastAnalytics() if(self.useBeastAnalytics) else False


    def registerBeast(self, beast):
        """
        registers a Beast instance: give it a name, create a BeastObject 
        instance and store it in internal dictionary 'beastObjectMap'.
        This method is called when a new Beast joins.
        @param beast Beast: is the clients beast
        @return returns the beast's name
        """
        if self.gameSignOnPossible():
            name = string.ascii_letters[len(self.beastObjectMap)]
        else:
            self.log.warning('registered beast limit reached')
            return
            
        beastObject = BeastObject(beast, name, self.beastAnalytics)
        self.rankingList.append(None) # generates proper length of rankingList
        self.beastObjectMap[name] = beastObject
        
        self.log.info("beast " + name + " registered")
        return name
    
    def getStartInSeconds(self):
        return str(self.startTimeMillis-time.time())
    
    def run(self):
        """
        WorldMap creation, Beast and food positioning, game mechanics and final
        creation of ranking list
        also calling of the Visualisation and beastAnalytics
        """
        self.running = True
        if self.useNetworking:
            self.server.prepareGameStart()
                
        # ensure that at least configured minimum number of beasts are registered:
        availableBeasts = ['NikolaisBeast()', 'SamysBeast()', 'Team8Beast()']
        while (self.gameSignOnPossible() and len(self.beastObjectMap) < Config.__getMinimumBeasts__()):
            self.registerBeast(eval(random.choice(availableBeasts)))

        #final beastObjectMap gets passed to beastAnalytics
        if self.useBeastAnalytics:
            self.beastAnalytics.setBeastObjectMap(self.beastObjectMap)

        self.gameStarted = True
        
        #size = number of beast * value of fieldFactor(Config) * 25(beast-View)
        size = len(self.beastObjectMap) * Config.__getFieldFactor__() * 25
        self.worldMap = WorldMap(size, self)
        self.worldMap.placeBeasts()
        self.worldMap.placeStartFood()
        
        #calls outsourced round mechanic
        self.doRounds()
        self.gameFinished = True
        
        for beastObject in self.beastObjectMap.values():
            #this sends the last ten rounds to client after game is finished
            beastObject.beast.bewege(str(beastObject.energy) + ';' + 'Ende' + ';' + self.worldMap.getLastTenRoundsAsString() + ';')
          
        self.log.info(self.getRankingList())
        #BeastAnalytics
        if self.useBeastAnalytics and self.enableUrwidVisualisation == False:
            for i in range(len(self.getStatisticForBeast)):
                self.log.info(self.beastAnalytics.getStatistic(self.getStatisticForBeast[i]))
                self.beastAnalytics.getStatisticFile(self.getStatisticForBeast[i])

        # Added to stop Thread
        self.stop()
        
    def doRounds(self):
        """
        round mechanic -runs until maxRounds are reached or only 1 beast remains
        random food positioning and calling of move() for every beast
        """
        while (self.roundCounter < Config.__getMaxRounds__() and \
                    self.deadBeasts < len(self.beastObjectMap) - 1 and self.running):
            #Generate/Save WorldMap state of last round

            self.foodCounter = 0 #needed for food arrangement
            for beastObject in self.beastObjectMap.values():
                self.arrangeFoodEveryRound()
                
                #calls move() for every beast, also if it's already dead    
                beastObject.move(self.worldMap)                
                if self.enableUrwidVisualisation and beastObject.energy > 0:
                    time.sleep(self.urwidRoundDelay)
                    
            self.arrangeFoodEveryRound(whileRoundState=False)
            self.worldMap.insertWorldToLastTenRoundsAsString()
            self.roundCounter += 1                             

            #BeastAnalytics
            if self.useBeastAnalytics:
                self.beastAnalytics.nextRound()
        
    def arrangeFoodEveryRound(self, whileRoundState=True):
        """
        arranges the correct number of food items every round
        @param whileRoundState (default=True) marks if this method is called 
        while or at the end of a round
        """
        if whileRoundState:
            #calls placeFoodItem once per per 3/5 beast
            rnd = random.randint(1, len(self.beastObjectMap))
            if rnd in range(len(self.beastObjectMap) * 3 / 5) and \
                            self.foodCounter < len(self.beastObjectMap) * 3 / 5:
                self.worldMap.placeFoodItem()
                self.foodCounter += 1  
        else:
            # is called if not enough food has been rained
            if self.foodCounter < len(self.beastObjectMap) * 3 / 5:
                
                counter = 0
                while counter in range(len(self.beastObjectMap) * 3 / 5 - self.foodCounter):
                    self.worldMap.placeFoodItem()
                    counter += 1
                    
    def getBeastByName(self, name):
        """
        @param name String: beast name
        @return socket, srcAddr: Returns client-socket, client-source-address of given beast-name from BeastObjectMap
        """
        beast = self.beastObjectMap.get(name)
        return beast.socket, beast.srcAddr
    
    def gameSignOnPossible(self):
        """
        Checks if game is full or has already started
        @return Boolean 
        """
        if not(self.gameStarted) and (len(self.beastObjectMap) < len(string.ascii_letters)):
            return True
        return False

    def getRankingList(self):
        """
        calculates the ranking of the beasts depending on their time of death or
        their remaining energy
        @return String: the ranking list of the beasts
        """
        survivedBeasts = []
        for beast in self.beastObjectMap.values():
            if beast.alive:
                survivedBeasts.append(beast)
        tmp = sorted(survivedBeasts, key=lambda BeastObject:BeastObject.energy, reverse=True)
        for i in range(len(tmp)):
            self.rankingList[i] = tmp[i]
   
        #Create return string
        dots=lambda x: x>=9 and'.'*12 or'.'*13
        returnString = 'Ranking:\n'
        for i in range(len(self.rankingList)):
            returnString += str(i + 1) + str(dots(i)) + str(
                self.rankingList[i]) + ' with ' + str(
                    self.rankingList[i].energy) + ' energy\n'          
        return returnString
            
    def markDeadBeast(self, name):
        """
        marks beasts who died in a fight as dead and writes them in the 
        rankingList (LIFO)
        @param name String: puts in the name of the dead beast
        """
        self.rankingList[len(self.rankingList) - 1 - self.deadBeasts] = self.beastObjectMap[name]
        self.deadBeasts += 1

    def setupUrwid(self):
        """
        checks if urwid should be used and starts its loops
        """
        if self.enableUrwidVisualisation: 
            #update content Loop:
            self.gui.start()            
            #main urwid loop:
            self.gui.runLoop()
            
    def stop(self):
        """
        stops game thread
        """
        self.running = False
