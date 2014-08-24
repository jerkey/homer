#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import ptr as p
import os,datetime,time

#set up globally scoped variables
serialPort = '/dev/ttyACM0'
baudRate = 230400
cameraActivated = False
move_adder = {'x': 0.0, 'y': 0.0, 'z': 0.0}
home_switches = {'x': 240, 'y': 0, 'z': 0} # where does your machine go when it homes?
present_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
filePath = "/home/smacbook/gcode/" # prefix for all filenames in files
files = {ord('g') : {'name':'green resist for tai crystal','filename':'tai1.g'},
         ord('s') : {'name':'solder paste for screw, post, tai','filename':'sold.g'},
         ord('c') : {'name':'move plate to and return','filename':'cookr.g'}}
macros = {ord('p') : {'name':'resist block and cam next','keys':'pfc'},
          ord('d') : {'name':'dance','keys':'pcpc'},
          ord('s') : {'name':'solder paste block','keys':'pfc'}}
tools = {ord('e') : {'name':'plastic extruder'},
         ord('c') : {'name':'camera'},
         ord('g') : {'name':'green goo'},
         ord('p') : {'name':'solder paste'}}
for i in tools:
  for g in {'x','y','z'}:
    tools[i][g] = 0.0
seek_positions = { n : {'name': '', 'x': 0.0, 'y': 0.0, 'z': 0.0} for n in range(10)} # create empty array

datafilename = 'homer.dat'

def saveData(): # store the tools dictionary to a file, after renaming old one
  errText = ""
  try:
    #os.rename(datafilename,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+".dat") #timestamped backups
    os.rename(datafilename,"homer.dat.old")
  except OSError:
    errText = "(creating new) "
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
  except IOError:
    printInfo("error: could not open "+filename)
    return
  screen.erase() # we are going to print gcode to the screen, so erase all else
  printInfo("opened "+filename)
  screen.addstr("\n")
  line = fd.readline()
  for line in fd:
    updateCamera()
    line = line.rstrip().split(';')[0]
    if len(line) > 1:
      screen.addstr(line+"\n")
      screen.refresh()
      ptr.cmnd(line)
      now = time.time()
      ok = ptr.read1line()
      updateCamera()
      while not 'ok' in ok:
        if time.time() - now > 4.0: # seconds to timeout
          screen.addstr("no OK from printer")
          screen.refresh()
          break
        updateCamera()
        ok = ptr.read1line()
  fd.close()
  screen.addstr("Finished printing G-code file  "+filename+"  (press any key)")
  screen.refresh()
  ptr.cmnd("G1 F2000")
  ok = ptr.waitOk()
  ptr.cmnd("G 91")
  ok = ok + ptr.waitOk()
  if ok != "": printInfo(ok)
  press = screen.getch()
  while press == -1:
    press = screen.getch()
    updateCamera()
  screen.erase()
  printCommands()
  printInfo("Printed "+filename)

def printCommands():
  linenum = statusLines
  screen.addstr(linenum,0,"seek position memory registers")
  linenum += 1
  for i in range(0, 10):
    screen.addstr(linenum,0," seek {0}: X{1} Y{2} Z{3}  {4}".format(i,seek_positions[i]['x'],seek_positions[i]['y'],seek_positions[i]['z'],seek_positions[i]['name']))
    linenum += 1
  linenum += 1
  screen.addstr(linenum,0,"press ` and a macro key to activate a macro")
  linenum += 1
  for i in macros:
    screen.addstr(linenum,0," macro {0}: {1} = {2}".format(chr(i),macros[i]['name'],macros[i]['keys']))
    linenum += 1
  linenum += 1
  screen.addstr(linenum,0,"press f and a key to print a g-code file")
  linenum += 1
  for i in files:
    screen.addstr(linenum,0," files {0}: {1} = {2}".format(chr(i),files[i]['name'],files[i]['filename']))
    linenum += 1
  linenum = 0
  screen.addstr(linenum,midX,"command keys (arrowkeys, ]/pgup amd [/pgdn to move machine)".ljust(midX))
  linenum += 1
  for i in commands:
    screen.addstr(linenum+commands[i]['seq'],midX,str(" {0}: {1}".format(chr(i),commands[i]['descr'])).ljust(midX))
  linenum += len(commands)+1
  screen.addstr(linenum,midX,"press letter to switch tools, Shift- to home tool".ljust(midX))
  linenum += 1
  for i in tools:
    screen.addstr(linenum,midX,str(" tool {0}: {4}:  X{1} Y{2} Z{3}".format(chr(i),tools[i]['x'],tools[i]['y'],tools[i]['z'],tools[i]['name']).ljust(10)))
    linenum += 1

