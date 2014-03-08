import sys
import serial

def main(*arg):
  print "I moved the printer, G"+" "+" ".join(arg[1:])
if __name__=='__main__':
  sys.exit(main(*sys.argv))
class prntr:
  def __init__(self ):
    self.com = serial.Serial('/dev/ttyACM0', '230400', timeout = None)
    time.sleep(2)
  def wrk(self, *cmd):
    self.com.write(cmd)
