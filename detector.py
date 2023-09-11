import cv2
import threading
import os
import time

class Detector(threading.Thread):
  def __init__(self, camera):
    super(Detector, self).__init__()
    self.camera = camera
    self.hog = cv2.HOGDescriptor()
    self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    self.daemon = True
    self.stopped = False

    self.humanDetectedFramesThreshold = 10
    self.humanDetectedFrames = 0

    # create ./images directory if it doesn't exist
    if not os.path.exists('./images'):
      os.makedirs('./images')

  def run(self):
    while not self.stopped:
      with self.camera.lock:
        frame = self.camera.frame
      if frame is None:
        continue
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      boxes, weights = self.hog.detectMultiScale(gray, winStride=(8,8))
      if len(boxes) > 0:
        self.humanDetectedFrames += 1
        if self.humanDetectedFrames >= self.humanDetectedFramesThreshold:
          self.saveFrame()
      else:
        self.humanDetectedFrames = 0
  
  def saveFrame(self):
    with self.camera.lock:
      frame = self.camera.frame
    if frame is None:
      return

    # save the frame to ./images with the timestamp as the filename
    cv2.imwrite('./images/' + str(int(time.time())) + '.jpg', frame)

  def stop(self):
    self.stopped = True