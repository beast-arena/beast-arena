# -*- coding: utf-8 -*-

"""
This module supports in writing and reading data from sockets.
"""

def write(socket, data):
    """
    Append trailing '@' to data and write this string to socket.
    @param socket socket where data string will be sent to
    @param data string to be sent to socket
    """
    if socket is not None:
        try:
            socket.write(data + '@')        
        except Exception:
            raise # re-rase Exception that it can be handled by Server or Client
    

def read(socket):
    """
    Read from socket until the "EndOfTransmission" signal ('@') is received and
    then return the received string without trailing '@'.
    @param socket socket from which is read
    @return received data without trailing '@'
    """
    data = ''
    while socket is not None:
        try:
            data += socket.read()
        except Exception:
            raise # re-rase Exception that it can be handled by Server or Client
        if len(data) == 0:
            break
        if data[len(data)-1] == '@':
            data = data.rstrip('@')
            break
    return data
