from server import mcp
from utils.predict_model import predict_score, setup_model

setup_model()

@mcp.tool()
def make_prediction(price: float, 
                    release_month: int, 
                    tags: list[str], 
                    genres: list[str], 
                    platforms: list[str]
                    ) -> float:
    return predict_score(price, release_month, tags, genres, platforms)

