# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 16:14:07 2011
$Id: Config.py 510 2012-05-17 22:43:51Z mli $
"""
import ConfigParser

class Config(object):
    """ class for reading information from beast-arena.conf file """
    config = ConfigParser.SafeConfigParser()
    try:
        config.read('beast-arena.conf')
    except ConfigParser.ParsingError, err:
        print 'Could not parse:', err

    def __init__(self):
        """
        instantiation of Config.py is not possible
        """
        errorMessage = 'Instantiation of ' + type(self).__name__ \
            + ' is not possible'
        raise TypeError, errorMessage

    @staticmethod
    def __getStartEnergy__():
        '''@return the value of startEnergy in config file'''
        return int(Config.config.get('global', 'startEnergy'))

    @staticmethod
    def __getStartFoodItemsPerBeast__():
        '''@return the value of startFoodItems in config file'''
        return int(Config.config.get('global', 'startFoodItemsPerBeast'))

    @staticmethod
    def __getFieldFactor__():
        '''@return the value of fieldFactor in config file'''
        return float(Config.config.get('global', 'fieldFactor'))

    @staticmethod
    def __getMaxRounds__():
        '''@return the value of startEnergy in config file'''
        return int(Config.config.get('global', 'maxRounds'))

    @staticmethod
    def __getStartInSeconds__():
        '''@return the value of startInSeconds in config file'''
        return int(Config.config.get('global', 'startInSeconds'))

    @staticmethod
    def __getMovingCosts__(destination):
        '''@return the value of moving cost depending on the destination from
        config file
        @param destination int: destination from beast to get energy costs'''
        if destination in (7, 11, 13, 17):
            return int(Config.config.get('movingCosts', 'straight'))
        elif destination in (6, 8, 16, 18):
            return int(Config.config.get('movingCosts', 'diagonal'))
        elif destination in (2, 10, 14, 22):
            return int(Config.config.get('movingCosts', 'sprintStraight'))
        elif destination in (0, 4, 20, 24):
            return int(Config.config.get('movingCosts', 'sprintDiagonal'))
        elif destination == '?':
            return int(Config.config.get('movingCosts', 'hide'))
        else: # also covers '12'
            return int(Config.config.get('movingCosts', 'rest'))
    @staticmethod
    def __getFileLoggingLevel__():
        return int(Config.config.get('system', 'FileLoggingLevel'))
    
    @staticmethod
    def __getInterfaceLoggingLevel__():
        return int(Config.config.get('system', 'interfaceLoggingLevel'))
    
    @staticmethod
    def __getUseUrwidVisualisation__():
        return True if Config.config.get('system', 'useUrwidVisualisation')== 'True' else False
    
    @staticmethod
    def __getUseNetworking__():
        return True if Config.config.get('networking', 'useNetworking')=='True' else False

    @staticmethod
    def __getUseBeastAnalytics__():
        return True if Config.config.get('system', 'useBeastAnalytics')== 'True' else False
   
    @staticmethod
    def __getPort__():
        return int(Config.config.get('networking', 'port'))
    
    @staticmethod
    def __getSSLKey__():
        return Config.config.get('networking', 'sslkey')
    
    @staticmethod
    def __getUseFileLogging__():
        return True if Config.config.get('system', 'useFileLogging')=='True' else False
    
    @staticmethod
    def __getMinimumBeasts__():
        return int(Config.config.get('system', 'minimumBeasts'))
    
    @staticmethod
    def __getUrwidRoundDelay__():
        return int(Config.config.get('system', 'urwidRoundDelay'))
    
    @staticmethod
    def __getConnectionLimitPerClient__():
        return int(Config.config.get('networking', 'connectionLimitPerClient'))
    
