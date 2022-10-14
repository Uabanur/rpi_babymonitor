import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import app

config = Config()
config.bind = "0.0.0.0:5000"
asyncio.run(serve(app.app, config))
