#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import ptr as p
import os,datetime,time
from subprocess import Popen, PIPE, call

#set up globally scoped variables for telemetry
move_adder = {'x': 0.0, 'y': 0.0, 'z': 0.0}
present_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
commands = { 0 : {'key':'v','descr':'M106 turn fan on'},
             1 : {'key':'V','descr':'M107 turn fan off'},
             2 : {'key':'Q','descr':'Quit without saving'},
             3 : {'key':'q','descr':'quit (and save)'},
             4 : {'key':'h','descr':'home X and Y axes'},
             5 : {'key':'H','descr':'set present Z height to zero'},
             6 : {'key':'s','descr':'seek to # position'},
             7 : {'key':'S','descr':'Store present position to seek #'},
             8 : {'key':'g','descr':'send G-code to machine'},
             9 : {'key':'m','descr':'send M-code to machine'},
            10 : {'key':'1','descr':'set movement increment to 0.25'},
            11 : {'key':'2','descr':'set movement increment to 0.1'},
            12 : {'key':'3','descr':'set movement increment to 1.0'},
            13 : {'key':'4','descr':'set movement increment to 10.0'},
            14 : {'key':'W','descr':'Write save file'},
            15 : {'key':'R','descr':'Read save file'}}
tools = {ord('e') : {'name':'extruder'}, ord('c') : {'name':'cam'}, ord('p') : {'name':'paste'}}
for i in tools:
  for g in {'x','y','z'}:
    tools[i][g] = 0.0
seek_positions = { n : {'name': '', 'x': 0.0, 'y': 0.0, 'z': 0.0} for n in range(10)} # create empty array

datafilename = 'data.engine'

def saveData(): # store the tools dictionary to a file, after renaming old one to datetime
  errText = ""
  try:
    os.rename(datafilename,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+".dat")
  except OSError:
    errText = "old "+datafilename+" missing. "
  printInfo(errText+"writing tools to "+datafilename)
  with open(datafilename,'w') as dataFile:
    for i in tools:
      dataFile.write(chr(i)) # write the letter of the tool
      for g in ['name','x','y','z']:
        dataFile.write(",{0}".format(tools[i][g]))
      dataFile.write("\n")
    for i in seek_positions:
      dataFile.write(chr(i+48)) # write the 0-9 numeral of the seek position
      for g in ['name','x','y','z']:
        dataFile.write(",{0}".format(seek_positions[i][g]))
      dataFile.write("\n")
    dataFile.write("~,"+chr(tool_mode)) # tilde means present_position, comma so there are five datas
    for g in ['x','y','z']:
      dataFile.write(",{0}".format(present_position[g]))
    dataFile.write("\n")
    dataFile.close()

def readData(): # store the tools dictionary to a file, after renaming old one to datetime
  global tool_mode # we are going to modify a global variable that isn't a dictionary
  try:
    printInfo("reading tools dictionary from "+datafilename)
    with open(datafilename,'r') as dataFile:
      for line in dataFile:
        datas = line.rstrip().split(',') # parse each line for datas
        if len(datas) == 5:
          dindex = 1 # for indexing elements of datas
          for g in ['name','x','y','z']:
            if ord(datas[0]) in tools:
              if g == 'name': tools[ord(datas[0])][g] = datas[dindex]
              else: tools[ord(datas[0])][g] = float(datas[dindex])
            if (ord(datas[0])-48) in seek_positions:
              if g == 'name': seek_positions[ord(datas[0])-48][g] = datas[dindex]
              else: seek_positions[ord(datas[0])-48][g] = float(datas[dindex])
            if (datas[0] == '~'):
              if dindex == 1: # this is where we store tool_mode
                tool_mode = ord(datas[1])
              else:
                present_position[g] = float(datas[dindex])
            dindex += 1
      dataFile.close()
  except IOError:
    printInfo("couldn't open "+datafilename)

def printFile(filename, ptr):
  try:
    fd = open(filename,'r')
  except OSError:
    printInfo("error: could not open "+filename)
    return
  line = fd.readline()
  for line in fd:
    line = line.rstrip().split(';')[0]
    if len(line) > 1:
      ptr.cmnd(line)
      screen.addstr(line+"\n")
      now = time.time()
      ok = ptr.read1line()
      while not 'ok' in ok:
        if time.time() - now > 2.0: # seconds to timeout
          screen.addstr("no OK from printer")
          break
        ok = ptr.read1line()
  fd.close()
  ptr.cmnd("G1 F2000")
  ok = ptr.waitOk()
  ptr.cmnd("G 91")
  ok = ok + ptr.waitOk()
  if ok != "": printInfo(ok)
  time.sleep(5)

