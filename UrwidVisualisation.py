# -*- coding: utf-8 -*-
"""
$Id: UrwidVisualisation.py 515 2012-05-21 16:43:54Z sze $
"""
import urwid, time, threading, logging
from LoggingHandler import UrwidLoggingHandler

class UrwidVisualisation(threading.Thread):
    """
    main visualisation class which runs in its own thread and and is based on
    the python package urwid
    """
    
    def __init__(self, game):
        """
        UrwidVisualisation constructor with all initial parametrisation
        """
        threading.Thread.__init__(self)
        self.game = game
        self.newGame = None
        self.gameChanged = False
        self.statisticBeastName = None
        self.psychedelicMode = False 
        self.flash = False
        self.logEntrys = 0
        self.running = False
        self.beastAnalytics = self.game.beastAnalytics

        #adding a specific handler to the logger so all modules can log to urwid
        self.handler = UrwidLoggingHandler(self)
        self.handler.setLevel(logging.INFO)
        logging.getLogger('beast-arena-logging').addHandler(self.handler)
        
        self.palette = [
                        ('body', '', '', '', '#8f0', '#000'),
                        ('header', '', '', '', '#f00', '#000'),
                        ('frameHeader', '', '', '', '#000', '#f00'),
                        ('textContent', '', '', '', '#8f0', '#000'),
                        ('innerBorder', '', '', '', '', 'g31'),
                        ('outerBorder', '', '', '', '#0d0', '#8f0'),
                        ('innerBg', '', '', '', '#8f0', '#000'), ]
        
        self.rainbow_table = ['#00f', '#06f', '#08f', '#0af', '#0df', '#0ff', '#0fd', '#0fa', '#0f8', \
                              '#0f6', '#0f0', '#6d0', '#8d0', '#ad0', '#dd0', '#fd0', '#fa0', '#f80', \
                              '#f60', '#f00', '#f06', '#f08', '#f0a', '#f0d', '#f0f', '#d0f', '#a0f', '#80f', '#60f']
            
        self.palette = self.palette
        blank = urwid.Divider()
        
        #frame header box creation
        self.frameHeader = urwid.AttrMap(urwid.Text('Welcome to beast-arena - type the name of a beast to view its statistics!', 'center'), 'frameHeader')
        
        #headline box creation
        self.headline = urwid.Padding(urwid.BigText("beast-arena\n", urwid.font.HalfBlock7x7Font(),), 'center', width='clip')
        self.headline = self.getOutlinedObject(self.headline, 'innerBorder', 'header', 2)
        
        #worldmap box creation
        self.worldString = 'loading...'
        self.worldText = urwid.Text(self.worldString, 'center')
        self.world = urwid.AttrMap(self.worldText, 'innerBg')
        
        #ranking creation
        self.rankingText = urwid.Text("Ranking:")
        self.rankingBorder = self.getOutlinedObject(self.rankingText, 'innerBorder', 'textContent', 2)
        
        #statistic box generation
        self.statisticText = urwid.Text("Type valid beast name for individual analytics!")
        self.statisticBorder = self.getOutlinedObject(self.statisticText, 'innerBorder', 'textContent', 2)
                
        #logging box creation
        self.loggingTextBuffer = ''
        self.loggingText = urwid.Text(self.loggingTextBuffer, 'left')
        self.loggingList = urwid.ListBox([self.loggingText])
        self.logging = urwid.Pile([
                                   blank,
                                   urwid.AttrMap(blank, 'frameHeader'),
                                   urwid.AttrMap(urwid.Padding(urwid.Text("Logging:"), left=2), 'textContent'),
                                   urwid.Padding(urwid.BoxAdapter(self.loggingList, 10), left=2, right=2)
                                   ])
