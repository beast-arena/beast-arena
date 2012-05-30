# -*- coding: utf-8 -*-
"""
$Id: Observable.py 447 2012-01-13 16:36:30Z nkr $
"""
class Observable(object):
    """
    an observable class has to inherit this class and to call notifyObeservers()
    if the observable class has changed
    """
    
    def __init__(self):
        self.observers = []

    def register(self, observer):
        """
        @param observer: observer which registers to this observable
        """
        if observer not in self.observers:
            self.observers.append(observer)
        
    def notifyObservers(self):
        """
        calls notify of every registered observer
        """
        for observer in self.observers:
            observer.notify()
