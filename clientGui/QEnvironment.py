# -*- coding: utf-8 -*-

import sys,os
from PyQt4 import QtGui,QtCore

basePath = sys.argv[0].split('/')
sys.path.append(os.path.abspath(sys.argv[0]).rpartition('/')[0].rpartition('/')[0])

class QEnvironment(QtGui.QWidget):
    """
    extended by QtGui.QWidget
    widget for displaying the 5x5 environment of the own beast of the user, also for displaying moves
    """
    
    def __init__(self,qParent=None):
        """
        constructor
        @qParent: QObject to set as parent 
        """
        
        QtGui.QWidget.__init__(self,parent=qParent)
        self.setFixedSize(535,535)

        j = 0
        self.spacings=[0,107,214,321,428]
    
        self.frames=[]
        
        self.background=QtGui.QFrame(self)
        self.background.setFixedSize(535,535)

        #placing the frames which display the values of every index of environment on widget 
        counter=0
        for i in range(5):
            for j in range(5):
                x=self.spacings[j]
                y=self.spacings[i]
                frame=QtGui.QFrame(self)
                frame.setFixedSize(107,107)
                frame.move(x,y)
                frame.show()
                frame.setStyleSheet("background-color: transparent")
                self.frames.append(frame)
                counter+=1     
                
        
        self.cursorPic='resources/in_game/beast.png'
        self.redCrossPic='resources/in_game/cross.png'
        self.backgroundPic='resources/in_game/nosprint_background.jpg'
        self.backgroundSprintPic='resources/in_game/sprint_background.jpg'
        
        self.redCrossFrame=QtGui.QFrame(self)
        self.redCrossFrame.setFixedSize(107,107)
        self.redCrossFrame.setStyleSheet("image: url("+self.redCrossPic+");")
        self.redCrossFrame.hide()
        
        self.moveFrame=QtGui.QFrame(self)
        self.moveFrame.setFixedSize(107,107)
        self.moveFrame.setStyleSheet("image: url("+self.cursorPic+");")
        self.moveFrame.move(214,214)
        self.moveFrame.show()
        
        self.bigBeastPic='resources/in_game/evil_beast.png'
        self.smallBeastPic='resources/in_game/small_beast.png'
        self.foodPic='resources/in_game/food.png'
        self.hidePic='resources/hide.png'
        
        self.redListedDestinations=(QtCore.QPoint(107,0),QtCore.QPoint(0,107),QtCore.QPoint(0,321),QtCore.QPoint(428,107),QtCore.QPoint(428,321),QtCore.QPoint(321,0),QtCore.QPoint(107,428),QtCore.QPoint(321,428))
        
        self.destination=12
        self.destinations={}
        
        #fills a dictionary. key: position of frames, values: index of environment
        x=0
        y=0
        counter=0
        while y<=428:
            x=0
            while x<=428:
                self.destinations[(x,y)]=counter
                x+=107  
                counter+=1
            y+=107

        self.connect(qParent, QtCore.SIGNAL('setSprint(bool)'),self.setSprint)
        self.connect(qParent, QtCore.SIGNAL('setManual(bool,bool)'),self.setManual)
        self.manual=None
        self.sprint=True
        self.show()
        
    def setSprint(self,sprint):
        """
        called by the gui if the beast just sprinted or sprints are allowed again
        changes the instance variable sprint which represents if a sprint in game is currently allowed
        @param sprint boolean: flag if a sprint is allowed 
        """
        self.sprint=sprint
    
    def clear(self):
        """
        called by gui every round
        clears the widget by hiding every frame and sets the own beast to the center of widget
        """
        self.moveFrame.move(214,214)
        self.moveFrame.show()
        self.redCrossFrame.hide()
        for frame in self.frames:
            frame.hide()
    
    def setManual(self,manual, random):
        """
        called by gui if the user changes his  handling method
        changes the instance variable manual which represents if the user chose manual or automatic handling method
        """
        if random:
            self.cursorPic='resources/in_game/random_beast.png'
            self.moveFrame.setStyleSheet("image: url("+self.cursorPic+");")
        else:
            self.cursorPic='resources/in_game/beast.png'
            self.moveFrame.setStyleSheet("image: url("+self.cursorPic+");")
            

        self.manual=manual
  
    def keyPressEvent(self, event):
        """
        overwritten method of QtGui.QWidget
        called if a key on keyboard is pressed
        checks if a relevant key for beast controlling was pressed and conduct the move or sends the final destination to gui
        moreover it checks if the cursor frame moved to a forbitten game field and marks it in that case
        @param event QKeyEvent: represents the pressed key 
        """
        
        if self.manual:
            key=event.key()
            self.redCrossFrame.hide()
            self.moveFrame.show()
            
            #key 16777220: return, key 32: space
            if key==QtCore.Qt.Key_Return or key==QtCore.Qt.Key_Space:
                self.emit(QtCore.SIGNAL('sendKeyboardMove(QString)'),str(self.destination))
                return
            
            #key 72: H
            elif key==QtCore.Qt.Key_H:
                self.moveFrame.setStyleSheet("image: url("+self.hidePic+");")
                self.emit(QtCore.SIGNAL('sendKeyboardMove(QString)'),'?')
                return
            
            #key 16777235: arrow up
            elif key==QtCore.Qt.Key_Up:
                if self.moveFrame.y()>=107:
                    self.moveFrame.move(self.moveFrame.x(),self.moveFrame.y()-107)
            
            #key 16777237: arrow down
            elif key==QtCore.Qt.Key_Down:
                if self.moveFrame.y()<=321:
                    self.moveFrame.move(self.moveFrame.x(),self.moveFrame.y()+107)
            
            #key 16777234: arrow left
            elif key==QtCore.Qt.Key_Left:
                if self.moveFrame.x()>=107:
                    self.moveFrame.move(self.moveFrame.x()-107,self.moveFrame.y())
            
            #key 16777236: arrow right 
            elif key==QtCore.Qt.Key_Right:
                if self.moveFrame.x()<=321:
                    self.moveFrame.move(self.moveFrame.x()+107,self.moveFrame.y())
        
            if self.moveFrame.pos() in self.redListedDestinations:
                self.redCrossFrame.move(self.moveFrame.pos())
                self.redCrossFrame.show()
                self.moveFrame.hide()
                
            if not self.sprint and self.destinations[self.moveFrame.x(),self.moveFrame.y()] in (0,2,4,10,14,20,22,24):
                self.redCrossFrame.move(self.moveFrame.pos())
                self.redCrossFrame.show()
                self.moveFrame.hide()
            self.destination=self.destinations[self.moveFrame.x(),self.moveFrame.y()] 
    
    def draw(self,surrounding):
        """
        called by gui every round
        displays the 5x5 environment based on a passed string by setting the changing the frame images 
        @param surrounding QString: consists of 5x5 environment of the beast of the user, parsed column by column to string
        """
        if self.sprint:
            self.background.setStyleSheet("image: url("+self.backgroundSprintPic+");")
        else:
            self.background.setStyleSheet("image: url("+self.backgroundPic+");")
            
        self.moveFrame.setStyleSheet("image: url("+self.cursorPic+");")
        self.clear()
        
        for i in range (25):
            frame= self.frames[i]
            if surrounding[i]=='.' or i==12:
                frame.hide()
                continue
                
            elif surrounding[i]=='*':
                frame.setStyleSheet("image: url("+self.foodPic+");")
               
            elif surrounding[i]=='>':
                frame.setStyleSheet("image: url("+self.bigBeastPic+");")
            
            else:
                frame.setStyleSheet("image: url("+self.smallBeastPic+");")
       
            frame.show()    
   
    def moveTo(self,destination):
        """
        called by gui if a move happens, except the move was executed by keyboard handling
        displays the move in widget by moving the cursor frame which represents the beast to destination position
        @param destination QString: destination of beasts move. Represents the index of column by column string parsed 5x5 environment (0-24) or '?' for hide
        """
        
        if destination not in ('?',12):
            self.moveFrame.move(self.frames[int(destination)].pos())
            
        elif destination=='?':
            self.moveFrame.setStyleSheet("image: url("+self.hidePic+");")
        


if __name__ == '__main__':
        
    app = QtGui.QApplication(sys.argv)
    parent=QtGui.QWidget()
    parent.setFixedSize(535,535)
    parent.show()
    ex=QEnvironment(parent)
#    ex.draw('...><>.=...**.**.>*...>..')
#    ex.moveTo(0)
#    ex.clear()
    sys.exit(app.exec_())

