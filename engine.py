#!/usr/bin/env python
# -*- coding: utf-8 -*-

#set up globally scoped variables for telemetry 
tool_home = {'x': 0.0, 'y': 0.0, 'z': 0.0}
cam_home = {'x': 0.0, 'y': 0.0, 'z': 0.0}
#these two dictionaries will store the arithmetic from each movement

import curses
import need
from subprocess import Popen, PIPE, call
screen = curses.initscr()  #we're not in kansas anymore
curses.noecho()    #could be .echo() if you want to see what you type
curses.curs_set(0)
screen.keypad(1)  #nothing works without this

screen.addstr("m g up down left right pgup pgdn increment c t\n")
while True:

  
  press = screen.getch()
  if press == ord("q"): break  #quit  ord values are important
  

""" these methods are for moving the tool head around
they still need a scalar variable implementation"""


  elif press == curses.KEY_LEFT:  #this is pretty straightforward
    screen.clear()
    screen.addstr( "left")
    ptr.xp(increment)  #x axis plus
    cam_home['x']+=increment
    tool_home['x']+=increment  #this needs to be modular for scalar
  elif press == curses.KEY_RIGHT: 
    screen.clear()
    screen.addstr( "right")
    ptr.xm(increment)  #x axis minus
    cam_home['x']-=increment
    tool_home['x']-=increment  #this needs to be modular for scalar
  elif press == curses.KEY_UP:
    screen.clear()
    screen.addstr( "up")
    cam_home['y']+=increment
    tool_home['y']+=increment #this needs to be modular for scalar
    ptr.yp(increment)
  elif press == curses.KEY_DOWN:  
    screen.clear()
    screen.addstr( "down")
    ptr.ym(increment)
    cam_home['y']-=increment
    tool_home['y']-=increment  #this needs to be modular for scalar

  elif press == curses.KEY_PPAGE:  
    screen.clear()
    screen.addstr( "pgup")
    ptr.zp(increment)
    cam_home['z']+=increment
    tool_home['z']+=increment #this needs to be modular for scalar

  elif press == curses.KEY_NPAGE: 
    screen.clear()
    screen.addstr( "pgdn")
    ptr.zm(increment)
    cam_home['z']-=increment
    tool_home['z']-=increment  #this needs to be modular for scalar


"""these methods provide telemetry, orientation data for the user"""

  elif press == ord("t"):
    #these functions need a vector to track
    screen.clear()   
    screen.addstr("toolhead home")
    for i in tool_home:
      tool_home[i] = 0  #make this the starting point
  elif press == ord("c"):
    #these functions need a vector to track
    screen.clear()   
    screen.addstr("camera home")
    for i in cam_home:
      cam_home[i] = 0  #make this the starting point
  
"""these methods  allow the user to send raw g code to the printer"""

  elif press == ord("g"):
    screen.clear()   #otherwise things get messy
    moment = screen.getstr()
    screen.addstr(moment)
    ptr.cmnd("G {0}".format(moment))
  
  elif press == ord("m"):
    screen.clear()   #otherwise things get messy
    moment = screen.getstr()
    screen.addstr(moment)
    ptr.cmnd("M {0}".format(moment))

  elif press == ord("1"):
    increment = 0.01
  elif press == ord("2"):
    increment = 0.1
  elif press == ord("3"):
  increment = 1.0


curses.endwin() #there's no place like home
