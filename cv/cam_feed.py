import cv2

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
  rval, frame = vc.read()
else:
  rval = False

while rval:
  x = 310
  y = 240
  text_color = (255,0,0) # B,G,R
  
  cv2.putText(frame, "x", (x,y), cv2.FONT_HERSHEY_PLAIN, 4.0, text_color, thickness=3) 
  cv2.imshow("preview", frame)
  rval, frame = vc.read()
  key = cv2.waitKey(20)
  if key == 27: # exit on ESC
    break
cv2.destroyWindow("preview")
