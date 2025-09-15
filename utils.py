import re
import os
import dotenv
import pandas as pd
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import html
from langdetect import detect, LangDetectException

EXCLUDE_WORDS = ["tutorial",
            "analysis",
            "lesson",
            "fragment",
            "excerpt",
            "review",
            "preview",
            "shorts",
            "masterclass",
            "master class",
            "explanation",
            "guide",
            "demonstration",
            "practice",
            "explained",
            "walkthrough",
            "how to play",
            "how to perform",
            "how to improve",
            "how to learn"
]

SENTIMENT_MAP = {
    'very positive': 'positive',
    'positive': 'positive',
    'neutral': 'neutral',
    'negative': 'negative',
    'very negative': 'negative'
}

SENTIMENT_MAP_STARS = {
    '5 stars': 'positive',
    '4 stars': 'positive',
    '3 stars': 'neutral',
    '2 stars': 'negative',
    '1 star': 'negative'
}

SENTIMENT_MAP_SCORE = {
    'very positive': 1,
    'positive': 1,
    'neutral': 0,
    'negative': -1,
    'very negative': -1
}

SENTIMENT_MAP_STARS_SCORE = {
    '5 stars': 1,
    '4 stars': 1,
    '3 stars': 0,
    '2 stars': -1,
    '1 star': -1
}

def initialize_youtube_api():
    """
    Initialize the YouTube API.
    """
    dotenv.load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is not set in the environment variables")
    return build("youtube", "v3", developerKey=api_key)

# ISO 8601 to hh:mm:ss
def iso_to_hhmmss(iso_time):
    # Parse ISO 8601 duration format (PT#H#M#S)
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, iso_time)
    
    if not match:
        return "00:00:00"
    
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def is_performance_video(video_title):
    """
    Check if the video title is a performance video using the EXCLUDE_WORDS list.
    """
    title_lower = video_title.lower()
    for word in EXCLUDE_WORDS:
        clean_word = word.replace('"', '')
        pattern = r'\b' + re.escape(clean_word) + r'\b'
        if re.search(pattern, title_lower):
            print(f"Filtered out {video_title} because it contains {clean_word}")
            return False
    return True

def save_results_to_csv(data, filename):
    """
    Saves a list of dictionaries to a CSV file with UTF-8 encoding.
    
    Args:
        data (list): A list of dictionaries to save.
        filename (str): The name of the output CSV file.
        fieldnames (list): A list of strings for the CSV header.
    """
    if not data:
        print("No data to save.")
        return
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"Data saved to {filename}, total {len(data)} saved")

def preprocess_text(text):
    """
    Preprocess the text by:
    1. removing the HTML tags using BeautifulSoup
    2. removing the URLs using regex
    3. Decode the HTML entities
    4. Standardize the whitespace
    """
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.find_all('a'):
        a.decompose()
    text = soup.get_text()
    text = re.sub(r'(https?://|www\.)\S+', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text

def detect_language(text):
    """
    Detect the language of the text using the langdetect library.
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"
