#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
  elif press == curses.KEY_LEFT:  #this is pretty straightforward
    screen.clear()
    screen.addstr( "left")
  elif press == curses.KEY_PPAGE:  #this is pretty straightforward
    screen.clear()
    screen.addstr( "pgup")
  elif press == curses.KEY_NPAGE:  #this is pretty straightforward
    screen.clear()
    screen.addstr( "pgdn")
  elif press == curses.KEY_RIGHT:  #this is pretty straightforward
    screen.clear()
    screen.addstr( "right")
  elif press == ord("g"):
    screen.clear()   #otherwise things get messy
    moment = screen.getstr()
    #ret = moment.split(" ")
    #nret = "".join(ret)
    screen.addstr(moment)
    #screen.refresh()
    need.main(moment)
curses.endwin() #there's no place like home
