import cv2, math, os
import numpy

focusWindowSize = 0.3 # the portion of the frame that is masked (center)

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

# create a focusWindow
height, width = frame.shape[:2]
focusWindow = numpy.zeros((height,width), numpy.uint8)
vborder = (height*(1-focusWindowSize))/2
hborder = (width*(1-focusWindowSize))/2
focusWindow[vborder:height-vborder, hborder:width-hborder] = 255

while rval:
  # Calculate histogram with mask and without mask
  # Check third argument for mask
  hist_full = cv2.calcHist([frame],[0],None,[256],[0,256])
  hist_focusWindow = cv2.calcHist([frame],[0],focusWindow,[256],[0,256])

  histogram = [item for sublist in hist_focusWindow for item in sublist]

  histogram_length = sum(histogram)

  samples_probability = [float(h) / histogram_length for h in histogram]

  entropy = -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

  print entropy

  cv2.imshow("preview", frame)
  # key = cv2.waitKey(20)
  # cv2.imshow("preview", focusWindow) # show the focus window for comparison
  rval, frame = camera.read()
  key = cv2.waitKey(20)

  if key in {27,32}: # exit on ESC or space
    break
  
cv2.destroyWindow("preview")
