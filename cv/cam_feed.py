import cv2

cv2.namedWindow("preview")
camera = cv2.VideoCapture(0)

if camera.isOpened(): # try to get the first frame
  rval, frame = camera.read()
else:
  rval = False
imgnum = 0

while rval:
  cv2.putText(frame, "x", (310,240), cv2.FONT_HERSHEY_PLAIN, 4.0, (255,0,0), thickness=3)
  cv2.imshow("preview", frame)
  rval, frame = camera.read()
  key = cv2.waitKey(20)
  if key == 32: # spacebar, take a picture
    cv2.imwrite(str(imgnum)+'.png',frame)
    imgnum += 1
  if key == 27: # exit on ESC
    break
cv2.destroyWindow("preview")