#        self.logging = self.getOutlinedObject(self.logging, 'innerBorder', 'textContent')
       
        #main area creation
        self.mainArea = urwid.AttrMap(urwid.Columns([
                                                     ('fixed', 40, self.statisticBorder),
                                                     self.world,
                                                     ('fixed', 40, self.rankingBorder)
                                                     ]), 'innerBg')
            
        self.listContent = [
                            blank,
                            self.headline,
                            blank,
                            self.mainArea,
                            urwid.AttrMap(blank, 'innerBg'),
                            self.logging,
#                            urwid.AttrMap(blank,'outerBorder')          
                            ]
               
        self.content = urwid.Pile(self.listContent)       
        
        self.fill = urwid.Filler(self.content, 'middle')
        self.map = urwid.AttrMap(self.fill, 'body')

        frame = urwid.Frame(self.map, header=self.frameHeader)
        
        def inputHandler(key):
            """
            handles all user input
            """
            if str(key) is not "up" and str(key) is not "down":
                if str(key) is " ":
                    if not self.psychedelicMode:
                        self.psychedelicMode = True
                        return
                    elif not self.flash and self.psychedelicMode:
                        self.flash = True
                        return
                    else: 
                        self.psychedelicMode = False
                        self.flash = False
                        return
                    
                if self.beastAnalytics.analyticBeastMap.has_key(str(key)):
                    self.statisticBeastName = str(key)
                else:
                    self.statisticBeastName = None
                    self.statisticText.set_text("invalid beastname! choose valid beast")
            
            if str(key) == "esc":
                raise KeyboardInterrupt
                        
        self.loop = urwid.MainLoop(frame, self.palette, unhandled_input=inputHandler)
        self.loop.screen.set_terminal_properties(colors=256)
        
        #psychedelic variables
        self.flashSwitchState = False                                    
        self.colorOffset = 0
        
    def getOffsetColor (self, offset):
        """
        for internal use only (psychedelic mode)
        """
        tmp = self.colorOffset + offset
        while tmp > len(self.rainbow_table) - 1:
            tmp -= len(self.rainbow_table)
        return self.rainbow_table[tmp]
    
    def getOutlinedObject(self, obj, borderStyle, innerStyle, padding):
        """
        used to generate specific borders around given urwid objects
        """
        return urwid.Pile([urwid.AttrMap(urwid.Divider(), borderStyle),
                           urwid.AttrWrap(urwid.Padding(urwid.AttrWrap(urwid.AttrMap(urwid.Padding(obj, \
                           left=padding, right=padding), innerStyle), innerStyle), left=padding, right=padding), borderStyle),
                           urwid.AttrMap(urwid.Divider(), borderStyle)
                           ])
    
    def updateWorld(self):
        """
        updates the world. is to be called exclusively from "run"
        """
        self.worldString = '\n'
        for j in range(self.game.worldMap.height):
            for i in range(self.game.worldMap.height):
                self.worldString += self.game.worldMap.world[j, i] + ' '
            self.worldString += '\n'
        self.worldText.set_text(self.worldString)
        
    def changeGame(self, game):
        """
        signals run() to react to changed game to visualize
        """
        self.newGame = game
        self.gameChanged = True
        self.log('game changed')
        
    def run(self):
        """
        main urwid loop to update content of all boxes
        gets called by gui.start() in Game
        """
        time.sleep(0.1)
        self.running=True
        while self.running:

            if self.gameChanged:
                #reset variables. used to switch game:
                self.game = self.newGame
                self.newGame = None
                self.gameChanged = False
                self.statisticBeastName = None
                self.logEntrys = 0
                self.loggingTextBuffer = ''
                self.beastAnalytics = self.game.beastAnalytics
                
            if not self.game.gameStarted:
                self.log("Waiting for Game to start...")

            while not self.game.gameStarted and self.running:
                if self.gameChanged:
                    break
                time.sleep(0.05)
            
            while self.game.gameStarted and not self.gameChanged and self.running:
                self.updateWorld()
                self.rankingText.set_text(self.game.getRankingList())
                if self.statisticBeastName is not None:
                    self.statisticText.set_text('\n' + self.beastAnalytics.getStatistic(self.statisticBeastName) + '\n') 
                else:     
                    self.statisticText.set_text('\ntype valid beast name to view analytics!\n')   
                self.loggingText.set_text(self.loggingTextBuffer)
                
    #            psychocolorswitch
                if self.psychedelicMode and self.running:
                    if self.flash:
                        if self.flashSwitchState:
                            self.loop.screen.register_palette([ ('body', '', '', '', '#fff', '#fff'),
                                                            ('header', '', '', '', '#fff', '#fff'),
                                                            ('frameHeader', '', '', '', '#fff', '#fff'),
                                                            ('textContent', '', '', '', '#fff', '#fff'),
                                                            ('innerBorder', '', '', '', '', '#fff'),
                                                            ('outerBorder', '', '', '', '', '#fff'),
                                                            ('innerBg', '', '', '', '#fff', '#fff'),
                                                            ]
                                                          )
                        self.flashSwitchState = not(self.flashSwitchState)
                        self.loop.draw_screen()
                        time.sleep(0.05)
                        
                    self.loop.screen.register_palette([ ('body', '', '', '', self.getOffsetColor(6), self.getOffsetColor(0)),
                                                        ('header', '', '', '', self.getOffsetColor(12), self.getOffsetColor(18)),
                                                        ('frameHeader', '', '', '', self.getOffsetColor(28), self.getOffsetColor(5)),
                                                        ('textContent', '', '', '', self.getOffsetColor(20), self.getOffsetColor(15)),
                                                        ('innerBorder', '', '', '', '', self.getOffsetColor(20)),
                                                        ('outerBorder', '', '', '', '', self.getOffsetColor(10)),
                                                        ('innerBg', '', '', '', self.getOffsetColor(9), self.getOffsetColor(25)),
                                                        ]
                                                      )
                    if (self.colorOffset + 1) > len(self.rainbow_table):
                        self.colorOffset = 0
                    else: self.colorOffset += 1
                
                if not self.psychedelicMode and self.running:
	            self.loop.screen.register_palette(self.palette)
                if self.running:
                    self.loop.draw_screen()
                    time.sleep(0.1)
            
    def runLoop(self):
        """
        main urwid loop (does not check updated content! only redraws screen on keystrokes or via manually called drawscreen() )
        """
        self.loop.run()
        
    def log(self, string):
        """
        method for logging module to print to urwid TUI console
        """
        self.logEntrys += 1
        self.loggingTextBuffer = string + "\n" + self.loggingTextBuffer
    
    def stop(self):
        """
        stops urwid-thread run() by setting running flag
        stops game-thread
        """
#        self.log.warning('urwidVisualisatoin: Stop() called ')
        self.running = False
        #only raise urwid.ExitMainLoop-Exception if stop initiated by key-press
     
