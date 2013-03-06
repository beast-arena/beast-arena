#! /usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, uic
import  time, sys, os, imp, string
basePath = sys.argv[0].split('/')
sys.path.append(os.path.abspath(sys.argv[0]).rpartition('/')[0].rpartition('/')[0])
from QClient import QClient
from SamysBeast import SamysBeast
from NikolaisBeast import NikolaisBeast
from Team8Beast import Team8Beast
from QWorld import QWorld
from ClientGuiLogic import *

class ClientGui(QtGui.QMainWindow):
    """
    extended by QtGui.QMainWindow
    Class for PyQt4 based graphical user interface displaying the progress of PyBeasts game. 
    This Class is extended by QMainWindow and represents the mainWindow of the gui
    """

    def __init__(self):
        """
        constructor
        """
        QtGui.QMainWindow.__init__(self)
        self.setFixedSize(1024,576)
        
        self.widgets={}
        self.widgets['choose']=uic.loadUi('widgetChoose.ui')
        self.widgets['beasts']=uic.loadUi('widgetBeasts.ui')
        self.widgets['server']=uic.loadUi('widgetServer.ui')
        self.widgets['play']=uic.loadUi('widgetPlay.ui')
        self.widgets['waiting']=uic.loadUi('widgetWaiting.ui')
        self.widgets['countdown']=uic.loadUi('widgetCountdown.ui')
        
        self.startTime=None
        self.automaticDestination=12
        self.beast = None
        self.firstRound = True
        self.currentServer = None
        self.serverMap = {}
        self.sleepAfterMove=QtCore.QTimer()
        self.sleepDuringMove=QtCore.QTimer()
        self.sleepBeforeMove=QtCore.QTimer()
        self.client = QClient(self)
        self.timerProgressBar = QtCore.QTimer()
        self.countdownTimer = QtCore.QTimer()
        self.availableServers = CheckTeamServerAvailability(self)
        self.handling = 'manual'
        self.gameWorldState=None
        self.sprintCooldown=0
        self.roundsWorld=None
        self.destination=12
        self.startTime = None
        self.countdownBarStartTime = None

        self.widgets['play'].labelWonOrLost.hide()
        self.widgets['beasts'].labelLogging.hide()
        self.widgets['play'].widgetSwitchRounds.hide()
        self.widgets['play'].widgetGameEnded.hide()
        self.widgets['server'].widgetAddNew.hide()
        self.widgets['server'].labelLogging.hide()
       
        self.connect(self.sleepDuringMove, QtCore.SIGNAL('timeout()'),self.stopSleepDuringMove)
        self.connect(self.sleepBeforeMove, QtCore.SIGNAL('timeout()'),self.stopSleepBeforeMove)
        self.connect(self.sleepAfterMove, QtCore.SIGNAL('timeout()'),self.stopSleepAfterMove)
        self.connect(self.client, QtCore.SIGNAL('sendAutomaicDestination(QString)'),self.setAutomaticDestination)
        self.connect(self.client, QtCore.SIGNAL('sendStartTime(QString)'),self.setStartTime)    
        self.connect(self.widgets['play'].widgetEnvironment,QtCore.SIGNAL('sendKeyboardMove(QString)'),self.sendKeyboardMove)
        self.connect(self.timerProgressBar, QtCore.SIGNAL('timeout()'), self.updateWaitingProgressBar)
        self.connect(self.availableServers, QtCore.SIGNAL('fillTeamServerList(PyQt_PyObject)'), self.fillTeamServerList)
        self.connect(self.countdownTimer, QtCore.SIGNAL("timeout()"), self.updateCountdown)
        self.connect(self.client, QtCore.SIGNAL("notify(QString,QString,QString)"), self.notify)
        self.connect(self.client, QtCore.SIGNAL("clientConnected(QString)"), self.clientConnected)
        
        self.connect(self.widgets['beasts'].toolButtonFileDialog, QtCore.SIGNAL("clicked()"), self.btnBuildFileDialogBeasts)
        self.connect(self.widgets['beasts'].pushButtonBack, QtCore.SIGNAL("clicked()"), self.widgets['choose'].show)
        self.connect(self.widgets['beasts'].pushButtonNext, QtCore.SIGNAL("clicked()"), self.btnChooseBeast)
        
        self.connect(self.widgets['choose'].manual_play_btn, QtCore.SIGNAL("clicked()"), self.btnSetHandling)
        self.connect(self.widgets['choose'].random_beast_btn, QtCore.SIGNAL("clicked()"), self.btnSetHandling)
        self.connect(self.widgets['choose'].custom_beast_btn, QtCore.SIGNAL("clicked()"), self.btnSetHandling)
        
        self.connect(self.widgets['countdown'].pushButtonCancel, QtCore.SIGNAL("clicked()"), self.btnCancelAndLeaveServer)
        
        self.connect(self.widgets['play'].pushButtonPreviousRound, QtCore.SIGNAL("clicked()"), self.btnRoundDecrement)
        self.connect(self.widgets['play'].pushButtonNextRound, QtCore.SIGNAL("clicked()"), self.btnRoundIncrement)
        self.connect(self.widgets['play'].pushButtonLastRound, QtCore.SIGNAL("clicked()"), self.btnJumpToLastRound)
        self.connect(self.widgets['play'].pushButtonFirstRound, QtCore.SIGNAL("clicked()"), self.btnJumpToFirstRound)
        self.connect(self.widgets['play'].pushButtonRegisterAgain, QtCore.SIGNAL("clicked()"), self.btnRegisterAgain)
        self.connect(self.widgets['play'].pushButtonLeaveServer, QtCore.SIGNAL("clicked()"), self.btnLeaveServer)
        self.connect(self.widgets['play'].checkBoxWorld, QtCore.SIGNAL("stateChanged(int)"), self.cbChangeWorldView)
        self.connect(self.widgets['play'].pushButtonLeaveGame, QtCore.SIGNAL("clicked()"), self.btnCancelAndLeaveServer)
        
        self.connect(self.widgets['server'].pushButtonConnectToTeamServer, QtCore.SIGNAL('clicked()'),self.btnConnectToTeamServer)
        self.connect(self.widgets['server'].pushButtonBack, QtCore.SIGNAL("clicked()"), self.widgets['choose'].show)
        self.connect(self.widgets['server'].pushButtonConnect, QtCore.SIGNAL("clicked()"), self.btnConnectToNewServer) 
        self.connect(self.widgets['server'].pushButtonNext, QtCore.SIGNAL("clicked()"), self.btnConnectClient)                                                              
        self.connect(self.widgets['server'].toolButtonFileDialog, QtCore.SIGNAL("clicked()"), self.btnBuildFileDialogCertificate)
        
        self.connect(self.widgets['waiting'].pushButtonCancel, QtCore.SIGNAL("clicked()"), self.btnCancelAndLeaveServer)
        
        for child in self.widgets['play'].groupBoxMove.children():
            self.connect(child, QtCore.SIGNAL("clicked()"), self.btnSendManualMove)
        
        for widget in self.widgets.values():
            widget.hide()
            widget.setParent(self)
        
        readServersFromFile(self.widgets['server'].comboBoxHostPortCert,self.serverMap)    
        
        rect = self.geometry()
        rect.moveCenter(QtGui.QApplication.desktop().availableGeometry().center())
        self.setGeometry(rect)
        
        self.widgets['choose'].show()
        self.availableServers.start()
        self.show()
        
    def setAutomaticDestination(self,destination):
        """
        Sets the instance variable automaticDestination. 
        It is called over a SIGNAL from QClient and sends the destination which was calculated by the costom beast for next move.
        @param destination QString: destination which was calculated by the costom beast
        """
        if destination!='?' and int(destination) in (0,2,4,10,14,20,22,24):
            self.sprintCooldown=4
            
        self.automaticDestination=destination
            
        
    def updateWaitingProgressBar(self):
        """
        method for updating a progress bars value. 
        it is connected to the timeout()-signal of the self.timerProgressBar which will be started to update progressBarWaiting on the WAITING widget 
        """
        updateWaitingProgressBar(self.widgets['waiting'].progressBarWaiting)
        
    def cbChangeWorldView(self):
        """
        checkBox method: connected to checkBoxWorld in PLAY widget
        changes between showing the big worlds widget and the play environment widget on PLAY widget depending on the check box condition
        """
        if self.widgets['play'].checkBoxWorld.isChecked():
            self.widgets['play'].widgetWorld.show()
            self.widgets['play'].widgetEnvironment.hide()
            return
        self.widgets['play'].widgetWorld.hide()
        self.widgets['play'].widgetEnvironment.show()    
                
    def btnJumpToLastRound(self):
        """
        pushButton method: connected to pushButtonLastRound on PLAY widget
        jumps to the last played round and order to draw it by calling setWorldRound()
        """
        self.roundsWorld.setStatusTip(str(len(self.gameWorldState)-1))
        self.setWorldRound()
    
    def btnJumpToFirstRound(self):
        """
        pushButton method: connected to pushButtonFirstRound on PLAY widget
        jumps to the first played round and order to draw it by calling setWorldRound()
        """
        self.roundsWorld.setStatusTip(str(0))
        self.setWorldRound()
        
    def btnCancelAndLeaveServer(self):
        """
        pushButton method: connected to pushButtonLeaveGame on PLAY widget, pushButtonCancel on WAITING widget, pushButtonCancel on COUNTDOWN widget
        disconnects client from current server and shows the SERVER widget again
        """
        self.widgets['play'].checkBoxWorld.setChecked(False)
        self.widgets['play'].widgetEnvironment.releaseKeyboard()
        self.emit(QtCore.SIGNAL('leaveServer()'))
        self.countdownTimer.stop()
        self.widgets['play'].widgetGameEnded.hide()
        if self.roundsWorld!=None:
            self.roundsWorld.hide()
        for widget in self.widgets.values():
            widget.hide()  
        self.widgets['server'].show()   
    
    def btnChooseBeast(self):
        """
        pushButton method: connected to pushButtonNext on BEASTS widget
        first checks if the user wants to use one of the available custom beasts. if so the chosen beast will be the beast to play with
        if not, the user wants to use a own implemented beast. if all parameters correct (file path,module name,class name) 
        the beast module will be imported and set to the beast to play with
        """        
        if self.widgets['beasts'].lineEditOwnImplementation.text() == '':
            beast = str(self.widgets['beasts'].comboBoxAvailableBeasts.currentText())
            try:
                beastInst = getattr(sys.modules[beast], beast)
            except:
                self.widgets['beasts'].labelLogging.setText('no beast chosen!')
                self.widgets['beasts'].labelLogging.show()
                return   
        
        else:
            try:   
                modName = str(self.widgets['beasts'].lineEditModuleName.text())
                beastName = str(self.widgets['beasts'].lineEditClassName.text())
                filepath = str(self.widgets['beasts'].lineEditOwnImplementation.text())
                
                imp.load_source(modName, filepath)                
                beastInst = getattr(sys.modules[modName], beastName)
                                  
            except:
                self.widgets['beasts'].labelLogging.setText('invalid file path, module name or class name') 
                self.widgets['beasts'].labelLogging.show() 
                return
        
        self.widgets['beasts'].labelLogging.hide()
        self.beast = beastInst()
        self.widgets['beasts'].hide()
        self.widgets['server'].show()
    
    def btnBuildFileDialogCertificate(self):
        """
        toolButton method: connected to toolButtonFileDialog on SERVER widget
        builds a file dialog window for choosing the server certificates' path 
        """
        path = QtGui.QFileDialog.getOpenFileName(self, 'choose certificate', 'certs')
        self.widgets['server'].lineEditCert.setText(path)
        
    def btnBuildFileDialogBeasts(self):
        """
        toolButton method: connected to toolButtonFileDialog on BEASTS widget
        builds a file dialog window for choosing the beast modules' path 
        """
        path = QtGui.QFileDialog.getOpenFileName(self, 'choose beast implementation (only .py files)', '..')
        self.widgets['beasts'].lineEditOwnImplementation.setText(path)

    def btnSetHandling(self):
        """
        pushButton method: connected to pushButtonCustom,pushButtonRandom,pushButtonManual all on CHOOSE widget
        checks which tactical method the user wants to use 
        (manual beast handling, simulate the movement with a custom beast implementation or just use a random movement)
        if it is custom handling the BEASTS widget will be called for choosing a beasts implementation
        """
        self.handling = str(self.sender().statusTip())

        if self.handling == 'costom':
            self.widgets['choose'].hide()
            self.widgets['beasts'].show()
            self.widgets['play'].emit(QtCore.SIGNAL('setManual(bool,bool)'),False,False)
            return
        elif self.handling == 'random':
            self.widgets['play'].emit(QtCore.SIGNAL('setManual(bool,bool)'),False,True)
        else:
            self.widgets['play'].emit(QtCore.SIGNAL('setManual(bool,bool)'),True,False)

        self.widgets['choose'].hide() 
        self.widgets['server'].show()

        self.widgets['server'].labelLogging.hide()
        self.widgets['beasts'].labelLogging.hide()
        self.beast=SamysBeast()
        
    def sendKeyboardMove(self,destination):
        """
        called by typing 'return' key on play mode if manual handling is chosen
        sends a chosen destination (manual keyboard handling) to the QClient 
        if the it is a sprint destination, sprintCooldown will be set to 4 (next for rounds sprints won't be allowed) and the sprint buttons on groupBoxMove (PLAY widget) will be disabled
        @param destination QString: the destination for the next move which the user chose over keyboard handling
        """
        if destination !='?' and int(destination) in (0,2,4,10,14,20,22,24)and self.sprintCooldown==0:
            self.sprintCooldown=4
            
        self.emit(QtCore.SIGNAL('sendManualMove(QString)'), destination)
        self.widgets['play'].widgetEnvironment.releaseKeyboard()
        self.widgets['play'].groupBoxMove.setEnabled(False)
        self.widgets['play'].widgetEnvironment.moveTo(destination)
     
    def btnSendManualMove(self):
        """
        pushButton method: connected to every button included in groupBoxManual on PLAY widget
        sends a chosen destination (manual handling), which is read out of the status tip of the pushed button, to the QClient 
        if the it is a sprint destination, sprintCooldown will be set to 4 (next for rounds sprints won't be allowed) and the sprint buttons on groupBoxMove (PLAY widget) will be disabled
        """
        destination = self.widgets['play'].groupBoxMove.sender().statusTip()
        
        if destination!='?'and int(destination) in (0,2,4,10,14,20,22,24) and self.sprintCooldown==0:
            self.sprintCooldown=4
        
        self.widgets['play'].groupBoxMove.setEnabled(False)
        self.destination=destination    
        self.sleepDuringMove.start()
        
    
    def connectClient(self, hostPortCert):
        """
        called by btnConnectClient() ,btnConnectToNewServer(),btnRegisterAgain(),btnConnectToTeamServer()
        connects the QClient to the server with the given details, checks if the connection was successful and try to register the QClient in servers game
        if the connection fails, a message will be displayed on SERVER widget
        if the registration fails the WAITING widget will be shown
        @param hostPortCert tuple: includes three separated strings: host, port and server certificate
        """
        if len(hostPortCert) != 3:
            # TODO: Logging, Exceptions or sth. similiar
            print 'method called with wrong arguments', hostPortCert
            return
    
        host = str(hostPortCert[0])
        port = int(hostPortCert[1])
        cert = str(hostPortCert[2])
        
        self.emit(QtCore.SIGNAL('setClientDetails'), (host, int(port)), cert, self.beast)
        self.emit(QtCore.SIGNAL('connectToServer()'))
        
        if self.client.connectedToServer:
            self.currentServer = hostPortCert

            self.setCursor(QtCore.Qt.WaitCursor)
            self.emit(QtCore.SIGNAL("waitingForRegistration()"))
            time.sleep(0.5)
            if not self.client.registeredInGame:
                self.widgets['server'].hide()
                self.widgets['waiting'].show()
                self.timerProgressBar.start(10)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.widgets['server'].labelLogging.hide()
            return
        
        self.widgets['server'].labelLogging.setText('Connection to server ' + host + ' failed.')
        self.widgets['server'].labelLogging.show()
                    
    def btnConnectClient(self):
        """
        pushButton method: connected to pushButtonNext on SERVER widget
        reads the host and port from comboBoxHostPortCert on SERVER widget, looks for the fitting item (host:port:certificate) in serverMap and calls connectClient with it 
        """
        hostPort = str(self.widgets['server'].comboBoxHostPortCert.currentText())
        if hostPort!='':
            self.connectClient(self.serverMap[hostPort])
           
    def btnConnectToNewServer(self):   
        """
        pushButton method: connected to pushButtonConnect on SERVER widget
        reads the host, the port and the certificates path the fitting lineEdits on SERVER widget and calls connectClient with the generated tuple 
        if the connection was successful, lineEdits will be cleared and the server will be written into the serverAddresses file
        """  
        host = str(self.widgets['server'].lineEditHost.text())
        port = self.widgets['server'].lineEditPort.text()
        cert = str(self.widgets['server'].lineEditCert.text())
        
        self.connectClient((host, port, cert))
            
        if self.client.connectedToServer:
            self.widgets['server'].pushButtonNext.show()
            self.widgets['server'].widgetAddNew.hide()
            server = host + ':' + str(port) + ':' + cert + '\n'
            
            appendServerToFile(server)
            
            hostPort = host + ':' + port
            self.widgets['server'].comboBoxHostPortCert.insertItem(0, hostPort)
            self.serverMap[str(hostPort)] = (host, str(port), cert)
            self.widgets['server'].lineEditHost.clear()
            self.widgets['server'].lineEditPort.clear()
            self.widgets['server'].lineEditCert.clear()
            
    
    def doFirstRoundStuff(self):
        try:
            self.worldSize = self.client.getWorldSize()
        except:
            self.emit(QtCore.SIGNAL('leaveServer()'))
            self.widgets['server'].show()
            self.widgets['play'].hide()
            self.widgets['server'].labelLogging.setText('an error occurred!')
            self.widgets['server'].labelLogging.show()
            return
        
        self.gameWorldState=[]
        self.widgets['play'].widgetWorld=QWorld(self.widgets['play'])
        self.widgets['play'].widgetWorld.initiate(self.worldSize, self.beast.name)
        self.sprintCooldown=0
        self.firstRound = False
        self.widgets['play'].checkBoxWorld.setChecked(False)
        self.widgets['play'].widgetEnvironment.show()
        self.widgets['play'].widgetWorld.hide()
        if self.handling!='manual':
            self.widgets['play'].groupBoxMove.setEnabled(False)
    
    def doGameEndedStuff(self,energy,lastTenRounds):
            self.widgets['play'].checkBoxWorld.hide()
            self.widgets['play'].checkBoxWorld.setChecked(False)
            self.widgets['play'].widgetSwitchRounds.show()
            self.widgets['play'].labelEnergy.setText(str(energy))
            self.widgets['play'].pushButtonLeaveGame.hide()
            self.widgets['play'].widgetGameEnded.show()
            self.widgets['play'].widgetWorld.hide()
            self.widgets['play'].widgetWorld.clear()
            self.widgets['play'].widgetEnvironment.clear()
            self.widgets['play'].widgetEnvironment.hide()
            lastTenRounds = str(lastTenRounds).split(';')
    
            try:
                lastTenRounds.remove('')
            except:
                pass
            self.gameWorldState+=lastTenRounds
            
            if self.beast.name in self.gameWorldState[len(self.gameWorldState)-1]:
                self.widgets['play'].labelWonOrLost.setText("You are the winner!!!")
                for letter in string.ascii_letters:
                    if letter != self.beast.name and letter in self.gameWorldState[len(self.gameWorldState)-1]:
                        self.widgets['play'].labelWonOrLost.setText('You are part of the winners list.')
                        break
            else:
                self.widgets['play'].labelWonOrLost.setText("You lost!")
                
            self.widgets['play'].labelWonOrLost.show()
            self.roundsWorld.initiate(self.worldSize,self.beast.name)
            self.roundsWorld.setStatusTip(str(len(self.gameWorldState)-1))
            self.setWorldRound()
            self.widgets['play'].widgetEnvironment.releaseKeyboard()
            
    def notify(self, surrounding, energy, worldBeforeTenRounds):
            """
            called by the QClients listening loop every round that is played
            in first round of game world size of current game is retrieved from client and transfered to worldWidget on PLAY widget 
            decrements the sprntCooldown if it is bigger than zero and informs widgetEnvironment on PLAY widget if sprints are allowed in current round
            checks if the game has ended. if so the game round gameWorldState which is the summary of all played rounds is completed, last round is displayed and setWorldRound. method returns.
            if beast is not dead (energy is not an empty string) surrounding is drawn in widgetEnvironment, otherwise widgetEnvironment is hidden and widgetWorld is shown on PLAY widget
            if it is round ten or higher (worldBeforeTenRounds is not an empty string) worldBeforeTenRounds is added to gameWorldState
            otherwise it checks the chosen handling method. if it is not manual, time delay before automatic move is set 
            @param surrounding QString: current surrounding 5x5 to string (length 25) of the beast
            @param energy QString: current energy of the beast
            @param worldBeforeTenRounds QString: Normally world state before ten rounds. At last round it represents last ten world states, concatenated and seperated with ';' 
            """
            
            if surrounding == 'Ende':
                self.doGameEndedStuff(energy,worldBeforeTenRounds)
                return
            
            if self.firstRound:
                self.doFirstRoundStuff()
            
            if self.sprintCooldown>0:
                if self.handling=='manual':
                    counter=0
                    for child in self.widgets['play'].groupBoxMove.children():
                        if 'Sprint' in child.objectName():
                            child.setEnabled(False)
                        counter+=1
                self.widgets['play'].emit(QtCore.SIGNAL('setSprint(bool)'),False)
                self.sprintCooldown-=1
                
            if self.sprintCooldown==0:
                self.widgets['play'].emit(QtCore.SIGNAL('setSprint(bool)'),True)
                if self.handling=='manual':
                    for child in self.widgets['play'].groupBoxMove.children():
                        child.setEnabled(True)

            if worldBeforeTenRounds != '':
                self.widgets['play'].checkBoxWorld.show()
                self.widgets['play'].widgetWorld.draw(worldBeforeTenRounds)
                self.gameWorldState.append(worldBeforeTenRounds)
                  
            if self.client.connection:
                if self.client.deadBeast:
                    self.widgets['play'].labelWonOrLost.setText("you are dead!")
                    self.widgets['play'].labelWonOrLost.show()
                    self.widgets['play'].checkBoxWorld.setChecked(True)
                    self.widgets['play'].checkBoxWorld.hide()
                    self.widgets['play'].groupBoxMove.setEnabled(False)  
                    self.widgets['play'].widgetEnvironment.releaseKeyboard()
                    self.widgets['play'].labelEnergy.setText(str(0))
                    return
                
                self.widgets['play'].labelEnergy.setText(str(energy))
                self.widgets['play'].widgetEnvironment.draw(surrounding)
                
                if self.handling!='manual':
                    self.sleepBeforeMove.start(500)  
                else:
                    self.widgets['play'].widgetEnvironment.grabKeyboard()
                    self.widgets['play'].groupBoxMove.setEnabled(True)
                    self.widgets['play'].checkBoxWorld.setChecked(False)              
            else:
                self.widgets['play'].labelWonOrLost.setText('connection lost')
                self.widgets['play'].checkBoxWorld.hide()
                
    def stopSleepBeforeMove(self):
        """
        connected to timer sleepBeforeMove timeout()
        stops sleepBeforeMove timer
        asks QClient to send either an automatic move or a random move depending on the current chosen handling method
        """
        self.sleepBeforeMove.stop()
        
        if self.handling=='costom':
            self.emit(QtCore.SIGNAL('sendAutomaticMove()'))     
        else:
            self.emit(QtCore.SIGNAL('sendRandomMove()'))
            
        self.widgets['play'].widgetEnvironment.moveTo(self.automaticDestination)
        
    def stopSleepDuringMove(self):
        """
        connected to timer sleepDuringMove timeout()
        stops sleepDuringMove timer
        only called if manual handling method is chosen and user uses groupBoxManual on PLAY widget for movements 
        chosen move is displayed on widgetEnvironment on PLAY widget and the displaying delay after the move is set.
        """
        self.sleepDuringMove.stop() 
        if self.handling=='manual':
            self.widgets['play'].widgetEnvironment.moveTo(str(self.destination))
            self.widgets['play'].groupBoxMove.setEnabled(False)
            self.sleepAfterMove.start(500) 
        
    
    def stopSleepAfterMove(self): 
        """
        connected to timer sleepAfterMove timeout()
        stops sleepAfterMove timer 
        only called if manual handling method is chosen and user uses groupBoxManual on PLAY widget for movements 
        
        """
        self.emit(QtCore.SIGNAL('sendManualMove(QString)'),str(self.destination))
        self.sleepAfterMove.stop()
        
       
    def btnRoundIncrement(self):
        """
        pushButton method: connected to pushButtonNextRound on PLAY widget
        increments the status tip of rounds which represents the round number and calls setWorldRound()
        """
        self.roundsWorld.setStatusTip(str(int(self.roundsWorld.statusTip())+1))
        self.setWorldRound()
        
    def btnRoundDecrement(self):
        """
        pushButton method: connected to pushButtonPreviousRound on PLAY widget
        decrements the status tip of rounds which represents the round number and calls setWorldRound()
        """
        self.roundsWorld.setStatusTip(str(int(self.roundsWorld.statusTip())-1))
        self.setWorldRound()
    
    def setWorldRound(self):
        """
        called by notify(), btnRoundDecrement(), btnRoundIncrement()
        sets pushButtons text on widgetSwitchRounds and disable the adequate button depending on the current selected round
        """
        self.widgets['play'].pushButtonPreviousRound.setEnabled(True)
        self.widgets['play'].pushButtonNextRound.setEnabled(True)
        self.widgets['play'].pushButtonLastRound.setEnabled(True)
        self.widgets['play'].pushButtonFirstRound.setEnabled(True)
        
        newRound=int(self.roundsWorld.statusTip())
        numberOfRounds=len(self.gameWorldState)-1
        
        if newRound==0:
            self.widgets['play'].labelCurrentRound.setText('first round')
            self.widgets['play'].pushButtonPreviousRound.setEnabled(False)
            self.widgets['play'].pushButtonFirstRound.setEnabled(False)
            self.roundsWorld.draw(self.gameWorldState[int(newRound)])
            return
        elif newRound==numberOfRounds:
            self.widgets['play'].labelCurrentRound.setText('last round')
            self.widgets['play'].pushButtonNextRound.setEnabled(False)
            self.widgets['play'].pushButtonLastRound.setEnabled(False)
            self.roundsWorld.draw(self.gameWorldState[int(newRound)])
            return
        
        self.widgets['play'].labelCurrentRound.setText('round '+str(newRound+1))
        self.roundsWorld.draw(self.gameWorldState[int(newRound)])
                                
    def updateCountdown(self):
        """
        connected to countdownTimer timeout()
        calls updateProgressBar to update value of progressBarWaiting on COUNTDOWN widget
        checks if the start time of the game the client is registered in is reached
        """
        if not self.countdownBarStartTime:
            self.countdownBarStartTime = datetime.datetime.now()
        if self.startTime:
            gameStartTime = self.startTime
        else:
            gameStartTime = None
        updateProgressBar(self.widgets['countdown'].progressBarWaiting, self.countdownBarStartTime, gameStartTime)
    
        if self.startTime <= datetime.datetime.now():
            self.countdownTimer.stop()                
            self.widgets['countdown'].progressBarWaiting.setStatusTip('forward')
            self.widgets['countdown'].progressBarWaiting.setValue(0)
            self.countdownBarStartTime = None
            self.widgets['play'].widgetEnvironment.clear()
            self.widgets['play'].widgetEnvironment.show()
            self.widgets['play'].labelEnergy.clear()
            self.widgets['play'].labelWonOrLost.hide()
            self.widgets['play'].widgetWorld.hide()
            self.widgets['play'].checkBoxWorld.hide()
            self.roundsWorld=QWorld(self.widgets['play'])
            self.widgets['play'].pushButtonLeaveGame.show()
            self.widgets['play'].widgetSwitchRounds.hide()
            self.widgets['countdown'].hide()
            self.widgets['play'].show()
            self.sprintCooldown=0
            self.firstRound=True
    
    def setStartTime(self,startTime):
        """
        connected to QClient, called if a game starts 
        set the start time of the next game and display it on COUNTDOWN widget
        @param startTime QString: start time of the next game
        """
        self.startTime=parseStartTime(startTime)
    
    def startCountdown(self):
        """
        called by clientConnected()
        calls the client, that the start time of the next game is needed
        starts countdownTimer to wait for game start
        """
        self.emit(QtCore.SIGNAL('getStartTime()'))
        if self.startTime is not None:
            self.widgets['server'].hide()
            self.widgets['countdown'].show()
            startTime = string.rsplit(str(self.startTime),'.')[0]
            self.widgets['countdown'].labelTime.setText(startTime)
            self.countdownTimer.start(10)
        else:
            self.widgets['server'].labelLogging.setText('error occured')
        
    def clientConnected(self, beastName):
        """
        connected to QClient, called if the connection to a server succeeded
        COUNTDOWN widget is shown 
        @param beastName QString: name (letter between a and Z) of the beast in registered game
        """
        self.beast.name = str(beastName)
        self.startCountdown()
        self.timerProgressBar.stop()
        self.widgets['waiting'].hide()
        self.widgets['waiting'].progressBarWaiting.setValue(0)
        self.widgets['waiting'].progressBarWaiting.setStatusTip('forward')
       
    def btnRegisterAgain(self):
        """
        pushButton method: connected to pushButtonRegisterAgain on PLAY widget
        clears the PLAY widget and connects to current server again
        """
        self.roundsWorld.hide()
        self.widgets['play'].widgetEnvironment.clear()
        self.widgets['play'].widgetWorld.clear()
        self.widgets['play'].widgetGameEnded.hide()
        self.widgets['play'].hide()
        self.connectClient(self.currentServer) 

    def btnLeaveServer(self):
        """
        pushButton method: connected to pushButtonLeave on PLAY widget
        clears the PLAY widget and shows SERVER widget 
        """
        self.widgets['play'].checkBoxWorld.setChecked(False)
        self.widgets['play'].widgetEnvironment.releaseKeyboard()     
        self.roundsWorld.hide()
        self.widgets['play'].widgetGameEnded.hide()
        self.widgets['play'].hide()
        self.widgets['server'].show()
        
            
    def fillTeamServerList(self, sList):
        serverList = self.widgets['server'].teamServerList
        self.widgets['server'].pushButtonConnectToTeamServer.hide()
        selectedRow = None
        if len(serverList.selectedItems()) > 0:
            selectedRow = serverList.row(serverList.selectedItems()[0])
        serverList.clear()
        for s in sList:
            teamServer = QtGui.QListWidgetItem(serverList)
            teamServer.setTextColor(QtGui.QColor('red'))
            teamServer.setIcon(QtGui.QIcon('resources/server/cross.png'))
            
            if s[1] == 'online':
                teamServer.setTextColor(QtGui.QColor('green'))
                teamServer.setIcon(QtGui.QIcon('resources/server/check.png'))  
            teamServer.setText(s[0])
            serverList.addItem(teamServer)
        if selectedRow is not None:
            serverList.setCurrentRow(selectedRow)
            self.widgets['server'].pushButtonConnectToTeamServer.show()
        self.widgets['server'].labelLastUpdate.setText('last update: ' + time.strftime('%H:%M:%S'))
        serverList.show()

    def btnConnectToTeamServer(self):
        host = 'vsqueeze64.informatik.fh-augsburg.de'
        serverList = self.widgets['server'].teamServerList
        server = serverList.selectedItems()[0]
        
        port = 10001 + serverList.row(server)
        cert = 'certs/team' + str(port - 10000) + '.crt'
        self.connectClient((host, port, cert))
                                              
