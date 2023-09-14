import cv2
from camera import Camera
from flask import Flask, Response, request, send_from_directory
from client import Client
from detector import Detector
import glob

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


@app.route('/activities')
def activities():
    # read the files in the ./images directory
    files = glob.glob('./images/*.jpg')
    # sort the files by the timestamp in the filename
    files.sort(key=lambda x: int(x.split('/')[2].split('.')[0]))
    # reverse the list so that the newest files are first
    files.reverse()
    # only return the 10 newest files
    files = files[:10]
    # remove the ./images/ prefix from the filenames & the .jpg suffix
    files = [f.split('/')[2].split('.')[0] for f in files]
    # return the list of files
    return {'activities': files}

@app.route('/image')
def getImage():
    # get the imageId from the query params
    imageId = request.args.get('imageId')
    print('loading image: ' + imageId)
    # load the image with opencv
    img = cv2.imread('./images/' + imageId + '.jpg')
    ret, buffer = cv2.imencode('.jpg', img)
    frame_bytes = buffer.tobytes()
    return Response(frame_bytes, mimetype='image/jpeg')

if __name__ == '__main__':
    ws_client = Client(camera)
    ws_client.start()

    detector = Detector(camera)
    detector.start()

    app.run(host='0.0.0.0', port=5000)