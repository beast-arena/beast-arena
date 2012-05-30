# -*- coding: utf-8 -*-
"""
$Id: SamysBeast.py 444 2012-01-13 12:53:39Z sze $
"""
import numpy
import random

class SamysBeast(object):
    '''Beast for pyBeasts by Samy'''
    
    def __init__(self):
        self.worldMapStateArray=None
        self.surrounding=''
        self.sprintCounter=0
        self.destinations=[0,None, 2,None, 4,None, 6, 7, 8,None, 10, 11, 12, 13, 14,None, 16, 17, 18, None,
                            20, None,22,None, 24] # +? for rest                      
    
    def setDestinationNull(self, *toRemove):
        '''removes selected destinations'''
        for i in range(len(toRemove)):
            if toRemove[i] in self.destinations:
                self.destinations[self.destinations.index(toRemove[i])]=None

    def checkForFood(self,destination,searched):
        '''checks if a given destination carries food and is close to an equal beast'''
        
        if searched is '=' and destination in (6,7,8,11,13,16,17,18)and self.surrounding[destination] is '*':
            return True
        return False
   
    def loopForRemove(self,coordinates,j,searched):
        '''goes through a given map with coordinates and removes the surrounding destinations''' 
        
        for i in range(6):
                if j!=i:
                    if coordinates[i]!= None:
                        if self.checkForFood(coordinates[i],searched):
                            return coordinates[i]
                        self.setDestinationNull(coordinates[i])
     
    def removeBeastSurroundings(self,searched,i,j,cursor):
        '''set the surrounding destination of bigger and eventually equal beasts to none'''
        
        #maps represent the destinations to remove if j is NOT the key value
        self.setDestinationNull(cursor)
        self.loopForRemove({0:cursor-1,1:cursor-2,2:None,3:cursor+2,4:cursor+1,5:None},j,searched)
        self.loopForRemove({0:cursor-2,1:None,2:None,3:None,4:cursor+2,5:None},j,searched)
        
        #i represents line in surroundingArray
        if i!=0:
            if self.loopForRemove({0:cursor-6,1:None,2:None,3:None,4:cursor-4,5:cursor-5},j,searched)!=None:
                return self.loopForRemove({0:cursor-6,1:None,2:None,3:None,4:cursor-4,5:cursor-5},j,searched)
       
        if  i!=0 and i!=1:
            if self.loopForRemove({0:cursor-12,1:cursor-12,2:None,3:cursor-8,4:cursor-8,5:cursor-10},j,searched)!=None:
                return self.loopForRemove({0:cursor-12,1:cursor-12,2:None,3:cursor-8,4:cursor-8,5:cursor-10},j,searched)
        if i!=4:
            if self.loopForRemove({0:cursor+4,1:None,2:None,3:None,4:cursor+6,5:cursor+5},j,searched)!=None:
                return self.loopForRemove({0:cursor+4,1:None,2:None,3:None,4:cursor+6,5:cursor+5},j,searched)
        if i !=4 and i!=3:
            if self.loopForRemove({0:cursor+8,1:cursor+8,2:None,3:cursor+12,4:cursor+12,5:cursor+10},j,searched)!=None:    
                return self.loopForRemove({0:cursor+8,1:cursor+8,2:None,3:cursor+12,4:cursor+12,5:cursor+10},j,searched)                     
        
    def preventiveInspection(self, searched):
        '''checks if there are any smaller or similar beast or food in the environment of a destination'''   
        toInspect=(10,14,2,22,0,1,3,4,5,9,15,19,20,21,23,24)
        moveTo={1:(7,6),2:(7,6,8),3:(7,8),5:(11,6),9:(13,8),10:(11,6,16),14:(13,8,18),15:(11,16),19:(13,18),21:(17,16),22:(17,16,18),23:(17,18),0:(6,None),4:(8,None),20:(16,None),24:(18,None)}
        
        if searched is '*':

            for i in range (len(toInspect)):
                for j in range(2):
                    if moveTo.get(toInspect[i])[j] in self.destinations and self.surrounding[toInspect[i]] is '*':
                        return moveTo.get(toInspect[i])[j]
        
        else:
            coordinates={0:(0,0),1:(0,1),2:(0,2),3:(0,3),4:(0,4),5:(1,0),9:(1,4),10:(2,0),14:(2,4),15:(3,0),19:(3,4),20:(4,0),21:(4,1),22:(4,2),23:(4,3),24:(4,4)}
            for i in range(len(toInspect)):
                for j in range (2):
                    if self.surrounding[toInspect[i]] is searched and moveTo.get(toInspect[i])[j] in self.destinations:                
                        if searched is '=':
                            tmp=self.removeBeastSurroundings('=',coordinates.get(toInspect[i])[0],coordinates.get(toInspect[i])[1],toInspect[i])
                            if tmp!=None:
                                return tmp
                        else:    
                            return moveTo.get(toInspect[i])[j]
    
    def surroundingInspection(self,searched) :
        '''checks specified destinations for feed and smaller monsters'''
        toInspect=(7,11,13,17,6,8,16,18)

        #checks straight and after diagonal destinations for feed and smaller monsters
        for i in range(8):
            if self.surrounding[toInspect[i]] is searched and toInspect[i] in self.destinations:              
                return toInspect[i]   
        
        if searched!='*': 
            
            #field to inspect is 5x5
            toInspectSprint=(2,10,14,22,0,4,20,24)
            
            for i in range (8):
                #checks sprint straight and after diagonal destinations for feed and smaller monsters
                if self.surrounding[toInspectSprint[i]] is searched and toInspectSprint[i] in self.destinations and self.sprintCounter == 0: 
                    self.sprintCounter=4
                    return toInspectSprint[i]
            
    def bewege(self, paramString):
        params = paramString.split(';', 2)
        if len(params[0]) > 0:
            energy = int(params[0])
        else:
            energy = 0
        environment = params[1]
        
        if environment=='Ende' or environment=='':
            return
        
        return self.bewegen(energy,environment)
        
    def bewegen(self, energy, surrounding):
        '''calculates the best desttination for the beast to move'''        
        
        self.destinations=[0,None, 2,None, 4,None, 6, 7, 8,None, 10, 11, 12, 13, 14,None, 16, 17, 18, None,
                            20, None,22,None, 24]
        self.surrounding=surrounding 
        
       
        #beast isn't allowed to sprint
        if self.sprintCounter!=0 or surrounding == '.'*25: #think about if it makes sense not to sprint if the environment is empty
            self.sprintCounter-=1     
            self.setDestinationNull(0,4,24,20,2,22,10,14)
       
 
        # built an array out of the surrounding string for complex calculation (bigger beasts)
        surroundingArray=numpy.chararray(shape=(5,5)) 
        
        cursor=0
        for i in range(5):
            for j in range(5):
                surroundingArray[i,j]=self.surrounding[cursor]
                cursor+=1
        
        #find bigger beasts and remove the surrounding destinations        
        cursor=0
        for i in range(5): 
            for j in range (5):
                if surroundingArray[i,j] is '>':
                    self.removeBeastSurroundings('>',i,j,cursor)
                cursor+=1
        
        #search for equal beasts to consum in the surrounding 3x3 and after 5x5   
        char= self. surroundingInspection('=')
        if char!=None:
                return char
        
        #search for smaller beasts to consum in the surrounding 3x3 and after 5x5
        char= self. surroundingInspection('<')
        if char!=None:
            return char
        
        #search for hidden beasts to consum in the surrounding 3x3 and after 5x5
        char= self. surroundingInspection('?')
        if char!=None:
            return char        
    
        
        #if there is no beast is located in range 5x5 it doesn't make sence to sprint
        self.setDestinationNull(0,4,24,20,2,22,10,14)
        
