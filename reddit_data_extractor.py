import praw
import pandas as pd
from datetime import datetime
import time
import random
import os

# --- 1. Load API Credentials from credentials.py ---
try:
    from credentials import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
except ImportError:
    print("Error: Reddit API credentials not found in credentials.py. Please add them.")
    exit()

# --- 2. Initialize PRAW Reddit Instance ---
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent="AI_Content_Optimizer_Bot_v1.0 (by /u/YOUR_REDDIT_USERNAME_HERE)" # Replace with your Reddit username
)

# --- 3. Define Search Parameters ---
# A list of subreddits to monitor for product-related content
TARGET_SUBREDDITS = [
    "technology", "gadgets", "futurology", "innovation", "tech",
    "artificialintelligence", "MachineLearning", "programming",
    "wearables", "smartwatch",
    "electricvehicles", "cars", "automotive",
    "food", "plantbased", "vegan",
    "health", "medtech", "digitalhealth",
    "fashion", "malefashionadvice", "femalefashionadvice", "sustainablefashion",
    "products", "BuyItForLife", "DidYouKnow",
    "AskReddit" # For broader discussions, will need specific search queries
]

# General search terms to use if searching across multiple subreddits or in 'AskReddit'
REDDIT_PRODUCT_SEARCH_TERMS = [
    "\"new product\"",
    "\"product launch\"",
    "\"review\"",
    "\"best tech 2024\"",
    "\"future of AI\"",
    "\"new phone\"",
    "\"new headphones\"",
    "\"electric car\"",
    "\"smart home\"",
    "\"AI trend\"",
    "\"wearable technology\""
]

LIMIT_PER_SUBREDDIT = 25 # How many posts to fetch from each subreddit (hot/new/top)
LIMIT_PER_SEARCH_TERM = 25 # How many posts to fetch per general search term
TIME_FILTER = "week" # 'day', 'week', 'month', 'year', 'all' for top/controversial posts

def get_reddit_product_posts(subreddits, search_terms, limit_sub=LIMIT_PER_SUBREDDIT, limit_search=LIMIT_PER_SEARCH_TERM, time_filter=TIME_FILTER):
    """
    Fetches product-centric posts from specified subreddits and general searches on Reddit.
    """
    all_posts_data = []
    seen_post_ids = set() # To prevent duplicate posts if they appear in multiple searches/subreddits

    print(f"Starting Reddit data extraction...")

    # --- Fetch from specific subreddits (Top posts of the week) ---
    print("\nFetching 'top' posts from target subreddits...")
    for sub_name in subreddits:
        print(f"  From r/{sub_name}")
        try:
            subreddit = reddit.subreddit(sub_name)
            # Fetch top posts for the last week
            for submission in subreddit.top(limit=limit_sub, time_filter=time_filter):
                if submission.id not in seen_post_ids:
                    all_posts_data.append(extract_submission_data(submission, f"subreddit_top:{sub_name}"))
                    seen_post_ids.add(submission.id)
            time.sleep(random.randint(2, 5)) # Be polite
        except Exception as e:
            print(f"    Error fetching from r/{sub_name}: {e}")

    # --- Perform general searches (e.g., in r/all or specific subreddits) ---
    print("\nPerforming general searches across subreddits (using search terms)...")
    for term in search_terms:
        print(f"  Searching for: '{term}'")
        try:
            # You can search `reddit.subreddit('all').search(term, ...)` for broader,
            # but it's often better to search within relevant subreddits or broad ones like `AskReddit`
            # For this example, let's search `r/all` for general terms.
            # Be cautious with 'all' as it can yield very broad results.
            for submission in reddit.subreddit('all').search(term, sort='relevance', limit=limit_search, time_filter='week'):
                if submission.id not in seen_post_ids:
                    all_posts_data.append(extract_submission_data(submission, f"search_term:'{term}'"))
                    seen_post_ids.add(submission.id)
            time.sleep(random.randint(2, 5)) # Be polite
        except Exception as e:
            print(f"    Error searching for '{term}': {e}")
    
    return pd.DataFrame(all_posts_data)

def extract_submission_data(submission, source_identifier):
    """Helper function to extract relevant data from a PRAW Submission object."""
    try:
        return {
            "platform": "Reddit",
            "post_id": submission.id,
            "title": submission.title,
            "url": submission.url,
            "selftext": submission.selftext, # The main text content of the post
            "subreddit": submission.subreddit.display_name,
            "author": submission.author.name if submission.author else "[deleted]",
            "score": submission.score, # Upvotes - Downvotes
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "created_utc": datetime.fromtimestamp(submission.created_utc),
            "permalink": f"https://www.reddit.com{submission.permalink}",
            "is_original_content": submission.is_original_content,
            "is_video": submission.is_video,
            "over_18": submission.over_18,
            "distinguished": submission.distinguished,
            "source_category": source_identifier # To know how this post was found
        }
    except Exception as e:
        print(f"  Error extracting data for submission {submission.id}: {e}")
        return None # Return None if extraction fails for a post

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Reddit Product Marketing Data Extraction ---")
    reddit_posts_df = get_reddit_product_posts(TARGET_SUBREDDITS, REDDIT_PRODUCT_SEARCH_TERMS)

    # Filter out any None entries from failed extractions
    reddit_posts_df = reddit_posts_df.dropna(subset=['post_id'])

    if not reddit_posts_df.empty:
        output_csv_path = "reddit_product_marketing_posts.csv"
        reddit_posts_df.to_csv(output_csv_path, index=False)
        print(f"\nSuccessfully extracted {len(reddit_posts_df)} unique product-related Reddit posts.")
        print(f"Data saved to {output_csv_path}")
        print("\nFirst 5 rows of extracted data:")
        print(reddit_posts_df.head())

        # --- Integrate with Google Sheets ---
        try:
            from upload_to_sheets import upload_to_google_sheet
            print("\nAttempting to upload data to Google Sheets...")
            upload_to_google_sheet(reddit_posts_df, "AI_Content_Optimizer_Data", "Reddit_Product_Content")
        except ImportError:
            print("\nWarning: upload_to_sheets.py not found. Skipping Google Sheets upload.")
        except Exception as e:
            print(f"\nError uploading to Google Sheets: {e}")

    else:
        print("\nNo product marketing Reddit posts found or an error occurred during extraction.")
    
    print("\n--- Reddit Product Marketing Data Extraction Complete ---")

    # --- Slack Notification Integration ---
    from slack_notifier import send_slack_notification

    if send_slack_notification:
        slack_message = (
            f":sparkles: New Reddit product marketing posts found! :reddit:\n"
            f"Extracted {len(reddit_posts_df)} unique product-related Reddit posts.\n"
            f"Check the Google Sheet here: https://docs.google.com/spreadsheets/d/1aAdsgz9AagAOxkRSoxdaIaJ6N76U8G1xb4mPC-_h5HE/edit?usp=sharing\n" # IMPORTANT: Replace with actual link
            f"Worksheet: AI_Content_Optimizer_Data\n"
            f"Check: Reddit_Product_Content worksheet for the details."
        )
        send_slack_notification(slack_message)

    else:
        print("Slack notification function not available.")
    