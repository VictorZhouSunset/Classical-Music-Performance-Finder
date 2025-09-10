import re
import time
import os
import dotenv
import pandas as pd
from googleapiclient.discovery import build

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

def save_results_to_csv(data, filename, fieldnames):
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


