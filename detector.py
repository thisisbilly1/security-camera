import cv2
import threading
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

    self.max_frame_rate = 30
    self.frame_interval = 1.0 / self.max_frame_rate

  def run(self):
    prev = 0
    while not self.stopped:
      with self.camera.lock:
        frame = self.camera.frame
      if frame is None:
        continue
      
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      # if a human is detected, save the frame
      # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      (boxes, weights) = self.hog.detectMultiScale(gray, winStride=(8,8))

      if len(boxes) > 0:
        self.humanDetectedFrames += 1
        if self.humanDetectedFrames >= self.humanDetectedFramesThreshold:
          self.camera.takePicture()
          self.humanDetectedFrames = 0
      else:
        self.humanDetectedFrames -= 1

      # sleep for the remaining frame interval time
      curr = time.time()
      diff = curr - prev
      if diff < self.frame_interval:
        time.sleep(self.frame_interval - diff)
      prev = curr

  def stop(self):
    self.stopped = True