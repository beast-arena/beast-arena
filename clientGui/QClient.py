# -*- coding: utf-8 -*-

from PyQt4 import QtCore
import ssl, time, string, random
from SocketCommunication import read, write
from Beast import Beast
from socket import socket

class QClient(QtCore.QThread):
    """
    extended by QtCore.QThread
    client especially written for PyQt4 GUI for communication between a ssl server and the GUI 
    """
    
    def __init__(self, gui):
        """
        constructor
        @param gui QMainWindow: window to connect the own signals to
        """
        QtCore.QThread.__init__(self) 
        self.hostPort = None
        self.serverCert = None
        self.beast = None
        self.connection = None
        self.bewegeString = None
        self.worldSize = None
        self.running = True
        self.connect(gui, QtCore.SIGNAL('sendManualMove(QString)'), self.sendManualMove)
        self.connect(gui, QtCore.SIGNAL('sendRandomMove()'), self.sendRandomMove)
        self.connect(gui, QtCore.SIGNAL('sendAutomaticMove()'), self.sendAutomaticMove)
        self.connect(gui, QtCore.SIGNAL('setClientDetails'), self.setClientDetails)
        self.connect(gui, QtCore.SIGNAL('connectToServer()'), self.connectToServer)
        self.connect(gui, QtCore.SIGNAL('waitingForRegistration()'), self.waitingForRegistration)
        self.connect(gui, QtCore.SIGNAL('leaveServer()'), self.leaveServer)
        self.connect(gui,QtCore.SIGNAL('getStartTime()'),self.getGameStartTime)
    
        self.connDetailsNotSet = True
        self.connectedToServer = False
        self.registeredInGame = False
        
        self.firstTry=True
              
    def waitingForRegistration(self):
        """
        called by GUI if client connected to a server
        if it is the first server connection of current session, it starts the own thread instantly
        if not so, it waits until the channel of own thread is open for starting again and starts it 
        """
        if self.firstTry:
            self.start()
            self.firstTry=False
            return
        while not self.isFinished():
            pass
        self.start()
              
    def run(self):
        """
        overwritten method from QtCore.QThread
        called if start() is called, starts the own thread
        try to register the client in connected servers' game 
        if it fails, this will be repeated until it worked by disconnecting from and connecting to server again
        if client is registered listening loop will be started
        """
        
        self.running = True
        self.deadBeast = False
         
        if not self.registration():
            while True:
                self.closeConnection()
                time.sleep(1)
                self.connectToServer()
                if self.registration():
                    break

        time.sleep(0.5)
        self.listening()
        
    def stop(self):
        """
        called by leaveServer()
        stops the listening loop
        """
        self.running = False

    def listening(self):
        """
        loop in which the client waits for the servers bewegeString 
        bewegeString is split to particular arguments which will be sent to GUI
        after we get 'Ende' the ssl connection will be closed
        """
        while self.running:
            try:

                self.bewegeString = read(self.connection)
                
                surrounding = self.bewegeString.split(';')[1]
                energy = self.bewegeString.split(';')[0]
                worldBeforeTenRounds=self.bewegeString.split(';')[2]
                
                if self.deadBeast and worldBeforeTenRounds!='':
                    time.sleep(0.2)
                
                if self.worldSize == None:
                    write(self.connection, 'Weltgroesse?')
                    self.worldSize = read(self.connection)
                    
                if 'Ende' in self.bewegeString:
                    if self.connectedToServer:
                        self.leaveServer()
                               
                if self.bewegeString.startswith(';;'):
                    self.deadBeast = True

                if 'Ende' in self.bewegeString:
                    semiCounter=0
                    counter=0
                    while semiCounter<2:
                        if self.bewegeString[counter]==';':
                            semiCounter+=1
                        counter+=1
                    strLastTenRounds=self.bewegeString[counter:] 
                    self.emit(QtCore.SIGNAL("notify(QString,QString,QString)"), surrounding, energy, strLastTenRounds)
                    break
                self.emit(QtCore.SIGNAL("notify(QString,QString,QString)"), surrounding, energy, worldBeforeTenRounds)
                
            except Exception as e:
                print time.asctime(), e, ': lost connection to Server'
                self.leaveServer()                
                
    def leaveServer(self):
        """
        called by GUI if user wants to leave current server and if game ends
        stops the own thread, cleans server-linked instance variables and closes ssl connection
        """
        self.stop()
        self.hostPort = None
        self.worldSize = None
        self.serverCert = None
        self.connDetailsNotSet = True
        self.beast = None 
        self.closeConnection()
        self.registeredInGame = False
        self.connectedToServer = False
        
    def sendManualMove(self, destination):
        """
        Sends manual move to server, e. g. when called from client GUI.
        @param destination QString: destination of the move
        """
        write(self.connection, str(destination))
    
    def sendRandomMove(self):
        """
        Sends random move to server, e. g. when called from client GUI.
        sends selected destination back to GUI
        """
        destination = random.choice((0, 2, 4, 6, 7, 8, 10, 11, 12, 13, 14, 16, 17, 18, 20, 22, 24, '?'))
        self.emit(QtCore.SIGNAL('sendAutomaicDestination(QString)'),str(destination))
        time.sleep(0.3)
        write(self.connection, str(destination))
        
    def sendAutomaticMove(self):
        """
        Sends random move to server, e. g. when called from client GUI.
        sends selected destination back to GUI
        """
        if self.beast:
            destination = self.beast.bewege(self.bewegeString)
        else:
            destination=None
        if destination != None:
            self.emit(QtCore.SIGNAL('sendAutomaicDestination(QString)'),str(destination))
            time.sleep(0.3)
            write(self.connection, str(destination)) # cast to str finally here because str(None)=='None'
        
    def connectToServer(self):
        """
        called by GUI if user wants to connect server and has sent server details (host, port, certificates path)
        tries to connect to a ssl server 
        """
        try:
		    if (False): # TODO: add checkbox in GUI for ssl usage
		        self.connection = ssl.wrap_socket(socket(), cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_SSLv3, ca_certs=self.serverCert)
		    else:
		    	self.connection = socket()
		    self.connection.connect(self.hostPort)
		    self.connectedToServer = True
        except Exception:
            self.connDetailsNotSet = True
            self.connectedToServer = False
            
    def closeConnection(self):
        """
        called by run() and leaveServer()
        tries to close connection to ssl server
        """
        try:
            self.connection.close()
        except Exception:
            pass
        
        self.connection = None
        self.connectedToServer=False
     
     
    def getGameStartTime(self): 
        """
        sends ask for the start time of next game to GUI
        """
        if 10008 in self.hostPort:
            write(self.connection, "startdelay?") 
        else:  
            write(self.connection, "Spielbeginn?") 
        self.emit(QtCore.SIGNAL('sendStartTime(QString)'),read(self.connection))
     
    def getWorldSize(self):
        """
        returns the world size of current game
        """
        sizeSplit = self.worldSize.split('x')
        x = int(sizeSplit[0])
        y = int(sizeSplit[1])
        return ((x, y))    

    def registerBeast(self):
        """
        called by registration()
        register the client in current game
        """
        write(self.connection, "Anmeldung!")
        beastName = read(self.connection)
        return beastName
        
    def isRegisterAllowed(self):
        """
        called by registration()
        checks if server provides an open game to register in
        """
        write(self.connection, "Anmeldung moeglich?")
        response = read(self.connection)
        if response == 'Ja':
            return True
        return False
        
    def registration(self):
        """
        called by run()
        calls methods to register client in current game, sends the received beast name if registration was successful and return weather registration was successful
        """
        try:
            if self.isRegisterAllowed():
                beastName = self.registerBeast()
                if beastName in string.ascii_letters and len(beastName) == 1:
                    self.registeredInGame=True
                    self.emit(QtCore.SIGNAL("clientConnected(QString)"), beastName)
                    return True
            return False
        except:
            return False

    def setClientDetails(self, hostPort, serverCert, beast=Beast()):
        """
        called by GUI if user chose the server he wants connected to
        write server details to instance variables
        @param hostPort tuple: tuple that contains server address and port number
        @param serverCert string: path of local stored server certificate
        @param beast: class instance of chosen beast implementation  
        """
        if self.connDetailsNotSet:
            self.hostPort = hostPort
            self.serverCert = serverCert
            self.connDetailsNotSet = False
            self.beast = beast
            self.deadBeast = False

