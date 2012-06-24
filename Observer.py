# -*- coding: utf-8 -*-

class Observer(object):
    """
    an observer class has to inherit this class and reimplement notify()
    """
        
    def notify(self):
        """
        this method is called by an observable every time the observable changes
        """
        pass

