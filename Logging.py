# -*- coding: utf-8 -*-

from Config import Config
import os.path
from datetime import datetime

class Logging(object):
    """
    logs every incoming string to chosen destination and to file
    if logginglevel is high enough
    The higher the loggingLevel of a message, the more important it is.
    
    Logging-Level-Explanation:
    1: DEBUG mode: use to print almost everything to debug
    2: VERBOSE mode: use to print game related, but mostly unnecessary messages 
    3: SUCCINT mode: use to print highly important messages only! always appear in every log
    """
    def __init__(self, game):
        self.game = game
        self.useFileLogging = Config.__getUseFileLogging__()
        self.interfaceLoggingLevel = Config.__getInterfaceLoggingLevel__()
        self.fileLoggingLevel = Config.__getFileLoggingLevel__()
        self.logFileName = ''
        
    def logToGui(self, string, loggingLevel=1):
        """
        send logstring exclusive to urwid server-tui, if enabled and loggingLevel is high enough
        """
        if self.game.enableUrwidVisualisation and loggingLevel >= self.interfaceLoggingLevel:
            self.game.gui.log(string)
        
    def log(self, string, loggingLevel=1):
        """
        log certain string either to enabled server tui or to standard console output
        """
        if loggingLevel >= self.interfaceLoggingLevel:
            if self.game.enableUrwidVisualisation:
                self.game.gui.log(string)
            else: 
                self.logToConsole(string, loggingLevel)
            if self.useFileLogging:
                self.logToFile(string, loggingLevel)
     
    def logToConsole(self, string, loggingLevel=1):
        """
        send logstring exclusive to standard console if server-tui is disabled
        """
        if not self.game.enableUrwidVisualisation:
            print string
            
            
    def logToFile(self, string, loggingLevel=1):
        """
        writes log message to file, handles fileoutput, and logs exclusive to file if called directly
        """
        if self.useFileLogging and loggingLevel >= self.fileLoggingLevel:
            if self.logFileName == '':
                self.logFileName = str(datetime.now()) + '.txt' 
                #creates log dir if necessary
                if not os.path.isdir('log'):
                    os.mkdir('log')
                #deletes all files except the 10 latest ones and generates header for new log
                try:
                    files = sorted(os.listdir('./log/'))
                    if len(files) >= 10:
                        i = len(files)
                        j = 0
                        while i >= 10:
                            os.remove('./log/' + files[0 + j])
                            j += 1
                            i -= 1
                        
                    f = open('./log/' + self.logFileName, 'a')
                    c = open("beast_config")
                    f.write("Settings:\n" + c.read() + '\n\n\n')
                    c.close()
                    f.close()
                except IOError as exc:
                    print 'Error occured while logging to file: ', exc
                
            #logs certain message to file
            try:
                f = open('./log/' + self.logFileName, 'a')
                f.write('LogLevel: ' + str(loggingLevel) + ", " + str(datetime.now()) + ": " + string + '\n')
                f.close()
            except IOError as exc:
                print 'Error occured while logging to file: ', exc

