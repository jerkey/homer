import serial,sys
port_id = "/dev/ttyACM0"
baud = 230400
 
print "FLUSHING..."
ser = serial.Serial(port=port_id, baudrate=baud, timeout=2)
while True:
    response = ''
    response = ser.readline()
    print response.strip('\n')
    if response is "":
   	print "this is where the rest of the routine SHOULD RUN "
	print "but there seems to be some sort of authentication shit"
	print "maybe a handshake?"
        break
ser.close()
