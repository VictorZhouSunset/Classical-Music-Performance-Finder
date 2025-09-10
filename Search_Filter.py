from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import dotenv
import pandas as pd
from utils import iso_to_hhmmss, initialize_youtube_api, is_performance_video, save_results_to_csv
from utils import EXCLUDE_WORDS

youtube = initialize_youtube_api()

def get_comments(video_id, num_comments=100):
    """
    Get the comments for a video.
    """
    comments = []

    comments_request = youtube.commentThreads().list(
        part="id, snippet",
        videoId=video_id,
        maxResults=num_comments
    )
    comments_response = comments_request.execute()
    for comment in comments_response.get("items", []):
        top_level_comment = comment.get("snippet", {}).get("topLevelComment", {})
        comment_snippet = top_level_comment.get("snippet", {})
        comments.append({
            "comment_id": top_level_comment.get("id", "N/A"),
            "author": comment_snippet.get("authorDisplayName", "N/A"),
            "text": comment_snippet.get("textDisplay", "N/A"),
            "like_count": comment_snippet.get("likeCount", "N/A")
            # "published_at": comment_snippet.get("publishedAt", "N/A")
        })
    return comments

def search_and_filter(search_query, num_candidates=50, min_duration_in_seconds=None, verbose=False):
    """
    Search for videos on YouTube and filter them based on the search query.
    """
    print(f"--- Starting search for {search_query} with {num_candidates} candidates ---")

    # Make the API request
    if verbose:
        print(f"--- Making YouTube API request for {search_query} with {num_candidates} candidates ---")
    search_request = youtube.search().list(
        part="id, snippet",
        q=search_query,
        type="video",
        maxResults=num_candidates
    )
    # Execute the request
    search_response = search_request.execute()

    # Filter the videos
    print(f"--- Filtering {num_candidates} videos ---")
    filtered_video_ids = []
    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        video_title = item["snippet"]["title"]
        if is_performance_video(video_title):
            filtered_video_ids.append(video_id)
    print(f"--- Filtering done! {len(filtered_video_ids)} videos left after filtering ---")
    if not filtered_video_ids:
        print("--- No videos left after filtering ---")
        return

    # Get the video information
    v_request = youtube.videos().list(
        part="snippet, statistics, contentDetails",
        id=",".join(filtered_video_ids)
    )
    v_response = v_request.execute()

    # Save the video information
    video_general_results = []
    video_comments_results = []
    video_with_comments = 0
    for video in v_response.get("items", []):
        video_id = video["id"]
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        contentDetails = video.get("contentDetails", {})
        duration = iso_to_hhmmss(contentDetails.get('duration', 'PT0S'))
        # Filter out videos that are less than the minimum duration
        duration_in_seconds = int(duration.split(':')[0]) * 3600 + int(duration.split(':')[1]) * 60 + int(duration.split(':')[2])
        if min_duration_in_seconds and duration_in_seconds < min_duration_in_seconds:
            print(f"Filtered out {snippet.get('title', 'N/A')} because it is less than {min_duration_in_seconds} seconds")
            continue
        video_general_results.append({
            "video_id": video["id"],
            "title": snippet.get('title', 'N/A'),
            "duration": duration,
            "view_count": statistics.get('viewCount', 'N/A'),
            "like_count": statistics.get('likeCount', 'N/A'),
            "comment_count": statistics.get('commentCount', 'N/A'),
        })
        # Fetch the comments
        try:
            print(f"Fetching the first 100 comments for {snippet.get('title', 'N/A')}")
            comments = get_comments(video_id)
            if comments:
                video_with_comments += 1
            print(f"Fetched {len(comments)} comments for {snippet.get('title', 'N/A')}")
        except HttpError as e:
            if verbose:
                print(f"Error fetching comments for {snippet.get('title', 'N/A')}: {e}")
            else:
                print(f"Error fetching comments for {snippet.get('title', 'N/A')}")
            if e.resp.status == 403:
                print(f"Error Details: Maybe the comments of the video are turned off")
            comments = []
        for comment in comments:
            video_comments_results.append({
                "video_id": video_id,
                "comment_id": comment["comment_id"],
                "author": comment["author"],
                "text": comment["text"],
                "like_count": comment["like_count"]
            })
    return video_general_results, video_comments_results, video_with_comments

def main():
    """
    Main workflow for the project.
    """
    search_query = "Mozart Violin Sonata in E minor"
    video_general_results, video_comments_results, video_with_comments = search_and_filter(search_query, num_candidates=50, min_duration_in_seconds=65)
    # fieldnames, see func search_and_filter
    video_fieldnames = ['video_id', 'title', 'duration', 'view_count', 'like_count', 'comment_count']
    comment_fieldnames = ['video_id', 'comment_id', 'author', 'text', 'like_count']
    filename_general = f"{search_query.replace(' ', '_')}_general_results.csv"
    filename_comments = f"{search_query.replace(' ', '_')}_comments_results.csv"
    # save results to csv for both video and comment
    if video_general_results:
        save_results_to_csv(video_general_results, filename_general, video_fieldnames)
    else:
        print("No videos found.")
    if video_comments_results:
        save_results_to_csv(video_comments_results, filename_comments, comment_fieldnames)
    else:
        print("No video comments found.")
    # print summary
    print(f"\nSummary:")
    print(f"Search query: {search_query}")
    print(f"Total videos found: {len(video_general_results)}")
    print(f"Total videos with comments: {video_with_comments}")
    print(f"Results saved to: {filename_general} and {filename_comments}")

if __name__ == "__main__":
    main()
        