def printSeeks():
  for i in range(0, 10):
    screen.addstr(9,0,"press s# to seek to a position, capital S# to store current position")
    screen.addstr(10+i,0," seek {0}: X{1} Y{2} Z{3}  {4}".format(i,seek_positions[i]['x'],seek_positions[i]['y'],seek_positions[i]['z'],seek_positions[i]['name']))
  linenum = 20
  screen.addstr(linenum,0,"press tool letter to switch to that tool, Shift-letter to home that tool")
  linenum += 1
  for i in tools:
    screen.addstr(linenum,0," tool {0}: {4}:  X{1} Y{2} Z{3}".format(chr(i),tools[i]['x'],tools[i]['y'],tools[i]['z'],tools[i]['name'].ljust(10)))
    linenum += 1
  linenum = 9
  screen.addstr(linenum,midX,"press letter of a command (arrow keys and pgup/pgdn to move machine)")
  linenum += 1
  for i in commands:
    screen.addstr(linenum,midX," {0}: {1}".format(commands[i]['key'],commands[i]['descr']))
    linenum += 1

def printInfo(text):
  # curpos = curses.getsyx()
  screen.addstr(4,0,"mode = {0}".format(tools[tool_mode]['name'])+"       ")
  screen.addstr(5,0,"absolute position: %.3f, %.3f, %.3f                     \n" % (present_position['x'],present_position['y'],present_position['z'])+str(text)+"\n")

screen = curses.initscr()  #we're not in kansas anymore
curses.noecho()    #could be .echo() if you want to see what you type
curses.curs_set(0)
screenSize = screen.getmaxyx()
midX = int(screenSize[1]/2) # store the midpoint of the width of the screen
screen.keypad(1)  #nothing works without this
ptr=p.prntr()
increment = 1.0
tool_mode = ord('c') # you better have a valid tool in here to start with

readData()
printInfo(ptr.init())
printSeeks()
while True:

  press = screen.getch()
  if press == ord("V"):
    ptr.cmnd("M107     ")
    printInfo("M107     ")
    printInfo("updn")
  if press == ord("v"):
    ptr.cmnd("M106     ")
    printInfo("M106     ")
  if press == ord("Q"): break  #quit without saving
  if press == ord("q"): # save configuration before quitting
    saveData()
    break  #quit  ord values are important
  elif press == ord("W"): saveData() # write config data to datafilename
  elif press == ord("R"):
    readData() # read config data from datafilename
    printSeeks() # update display of tool coordinates
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
      ptr.cmnd("G1 X{0} Y{1} Z{2} F7000".format(move_adder['x'],move_adder['y'],move_adder['z'])) #ptr.cmnd
    printInfo( "mode = {0}".format(tools[press]['name']))

  elif (press + 32) in tools:  # capital letter version of a tool key
    press += 32 # change it to lowercase version
    tool_mode = press
    printInfo( "{0} home".format(tools[press]['name']))
    for i in {'x','y','z'}:
      tools[press][i] = present_position[i]
    printSeeks() # update display of tool coordinates

  elif press == ord("h"):
    present_position['x'] = 240
    present_position['y'] = 0
    printInfo( "actually home machine XY")
    ptr.hx()
    ptr.hy()
  elif press == ord("H"):
    present_position['z'] = 0
    printInfo( "set Z axis to home at present height")
  
  elif press == ord("s"):
    printInfo("seek to which stored position? 0-9  ")
    press = screen.getch()
    if press >= ord('0') and press <= ord('9'):
      if tool_mode != ord('c'):
        ptr.cmnd("G1 Z5 F4000"); # move up 5 before traversing, if not on camera
      for i in {'x','y','z'}:
        move_adder[i] = seek_positions[press-48][i] - present_position[i]
        present_position[i] += move_adder[i]
      printInfo("seeking to stored position {0}                           ".format(chr(press)))
      ptr.cmnd("G1 X{0} Y{1} Z{2} F8000".format(move_adder['x'],move_adder['y'],move_adder['z'])) #ptr.cmnd(
      if tool_mode != ord('c'):
        ptr.cmnd("G1 Z-5 F10000"); # move down 5 after traversing, if not on camera
    else:
      printInfo("not a numeral, seek cancelled.                           ")

  elif press == ord("S"):
    printInfo("STORE POSITION to which stored position? 0-9  ")
    press = screen.getch()
    if press >= ord('0') and press <= ord('9'):
      for i in {'x','y','z'}:
        seek_positions[press-48][i] = present_position[i] # store position
        # if tool_mode != ord('c'): # if we are not already in camera mode, compensate
        #   seek_positions[press-48][i] += tools[tool_mode][i] - tools[ord('c')][i] #add the offset to camera mode
    else:
      screen.addstr(5,0,"not a numeral, store cancelled.                           ")
    printSeeks() # update display of seek coordinates

  #these methods  allow the user to send raw g code to the printer

  elif press == ord("g"):
    moment = screen.getstr()
    printInfo("G"+moment)
    ptr.cmnd("G{0}".format(moment))
  
  elif press == ord("m"):
    moment = screen.getstr()
    printInfo("M"+moment)
    ptr.cmnd("M{0}".format(moment))

  elif press == ord("1"):
    increment = 0.025
  elif press == ord("2"):
    increment = 0.1
  elif press == ord("3"):
    increment = 1.0
  elif press == ord("4"):
    increment = 10.0

  elif press == ord("f"):
    filename = "sline.g"
    printInfo("Printing G-code file "+filename)
    printFile(filename,ptr)
    printInfo("Finished printing G-code file "+filename)

curses.endwin() #there's no place like home
