from googleapiclient.discovery import build
import os
import dotenv

# Load the API key from the .env file
dotenv.load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")

# Build the YouTube API client
youtube = build("youtube", "v3", developerKey=api_key)

# Make the API request
request = youtube.videos().list(
    part="snippet, statistics",
    id="OflReU5RlZM"
)

# Execute the request
response = request.execute()

# Print the response
if "items" in response and len(response["items"]) > 0:
    video = response["items"][0]
    snippet = video["snippet"]
    statistics = video["statistics"]
    print(f"Title: {snippet['title']}")
    print(f"Description: {snippet['description']}")
    print(f"Published at: {snippet['publishedAt']}")
    print(f"View count: {statistics['viewCount']}")
    print(f"Like count: {statistics['likeCount']}")
    print(f"Comment count: {statistics['commentCount']}")
else:
    print("No response from the API")

