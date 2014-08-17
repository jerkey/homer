import cv2
import numpy as np
cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
  rval, frame = vc.read()
else:     
  rval = False
        
while rval:
  x = 310    
  y = 240
  text_color = (255,255,255) # B,G,R
  rval, frame = vc.read()
  biggest =None
  max_area = 0
  grey = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
  #blk = cv2.bitwise_not(grey)
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
  res = cv2.morphologyEx(grey,cv2.MORPH_OPEN,kernel)
  ret,thresh = cv2.threshold(grey,127,255,0)
  contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
  dest = np.zeros(thresh.shape, np.uint8)
  print contours
  print len(contours[0])
  print hierarchy
  for cnt in contours[::1]:
    rect  = cv2.minAreaRect(cnt)
    points = cv2.cv.BoxPoints(rect)
    points  = np.int0(np.around(points))
    #cv2.drawContours(dest, [cnt],0,(0,255,0),2)
    #cv2.polylines(dest, [points], True,( 255,255,255), 2 )
    cv2.fillPoly(dest, [cnt], (255,255,255), 4)
    img = cv2.cvtColor(dest,cv2.COLOR_GRAY2RGB)
    cv2.putText(img, "x", (x,y), cv2.FONT_HERSHEY_PLAIN, 4.0, text_color, thickness=3) 
    cv2.imshow("preview", img)
  key = cv2.waitKey(20)

  if key == 27: # exit on ESC
    break
cv2.destroyWindow("preview") 
