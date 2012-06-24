# -*- coding: utf-8 -*-

import string

class GameWinners(object):
    """
    holds the winner of every game
    """
    def __init__(self):
        self.winnerMap = {}
        
    def addWinner(self, rankingList, totalGames):
        """
        @param rankingList: ranking list which is given by Game.py
        @param totalGames: total games played
        @return: returns if their was no winner
        """
        try:
            tmp = str(type(rankingList[0].beast))
            winner = string.rsplit(string.rsplit(tmp,'.')[1],"'")[0]
        except Exception:
            return
    
        if winner not in self.winnerMap.keys():
            self.winnerMap[winner] = 1
        else:
            self.winnerMap[winner] += 1      
        self.winnerMap['totalGames'] = totalGames
        self.writeWinnersInFile()
            
    def writeWinnersInFile(self):
        """
        writes winners into file
        @return: returns if file is not writeable
        """
        try:
            f = open('log/Winners.txt', 'w')
        except Exception:
            return
        
        for item in self.winnerMap.items():
            s = str(item[0]) + ': ' + str(item[1]) + '\n'
            f.write(s)

