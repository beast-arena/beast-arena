# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 11:06:09 2011
$Id: Visualisation.py 447 2012-01-13 16:36:30Z nkr $
"""
import curses, time

class Visualisation(object):   
    """
    Basic visualisation of the world map, powered by curses.
    """
    def __init__(self, worldMap):
        self.size = worldMap.height
        self.worldMap = worldMap
        curses.initscr()
        self.win = curses.newwin(0, 0)

    def drawScreen(self):
        """
        Updates the screen with the current world map state. This method can be
        called e. g. after every move of a beast or after every game round.
        """
        for j in range(self.size):
            for i in range(self.size):
                self.win.addch(j, i*2, self.worldMap.world[i, j])
        self.win.refresh()
        time.sleep(0.2)

    def close(self):
        """
        Closes the curses window so that the terminal is usable by the user again.
        """
        curses.endwin()
