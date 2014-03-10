import sys
import serial
from time import sleep
class prntr:
  def __init__(self ):
    self.com = serial.Serial('/dev/ttyACM0', 230400, timeout = 2)
    sleep(2)
  def wrk(self, *cmd):
    self.com.write(cmd)
  def test(self):
   self.com.write("M106 S255\n\r")
def main(*arg):
  print "I moved the printer, G"+" "+" ".join(arg[1:])
  bot = prntr()
  sleep(6)
  print bot.test()


if __name__=='__main__':
  sys.exit(main(*sys.argv))

