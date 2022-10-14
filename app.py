import logger
import json
from camera_manager import CameraManager
from quart import Quart, render_template, make_response, request

app = Quart(__name__)
cam = CameraManager()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/video_feed')
async def video_feed():
    stream = cam.get_stream()
    mimetype = 'multipart/x-mixed-replace; boundary=frame'
    response = await make_response(stream)
    response.mimetype = mimetype
    response.timeout = None
    return response

@app.route('/move_camera', methods=['POST'])
async def move_camera():
    data = await request.get_json()
    logger.debug("move_camera: " + repr(data))
    x_change = data.get("x", None)
    y_change = data.get("y", None)

    if x_change == None or y_change == None:
        return "x and y coordinate required", 400

    cam.move_camera(x_change, y_change)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/zoom_camera', methods=['POST'])
async def zoom_camera():
    data = await request.get_json()
    logger.debug("zoom_camera: " + repr(data))
    zoom_change = data.get('zoom', None)
    if zoom_change == None:
        return "zoom change required", 400

    cam.zoom_camera(zoom_change)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/reset_camera', methods=['POST'])
def reset_camera():
    logger.debug("reset_camera")
    cam.reset_camera()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

if __name__ == "__main__":
    app.run(debug=True)
