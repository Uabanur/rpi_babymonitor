import threading
from camera import Camera
import logger
from PIL import Image
from io import BytesIO
import asyncio

class CameraManager:
    def __init__(self):
        logger.debug("Initializing camera manager")
        self.camera = Camera()
        self.clients = 0
        self.manager_lock = threading.Lock()
        self.frame_lock = threading.Lock()
        self.last_frame = None
        self.last_frame_count = 0
        self.stream_thread = None
        self.stream_running = False
        self.connecting_frame = self._load_connecting_frame()

    def _get_frame(self):
        if self.last_frame:
            return self.last_frame
        if self.connecting_frame:
            return self.connecting_frame
        return None

    def _load_connecting_frame(self):
        try:
            img = Image.open('images/connecting.jpg')
            stream = BytesIO()
            img.save(stream, format='JPEG')
            return self.camera.frame_from_stream(stream)
        except Exception as e: 
            logger.error("Failed to load connecting frame. " + str(e))

    def add_client(self):
        logger.debug("add_client invoked")
        with self.manager_lock:
            logger.debug("Adding client")
            if self.clients == 0:
                self.start_stream()

            self.clients += 1
            logger.debug(f"Total clients: {self.clients}")

    def remove_client(self):
        logger.debug("remove_client invoked")
        with self.manager_lock:
            logger.debug("Removing client")
            self.clients -= 1
            logger.debug(f"Total clients: {self.clients}")
            if self.clients == 0:
                self.stop_stream()

    async def stream_job(self):
        logger.debug("stream_job invoked")
        stream = self.camera.get_stream()
        async for frame in stream:
            with self.frame_lock:
                self.last_frame = frame
                self.last_frame_count += 1

            if not self.stream_running:
                logger.debug("stream runnning flag is false")
                await stream.aclose()
        logger.debug("Stream job finished")

    def start_stream(self):
        logger.debug("start_stream invoked")
        if self.stream_thread:
            logger.debug("stream is not None")
        else:
            self.stream_running = True
            self.stream_thread = threading.Thread(target=asyncio.run, args=(self.stream_job(),))
            self.stream_thread.start()

    def stop_stream(self):
        logger.debug("stop_stream invoked")
        if not self.stream_thread:
            logger.debug("Stream is already none")
            return

        self.stream_running = False
        self.stream_thread.join()
        self.stream_thread = None
        self.last_frame = None
        self.last_frame_count = 0
        logger.debug("stream stopped")

    async def get_stream(self):
        logger.debug("get_stream invoked")

        try:
            self.add_client()
            while True:
                with self.frame_lock:
                    frame = self._get_frame()

                if not frame:
                    await asyncio.sleep(0.3)
                    continue

                yield frame
                await asyncio.sleep(0.3)
        finally:
            self.remove_client()

    def _limit_state(self, state):
        x,y,zx,zy = state
        if x < 0: x = 0
        if y < 0: y = 0
        if x > 1-zx: x = 1-zx
        if y > 1-zy: y = 1-zy
        return (x,y,zx,zy)

    def _add_tuples_limited01(self, state, change):
        return self._limit_state(tuple(a+b for a,b in zip(state,change)))

    def _set_camera(self, state):
        logger.debug(f"camera updated to state: {state}")
        self.camera.zoom = tuple(state)

    def _change_camera(self, diff):
        self._set_camera(
            self._add_tuples_limited01(
                    self.camera.zoom,
                    diff))

    def move_camera(self, x,y):
        logger.debug(f"move camera: x:{x}, y:{y}")
        # scale movement by zoom level
        _,_,zx,zy = self.camera.zoom
        self._change_camera((zx*x,zy*y,0,0))

    def zoom_camera(self, zoom):
        logger.debug(f"zoom camera: zoom:{zoom}")
        # move x and y by half zoom to center the zoom focus
        self._change_camera((-zoom/2,-zoom/2,zoom,zoom))

    def reset_camera(self):
        logger.debug("reset camera")
        self._set_camera((0, 0, 1, 1))

