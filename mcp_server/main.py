#!/usr/bin/env python3
"""
MCP Server using FastMCP from the official MCP Python SDK
"""

from mcp.server.fastmcp import FastMCP
import json

# Import your prediction functions
try:
    from utils.predict_model import predict_score, setup_model
    setup_model()
    print("✅ Model setup complete!")
    MODEL_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Warning: Model setup failed: {e}")
    MODEL_AVAILABLE = False
    predict_score = None

# Create FastMCP server
mcp = FastMCP("Game Prediction Server")

@mcp.tool()
def make_prediction(
    price: float = None, 
    release_month: int = None, 
    tags: list = None, 
    genres: list = None, 
    platforms: list = None
) -> dict:
    """
    Predict a game's score based on its characteristics.
    
    Args:
        price: Game price in dollars (optional)
        release_month: Month of release (1-12, optional)
        tags: List of game tags (optional)
        genres: List of game genres (optional)  
        platforms: List of platforms (optional)
        
    Returns:
        Dictionary with predicted score and input parameters
    """
    try:
        if not MODEL_AVAILABLE or predict_score is None:
            return {
                "error": "Prediction model not available",
                "predicted_score": None,
                "input_parameters": {
                    "price": price,
                    "release_month": release_month,
                    "tags": tags or [],
                    "genres": genres or [],
                    "platforms": platforms or []
                }
            }
        
        # Set defaults if None
        if tags is None:
            tags = []
        if genres is None:
            genres = []
        if platforms is None:
            platforms = []
        
        print(f"🎯 Making prediction with: price={price}, month={release_month}, tags={tags}, genres={genres}, platforms={platforms}")
        
        # Make prediction
        predicted_score = predict_score(
            price=price,
            release_month=release_month,
            tags=tags,
            genres=genres,
            platforms=platforms
        )
        
        result = {
            "predicted_score": round(float(predicted_score), 2),
            "input_parameters": {
                "price": price,
                "release_month": release_month,
                "tags": tags,
                "genres": genres,
                "platforms": platforms
            }
        }
        
        print(f"✅ Prediction result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Prediction failed: {str(e)}",
            "predicted_score": None,
            "input_parameters": {
                "price": price,
                "release_month": release_month,
                "tags": tags or [],
                "genres": genres or [],
                "platforms": platforms or []
            }
        }

@mcp.tool()
def get_sample_data() -> dict:
    """Get sample data for testing predictions"""
    return {
        "sample_tags": ["Action", "Adventure", "RPG", "Shooter", "Strategy", "Indie", "Simulation", "Sports"],
        "sample_genres": ["Action", "Adventure", "RPG", "Simulation", "Strategy", "Sports", "Racing"],
        "sample_platforms": ["PC", "PlayStation", "Xbox", "Nintendo Switch", "Mobile"],
        "example_predictions": [
            {
                "description": "Indie action game",
                "price": 19.99,
                "release_month": 3,
                "tags": ["Action", "Adventure", "Indie"],
                "genres": ["Action"],
                "platforms": ["PC", "PlayStation"]
            },
            {
                "description": "AAA RPG",
                "price": 59.99,
                "release_month": 11,
                "tags": ["RPG", "Adventure", "Open World"],
                "genres": ["RPG", "Adventure"],
                "platforms": ["PC", "PlayStation", "Xbox"]
            },
            {
                "description": "Free mobile game",
                "price": 0.0,
                "release_month": 6,
                "tags": ["Casual", "Mobile"],
                "genres": ["Casual"],
                "platforms": ["Mobile"]
            }
        ]
    }

@mcp.tool()
def health_check() -> dict:
    """Check if the server and prediction model are working"""
    return {
        "server_status": "healthy",
        "model_available": MODEL_AVAILABLE,
        "prediction_function": predict_score is not None,
        "message": "Server is running normally" if MODEL_AVAILABLE else "Server running but prediction model unavailable"
    }

if __name__ == "__main__":
    print("🚀 Starting Game Prediction MCP Server...")
    print(f"📊 Model available: {MODEL_AVAILABLE}")
    
    # Run the server - this will use stdio transport by default
    mcp.run()
