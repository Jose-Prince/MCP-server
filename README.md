# Game-predictor MCP Server

A Model Context Protocol (MCP) server that predicts video game scores using machine learning based on game characteristics like price, release month, tags, genres, and platforms.

## Purpose

This MCP server provides AI assistants with the capability to predict game scores (similar to Metacritic ratings) by analyzing various game attributes. It uses a Random Forest regression model trained on Steam game data to make predictions.

## Features

- **Score Prediction**: Predicts game scores (0-100 scale) based on game characteristics
- **Steam Data Integration**: Automatically collects game data from Steam API and SteamSpy
- **RAWG API Integration**: Retrieves additional platform information
- **Machine Learning**: Uses scikit-learn's Random Forest algorithm for predictions
- **MCP Protocol**: Compatible with Claude Desktop and other MCP clients

## Requirements

### Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### API Keys

You'll need a RAWG API key for platform data:

1. Sign up at [RAWG.io](https://rawg.io/apidocs)
2. Create a `.env` file in the project root:

```env
RAWG_KEY=your_rawg_api_key_here
```

## Installation & Setup

1. **Clone/Download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**:
   ```bash
   echo "RAWG_KEY=your_api_key" > .env
   ```
4. **Run the server**:
   ```bash
   python mcp_server/main.py
   ```

## How It Works

### Data Collection
- On first run, the server automatically creates a dataset by fetching game information from:
  - **SteamSpy**: Player statistics and tags
  - **Steam Store API**: Game details and pricing
  - **RAWG API**: Platform information and ratings
- Data is saved to `data/games_dataset.csv`

### Model Training
- Uses Random Forest regression with 200 estimators
- Features include: price, release month, encoded tags/genres/platforms, and player statistics
- Target variable: Game score (Metacritic or RAWG rating converted to 0-100 scale)

## Available Tools

### `make_prediction`

Predicts a game's score based on its characteristics.

**Parameters:**
- `price` (float): Game price in USD
- `release_month` (int): Month of release (1-12)
- `tags` (list[str]): List of game tags (e.g., ["Action", "Multiplayer"])
- `genres` (list[str]): List of game genres (e.g., ["Action", "Adventure"])
- `platforms` (list[str]): List of platforms (e.g., ["PC", "PlayStation 5"])

**Returns:** Predicted score (float, 0-100 scale)

## Usage Examples

Here are some example queries you can use with the MCP server:

### Basic Prediction
```
"Predict the score for a $29.99 action game releasing in December with tags 'Action' and 'Singleplayer', genre 'Action', on PC platform"
```

### Indie Game Prediction
```
"What score would you predict for an indie puzzle game costing $14.99, releasing in March, with tags ['Indie', 'Puzzle', 'Casual'], genres ['Indie', 'Casual'], and available on ['PC', 'Nintendo Switch']?"
```

### AAA Game Prediction
```
"Predict the score for a $59.99 AAA RPG releasing in November with tags ['RPG', 'Open World', 'Multiplayer'], genres ['Action', 'RPG'], on ['PC', 'PlayStation 5', 'Xbox Series X/S']"
```

### Free-to-Play Game
```
"What would be the predicted score for a free-to-play battle royale game (price: 0) releasing in June with tags ['Free to Play', 'Battle Royale', 'Multiplayer'], genres ['Action'], on ['PC', 'Mobile']?"
```

## File Structure

```
mcp_server/
├── main.py                 # Entry point
├── server.py              # FastMCP server setup
├── tools/
│   └── predict_tool.py    # Prediction tool definition
├── utils/
│   ├── game.py           # Game data collection utilities
│   └── predict_model.py  # ML model setup and prediction
├── data/                 # Generated dataset storage
│   └── games_dataset.csv # Game data (auto-generated)
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables (you create this)
```

## Configuration with Claude Desktop

To use this server with Claude Desktop, add it to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "game-predictor": {
      "command": "python",
      "args": ["/path/to/your/mcp_server/main.py"],
      "env": {
        "RAWG_KEY": "your_rawg_api_key_here"
      }
    }
  }
}
```

## Limitations

- **Dataset Size**: Initially limited to 1000 games to avoid API rate limits
- **API Dependencies**: Requires internet connection for RAWG API
- **Rate Limiting**: Includes 1-second delays between API calls
- **Data Quality**: Predictions depend on the quality of training data
- **Regional Variations**: Scores may not reflect regional preferences

## Troubleshooting

### Common Issues

1. **"games_dataset.csv not found"**: 
   - This is normal on first run. The server will automatically create the dataset.

2. **API Rate Limiting**:
   - The server includes built-in delays to respect API limits
   - If you encounter rate limits, wait before retrying

3. **Model Not Trained Error**:
   - Ensure `setup_model()` is called before making predictions
   - Check that the CSV file was created successfully

4. **Missing RAWG API Key**:
   - Verify your `.env` file exists and contains the correct API key
   - Ensure the key is valid and active
