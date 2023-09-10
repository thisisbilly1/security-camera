import cv2
from camera import Camera
from flask import Flask, Response
from client import Client

app = Flask(__name__)

camera = Camera()
camera.start()

def generate_frames():
    while True:
        with camera.lock:
            frame = camera.frame.copy()
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/thumbnail')
def thumbnail():
    with camera.lock:
        frame = camera.frame
    if frame is not None:
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            return Response(status=500)
        frame_bytes = buffer.tobytes()
        return Response(frame_bytes, mimetype='image/jpeg')
    else:
        return Response(status=500)

if __name__ == '__main__':
    ws_client = Client(camera)
    ws_client.start()
    app.run(host='0.0.0.0', port=5000)