import asyncio
import json
import logging
import websockets
from websockets.exceptions import ConnectionClosed
from fastmcp import FastMCP
import traceback
import inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("mcp_server")

class FastMCPWebSocketServer:
    def __init__(self, fastmcp_instance):
        self.fastmcp = fastmcp_instance
    
    async def handle_message(self, message_data: dict):
        try:
            if "method" not in message_data:
                return {
                    "jsonrpc": "2.0",
                    "id": message_data.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid request: missing method"
                    }
                }
            
            method = message_data["method"]
            params = message_data.get("params", {})
            request_id = message_data.get("id")
            
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "mcp_server",
                        "version": "1.0.0"
                    }
                }
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
                
            elif method == "tools/list":
                tools = []
                for tool_name, tool_func in self.fastmcp._tools.items():
                    sig = inspect.signature(tool_func)
                    doc = inspect.getdoc(tool_func) or f"Tool: {tool_name}"
                    
                    properties = {}
                    required = []
                    
                    for param_name, param in sig.parameters.items():
                        param_type = "string"
                        param_desc = f"Parameter {param_name}"
                        
                        if param.annotation != inspect.Parameter.empty:
                            if param.annotation == int:
                                param_type = "integer"
                            elif param.annotation == float:
                                param_type = "number"
                            elif param.annotation == bool:
                                param_type = "boolean"
                            elif param.annotation == list:
                                param_type = "array"
                            elif param.annotation == dict:
                                param_type = "object"
                        
                        properties[param_name] = {
                            "type": param_type,
                            "description": param_desc
                        }
                        
                        if param.default == inspect.Parameter.empty:
                            required.append(param_name)
                    
                    tool_def = {
                        "name": tool_name,
                        "description": doc,
                        "inputSchema": {
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }
                    }
                    tools.append(tool_def)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }
                
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                if tool_name in self.fastmcp._tools:
                    try:
                        result = await self._call_tool(tool_name, tool_arguments)
                        
                        if isinstance(result, dict):
                            result_text = json.dumps(result, indent=2)
                        else:
                            result_text = str(result)
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": result_text
                                    }
                                ],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        logger.error(f"Tool {tool_name} failed: {e}")
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text", 
                                        "text": f"Tool execution failed: {str(e)}"
                                    }
                                ],
                                "isError": True
                            }
                        }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling message: {e}\n{traceback.format_exc()}")
            return {
                "jsonrpc": "2.0",
                "id": message_data.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _call_tool(self, tool_name: str, arguments: dict):
        """Call a tool function with the given arguments"""
        tool_func = self.fastmcp._tools[tool_name]
        
        if asyncio.iscoroutinefunction(tool_func):
            return await tool_func(**arguments)
        else:
            return tool_func(**arguments)

websocket_server = FastMCPWebSocketServer(mcp)

async def websocket_handler(websocket):
    """Handle WebSocket connections"""
    client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}" if websocket.remote_address else "unknown"
    logger.info(f"New connection from {client_address}")
    
    try:
        async for raw_message in websocket:
            try:
                if isinstance(raw_message, str):
                    message_dict = json.loads(raw_message)
                else:
                    message_dict = json.loads(raw_message.decode('utf-8'))
                
                logger.debug(f"Received message: {message_dict}")
                
                response = await websocket_server.handle_message(message_dict)
                
                if response:
                    response_json = json.dumps(response)
                    await websocket.send(response_json)
                    logger.debug(f"Sent response: {response_json}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received from {client_address}: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    },
                    "id": None
                }
                await websocket.send(json.dumps(error_response))
                
            except Exception as e:
                logger.error(f"Error processing message from {client_address}: {e}\n{traceback.format_exc()}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    },
                    "id": message_dict.get('id') if 'message_dict' in locals() else None
                }
                await websocket.send(json.dumps(error_response))
                
    except ConnectionClosed:
        logger.info(f"Connection closed by {client_address}")
    except websockets.exceptions.WebSocketException as e:
        logger.warning(f"WebSocket error with {client_address}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error with {client_address}: {e}")
    finally:
        logger.info(f"Connection handler finished for {client_address}")

async def start_server(host="localhost", port=8765):
    """Start the WebSocket server"""
    logger.info(f"[MCP Server] WebSocket listening on ws://{host}:{port}")
    
    server = await websockets.serve(
        websocket_handler,
        host,
        port,
        ping_interval=20,
        ping_timeout=10,
        close_timeout=10
    )
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        server.close()
        await server.wait_closed()
        logger.info("Server shutdown complete")

__all__ = ['mcp', 'start_server']