def printInfo(text):
  # curpos = curses.getsyx()
  screen.addstr(0,0,str("mode = {0}".format(tools[tool_mode]['name'])+"     movement increment = "+str(increment)).ljust(midX))
  screen.addstr(1,0,str("absolute position: %.3f, %.3f, %.3f        "  % (present_position['x'],present_position['y'],present_position['z'])).ljust(midX))
  screen.addstr(2,0,text.ljust(midX))
  screen.refresh() # tell curses to actually show it now

def fanOn():
  ptr.cmnd("M106     ")
  printInfo("M106     ")

def fanOff():
  ptr.cmnd("M107     ")
  printInfo("M107     ")

def saveQuit(): # save configuration before quitting
  saveData()
  noSaveQuit()

def noSaveQuit(): # quit without saving
  if cameraActivated:
    cv2.destroyWindow("preview")
  curses.nocbreak()
  screen.keypad(0)
  curses.echo()
  curses.endwin() #there's no place like home
  quit() #quit  ord values are important

def Write():
  saveData() # write config data to datafilename

def Read():
  readData() # read config data from datafilename
  printCommands() # update display of tool coordinates

def homeOne():
  homeList= ""
  for axes in home_switches:
    homeList = homeList+str(axes)
  printInfo("home which axis? choose "+homeList)
  press = screen.getch()
  while press == -1:
    press = screen.getch()
  if chr(press) in home_switches:
    ptr.cmnd("G28 "+chr(press & 223)) # CAPITALIZE axis letter
    present_position[chr(press)] = home_switches[chr(press)] # where are your limit switches?
    printInfo( "homed machine axis "+chr(press & 223)) # CAPITALIZE axis letter
  else:
    printInfo("Not a valid axis letter")

def homeAll(): # home all axes in homeList
  homeList= ""
  for axes in home_switches:
    homeList = homeList+str(axes).upper()
    present_position[axes] = home_switches[axes] # where are your limit switches?
  ptr.cmnd("G28 "+homeList)
  printInfo( "homed ALL machine axes "+homeList)

def zeroOne():
  zeroList= ""
  for axes in present_position:
    zeroList = zeroList+str(axes)
  printInfo("zero which axis? "+zeroList)
  press = screen.getch()
  while press == -1:
    press = screen.getch()
  if chr(press) in present_position:
    present_position[chr(press)] = 0.0
    printInfo( "zeroed axis "+chr(press & 223)) # CAPITALIZE axis letter
  else:
    printInfo("Not a valid axis letter")

def zeroAll(): # zero all axes in zeroList
  zeroList= ""
  for axes in present_position:
    zeroList = zeroList+str(axes)
    present_position[axes] = 0
  printInfo( "zerod ALL software axes "+zeroList)

def seek():
  printInfo("seek to which stored position? 0-9")
  press = screen.getch()
  while press == -1:
    press = screen.getch()
  if press >= ord('0') and press <= ord('9'):
    if tool_mode != ord('c'):
      ptr.cmnd("G1 Z5 F4000"); # move up 5 before traversing, if not on camera
    for i in {'x','y','z'}:
      move_adder[i] = seek_positions[press-48][i] - present_position[i]
      present_position[i] += move_adder[i]
    printInfo("seeking to stored position {0}".format(chr(press)))
    ptr.cmnd("G1 X{0} Y{1} Z{2} F8000".format(move_adder['x'],move_adder['y'],move_adder['z'])) #ptr.cmnd(
    if tool_mode != ord('c'):
      ptr.cmnd("G1 Z-5 F10000"); # move down 5 after traversing, if not on camera
  else:
    printInfo("not a numeral, seek cancelled.")

