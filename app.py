import logger
import json
from camera_manager import CameraManager
from quart import Quart, render_template, make_response, request

app = Quart(__name__)
cam = CameraManager()


success_response = tuple(
    content=json.dumps({'success': True}),
    headers={'ContentType': 'application/json'},
    status_code=200
)


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/video')
async def video():
    return await render_template('video.html')


@app.route('/video_feed')
async def video_feed():
    stream = cam.get_stream()
    response = await make_response(stream)
    response.mimetype = 'multipart/x-mixed-replace; boundary=frame'
    response.timeout = None
    return response


@app.route('/move_camera', methods=['POST'])
async def move_camera():
    data = await request.get_json()
    logger.debug("move_camera: " + repr(data))
    x_change = data.get("x", None)
    y_change = data.get("y", None)

    if x_change is None or y_change is None:
        return "x and y coordinate required", 400

    cam.move_camera(x_change, y_change)
    return success_response


@app.route('/zoom_camera', methods=['POST'])
async def zoom_camera():
    data = await request.get_json()
    logger.debug("zoom_camera: " + repr(data))
    zoom_change = data.get('zoom', None)
    if zoom_change is None:
        return "zoom change required", 400

    cam.zoom_camera(zoom_change)
    return success_response


@app.route('/reset_camera', methods=['POST'])
def reset_camera():
    logger.debug("reset_camera")
    cam.reset_camera()
    return success_response


if __name__ == "__main__":
    app.run(debug=True)
