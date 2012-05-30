# -*- coding: utf-8 -*-
"""
$Id: LoggingHandler.py 467 2012-01-16 10:34:40Z mli $
"""
import logging

class UrwidLoggingHandler(logging.Handler):
    """
    logging handler which logs messages to urwid
    """
    def __init__(self, urwid):
        """
        logging.Handler constructor call and custom urwid actions
        """
        logging.Handler.__init__(self)
        self.urwid = urwid

    def emit(self, record):
        """
        delegate message output to urwid
        """
        self.urwid.log(record.getMessage())

class GuiLoggingHandler(logging.Handler):
    """
    logging handler which logs messages to the gui
    """
    def __init__(self, gui):
        """
        logging.Handler constructor call and custom gui actions
        """
        logging.Handler.__init__(self)
        self.gui = gui

    def emit(self, record):
        """
        here should the gui slot be targeted to display messages!
        """
        print record
