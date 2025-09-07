import asyncio
from server import mcp, start_server
from tools.predict_tool import register_predict_tool

def setup_server():
    try:
        print("Setting up prediction model...")
        from utils.predict_model import setup_model
        setup_model()
        print("Model setup complete!")
    except Exception as e:
        print(f"Warning: Model setup failed: {e}")
        print("Continuing without model...")
    
    print("Registering prediction tools...")
    register_predict_tool(mcp)
    print("Tools registered!")
    
    print("FastMCP server configured and ready!")

if __name__ == "__main__":
    setup_server()
    
    print("Starting WebSocket server...")
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server failed: {e}")
