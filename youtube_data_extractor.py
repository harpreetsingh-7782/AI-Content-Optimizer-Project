import os
import googleapiclient.discovery
import pandas as pd
from datetime import datetime, timedelta
import time
import random

# --- 1. Load API Credentials from credentials.py ---
try:
    from credentials import YOUTUBE_API_KEY
except ImportError:
    print("Error: YOUTUBE_API_KEY not found in credentials.py. Please add it.")
    exit()

# --- 2. Initialize YouTube API Client ---
# API service name and version
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Build the client
youtube = googleapiclient.discovery.build(
    API_SERVICE_NAME, API_VERSION, developerKey=YOUTUBE_API_KEY
)

# --- 3. Define Search Parameters ---
YOUTUBE_PRODUCT_SEARCH_TERMS = [
    # General Product Discovery
    "\"new product review\"",           # Exact phrase
    "\"product launch\"",               # Exact phrase
    "unboxing",
    "\"first look\"",
    "\"tech gadgets 2024\"",
    "\"innovation spotlight\"",
    
    # Industry-Specific
    "\"AI explained\"",                 # For AI trends/products
    "\"wearable tech\"",
    "\"electric vehicle news\"",
    "\"sustainable fashion brands\"",
    "\"food innovation\"",
    "\"health tech review\"",
    "\"smart home devices\"",
]

MAX_RESULTS_PER_QUERY = 50 # Max 50 per page, can get up to 500 per query with pagination
DAYS_AGO = 7 # Look for videos published in the last N days

def get_product_marketing_videos(search_terms, max_results=MAX_RESULTS_PER_QUERY, days_ago=DAYS_AGO):
    """
    Searches YouTube for product-centric videos and extracts relevant data.
    """
    all_video_data = []
    
    # Calculate `publishedAfter` for recent videos
    published_after = (datetime.utcnow() - timedelta(days=days_ago)).isoformat("T") + "Z"

    print(f"Starting YouTube data extraction for {len(search_terms)} terms, looking back {days_ago} days...")
    
    # Use a set to store unique video IDs to avoid duplicates
    seen_video_ids = set()

    for term in search_terms:
        print(f"\nSearching for term: '{term}'")
        try:
            # Perform the search request
            request = youtube.search().list(
                part="snippet",
                q=term,
                type="video", # We only want videos
                order="relevance", # Sort by relevance
                publishedAfter=published_after, # Only recent videos
                maxResults=max_results,
                relevanceLanguage="en", # Filter for English videos
            )
            response = request.execute()

            video_ids_for_stats = []
            if response.get('items'):
                print(f"  Found {len(response['items'])} potential videos for '{term}'")
                for item in response['items']:
                    video_id = item['id']['videoId']
                    if video_id not in seen_video_ids:
                        video_ids_for_stats.append(video_id)
                        seen_video_ids.add(video_id)
            else:
                print(f"  No videos found for '{term}' in the last {days_ago} days.")

            # If we found video IDs, get their statistics (views, likes, comments)
            if video_ids_for_stats:
                # Max 50 video IDs per videos.list request
                for i in range(0, len(video_ids_for_stats), 50):
                    batch_ids = video_ids_for_stats[i:i+50]
                    videos_request = youtube.videos().list(
                        part="snippet,statistics",
                        id=",".join(batch_ids)
                    )
                    videos_response = videos_request.execute()

                    for video_item in videos_response.get('items', []):
                        snippet = video_item['snippet']
                        stats = video_item.get('statistics', {}) # statistics might be missing for some videos

                        video_info = {
                            "platform": "YouTube",
                            "video_id": video_item['id'],
                            "search_term_matched": term,
                            "title": snippet['title'],
                            "description": snippet['description'],
                            "published_at": snippet['publishedAt'],
                            "channel_title": snippet['channelTitle'],
                            "channel_id": snippet['channelId'],
                            "view_count": stats.get('viewCount', 0),
                            "like_count": stats.get('likeCount', 0), # Likes might be disabled/hidden
                            "comment_count": stats.get('commentCount', 0), # Comments might be disabled
                            "tags": snippet.get('tags', []), # Hashtags in description or video tags
                            # You can add more fields if needed, e.g., default_thumbnail.url
                            "thumbnail_url": snippet['thumbnails']['high']['url'] if 'thumbnails' in snippet and 'high' in snippet['thumbnails'] else None,
                        }
                        all_video_data.append(video_info)
            
            # Be polite to the API
            time.sleep(random.randint(5, 15))

        except googleapiclient.errors.HttpError as e:
            print(f"  YouTube API HTTP Error for term '{term}': {e}")
            if e.resp.status == 403: # Forbidden, often means API Key issues or quota exceeded
                print("  Quota Exceeded or API Key issue. Check your Google Cloud Console for daily quota.")
                # You might want to break here if it's a hard quota
            elif e.resp.status == 400: # Bad Request
                print("  Bad request. Check your search query parameters.")
            print("  Skipping to next term due to API error.")
        except Exception as e:
            print(f"  An unexpected error occurred for term '{term}': {e}")

    return pd.DataFrame(all_video_data)

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting YouTube Product Marketing Video Extraction ---")
    youtube_videos_df = get_product_marketing_videos(YOUTUBE_PRODUCT_SEARCH_TERMS)

    if not youtube_videos_df.empty:
        output_csv_path = "youtube_product_marketing_videos.csv"
        youtube_videos_df.to_csv(output_csv_path, index=False)
        print(f"\nSuccessfully extracted {len(youtube_videos_df)} unique product-related YouTube videos.")
        print(f"Data saved to {output_csv_path}")
        print("\nFirst 5 rows of extracted data:")
        print(youtube_videos_df.head())

        # --- Integrate with Google Sheets ---
        try:
            from upload_to_sheets import upload_to_google_sheet
            print("\nAttempting to upload data to Google Sheets...")
            upload_to_google_sheet(youtube_videos_df, "AI_Content_Optimizer_Data", "YouTube_Product_Content")
        except ImportError:
            print("\nWarning: upload_to_sheets.py not found. Skipping Google Sheets upload.")
        except Exception as e:
            print(f"\nError uploading to Google Sheets: {e}")

    else:
        print("\nNo product marketing videos found or an error occurred during extraction.")
    print("\n--- YouTube Product Marketing Video Extraction Complete ---")


    # --- Slack Notification Integration ---
    from slack_notifier import send_slack_notification

    if send_slack_notification:
        slack_message = (
            f":sparkles: New YouTube product marketing videos found! :youtube:\n"
            f"Extracted {len(youtube_videos_df)} unique product-related YouTube videos.\n"
            f"Check the Google Sheet here: https://docs.google.com/spreadsheets/d/1aAdsgz9AagAOxkRSoxdaIaJ6N76U8G1xb4mPC-_h5HE/edit?usp=sharing\n" # IMPORTANT: Replace with actual link
            f"Worksheet: AI_Content_Optimizer_Data\n"
            f"Check: YouTube_Product_Content worksheet for the details."
        )
        send_slack_notification(slack_message)
        
    else:
        print("Slack notification function not available.")
    