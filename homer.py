#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import ptr as p
import os,datetime,time

#set up globally scoped variables
serialPort = '/dev/ttyACM0'
baudRate = 230400
cameraActivated = False
fanOn = False
focusWindowSize = 0.3 # portion of center of camera view to focus on
hotbedTemp = 200 # temperature of heated bed (0 when off)
macro_buffer = [] # put any startup commands in here, as integers with ord() or curses.KEY_whatever
move_adder = {'x': 0.0, 'y': 0.0, 'z': 0.0}
homed_axes = {'x': False, 'y': False, 'z': False} # has this axis been hardware homed?
present_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
filePath = "/home/smacbook/gcode/" # prefix for all filenames in files
files = {ord('g') : {'name':'green resist for tai crystal','filename':'tai1.g'},
         ord('s') : {'name':'solder paste for screw, post, tai','filename':'taisold.g'},
         ord('b') : {'name':'green resist box for cyrium','filename':'box.g'},
         ord('j') : {'name':'solder paste busbar JDSU','filename':'sline-jdsu.g'},
         ord('c') : {'name':'solder paste only screwhole','filename':'screwonly.g'}}
macros = {ord('p') : {'name':'resist block and cam next','keys':'pfc'},
          ord('d') : {'name':'dance','keys':'pcpc'},
          ord('l') : {'name':'left 10.5','keys':'g1 x-10.5'+chr(10)},
          ord('r') : {'name':'right 10.5','keys':'g1 x10.5'+chr(10)},
          ord('p') : {'name':'previous copper','keys':'g1 x-15.22 Y0.09'+chr(10)},
          ord('s') : {'name':'activate sucker','keys':'m42 p6 s255\n'},
          ord('b') : {'name':'deactivate sucker and blow','keys':'m42 p6 s0\nm42 p8 s255\ng4 p100\nm42 p8 s0\n'}}
tools = {ord('e') : {'name':'plastic extruder'},
         ord('c') : {'name':'camera'},
         ord('r') : {'name':'resist mask'},
         ord('p') : {'name':'solder paste'}}
for i in tools:
  for g in {'x','y','z'}:
    tools[i][g] = 0.0
seek_positions = { n : {'name': '', 'x': 0.0, 'y': 0.0, 'z': 0.0} for n in range(10)} # create empty array

datafilename = 'homer.dat'

def getPosition(): # ask printer for present position with M114
  ptr.cmnd('M114')
  m114 = ptr.read1line().split('\n')[0] # get text back from printer
  axes_read = '' # which axes were read from hardware (because they were homed)
  if homed_axes['x']:
    present_position['x'] = float(m114.split(':')[1].split('Y')[0])
    axes_read += 'X '
  if homed_axes['y']:
    present_position['y'] = float(m114.split(':')[2].split('Z')[0])
    axes_read += 'Y '
  if homed_axes['z']:
    present_position['z'] = float(m114.split(':')[3].split('E')[0])
    axes_read += 'Z '
  if axes_read != '':
    printInfo('axes read from hardware: '+axes_read)
  else:
    printInfo('no axes read.  Have you homed any hardware axes yet?')

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
  screen.addstr("\n") # we are going to print the gcode to the screen, so newline
  line = fd.readline() # read the first line of the file
  for line in fd:
    line = line.rstrip().split(';')[0] # strip out comments, if any
    if len(line) > 1: # if any non-comment text, send it to printer
      ptr.cmnd(line) # send this command to the printer
      screen.addstr(line+ptr.waitOk()+"\n") # wait for OK and print errors
      screen.refresh()
      updateCamera(False)
  fd.close()
  screen.addstr("Finished printing G-code file  "+filename+"  (press any key)")
  screen.refresh()
  ptr.cmnd("G1 F2000")
  ok = ptr.waitOk()
  ptr.cmnd("G 91")
  ok = ok + ptr.waitOk()
  if ok != "": printInfo(ok)
  press = getKeyOrMacro()
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
  screen.addstr(linenum,midX,"tools available (press t to change tools)".ljust(midX))
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

def hotbedOn():
  ptr.cmnd("M140 S"+str(hotbedTemp))
  printInfo("M140 S"+str(hotbedTemp))

