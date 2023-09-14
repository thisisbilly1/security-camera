import cv2
import time
import os
import threading

class Camera(threading.Thread):
  def __init__(self):
    super(Camera, self).__init__()

    # create ./images directory if it doesn't exist
    if not os.path.exists('./images'):
      os.makedirs('./images')

    self.cap = cv2.VideoCapture(0)
    # self.cap = cv2.VideoCapture('test.mp4')

    # set the max resolution to 960x720
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    self.frame = None
    self.lock = threading.Lock()
    self.stopped = False

    self.max_frame_rate = 60
    self.frame_interval = 1.0 / self.max_frame_rate

    self.nightMode = False
    self.flipHorizontal = False
    self.flipVertical = False
    
    # set the daemon thread to true so that the thread will stop when the main thread stops
    self.daemon = True
  
  def toggleNightMode(self):
    self.nightMode = not self.nightMode
    if self.nightMode:
      self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
      self.cap.set(cv2.CAP_PROP_EXPOSURE, 0.01)
    else:
      self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
      self.cap.set(cv2.CAP_PROP_EXPOSURE, 0.25)

  def takePicture(self):
    with self.lock:
      frame = self.frame
    if frame is None:
      return
    # save the frame to ./images with the timestamp as the filename
    cv2.imwrite('./images/' + str(int(time.time())) + '.jpg', frame)

  def run(self):
    prev = 0
    while not self.stopped:
      success, frame = self.cap.read()
      if not success:
        # If the video file ends, rewind it and continue streaming
        # self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
      # flip the camera vertically & horizontally if needed
      if self.flipHorizontal:
        frame = cv2.flip(frame, 1)
      if self.flipVertical:
        frame = cv2.flip(frame, 0)
      self.frame = frame
      
      # sleep for the remaining frame interval time
      curr = time.time()
      diff = curr - prev
      if diff < self.frame_interval:
        time.sleep(self.frame_interval - diff)
      prev = curr
  
  def stop(self):
    self.stopped = True
    self.cap.release()
