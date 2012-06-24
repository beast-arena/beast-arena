# -*- coding: utf-8 -*-

import socket, time, select, logging
from SocketCommunication import read, write

class RemoteBeast(object):
    """
    Remote Beast class.
    """
    def __init__(self, socket, server):
        self.socket = socket
        self.server = server
        self.log = logging.getLogger('beast-arena-logging')

    def bewege(self, paramString):
        """
        forwards the paramString to the client
        @param paramString string from server
        @return destination by the client's beast calculated destination
        """
        try:
            if self.socket is None:
                return ''
            write(self.socket, paramString)
            params = paramString.split(';', 2)
            energy = params[0]
            environment = params[1]
            try:
                intEnergy = int(energy)
            except ValueError:
                intEnergy = 0
            if len(energy) > 0 and intEnergy > 0 and environment != 'Ende':
                timeoutTime = time.time() + 5 # 5 s timeout
                while time.time() < timeoutTime:
                    time.sleep(0.1)
                    inputReady, outputReady, exceptionReady = select.select([self.socket], [], [], 0)
                    for sendingClient in inputReady:
                        answer = read(sendingClient)
                        if answer == '?':
                            return answer
                        try:
                            if int(answer) in range(25):
                                return answer
                        except ValueError: # parsing to int
                            pass
                        if len(answer) > 0:
                            write(self.socket, self.server.processClientCommunication(socket, answer))
            return '' # if we haven't received a move after 5 s, return empty string
        except socket.error as e:
            self.log.warning(str(e) + ',socket.error: closing socket')
            self.socket.close()
            self.socket = None
        except AttributeError as e: # catch AttributeError: 'NoneType' object has no attribute 'write'
            self.log.warning(str(e) + ',AttributeError: closing socket')
            self.socket.close()
            self.socket = None

