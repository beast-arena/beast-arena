# -*- coding: utf-8 -*-
"""
$Id: Observer.py 447 2012-01-13 16:36:30Z nkr $
"""
class Observer(object):
    """
    an observer class has to inherit this class and reimplement notify()
    """
        
    def notify(self):
        """
        this method is called by an Obesrvable every time the observable changes
        """
        pass
