import sys
import serial
from time import sleep



class prntr:
  #this is the base class for all printer communication

  def __init__(self ): #anything that needs to happen when the device connects
    self.com = serial.Serial('/dev/ttyACM0', 230400, timeout = 2)
    sleep(8)  #wait for data
    self.com.readlines()
    self.com.flush()
    self.com.write("G 91\r\n")  #everything in this script is for relative motion
    print( self.com.readlines())

  def cmnd(self, *cmd):
    self.com.flush()
    self.com.write(*cmd[:-1],"\r\n")
    return self.com.readlines()

  def fan(self):
   self.com.write("M106 S255\r\n")
  
  #these methods are for controlling relative movement of the toolhead


  def xp(self, increment):  #eventually this is going to take a scalar type as well for an argument
    self.com.flush()
    self.com.write("G X {0}\r\n".format(increment))
    return self.com.readlines()

  def xm(self, increment):  #P for PLUS M for MINUS
    self.com.flush()
    self.com.write("G X -{0}\r\n".format(increment))
    return self.com.readlines()

  def yp(self, increment):
    self.com.flush()
    self.com.write("G Y {0}\r\n".format(increment))
    return self.com.readlines()

  def ym(self, increment): 
    self.com.flush()
    self.com.write("G Y -{0}\r\n".format(increment))
    return self.com.readlines()

  def zp(self, increment):
    self.com.flush()
    self.com.write("G Z {0}\r\n".format(increment))
    return self.com.readlines()

  def zm(self, increment): 
    self.com.flush()
    self.com.write("G Z -{0}\r\n".format(increment))
    return self.com.readlines()


#initialize the routine
bot = prntr

def main(*arg):
  print bot.cmnd()


if __name__=='__main__':
  sys.exit(main(*sys.argv))

