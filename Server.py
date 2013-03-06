# -*- coding: utf-8 -*-

from Config import Config
from RemoteBeast import RemoteBeast
from SocketCommunication import read, write
import socket, ssl, select, threading, sys, logging, time

class Server(threading.Thread):
    """
    @class Server
    this Server handles the connections to several clients, answers requests,
    sends the bewegeString to every client and waits for his response.
    """
    
    def __init__(self, app):
        self.game = app
        self.clientMap = {}
        # Map with key (client addr) and value (count of established connections)
        self.clientIpCountMap = {}
        self.connectionLimitPerClient = Config.__getConnectionLimitPerClient__()
        threading.Thread.__init__(self)
        self.daemon = True
        self.log = logging.getLogger('beast-arena-logger')
        self.running = False
        self.bindsocket = socket.socket()
        
        if self.game is not None:
            self.game.server = self
        
    def run(self):
        self.running=True
        try:
            self.log.info('Starting server on port ' + str(Config.__getPort__()) + '...')
            self.bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.bindsocket.bind(('', Config.__getPort__()))
            self.bindsocket.listen(5)
            self.bindsocket.settimeout(0.1)
    
            while self.running:
                # initialize 
                self.closeConnections()
                self.clientMap = {}
                self.clientIpCountMap = {}
                while self.running and not self.game.gameFinished:
                    try: # prevent exception if no client wants to connect
                        newsocket, fromaddr = self.bindsocket.accept()
                        newsocket.settimeout(0.1)
                        if (Config.__getSSL__()):
                        	client = ssl.wrap_socket(newsocket, server_side=True, certfile="ssl/server.crt",
                                        keyfile="ssl/server.key", ssl_version=ssl.PROTOCOL_SSLv3)
                        else:
                        	client = newsocket
                        self.clientMap[client] = fromaddr, None
                        self.log.info('client ' + str(self.clientMap[client]) + ' has connected')
                    except KeyboardInterrupt:
                        self.log.info('\nCtrl-C was pressed, stopping server...')
                        self.bindsocket.close()
                        self.log.info('Server stopped.')
                        sys.exit()
                    except socket.timeout:
                        pass
                    except socket.error as e:
                        # Spits out tons of exceptions
                        self.log.info(str(e.errno) + str(e))
                    
                    inputReady, outputReady, exceptionReady = select.select(self.clientMap.keys(), [], [], 0)
                    for client in inputReady: # go through all clients which sent a request
                        clientip = None #Overwritten by local variables?? TODO: check! -> see line 86
                        #try:                        
                        request = read(client)
                        #except Exception as e:
                        #    print e
                        response = self.processClientCommunication(client, request)
                        self.log.info('current clients: ' + str(self.clientMap))
                        self.log.info('current IP-Connections: ' + str(self.clientIpCountMap))
                        
                        try: # prevent exceptions if client has disconnected
                            write(client, response)
                        except:
                            self.log.info('client ' + str(self.clientMap[client]) + ' has gone')
                            self.clientMap.pop(client)
                            self.decreaseClientIpConnections(clientip)
                            
                    for client in exceptionReady and self.running:
                        self.log.info('assumed shutdown() -> exception occurred with client: ', str(self.clientMap[client]))
                        if self.clientMap.has_key(client):
                            client.shutdown(socket.RDWR)
                            client.close()
                            self.clientMap.pop(client)
                            self.decreaseClientIpConnections(clientip)
                time.sleep(0.01)

        finally:
            self.closeConnections()
            self.bindsocket.close()

    def processClientCommunication(self, client, request):
        '''
        Generate response-string depending on client's request.
        @return response String
        '''
        if request == 'Anmeldung moeglich?':
            if self.game.gameSignOnPossible():
                response = 'Ja'
            else:
                response = 'Nein'
        elif request == 'Anmeldung!':
            if self.game.gameSignOnPossible() and self.clientMap[client][1] == None:
                clientip, port = client.getpeername()
                if self.clientIpCountMap.has_key(clientip):
                    #TODO: @JKA move check if client is valid up to line 50,
                    #to not even let the client get into our clientmap if connectionLimit is reached
                    #currently in line 87 an exception is thrown as nonexisting sockets gets closed (or not)
                    if self.clientIpCountMap[clientip] < self.connectionLimitPerClient:
                        self.clientIpCountMap[clientip] = self.clientIpCountMap[clientip] + 1
                        response = self.registerClient(client, clientip)
                    else:
                        response = 'Fehler'
                else:
                    self.clientIpCountMap[clientip] = 1
                    response = self.registerClient(client, clientip)
            else:
                response = 'Fehler'
        elif request == 'Weltgroesse?':
            if self.game.gameStarted:
                return self.game.worldMap.getSize()
            else:
                return 'Fehler'
        elif request == 'Spielbeginn?':
            response = self.game.startTime
        elif request=='startdelay?':
            response=self.game.getStartInSeconds()
        else:
            response = 'Fehler'
        return response
    
    def registerClient(self, client, clientip):
        """
        registers the clients beast if possible
        @param client connection to one client which wants to register his beast
        @param clientip
        @return beastname returns the beasts name if registration was possible
        """
        beastName = self.game.registerBeast(RemoteBeast(client, self))
        self.clientMap[client] = self.clientMap[client][0], beastName
        return beastName

    def prepareGameStart(self):
        """
        Remove all registered clients (which have a beast name) from clientMap.
        This prevents that processClientCommunication() interfers with 
        RemoteBeast.bewege()'s socket communiations during the game. 
        """
        registeredClients = []
        for client in self.clientMap:
            if self.clientMap[client][1] is not None:
                registeredClients.append(client)
        for client in registeredClients:
            self.clientMap.pop(client)

    def decreaseClientIpConnections(self, clientip):
        if self.clientIpCountMap.has_key(clientip):
            if self.clientIpCountMap[clientip] <= 1:
                self.clientIpCountMap.pop(clientip)
                self.log.info('Removed ClientIP from clientIpCountMap: ' + str(clientip))
            else:
                self.clientIpCountMap[clientip] -= 1
                self.log.info('Decreased connection count by one for ip: ' + str(clientip) + ' Remaining open Connections: ' + self.clientIpCountMap[clientip])      
                
    def stop(self):
        """
        stops server thread
        """
        self.running = False
        
    def closeConnections(self):
        """
        trys to close all connections to clients and logs if a fail occurred
        """
        try:
            for client in self.clientMap:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
        except Exception as e:
            self.log.info('Error occured while trying to close connections: ' + str(e))

