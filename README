beast-arena
===========

beast-arena is a distributed simulation in which artifical creatures ("beasts") act in a two-dimensional world. The beasts act in a world of a specified size of N*N fields however for them it seems to be infinitely due to wrap-around.


Prerequisites
=============

To run beast-arena, the following programs and libraries are required:
- Python (tested with version 2.7.3)
- NumPy (e.g. 'apt-get install python-numpy' or http://www.scipy.org/Download)


Components
==========

beast-arena.py: main application which includes (optional) visualisation of the simulation and a socket server for allowing network clients to participate in games
Client.py: simple console based client which connects to a server via SSL over TCP and participates with a specified beast type
clientGui/ClientGui.py: graphical client based on Qt


Configure beast-arena
=====================

Open beast-arena.conf with your favourite editor.
The most important options are:

useNetworking: if set to True, socket server allows connections from clients to participate in games. If set to False, simulation will be done locally only
useUrwidVisualisation: if set to True, simulation will be displayed graphically on the terminal using urwid, a text user interface library (similar to ncurses, included in urwid/)


Run beast-arena
===============

$ python beast-arena.py

then, optionally:
$ python Client.py
or
$ cd clientGui/; python ClientGui.py


Bugs & Questions?
=================

contact info@beast-arena.de

