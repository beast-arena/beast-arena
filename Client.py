# -*- coding: utf-8 -*-
"""
$Id: Client.py 497 2012-01-17 22:25:21Z mli $
"""
import ssl,time
from SocketCommunication import read, write
from socket import socket
from SamysBeast import SamysBeast
from NikolaisBeast import NikolaisBeast
from Team8Beast import Team8Beast
import sys,select

class Client():
    """
    @class Client
    """

    def __init__(self):
        """
        creating ssl connection to given host and port
        you also have to spezifiy the server certificate
        """
        
#        if len(sys.argv) < 3:
#            print 'usage: Client.py <host> <team number>'
#            sys.exit()
        host = 'localhost'
        team = '8'

        print 'Host:', host, ', Team:', team

        self.hostPort = (host, 10000 + int(team))
        self.serverCert = 'clientGui/certs/team' + team + '.crt'
        self.beast = Team8Beast()
        self.worldSize = None
        self.connection = None
    
    def connectToServer(self):
        """
        trys to connect to server with given arguments
        @return: returns connection status
        """
        
        try:
            self.connection = ssl.wrap_socket(socket(), cert_reqs=ssl.CERT_REQUIRED,
                            ssl_version=ssl.PROTOCOL_SSLv3, ca_certs=self.serverCert)
            self.connection.connect(self.hostPort)
            return True
        except Exception as e:
            print 'Connection failed.'
            print e
            return False          
    
    def registration(self):
        """
        default activity with requests and responses between client and server
        after sending 'Anmeldung!' and receiving an char the client is 
        registered and the listening-loop will be started
        """
        
        if not self.connectToServer():
            return
        
        request = 'Spielbeginn?'
        write(self.connection, request)
        response = read(self.connection)
        print 'cur time:', time.asctime()
        print 'response:', response
        
        write(self.connection, 'Anmeldung moeglich?')
        if read(self.connection) == 'Ja':
            print 'Anmeldung moeglich? Ja' 
            write(self.connection,'startdelay?')
            
            gamestart=float(read(self.connection))-0.5
            print "please enter your prefered name, you have ",int(gamestart)," seconds to answer!"
            
            try:
                i,o, e = select.select([sys.stdin], [], [], gamestart)
                if (i):
                    write(self.connection, 'Anmeldung!' + sys.stdin.readline().strip()) 
                else:
                    write(self.connection, 'Anmeldung!')  
            except Exception:
                print 'Anmeldung gescheitert' 
                
                
            response = read(self.connection)
            print 'Assigned Beast name:', response
            print 'Waiting for bewege() requests...'

        else:
            print 'Anmeldung gescheitert'
            return
        time.sleep(0.5)
        self.listening()
    

   
    def listening(self):

        """
        loop in which the client waits for the servers bewegeString and answers
        with his calculated destination
        after we get 'Ende' the ssl connection will be closed
        """
        
        while True:
            try:
                bewegeString = read(self.connection)
                if self.worldSize == None:
                    write(self.connection, 'Weltgroesse?')
                    self.worldSize = read(self.connection)
                    print 'world size:', self.worldSize
                print 'bewegeString=' + bewegeString #string which is given by the server
                if 'Ende' in bewegeString:
                    break
                #sending our calculated destination
                destination = str(self.beast.bewege(bewegeString))
                if len(destination) > 0 and destination != 'None':
                    print 'sent=' + destination
                    write(self.connection, destination)
            except Exception as e:
                print time.asctime(), e.args, ': lost connection to Server'
                break
        self.connection.close()
        

if __name__ == '__main__':
    client = Client()
    client.registration()

