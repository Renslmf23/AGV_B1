import asyncio
import websockets


class WebSocketClient:
    def __init__(self, host, port, secret):
        self._secret = secret
        self._host = host
        self._port = port

    def start(self):
        asyncio.get_event_loop().run_until_complete(self._start_receiving())

    async def _start_receiving(self):
        url = f'ws://{self._host}:{self._port}/websocket-blog'
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(self._secret)
                while True:
                    await websocket.send(self._secret)
                    response = await websocket.recv()
                    print(f'Received Message: {response}')
        except websockets.ConnectionClosed as ex:
            print(ex)
            raise


if __name__ == "__main__":
    client = WebSocketClient("localhost", 11225, "CameraRecognizer")
    client.start()