def hotbedOff():
  ptr.cmnd("M140 S0")
  printInfo("M140 S0")

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
  for axes in homed_axes:
    homeList = homeList+str(axes)
  printInfo("home which axis? choose "+homeList)
  press = getKeyOrMacro()
  if chr(press) in homed_axes:
    ptr.cmnd("G28 "+chr(press & 223)) # CAPITALIZE axis letter
    present_position[chr(press)] = homed_axes[chr(press)] # where are your limit switches?
    printInfo( "homed machine axis "+chr(press & 223)) # CAPITALIZE axis letter
    homed_axes[chr(press)] = True
  else:
    printInfo("Not a valid axis letter")

def homeAll(): # home all axes in homeList
  homeList= ""
  for axes in homed_axes:
    homeList = homeList+str(axes).upper()
    resent_position[axes] = homed_axes[axes] # where are your limit switches?
    homed_axes[axes] = True
  ptr.cmnd("G28 "+homeList)
  printInfo( "homed ALL machine axes "+homeList)

def zeroOne():
  zeroList= ""
  for axes in present_position:
    zeroList = zeroList+str(axes)
  printInfo("zero which axis? "+zeroList)
  press = getKeyOrMacro()
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
  press = getKeyOrMacro()
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
  press = getKeyOrMacro()
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
    press = getKeyOrMacro()
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
  press = getKeyOrMacro()
  if press in files:
    filename = filePath+files[press]['filename']
    printInfo("Printing G-code file "+filename)
    printFile(filename,ptr)
  else:
    printInfo("not a valid files key")

def toolPicker():
  global tool_mode
  printInfo("press a tool key (with shift for homing)")
  press = getKeyOrMacro()
  if press in tools:  # if any tool is selected
    if tool_mode != press:
      for i in {'x','y','z'}:
        move_adder[i] = tools[press][i] - tools[tool_mode][i]
        present_position[i] += move_adder[i]
      tool_mode = press
      ptr.cmnd("G1 Z5 F800") # move up before moving
      errors = ptr.waitOk()
      moveString = "G1 X{0} Y{1} Z{2} F8000".format(move_adder['x'],move_adder['y'],move_adder['z']) #ptr.cmnd
      ptr.cmnd(moveString)
      errors = errors + ptr.waitOk()
      ptr.cmnd("G1 Z-5 F800") # move down after moving
      errors = errors + ptr.waitOk()
      printInfo(moveString+" select tool = {0}".format(tools[press]['name'])+errors)
    else:
      printInfo( "already selected tool = {0}".format(tools[press]['name']))

  elif (press + 32) in tools:  # capital letter version of a tool key
    press += 32 # change it to lowercase version
    tool_mode = press
    printInfo( "{0} home".format(tools[press]['name']))
    for i in {'x','y','z'}:
      tools[press][i] = present_position[i]
    printCommands() # update display of tool coordinates

  else:
    printInfo("not a valid tools key")

def macro():
  global macro_buffer
  printInfo("Which macro to execute?")
  press = getKeyOrMacro()
  if press in macros:
    screen.addstr(3,0,macros[press]['name']) # print the macro name (will be erased by getKeyOrMacro)
    if isinstance(macros[press]['keys'],str): # macro is a string of letters to press
      for i in macros[press]['keys']:
        macro_buffer.append(ord(i)) # make macro_buffer a list of integers from the letters
    if isinstance(macros[press]['keys'],list): # macro is a list of ord() and curses.KEY_stuff
      macro_buffer = macros[press]['keys'] # just copy the list of ints
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

def updateCamera(focus): # focus is True if you want it to return a focus value
  global cameraActivated, frame
  if cameraActivated:
    cameraWorking, frame = camera1.read()
    if focus:
      pass
      #cv2.putText(frame, "focusing", (200,240), cv2.FONT_HERSHEY_PLAIN, 4.0, (255,0,0), thickness=3)
    else:
      cv2.putText(frame, "x", (310,240), cv2.FONT_HERSHEY_PLAIN, 4.0, (255,0,0), thickness=3)
    cv2.imshow("preview", frame)
    key = cv2.waitKey(1) # Note This function is the only method in HighGUI that can fetch and handle events, so it needs to be called periodically for normal event processing unless HighGUI is used within an environment that takes care of event processing.
    if key == 27: # exit on ESC (-1 if no key pressed) in preview window
      cv2.destroyWindow("preview")
      cameraActivated = False
    if focus:
      #hist_full = cv2.calcHist([frame],[0],None,[256],[0,256])# Calculate histogram
      hist_focusWindow = cv2.calcHist([frame],[0],focusWindow,[256],[0,256]) # Calculate histogram with mask
      histogram = [item for sublist in hist_focusWindow for item in sublist] # flatten histogram into a list
      histogram_length = sum(histogram) # count the pixels
      samples_probability = [float(h) / histogram_length for h in histogram]
      entropy = -sum([p * math.log(p, 2) for p in samples_probability if p != 0])
      return entropy # return the focus value

