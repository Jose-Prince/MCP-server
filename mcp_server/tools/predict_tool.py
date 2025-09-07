from server import mcp
from utils.predict_model import predict_score, setup_model

setup_model()

def register_predict_tool(mcp_instance):
    from utils.predict_model import predict_score
    
    @mcp_instance.tool()
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
            if tags is None:
                tags = []
            if genres is None:
                genres = []
            if platforms is None:
                platforms = []
            
            # Make prediction
            predicted_score = predict_score(
                price=price,
                release_month=release_month,
                tags=tags,
                genres=genres,
                platforms=platforms
            )
            
            return {
                "predicted_score": round(float(predicted_score), 2),
                "input_parameters": {
                    "price": price,
                    "release_month": release_month,
                    "tags": tags,
                    "genres": genres,
                    "platforms": platforms
                }
            }
        except Exception as e:
            return {
                "error": f"Prediction failed: {str(e)}",
                "predicted_score": None
            }
    
    @mcp_instance.tool()
    def get_sample_data() -> dict:
        """Get sample data for testing predictions"""
        return {
            "sample_tags": ["Action", "Adventure", "RPG", "Shooter", "Strategy"],
            "sample_genres": ["Action", "Adventure", "RPG", "Simulation", "Strategy"],
            "sample_platforms": ["PC", "PlayStation", "Xbox", "Nintendo Switch"],
            "example_prediction": {
                "price": 29.99,
                "release_month": 6,
                "tags": ["Action", "Adventure"],
                "genres": ["Action"],
                "platforms": ["PC", "PlayStation"]
            }
        }
    
    return make_prediction, get_sample_data