#        #searches equal beasts in not reachable destinations and removes the surrounding destinations         
#        char= self.preventiveInspection('=')
#        if char!=None:
#                return char
#        
#        #searches for smaller beasts in not reachable destinations and set a near destination
#        char= self.preventiveInspection('<')     
#        if char!=None:
#                return char
#        
#        #searches for hidden beasts in not reachable destinations and set a near destination
#        char= self.preventiveInspection('?')
#        if char!=None:
#                return char
        #search for food to consum in the surrounding 3x3
        char= self. surroundingInspection('*')
        if char!=None:
            return char          
        
        #search for food in not valueable or not reachable destinations and set a near destination
        char= self.preventiveInspection('*')
        if char!=None:
                return char
      
        #instruction to prefer straight moves if there are possible ones left  
        straight=(7,11,13,17)
        for i in range(4):
            if straight[i] in self.destinations:
                self.setDestinationNull(6,8,16,18)
                break
            
        #write the remaining possible destinations in an array
        remainingDestinations=[]
        for i in range (len(self.destinations)):
            if self.destinations[i]!=None:
                remainingDestinations.append(self.destinations[i])       
        
        
        #beast won't rest if any move is possible except hide
        if len(remainingDestinations) != 1 and 12 in remainingDestinations:
            remainingDestinations.remove(12)    
               
        #select one random destination for move of the remaining possible destination   
        try:
            destination=random.choice(remainingDestinations) 
        except:
            #beast will hide if there is no possible move
            destination='?'
        
        #the destination the beast is going to move to     
        return destination  

def main():
    string='.......>..................'
    
    b = SamysBeast()
    print b.bewegen(30,string,)
    print b.bewegen(50,string,)
    
if __name__=='__main__':
    main()