def focusAway(): # move camera away from target to best focus point
  if not cameraActivated:
    printInfo("camera must be active before attempting auto-focus")
    return
  if not mathNumpyImported:
    printInfo("failed to load python module math or numpy, can't focus without them")
    return
  if increment > 2: # increment must be set to a reasonably small value
    printInfo("increment value is higher than 2, can't focus that way")
    return
  moveCount = 0 # how many times we've moved
  lastFocus = 0 # focus value where we were last
  while moveCount * increment < 10.0: # move no more than 10mm away from target
    focus = sum([updateCamera(True) for i in range(3)]) # add ten frames worth of focus measurement
    if focus > lastFocus: # if this focus is better than previous position
      lastFocus = focus
      ptr.zp(increment)
      present_position['z']+=increment
      printInfo( "focus up")
      ptr.cmnd("G4 P1") # make sure we wait until the machine arrives
      if ptr.waitOk() == "": # make sure we get an OK after that move
        moveCount += 1 # keep track of how far we've moved
      else:
        printInfo("ERROR: did not get OK from printer after move")
        return
    else: # previous focus position was better
      ptr.zm(increment)
      present_position['z']-=increment
      if moveCount == 1:
        printInfo("not close enough? can't find best focus")
      else:
        printInfo("achieved best focus")
      return
  printInfo("could not find best focus, returning to start point")
  for m in range(moveCount):
    ptr.zm(increment)
    present_position['z']-=increment

def getKeyOrMacro(): # return a keypress, or a macro stroke if there is one
  if len(macro_buffer) == 0:
    press = screen.getch()
    while press == -1:
      press = screen.getch()
      updateCamera(False)
    return press
  else:
    if len(macro_buffer) == 1: # last command, let's clear line 3 since macro is over
      screen.addstr(3,0," ".ljust(midX));
    return macro_buffer.pop(0) # give the first thing in the buffer as a keystroke

def vacPumpOff(): # turn OFF vacuum pump on pin 40
  ptr.cmnd("M42 P40 S0")

def vacPumpOn(): # turn ON vacuum pump on pin 40
  ptr.cmnd("M42 P40 S255")

def fanOnOff(): # toggle fan on or off
  global fanOn
  if fanOn:
    ptr.cmnd("M107") # turn fan off
    printInfo("M107")
    fanOn = False
  else:
    ptr.cmnd("M106") # turn fan on
    printInfo("M106")
    fanOn = True

def takePicture(): # save an image to disk with timestamp and coords
  if not cameraActivated:
    printInfo("camera must be active before taking a picture")
    return
  filename = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
  filename += " X%.3fY%.3fZ%.3f" % (present_position['x'],present_position['y'],present_position['z'])+'.png'
  printInfo('taking picture to '+filename)
  updateCamera(True)
  cv2.imwrite(filename,frame)

scriptFile = None # rpt2pnp.script to read from
configFile = None # rpt2pnp.config file to write to
scriptLine = '' # line of rpt2pnp.script we last read

def rpt2pnp(): # run an rpt2pnp script
  global scriptFile,configFile,scriptLine
  if scriptFile == None:
    printInfo('Do you want to open script.pnp and run it? y/n')
    press = getKeyOrMacro() # get a keystroke or macro step (and maintain camera)
    if press != ord('y'):
      printInfo('chose not to open script')
      return
    printInfo('opening script.pnp')
    scriptFile = open('script.pnp','r')
    configFile = open('config.pnp','w')
    scriptLine = scriptFile.readline().split('\n')[0]
    screen.addstr(3,0,scriptLine[scriptLine.find(':')+1:]+' and press R')
    screen.refresh()
    return
  getPosition() # update present position from hardware
  writeString = scriptLine.split(chr(9))[0]+chr(9)+"%.3f %.3f %.3f" % (present_position['x'],present_position['y'],present_position['z'])
  configFile.write(writeString+'\n')
  printInfo('wrote to configFile: '+writeString)
  scriptLine = scriptFile.readline().split('\n')[0]
  if scriptLine == '':
    screen.addstr(3,0," ".ljust(midX)) # clear script navigation line
    printInfo('finished reading from pnp script and writing config file')
    configFile.close() # done with the file we're writing
    scriptFile = None
    printCommands() # refresh the screen a little
    return
  screen.addstr(3,0,str(scriptLine[scriptLine.find(':')+1:]+' and press R').ljust(midX))
  screen.refresh()

