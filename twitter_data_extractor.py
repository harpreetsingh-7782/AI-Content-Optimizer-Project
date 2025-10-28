import tweepy
import pandas as pd
import time
import random
import os
from datetime import datetime, timedelta

# --- 1. Load API Credentials from a separate file (e.g., credentials.py) ---
try:
    from credentials import BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
except ImportError:
    print("Error: credentials.py not found or incomplete. Please create it with your Twitter API keys.")
    exit()

# --- 2. Initialize Tweepy Client ---
client = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# --- 3. Define ALL Search Parameters ---
# Keywords/hashtags to search for a wide range of product launches/trends
PRODUCT_SEARCH_TERMS = [
    # General Product Discovery Indicators
    "\"new product\"",           # Exact phrase
    "\"product launch\"",        # Exact phrase
    "#newtech",
    "#innovation",
    "#techtrends",
    "#futureof",                 # Broad term, will catch #futureofAI, #futureofmobility etc.
    "#unveiled",
    "#comingsoon",
    
    # Industry-Specific Indicators
    "#AI",                       # For AI trends, products
    "#wearables",                # For fitness trackers, smartwatches
    "#electricvehicle", "#EV",   # For automotive
    "#sustainablefashion",       # For clothing/fashion
    "#ecofriendly",              # General green products
    "#foodtech",                 # For food innovation
    "#plantbased",               # For food/dietary products
    "#medtech",                  # For pharma/health tech
    "#digitalhealth",            # Broader health tech
    "#smartdevice",              # For general electronics
    "#smarthome"                 # For home automation products
]

# Max tweets to fetch per search term (Twitter API v2 has limits)
MAX_TWEETS_PER_TERM = 100 # Adjust based on your API access level and data needs (max 100 per request)
RECENT_TWEETS_DAYS = 7 # Look for tweets in the last N days (max 7 days for search_recent_tweets)

def get_product_marketing_tweets(search_terms, max_results=MAX_TWEETS_PER_TERM, days_ago=RECENT_TWEETS_DAYS):
    """
    Fetches product-centric tweets from Twitter/X using specified search terms.
    Extracts content, engagement, and basic user info.
    """
    all_tweet_data = []
    
    # Calculate start time for recent tweets
    start_time = datetime.utcnow() - timedelta(days=days_ago)

    print(f"Starting Twitter data extraction for {len(search_terms)} terms, looking back {days_ago} days...")

    # We'll use a set to store unique tweet IDs to avoid duplicates if multiple terms match the same tweet
    seen_tweet_ids = set()

    for term in search_terms:
        # Twitter API v2's `search_recent_tweets` has a limit of 100 results per request.
        # If you need more than 100 per term, you'd need to implement pagination using `next_token`
        # For this initial phase, 100 per term is a good starting point.
        print(f"\nSearching for term: '{term}'")
        try:
            # Construct the query.
            # -is:retweet excludes retweets, -is:reply excludes replies
            # lang:en filters for English tweets
            # The '\"...\"' syntax ensures exact phrase matching for multi-word terms.
            query = f'{term} -is:retweet -is:reply lang:en' # No need for external quotes here, Tweepy handles it.
            
            # Use client.search_recent_tweets for up to 7 days of historical data
            response = client.search_recent_tweets(
                query=query,
                tweet_fields=['created_at', 'text', 'public_metrics', 'entities', 'author_id'],
                user_fields=['username', 'name', 'public_metrics'], # To get follower count etc.
                expansions=['author_id'],
                start_time=start_time,
                max_results=min(max_results, 100) # Max 100 per request for search_recent_tweets
            )

            if response.data:
                users = {user['id']: user for user in response.includes.get('users', [])}
                # Filter out tweets already seen from previous search terms
                new_tweets_count = 0
                for tweet in response.data:
                    if tweet.id not in seen_tweet_ids:
                        author = users.get(tweet.author_id)
                        
                        tweet_info = {
                            "platform": "Twitter",
                            "tweet_id": tweet.id,
                            "created_at": tweet.created_at,
                            "text": tweet.text,
                            "search_term_matched": term, # Which term caught this tweet
                            "likes": tweet.public_metrics.get('like_count', 0),
                            "retweets": tweet.public_metrics.get('retweet_count', 0),
                            "replies": tweet.public_metrics.get('reply_count', 0),
                            "quotes": tweet.public_metrics.get('quote_count', 0),
                            "impressions": tweet.public_metrics.get('impression_count', 0),
                            "author_id": tweet.author_id,
                            "author_username": author.username if author else None,
                            "author_name": author.name if author else None,
                            "author_followers": author.public_metrics.get('followers_count', 0) if author and author.public_metrics else 0,
                            "hashtags": [tag['tag'] for tag in tweet.entities.get('hashtags', [])] if tweet.entities else [],
                            "mentions": [mention['username'] for mention in tweet.entities.get('mentions', [])] if tweet.entities else [],
                            "urls": [url['expanded_url'] for url in tweet.entities.get('urls', [])] if tweet.entities else [],
                        }
                        all_tweet_data.append(tweet_info)
                        seen_tweet_ids.add(tweet.id)
                        new_tweets_count += 1
                print(f"  Added {new_tweets_count} new unique tweets (total found for term: {len(response.data)}) for '{term}'")
            else:
                print(f"  No tweets found for '{term}' in the last {days_ago} days.")

            # Be polite to the API and avoid rate limits. A longer sleep helps with many terms.
            time.sleep(random.randint(10, 25)) # Increased sleep time

        except tweepy.errors.TweepyException as e:
            print(f"  Tweepy API error for term '{term}': {e}")
            if "Rate limit exceeded" in str(e) or "429 Too Many Requests" in str(e):
                print("  Rate limit hit. Sleeping for 15 minutes before retrying or exiting.")
                time.sleep(900) # Sleep for 15 minutes (900 seconds)
            else:
                print("  Skipping to next term due to other API error.")
        except Exception as e:
            print(f"  An unexpected error occurred for term '{term}': {e}")

    return pd.DataFrame(all_tweet_data)

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Product Marketing Tweet Extraction ---")
    product_tweets_df = get_product_marketing_tweets(PRODUCT_SEARCH_TERMS, max_results=100)

    if not product_tweets_df.empty:
        output_csv_path = "product_marketing_tweets.csv"
        product_tweets_df.to_csv(output_csv_path, index=False)
        print(f"\nSuccessfully extracted {len(product_tweets_df)} unique product-related tweets.")
        print(f"Data saved to {output_csv_path}")
        print("\nFirst 5 rows of extracted data:")
        print(product_tweets_df.head())

        # --- Integrate with Google Sheets ---
        try:
            from upload_to_sheets import upload_to_google_sheet
            print("\nAttempting to upload data to Google Sheets...")
            # Use a distinct sheet/worksheet name for product tweets
            upload_to_google_sheet(product_tweets_df, "AI_Content_Optimizer_Data", "Twitter_Product_Content")
        except ImportError:
            print("\nWarning: upload_to_sheets.py not found. Skipping Google Sheets upload.")
        except Exception as e:
            print(f"\nError uploading to Google Sheets: {e}")

    else:
        print("\nNo product marketing tweets found or an error occurred during extraction.")
    print("\n--- Product Marketing Tweet Extraction Complete ---")

from slack_notifier import send_slack_notification