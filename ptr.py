import sys
import serial
import time



class prntr:
  #this is the base class for all printer communication

  def __init__(self ): #anything that needs to happen when the device connects
    self.com = serial.Serial('/dev/ttyACM0', 230400, timeout = 0.9)
    now = time.time()
    ok = self.com.readline()
    while not 'ok' in ok:
      if time.time() - now > 8.0: # seconds to timeout
        print("no OK from printer")
        break
      ok = self.com.readline()
    self.com.write("G 91\r\n")  #everything in this script is for relative motion
    now = time.time()
    ok = self.com.readline()
    while not 'ok' in ok:
      if time.time() - now > 8.0: # seconds to timeout
        print("no OK from printer")
        break
      ok = self.com.readline()
    self.com.flushInput()
#    print( self.com.readlines())

  def cmnd(self, cmd):
    self.com.flushInput()
    self.com.write(cmd[:-1]+"\r\n")
    return #self.com.readlines()

  def fan(self):
   self.com.write("M106 S255\r\n")
  
  #these methods are for controlling relative movement of the toolhead


  def xp(self, increment):  #P for PLUS M for MINUS
    self.com.write("G X {0}\r\n".format(increment))

  def xm(self, increment):  #P for PLUS M for MINUS
    self.com.write("G X -{0}\r\n".format(increment))

  def yp(self, increment):
    self.com.write("G Y {0}\r\n".format(increment))

  def ym(self, increment): 
    self.com.write("G Y -{0}\r\n".format(increment))

  def zp(self, increment):
    self.com.write("G Z {0}\r\n".format(increment))

  def zm(self, increment): 
    self.com.write("G Z -{0}\r\n".format(increment))

  def hx(self):
    self.com.write("G28 X\r\n")

  def hy(self):
    self.com.write("G28 Y\r\n")

  def hz(self):
    self.com.write("G28 Z\r\n")


#initialize the routine
bot = prntr

def main(*arg):
  print bot.cmnd()


if __name__=='__main__':
  sys.exit(main(*sys.argv))

