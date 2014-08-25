import cv2, math
import numpy as np

cv2.namedWindow("preview")
camera = cv2.VideoCapture(0)

if camera.isOpened(): # try to get the first frame
  rval, frame = camera.read()
else:
  rval = False

while rval:
  cv2.imshow("preview", frame)
  rval, frame = camera.read()
  key = cv2.waitKey(20)

  # create a mask
  mask = np.zeros(frame.shape[:2], np.uint8)
  mask[100:300, 100:400] = 255
  masked_frame = cv2.bitwise_and(frame,frame,mask = mask)

  # Calculate histogram with mask and without mask
  # Check third argument for mask
  hist_full = cv2.calcHist([frame],[0],None,[256],[0,256])
  hist_mask = cv2.calcHist([frame],[0],mask,[256],[0,256])
  print hist_mask

  if key == 27: # exit on ESC
    break
  
  while key != 32:
    key = cv2.waitKey(20)

cv2.destroyWindow("preview")