def seekStore():
  printInfo("STORE POSITION to which stored position? 0-9  ")
  press = screen.getch()
  while press == -1:
    press = screen.getch()
  if press >= ord('0') and press <= ord('9'):
    for i in {'x','y','z'}:
      seek_positions[press-48][i] = present_position[i] # store position
      # if tool_mode != ord('c'): # if we are not already in camera mode, compensate
      #   seek_positions[press-48][i] += tools[tool_mode][i] - tools[ord('c')][i] #add the offset to camera mode
      printInfo("STORED to position "+chr(press))
  else:
    printInfo("not a numeral, seek cancelled.")
  printCommands() # update display of seek coordinates

def gCode(): # send a command starting with G
  sendCode("G")

def mCode(): # send a command starting with M
  sendCode("M")

def sendCode(prefix):
  gcode = prefix # start command with whatever we were told to start with
  screen.addstr(3,0,"enter "+prefix+"-code to be sent (ESC to cancel)")
  printInfo(gcode)
  press = -1
  while press not in {27, 10, 13, curses.KEY_ENTER}: # until escape or enter
    press = -1 # get another key
    while press == -1:
      press = screen.getch()
    if press == curses.KEY_BACKSPACE: # user hit backspace
      gcode = gcode[:-1] # remove last character
    else:
      gcode = gcode + chr(press).upper() # capitalize everything typed
    printInfo(gcode) # update the display

  if press == 27: # if user hit escape OR an F-key that is escaped
    press = screen.getch() # if an escape sequence like F1 is hit, grab the second char (if there)
    screen.addstr(3,0," ".ljust(40)) # clear g-code entering instruction line
    printInfo("cancelled "+prefix+" code by pressing ESC")
    return

  gcode = gcode[:-1] # remove "enter" character from end
  ptr.cmnd(gcode) # actually send it to printer
  screen.addstr(3,0," ".ljust(40)) # clear g-code entering instruction line
  printInfo("sent "+gcode)
  printCommands()

def speed1():
  global increment
  increment = 0.025
  printInfo('set movement increment to '+str(increment))
def speed2():
  global increment
  increment = 0.1
  printInfo('set movement increment to '+str(increment))
def speed3():
  global increment
  increment = 1.0
  printInfo('set movement increment to '+str(increment))
def speed4():
  global increment
  increment = 10.0
  printInfo('set movement increment to '+str(increment))

def filePicker():
  printInfo("Which file do you want to print?")
  press = screen.getch()
  while press == -1:
    press = screen.getch()
  if press in files:
    filename = filePath+files[press]['filename']
    printInfo("Printing G-code file "+filename)
    printFile(filename,ptr)
  else:
    printInfo("not a valid files key")

def macro():
  printInfo("Which macro to execute?")
  press = screen.getch()
  while press == -1:
    press = screen.getch()
  if press in macros:
    printInfo(macros[press]['name'])
  else:
    printInfo("not a valid macro key")

def cameraOnOff():
  global cameraActivated
  if cameraActivated: # then turn camera off
    cameraActivated = False
    cv2.destroyWindow("preview")
    printInfo("camera shut off by user")
    return
  if cv2Imported: # otherwise, see if camera can be activated
    if cameraWorking:
      cameraActivated = True
      printInfo("camera opened successfully!")
    else:
      printInfo("opencv loaded but camera cannot be opened")
      return
  else:
    printInfo("could not import cv2 to open camera (need opencv2 for python)")

def updateCamera():
  global cameraActivated, frame
  if cameraActivated:
    cameraWorking, frame = camera1.read()
    cv2.putText(frame, "x", (310,240), cv2.FONT_HERSHEY_PLAIN, 4.0, (255,0,0), thickness=3)
    cv2.imshow("preview", frame)
    key = cv2.waitKey(1) # Note This function is the only method in HighGUI that can fetch and handle events, so it needs to be called periodically for normal event processing unless HighGUI is used within an environment that takes care of event processing.
    #printInfo(str(time.time()))
    if key == 27: # exit on ESC (-1 if no key pressed)
      cv2.destroyWindow("preview")
      cameraActivated = False

