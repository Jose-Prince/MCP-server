import asyncio
import websockets
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp_server")

async def websockter_handler(websocket):
    async for message in websocket:
        response = await mcp.handle_message(message)
        if response:
            await websocket.send(response)

async def start_server(host="localhost", port=8765):
    print(f"[MCP Server] Websocket listening in ws://{host}:{port}")
    async with websockets.serve(websockter_handler, host, port):
        await asyncio.Future()
