import asyncio

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
clients = set()
tasks = set()


async def read_card():
    while True:
        _, text = reader.read()
        if text:
            broadcast(text)
        await asyncio.sleep(1)


async def send_message(websocket, message):
    try:
        await websocket.send(message)
    except ConnectionClosed:
        pass


def broadcast(message):
    for websocket in clients:
        asyncio.create_task(send_message(websocket, message))


async def handler(websocket):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)


async def run_server():
    async with serve(handler, port=8765):
        await asyncio.get_running_loop().create_future()


async def main():
    tasks.add(asyncio.create_task(run_server()))
    tasks.add(asyncio.create_task(read_card()))


asyncio.run(main())
