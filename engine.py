#!/usr/bin/env python
# -*- coding: utf-8 -*-

#set up globally scoped variables for telemetry 
move_adder = {'x': 0.0, 'y': 0.0, 'z': 0.0}
present_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
tools = {ord('e') : {'name':'extruder'}, ord('c') : {'name':'cam'}, ord('p') : {'name':'paste'}}
for i in tools:
  for g in {'x','y','z'}:
    tools[i][g] = 0.0

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
tool_mode = ord('c')

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

  elif press in tools:  # if any tool is selected
    screen.clear()
    printInfo( "mode = {0}".format(tools[press]['name']))
    if tool_mode != press:
      for i in {'x','y','z'}:
        move_adder[i] = tools[press][i] - tools[tool_mode][i]
      tool_mode = press
      ptr.cmnd("G1 X{0} Y{1} Z{2}".format(move_adder['x'],move_adder['y'],move_adder['z'])) #ptr.cmnd

  elif (press + 32) in tools:  # capital letter version of a tool key
    press += 32 # change it to lowercase version
    tool_mode = press
    screen.clear()   
    printInfo( "{0} home".format(tools[press]['name']))
    for i in {'x','y','z'}:
      tools[press][i] = present_position[i]

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