class CheckTeamServerAvailability(QtCore.QThread):
    def __init__(self, window):
        QtCore.QThread.__init__(self)
        self.host = 'vsqueeze64.informatik.fh-augsburg.de'
        self.portRange = range(10001, 10012)
        self.tcount = 1
        self.sList = []
        self.window = window
        self.running = True
    
    def run(self):
        while self.running:
            self.sList = []
            self.tcount = 1
            for port in self.portRange:
                tString = 'Team ' + str(self.tcount)
                client = QClient(self.window)
                cert = 'certs/team' + str(self.tcount) + '.crt'
                client.setClientDetails((self.host,port), cert)
                #self.window.emit(QtCore.SIGNAL('setClientDetails'), (self.host, int(port)), cert,None)
                client.connectToServer()
                if client.connectedToServer:
                    self.sList.append((tString, 'online'))
                else:
                    self.sList.append((tString, 'offline'))
                self.tcount += 1
                del(client)
            self.emit(QtCore.SIGNAL('fillTeamServerList(PyQt_PyObject)'), self.sList)
            time.sleep(5)
        
    def stop(self):
        self.running = False    
                                                 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    splash = QtGui.QSplashScreen(QtGui.QPixmap('resources/intro/intro.jpg'))
    splash.show()
    time.sleep(3)
    gui= ClientGui()
    splash.destroy()
    sys.exit(app.exec_())

