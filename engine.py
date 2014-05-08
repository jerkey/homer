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
screen.addstr("m g forward backward left right pgup pgdn 0=0.025mm 1=0.1mm 2=1mm 3=10mm\ntools: ")
for i in tools:
  screen.addstr("{0}={1}  ".format(chr(i),tools[i]['name']))
screen.addstr(" (capital to home tool)\nPress s# to seek to a position, capital S# to store in #0-9\n")
ptr=p.prntr()
increment = 1.0
tool_mode = ord('c') # you better have a valid tool in here to start with

def printInfo(text):
    # curpos = curses.getsyx()
    screen.addstr(4,0,"mode = {0}".format(tools[tool_mode]['name'])+"       ")
    screen.addstr(5,0,"absolute position: %.3f, %.3f, %.3f                     \n" % (present_position['x'],present_position['y'],present_position['z'])+str(text)+"\n")

while True:

  press = screen.getch()
  if press == ord("q"): break  #quit  ord values are important
  elif press == curses.KEY_LEFT:  #this is pretty straightforward
    ptr.xm(increment)  #x axis minus
    present_position['x']-=increment  #this needs to be modular for scalar
    printInfo( "left ")
  elif press == curses.KEY_RIGHT: 
    ptr.xp(increment)  #x axis plus
    present_position['x']+=increment  #this needs to be modular for scalar
    printInfo( "right")
  elif press == curses.KEY_UP:
    present_position['y']+=increment #this needs to be modular for scalar
    ptr.yp(increment)
    printInfo( "forth")
  elif press == curses.KEY_DOWN:  
    ptr.ym(increment)
    present_position['y']-=increment  #this needs to be modular for scalar
    printInfo( "back ")
  elif press == curses.KEY_PPAGE:  # pageup
    ptr.zp(increment)
    present_position['z']+=increment #this needs to be modular for scalar
    printInfo( "up   ")
  elif press == curses.KEY_NPAGE:  # pagedown
    ptr.zm(increment)
    present_position['z']-=increment  #this needs to be modular for scalar
    printInfo( "down ")

  elif press in tools:  # if any tool is selected
    if tool_mode != press:
      for i in {'x','y','z'}:
        move_adder[i] = tools[press][i] - tools[tool_mode][i]
      tool_mode = press
      screen.addstr(4,0,"mode = {0}".format(tools[tool_mode]['name'])+"       ")
      screen.addstr(5,0,"moving machine to other toolhead                     ")
      ptr.cmnd("G1 X{0} Y{1} Z{2}".format(move_adder['x'],move_adder['y'],move_adder['z'])) #ptr.cmnd
    printInfo( "mode = {0}".format(tools[press]['name']))

  elif (press + 32) in tools:  # capital letter version of a tool key
    press += 32 # change it to lowercase version
    tool_mode = press
    printInfo( "{0} home".format(tools[press]['name']))
    for i in {'x','y','z'}:
      tools[press][i] = present_position[i]

  elif press == ord("h"):
    present_position['x'] = 240
    present_position['y'] = 0
    printInfo( "actually home machine XY")
    ptr.hx()
    ptr.hy()
  
  #these methods  allow the user to send raw g code to the printer

  elif press == ord("g"):
    moment = screen.getstr()
    screen.addstr(moment)
    ptr.cmnd("G {0}".format(moment))
  
  elif press == ord("m"):
    moment = screen.getstr()
    screen.addstr(moment)
    ptr.cmnd("M {0}".format(moment))

  elif press == ord("1"):
    increment = 0.025
  elif press == ord("2"):
    increment = 0.1
  elif press == ord("3"):
    increment = 1.0
  elif press == ord("4"):
    increment = 10.0

curses.endwin() #there's no place like home
