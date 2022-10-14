import logger
import math
import picamera
from io import BytesIO
import asyncio

class Camera:
    def __init__(self):
        self.resolution = 720
        self.ratio = 4/3
        self.frame_rate = 2
        self.zoom = tuple((0, 0, 1, 1))

    async def connect(self):
        cam = picamera.PiCamera()
        cam.resolution = (math.ceil(self.resolution * self.ratio), self.resolution)
        cam.framerate = self.frame_rate
        cam.zoom = self.zoom
        await asyncio.sleep(2)
        return cam
    
    async def get_picture(self):
        with await self.connect() as camera:
            output = BytesIO()
            camera.capture(output, 'jpeg')
            output.seek(0)
            return output.read()

    def frame_from_stream(self, stream):
        stream.seek(0)
        return (b'--frame\r\n'
             b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')  

    async def get_stream(self):
        try:
            logger.debug("Starting stream")
            with await self.connect() as camera:
                stream = BytesIO()
                for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                    yield self.frame_from_stream(stream)
                    stream.seek(0)
                    stream.truncate()
                    camera.zoom = self.zoom
        finally:
            logger.debug("Terminating stream")