commands = [ (ord('V'),{'descr':'turn hotbed to '+str(hotbedTemp)+' C','func':hotbedOn}),
             (ord('v'),{'descr':'turn hotbed off','func':hotbedOff}),
             (ord('F'),{'descr':'toggle fan on/off','func':fanOnOff}),
             (ord('P'),{'descr':'turn vacpump on','func':vacPumpOn}),
             (ord('p'),{'descr':'turn vacpump off','func':vacPumpOff}),
             (ord('Q'),{'descr':'Quit without saving','func':noSaveQuit}),
             (ord('q'),{'descr':'quit (and save)','func':saveQuit}),
             (ord('G'),{'descr':'get position from M114','func':getPosition}),
             (ord('h'),{'descr':'home a specific axis','func':homeOne}),
             (ord('H'),{'descr':'Home ALL axes','func':homeAll}),
             (ord('z'),{'descr':'zero a specific axis','func':zeroOne}),
             (ord('Z'),{'descr':'Zero ALL software axes','func':zeroAll}),
             (ord('s'),{'descr':'seek to stored position','func':seek}),
             (ord('t'),{'descr':'tool selector (or relative homing)','func':toolPicker}),
             (ord('S'),{'descr':'Store present position to memory','func':seekStore}),
             (ord('g'),{'descr':'send G-code to machine','func':gCode}),
             (ord('m'),{'descr':'send M-code to machine','func':mCode}),
             (ord('f'),{'descr':'print a g-code file to machine','func':filePicker}),
             (ord('A'),{'descr':'Auto-focus the camera Z+ from target','func':focusAway}),
             (ord('R'),{'descr':'run an rpt2pnp script','func':rpt2pnp}),
             (ord('`'),{'descr':'execute a keystroke macro','func':macro}),
             (ord('1'),{'descr':'set movement increment to 0.25','func':speed1}),
             (ord('2'),{'descr':'set movement increment to 0.1','func':speed2}),
             (ord('3'),{'descr':'set movement increment to 1.0','func':speed3}),
             (ord('4'),{'descr':'set movement increment to 10.0','func':speed4}),
             (ord('='),{'descr':'take a timestamped PNG with coordinates','func':takePicture}),
            (ord('\\'),{'descr':'turn on (or off) camera','func':cameraOnOff})]
i = 0 # we are going to turn the "list" above into a dictionary, with a sequence number
for c in commands:
  c[1]['seq'] = i
  i += 1
commands = dict(commands)

screen = curses.initscr()  #we're not in kansas anymore
curses.noecho()    #could be .echo() if you want to see what you type
curses.curs_set(0)
screen.timeout(0)
screen.scrollok(True) # allow gcode to scroll screen
screenSize = screen.getmaxyx()
midX = int(screenSize[1]/2) # store the midpoint of the width of the screen
screen.keypad(1)  #nothing works without this
ptr=p.prntr()
increment = 1.0
statusLines = 4 # how many lines are used for changing data (left side of screen)
tool_mode = ord('c') # you better have a valid tool in here to start with
try:
  import cv2 # need this for camera
  os.environ["DISPLAY"] = ":0" # tell it to open the camera on the local machine even if we're remote
  cv2.namedWindow("preview") # create the viewport
  camera1 = cv2.VideoCapture(0) # choose camera1 number here
  if camera1.isOpened(): # try to get the first frame
    cameraWorking, frame = camera1.read()
    if cameraWorking:
      try:
        import math, numpy # need these for autofocus
        height, width = frame.shape[:2]
        focusWindow = numpy.zeros((height,width), numpy.uint8) # create a focusWindow
        vborder = (height*(1-focusWindowSize))/2
        hborder = (width*(1-focusWindowSize))/2
        focusWindow[vborder:height-vborder, hborder:width-hborder] = 255
        mathNumpyImported = True
      except ImportError:
        mathNumpyImported = False
  cv2Imported = True
except ImportError:
  cv2Imported = False
  cameraWorking = False

readData()
printInfo(ptr.init(serialPort,baudRate))
printCommands()

while True: # main loop
  press = getKeyOrMacro() # get a keystroke or macro step (and maintain camera)
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
