import asyncio
import websockets

# Храним все активные подключения
CONNECTIONS = set()


async def broadcast(sender, message: str) -> None:
    """Отправить сообщение всем клиентам, кроме отправителя."""
    dead_connections = []

    for conn in CONNECTIONS:
        if conn is sender:
            continue
        try:
            await conn.send(message)
        except Exception:
            dead_connections.append(conn)

    for conn in dead_connections:
        CONNECTIONS.discard(conn)


async def handler(websocket):
    CONNECTIONS.add(websocket)
    try:
        async for message in websocket:
            await broadcast(websocket, message)
    finally:
        CONNECTIONS.discard(websocket)


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Signaling server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())