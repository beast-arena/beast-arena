#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id: beast-arena.py 515 2012-05-21 16:43:54Z sze $
"""
from Game import Game
from UrwidVisualisation import UrwidVisualisation
from Server import Server
from Config import Config
from GameWinners import GameWinners
import logging, sys, threading, time

class beast_arena(threading.Thread):
    '''
    main module where everything happens
    '''
    def __init__(self):
        '''
        basic constructor
        '''
        threading.Thread.__init__(self)
        self.urwid = None
        self.gamecount = 1
        self.game = None
        self.running = False
        self.server = None
        self.winners = GameWinners()
        self.useUrwid = Config.__getUseUrwidVisualisation__()
        self.useNetworking = Config.__getUseNetworking__()
        self.log = logging.getLogger('beast-arena-logging')
    
    def runUrwid(self):
        """
        runs all urwid loops.
        should be called after run() is started as program will stay in urwid main loop
        till finished
        """
        while not self.game:
            time.sleep(0.05)
        
        self.urwid = UrwidVisualisation(self.game)
#       update content Loop:
        self.urwid.start()            
        #main urwid loop:
        self.urwid.runLoop()
        
    def stop(self):
        """
        stops run() method by setting running=False
        """
        self.running = False

    def setupLogging(self):
        """
        initial setup of python built-in logging module
        """
        self.log.setLevel(logging.INFO)

        #adding streamHandler with console as target if no gui is enabled
        if not self.useUrwid:
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setLevel(logging.INFO)
            self.log.addHandler(streamHandler)
            
        fileHandler = logging.FileHandler('log/beast-arena.log')
        fileHandler.setLevel(logging.WARNING)
        self.log.addHandler(fileHandler)
        
    def run(self):
        """
        main-method of Game.py
        if networking is enabled the first part will be proceeded
        """
        self.running = True
        self.setupLogging()
    
        while self.running:    
            self.game = Game()
            
            if self.useUrwid:
                while not self.urwid:
                    time.sleep(0.1)
                self.urwid.changeGame(self.game)

            #loop for enabled networking
            if self.useNetworking:
                #first time server initialisation
                if self.server == None:
                    self.server = Server(self.game)
                    self.game.server = self.server
                    self.game.server.start()

                #for all games following first one
                self.game.server = self.server
                self.server.game = self.game
                    
                self.log.info('Game start will be: ' + str(self.game.startTime))
                
                while self.running:
                    if time.time() >= self.game.startTimeMillis and not(self.game.gameStarted):
                        if len(self.game.beastObjectMap) > 0:
                            self.log.info('Starting Game No. %s (' + str(self.game.startTime) + ')...', str(self.gamecount))
                            self.game.start()
                            self.gamecount += 1
                        else:
                            self.log.info('Canceled start of scheduled Game (' + str(self.game.startTime) + '): no client registered!')
                            self.game.gameFinished = True
                        break
                    time.sleep(0.05)
                    
            elif self.running:
                self.log.info('number of current game: ' + str(self.gamecount))
                self.gamecount += 1
                self.game.start()
            
            while self.running:
                if not self.running or self.game.gameFinished:
                    break
                time.sleep(0.1) 
                
            self.winners.addWinner(self.game.rankingList, self.gamecount - 1)                 
            time.sleep(2) # pause between two games
                        
if __name__ == '__main__':
    try:
        game = beast_arena()
        game.start()
        while not game.game:
            time.sleep(0.01)
        if game.game.enableUrwidVisualisation:
            game.runUrwid()
        else:
            while game.running:
                time.sleep(0.01)
  
    except KeyboardInterrupt, SystemExit:
        game.log.info("\nCaught KeyboardInterrupt, exiting...")
        game.log.debug("Currently running threads:")
        for thread in threading.enumerate():
            game.log.debug(' ' + str(thread))
            if not isinstance(thread,threading._MainThread) and thread.running:
		thread.stop()
	        thread.join()
	      

        game.log.debug('Threads after stop() & join():')
        for thread in threading.enumerate():
            game.log.debug(' ' + str(thread))
        game.log.debug('Exiting beast-arena MainThread...')
        game.log.info('beast-arena stopped: %s games played.', str(game.gamecount))
