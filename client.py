import socketio
import threading
import time

class Client(threading.Thread):
  def __init__(self):
    super(Client, self).__init__()
    self.uri = "http://localhost:4000"
    self.websocket = socketio.Client()

    self.websocket.on('connect', self.connect)
    self.websocket.on('disconnect', self.discconect)
    self.websocket.on('message', self.on_message)

    self.camera_name = "camera1"
    self.connected = False
    self.connecting = False
    self.daemon = True

  def connectToServer(self):
    if self.connecting:
      return
    self.connecting = True
    print('connecting to ws server')
    self.websocket.connect(self.uri, wait=True, wait_timeout=10)


  def on_message(self, id, data = None):
    if (id == 'pong'):
      self.pong()

  def pong(self):
    print('pong')
  
  def connect(self):
    print('connected to ws server')
    self.websocket.emit('cameraSetUp', self.camera_name)
    self.connected = True

  def discconect(self):
    self.connected = False
    print('disconnected from server... reconnecting')
    self.connectToServer()

  def send(self, id, data = None):
    if not self.connected:
      return
    if data is None:
      self.websocket.emit(id)
    else:
      self.websocket.emit(id, data)

  def run(self):
    while True:
      if not self.connected:
        self.connectToServer()
      self.send('ping')
      self.websocket.sleep(10)

if __name__ == "__main__":
  client = Client()
  client.start()

  while True:
    time.sleep(10)