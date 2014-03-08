#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from subprocess import Popen, PIPE, call
screen = curses.initscr()  #we're not in kansas anymore
curses.noecho()    #could be .echo() if you want to see what you type
curses.curs_set(0)
screen.keypad(1)  #nothing works without this

screen.addstr("m g up down left right pgup pgdn increment c t\r\n")
while True:
  press = screen.getch()
  if press == ord("q"): break  #quit  ord values are important
  elif press == curses.KEY_LEFT:  #this is pretty straightforward
    screen.clear()
    screen.addstr( "left")
  elif press == ord("g"):
    screen.clear()   #otherwise things get messy
    moment = screen.getstr()
    ret = moment.split(" ")
    ret.insert(0,"python")  
    ''' this part is really frustrating.  we should be able to do this with
        "import printr, prntr.main(*args)"  but fucking getstr() doesn't want
        to play nice... when it does we won't have messy .pyc shit and 
        spin-up hangtime'''

    ret.insert(1,"ptr.py")  #send G code here
    ret = call(ret)  #these are all the args in a list
curses.endwin() #there's no place like home