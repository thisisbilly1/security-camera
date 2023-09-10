import cv2
import time
import threading

class Camera(threading.Thread):
  def __init__(self):
    super(Camera, self).__init__()
    self.cap = cv2.VideoCapture(0)
    # self.cap = cv2.VideoCapture('test.mp4')

    self.frame = None
    self.lock = threading.Lock()
    self.stopped = False

    self.max_frame_rate = 30
    self.frame_interval = 1.0 / self.max_frame_rate

    self.nightMode = False
    
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

  def run(self):
    while not self.stopped:
      start_time = time.time()
      success, frame = self.cap.read()
      if not success:
        # If the video file ends, rewind it and continue streaming
        # self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
      with self.lock:
        self.frame = frame
      elapsed_time = time.time() - start_time
      if (elapsed_time < self.frame_interval):
        time.sleep(self.frame_interval - elapsed_time)
  
  def stop(self):
    self.stopped = True
    self.cap.release()