# -*- coding: utf-8 -*-
"""
$Id: QWorld.py 492 2012-01-17 11:41:10Z sze $
"""
import sys,os
from PyQt4 import QtGui

basePath = sys.argv[0].split('/')
sys.path.append(os.path.abspath(sys.argv[0]).rpartition('/')[0].rpartition('/')[0])

class QWorld(QtGui.QWidget):
    """
    extended by QtGui.QWidget
    """
    
    def __init__(self,qParent=None):
        """
        constructor
        @qParent: QObject to set as parent 
        """

        QtGui.QWidget.__init__(self,parent=qParent)
     
        self.beastPic='resources/in_game/blue_beast.png'
        self.foodPic='resources/in_game/food.png'
        self.ownBeastPic='resources/in_game/beast.png'
        
        self.setFixedSize(535,535)
        self.frames=[]
        self.pos=[]
        self.beastName=None
        
        background=QtGui.QFrame(self)
        background.setStyleSheet("image: url(resources/in_game/in_game_clean_background);")
        background.setFixedSize(self.width(),self.height())
        self.hide()
        
    def initiate(self,worldSize,beastName):
        """
        initiates the frame size depending on the passed world size 
        """
        
        self.beastName=beastName
    
        x=worldSize[0]
        y=worldSize[1]
        
        xSpacing=float(self.width())/x
        ySpacing=float(self.height())/y

                
        for i in range (y):
            for j in range (x):
                self.pos.append((j*xSpacing,i*ySpacing,))

        
        for i in range(x*y):
            frame=QtGui.QFrame(self)
            frame.setFixedSize(xSpacing,ySpacing)
            frame.move(self.pos[i][0],self.pos[i][1])
            frame.show()
            self.frames.append(frame)
    
        self.setWindowTitle('World')
        self.move(21,21)
        self.show()
    
    def clear(self):
        """
        clears the world by hiding every frame
        """
        for frame in self.frames:
            frame.hide()
    
    def draw(self,worldString):
        """
        displays the world before ten rounds based on a passed string by setting the changing the frame images 
        @param worldString QString: consists of the world, parsed column by column to string
        """
        for i in range (len(worldString)):
            frame=self.frames[i]
            if worldString[i]=='.':
                frame.hide()
                continue
            elif worldString[i]=='*':
                frame.setStyleSheet("image: url("+self.foodPic+");")
            elif worldString[i]==self.beastName:
                frame.setStyleSheet("image: url("+self.ownBeastPic+");")
            else:
                frame.setStyleSheet("image: url("+self.beastPic+");")
            frame.show()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex=QWorld()
    ex.initiate((12,12),'a')
    string='.'*12+'*'*12
    ex.drawWorld(string)
 
#    ex.moveTo(0)

    sys.exit(app.exec_())



if __name__ == '__main__':
    main()


