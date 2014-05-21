import sys
import serial
import time



class prntr:
  #this is the base class for all printer communication

  def init(self ): #anything that needs to happen when the device connects
    self.com = serial.Serial('/dev/ttyACM0', 230400, timeout = 1)
    self.com.readlines()
    returnMsg = ""
    self.com.write("G 91\r\n")  #everything in this script is for relative motion
    if self.waitOk() != "":
      returnMsg = returnMsg + "no 'ok' from printer after G 91"
    self.com.write("M201 Z50\r\n")  #change the Z acceleration to prevent upward stripping
    if self.waitOk() != "":
      returnMsg = returnMsg + "no 'ok' from printer after M201 Z50"
    if returnMsg == "": returnMsg = "ptr.init OK"
    return returnMsg

  def waitOk(self):
    now = time.time()
    ok = self.com.readline()
    returnMsg = ""
    while not 'ok' in ok:
      if time.time() - now > 5.0: # seconds to timeout
        returnMsg = returnMsg + "no 'ok' from printer"
        break
      ok = self.com.readline()
    self.com.flushInput()
    return returnMsg

  def cmnd(self, cmd):
    self.com.flushInput()
    self.com.write(cmd[:-1]+"\r\n")
    return #self.com.readlines()

  def read1line(self):
    return self.com.readline()

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

