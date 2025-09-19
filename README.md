# Classical Music Performance Finder

A data-driven solution for discovering the most popular and critically acclaimed performances of classical music pieces available on YouTube. This project uses sentiment analysis of YouTube comments to rank and recommend the best performances of classical compositions.

## Overview

The Classical Music Performance Finder analyzes YouTube videos of classical music performances by:
1. **Searching and filtering** classical music videos on YouTube
2. **Collecting comments** from the most relevant videos
3. **Performing sentiment analysis** on comments using multilingual AI models
4. **Calculating performance scores** based on comment sentiment and engagement
5. **Providing recommendations** for both the highest-rated and most polarizing performances

## Features

- **Intelligent Video Filtering**: Automatically filters out tutorials, lessons, and non-performance content
- **Multilingual Sentiment Analysis**: Supports comments in multiple languages using state-of-the-art transformer models
- **Dual Recommendation System**: 
  - **Best Performance**: Highest overall sentiment score
  - **Most Polarizing**: Performance that generates the most diverse opinions
- **Comprehensive Scoring**: Considers comment sentiment, engagement metrics, and relevance scores
- **Data Export**: Saves intermediate results to CSV files for analysis (in verbose mode)

## How It Works

### 1. Video Search & Filtering (`Search_Filter.py`)
- Searches YouTube for videos matching the classical piece query
- Filters out non-performance content (tutorials, lessons, analysis videos, etc.)
- Collects video metadata (views, likes, comments, duration)
- Fetches up to 100 comments per video

### 2. Sentiment Analysis (`Analyze_Sentiment.py`)
- Preprocesses comments (removes HTML, URLs, standardizes text)
- Detects comment language automatically
- Uses specialized models:
  - English: `cardiffnlp/twitter-roberta-base-sentiment-latest`
  - Multilingual: `tabularisai/multilingual-sentiment-analysis`
- Assigns sentiment scores (-1 to +1) and labels

### 3. Score Calculation (`Calculate_Score.py`)
- Calculates weighted sentiment scores based on comment likes
- Computes total performance scores with relevance weighting
- Identifies polarization scores for controversial performances
- Applies statistical adjustments for small sample sizes

### 4. Recommendation Engine (`Performance_Analyzer.py`)
- Ranks performances by total sentiment score
- Identifies most polarizing performances from top candidates
- Provides direct YouTube links to recommended videos

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Classical-Music-Performance-Finder
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up YouTube API**:
   - Get a YouTube Data API v3 key from [Google Cloud Console](https://console.cloud.google.com/)
   - Create a `.env` file in the project root:
     ```
     YOUTUBE_API_KEY=your_api_key_here
     ```

## Usage

### Command Line Interface

```bash
python Performance_Analyzer.py "Mozart Violin Sonata in E minor" --verbose
```

**Parameters**:
- `query`: The classical music piece to search for (required)
- `--verbose`: Enable verbose mode to save intermediate CSV files (optional)

### Programmatic Usage

```python
from Performance_Analyzer import PerformanceAnalyzer

# Initialize analyzer
analyzer = PerformanceAnalyzer(api_key="your_api_key")

# Get recommendations
best_video_id, best_score, polarized_video_id, polarized_score, std_dev = analyzer.get_recommendations(
    "Beethoven Symphony No. 9", 
    verbose=True
)
```

## Output

The system provides two types of recommendations:

1. **Best Performance**: Video with the highest overall sentiment score
2. **Most Polarizing**: Video that generates the most diverse opinions (high polarization score)

Example output:
```
Recommendations with the highest total score:
Video ID: dQw4w9WgXcQ, Score: 8.45
Video URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Recommendations with the most polarized version:
Video ID: abc123def456, Polarization score: 0.78, Std deviation: 0.45
Video URL: https://www.youtube.com/watch?v=abc123def456
```

## Data Files

When using `--verbose` mode, the system generates several CSV files:

- `{query}_general_results.csv`: Video metadata and statistics
- `{query}_comments_results.csv`: Raw comment data
- `{query}_comments_results_with_sentiment.csv`: Comments with sentiment analysis
- `{query}_comments_results_with_final_scores.csv`: Final performance scores

## Dependencies

- `pandas`: Data manipulation and analysis
- `transformers`: Hugging Face transformer models for sentiment analysis
- `torch`: PyTorch for deep learning models
- `google-api-python-client`: YouTube Data API integration
- `beautifulsoup4`: HTML parsing for comment preprocessing
- `langdetect`: Language detection for comments
- `python-dotenv`: Environment variable management

## Limitations

⚠️ **Current Limitation**: The filtering system sometimes allows highly-ranked performances of pieces that are not related to the intended search query to survive the filter process and appear in the candidate list. These unrelated but trending videos may beat other valid candidates due to their popularity and appear in the recommendations. I am actively working on improving the filtering methods to address this issue.

⚠️ **Solo Performance Bias**: For solo performances, amateur music enthusiasts often post their attemps and improvement progress on YouTube. These videos may have substantial fan bases that leave encouraging comments, potentially causing them to rank higher in the current algorithm despite not being professional performances. This bias is less prevalent in symphonies and concertos, which are typically performed by established orchestras and professional musicians.

## Contributing

We welcome contributions to improve the filtering accuracy and recommendation quality. Areas for improvement include:

- Enhanced relevance scoring algorithms
- Better video title and content analysis
- Improved sentiment analysis models
- More sophisticated filtering criteria

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YouTube Data API v3 for video and comment access
- Hugging Face for pre-trained sentiment analysis models
- The classical music community for providing valuable feedback and test cases
