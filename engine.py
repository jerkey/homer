#!/usr/bin/env python
# -*- coding: utf-8 -*-

#set up globally scoped variables for telemetry 
tool_home = {'x': 0.0, 'y': 0.0, 'z': 0.0}
cam_home = {'x': 0.0, 'y': 0.0, 'z': 0.0}
present_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
#these two dictionaries will store the arithmetic from each movement

import curses
import ptr as p
from subprocess import Popen, PIPE, call
screen = curses.initscr()  #we're not in kansas anymore
curses.noecho()    #could be .echo() if you want to see what you type
curses.curs_set(0)
screen.keypad(1)  #nothing works without this
screen.addstr("m g up down left right pgup pgdn increment c t\n")
ptr=p.prntr()
increment = 1.0

def printInfo(text):
    screen.addstr( str(text)+" %.3f, %.3f, %.3f" % (present_position['x'],present_position['y'],present_position['z'])) # left %.3f, %.3f, %.3f

while True:

  press = screen.getch()
  if press == ord("q"): break  #quit  ord values are important
  elif press == curses.KEY_LEFT:  #this is pretty straightforward
    screen.clear()
    ptr.xm(increment)  #x axis minus
    present_position['x']-=increment  #this needs to be modular for scalar
    printInfo( "left ")
  elif press == curses.KEY_RIGHT: 
    screen.clear()
    ptr.xp(increment)  #x axis plus
    present_position['x']+=increment  #this needs to be modular for scalar
    printInfo( "right")
  elif press == curses.KEY_UP:
    screen.clear()
    present_position['y']+=increment #this needs to be modular for scalar
    ptr.yp(increment)
    printInfo( "forth")
  elif press == curses.KEY_DOWN:  
    screen.clear()
    ptr.ym(increment)
    present_position['y']-=increment  #this needs to be modular for scalar
    printInfo( "back ")
  elif press == curses.KEY_PPAGE:  # pageup
    screen.clear()
    ptr.zp(increment)
    present_position['z']+=increment #this needs to be modular for scalar
    printInfo( "up   ")
  elif press == curses.KEY_NPAGE:  # pagedown
    screen.clear()
    ptr.zm(increment)
    present_position['z']-=increment  #this needs to be modular for scalar
    printInfo( "down ")


  #these methods provide telemetry, orientation data for the user

  elif press == ord("t"):
    #these functions need a vector to track
    screen.clear()   
    printInfo( "toolhead home")
    for i in tool_home:
      tool_home[i] = present_position[i]
  elif press == ord("c"):
    #these functions need a vector to track
    screen.clear()   
    printInfo( "camera home")
    for i in cam_home:
      cam_home[i] = present_position[i]
  elif press == ord("h"):
    screen.clear()   
    screen.addstr("actually home machine XY")
    ptr.hx()
    ptr.hy()
    present_position['x'] = 240
    present_position['y'] = 0
  
  #these methods  allow the user to send raw g code to the printer

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
  elif press == ord("4"):
    increment = 10.0


curses.endwin() #there's no place like home
