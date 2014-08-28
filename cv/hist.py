import cv2, math, os
import numpy as np

os.environ["DISPLAY"] = ":0" # tell it to open the camera on the local machine even if we're remote
cv2.namedWindow("preview")
camera = cv2.VideoCapture(0)

if camera.isOpened(): # try to get the first frame
  rval, frame = camera.read()
else:
  rval = False

cv2.imshow("preview", frame)
rval, frame = camera.read()
key = cv2.waitKey(20)

while rval:
  # create a mask
  mask = np.zeros(frame.shape[:2], np.uint8)
  mask[100:300, 100:400] = 255
  masked_frame = cv2.bitwise_and(frame,frame,mask = mask)

  # Calculate histogram with mask and without mask
  # Check third argument for mask
  hist_full = cv2.calcHist([frame],[0],None,[256],[0,256])
  hist_mask = cv2.calcHist([frame],[0],mask,[256],[0,256])

  histogram = [item for sublist in hist_full for item in sublist]

  histogram_length = sum(histogram)

  samples_probability = [float(h) / histogram_length for h in histogram]

  entropy = -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

  print entropy

  cv2.imshow("preview", frame)
  rval, frame = camera.read()
  key = cv2.waitKey(20)

  if key == 27: # exit on ESC
    break
  
cv2.destroyWindow("preview")
