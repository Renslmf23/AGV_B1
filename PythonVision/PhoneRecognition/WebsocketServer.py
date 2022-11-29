import asyncio
import datetime
import time

import websockets


class WebSocketServer:

    def __init__(self, host, port, secret):
        self._secret = secret
        self._server = websockets.serve(self._start, host, port)

    def start(self):
        asyncio.get_event_loop().run_until_complete(self._server)
        asyncio.get_event_loop().run_forever()

    async def _start(self, websocket, path):
        print(f"Connected from path ={path}")
        while True:
            secret = await websocket.recv()
            if secret == self._secret:
                time.sleep(0.01)
                msg = f"Sending message {datetime.datetime.now()}"
                await websocket.send(msg)
                print(msg)


if __name__ == "__main__":
    server = WebSocketServer("localhost", 11225, "CameraRecognizer")
    server.start()