commands = { ord('v'): {'seq': 0,'descr':'M106 turn fan on','func':fanOn},
             ord('V'): {'seq': 1,'descr':'M107 turn fan off','func':fanOff},
             ord('Q'): {'seq': 2,'descr':'Quit without saving','func':noSaveQuit},
             ord('q'): {'seq': 3,'descr':'quit (and save)','func':saveQuit},
             ord('h'): {'seq': 4,'descr':'home a specific axis','func':homeOne},
             ord('H'): {'seq': 5,'descr':'Home ALL axes','func':homeAll},
             ord('z'): {'seq': 6,'descr':'zero a specific axis','func':zeroOne},
             ord('Z'): {'seq': 7,'descr':'Zero ALL software axes','func':zeroAll},
             ord('s'): {'seq': 8,'descr':'seek to stored position','func':seek},
             ord('S'): {'seq': 9,'descr':'Store present position to memory','func':seekStore},
             ord('g'): {'seq':10,'descr':'send G-code to machine','func':gCode},
             ord('m'): {'seq':11,'descr':'send M-code to machine','func':mCode},
             ord('f'): {'seq':12,'descr':'print a g-code file to machine','func':filePicker},
             ord('`'): {'seq':13,'descr':'execute a keystroke macro (no work yet)','func':macro},
             ord('1'): {'seq':14,'descr':'set movement increment to 0.25','func':speed1},
             ord('2'): {'seq':15,'descr':'set movement increment to 0.1','func':speed2},
             ord('3'): {'seq':16,'descr':'set movement increment to 1.0','func':speed3},
             ord('4'): {'seq':17,'descr':'set movement increment to 10.0','func':speed4},
            ord('\\'): {'seq':18,'descr':'turn on (or off) camera','func':cameraOnOff},
             ord('W'): {'seq':19,'descr':'Write save file','func':Write},
             ord('R'): {'seq':20,'descr':'Read save file','func':Read}}

screen = curses.initscr()  #we're not in kansas anymore
curses.noecho()    #could be .echo() if you want to see what you type
curses.curs_set(0)
screen.timeout(0)
screenSize = screen.getmaxyx()
midX = int(screenSize[1]/2) # store the midpoint of the width of the screen
screen.keypad(1)  #nothing works without this
ptr=p.prntr()
increment = 1.0
statusLines = 4 # how many lines are used for changing data (left side of screen)
tool_mode = ord('c') # you better have a valid tool in here to start with
try:
  import cv2
  os.environ["DISPLAY"] = ":0" # tell it to open the camera on the local machine even if we're remote
  cv2.namedWindow("preview") # create the viewport
  camera1 = cv2.VideoCapture(0) # choose camera1 number here
  if camera1.isOpened(): # try to get the first frame
    cameraWorking, frame = camera1.read()
  cv2Imported = True
except ImportError:
  cv2Imported = False
  cameraWorking = False

readData()
printInfo(ptr.init(serialPort,baudRate))
printCommands()

while True: # main loop
  updateCamera()
  press = screen.getch() # get the character pressed by the user (non blocking)
  if commands.has_key(press): # if keystore is a known command in array
    printInfo(commands[press]['descr']) # print the command description
    commands[press]['func']() # run the appropriate subroutine
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
  elif (press == curses.KEY_PPAGE) or (press == ord(']')):  # pageup
    ptr.zp(increment)
    present_position['z']+=increment #this needs to be modular for scalar
    printInfo( "up   ")
  elif (press == curses.KEY_NPAGE) or (press == ord('[')):  # pagedown
    ptr.zm(increment)
    present_position['z']-=increment  #this needs to be modular for scalar
    printInfo( "down ")

  elif press in tools:  # if any tool is selected
    if tool_mode != press:
      for i in {'x','y','z'}:
        move_adder[i] = tools[press][i] - tools[tool_mode][i]
        present_position[i] += move_adder[i]
      tool_mode = press
      ptr.cmnd("G1 Z5 F800") # move up before moving
      ptr.cmnd("G1 X{0} Y{1} Z{2} F8000".format(move_adder['x'],move_adder['y'],move_adder['z'])) #ptr.cmnd
      ptr.cmnd("G1 Z-5 F800") # move down after moving
    printInfo( "moving machine to other tool = {0}".format(tools[press]['name']))

  elif (press + 32) in tools:  # capital letter version of a tool key
    press += 32 # change it to lowercase version
    tool_mode = press
    printInfo( "{0} home".format(tools[press]['name']))
    for i in {'x','y','z'}:
      tools[press][i] = present_position[i]
    printCommands() # update display of tool coordinates
