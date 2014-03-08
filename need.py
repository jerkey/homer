import sys
import serial

def main(*arg):
  print "called with these args: "+" "+" ".join(arg[1:])
if __name__=='__main__':
  sys.exit(main(*sys.argv))
