import asyncio
from mcp.server import run_local_server
from mcp.types import TextContent

from predict_model import setup_model, predict_score

def main():
    setup_model()

    async def predict_tool(price=None, release_month=None, tags=None, genres=None, platforms=None):
        try:
            score = predict_score(price, release_month, tags, genres, platforms)
            return [TextContent(type="text", text=f"Score: {score:.2f}/100")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error making prediction: {e}")]

    run_local_server(
        tools=[
            {
                "name": "predict_score",
                "description": "Predict game score of a custom game",
                "func": predict_tool
            }
        ],
        server_name="game-score-model"
    )

if __name__ == "__main__":
    main()

