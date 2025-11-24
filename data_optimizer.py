# data_optimizer.py
import pandas as pd
import os
import random
from collections import Counter
import re
import nltk

# --- NLTK Data Path Configuration ---
# Define a consistent NLTK data path
NLTK_DATA_PATH = os.path.join(os.path.expanduser("~"), "nltk_data") 

# Ensure this path is in NLTK's search paths
if NLTK_DATA_PATH not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_PATH)
    # print(f"Added {NLTK_DATA_PATH} to NLTK data paths.") # Optional debug

# Download NLTK resources to the specified path if they don't exist
# Check for 'punkt_tab' (required in NLTK 3.8+)
try:
    nltk.data.find('tokenizers/punkt_tab', paths=[NLTK_DATA_PATH])
except LookupError:
    print(f"Downloading 'punkt_tab' to {NLTK_DATA_PATH}...")
    nltk.download('punkt_tab', download_dir=NLTK_DATA_PATH)
    print("'punkt_tab' downloaded.")

# Check for 'stopwords'
try:
    nltk.data.find('corpora/stopwords', paths=[NLTK_DATA_PATH])
except LookupError:
    print(f"Downloading 'stopwords' to {NLTK_DATA_PATH}...")
    nltk.download('stopwords', download_dir=NLTK_DATA_PATH)
    print("'stopwords' downloaded.")
# --- END NLTK Data Path Configuration ---

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# --- IMPORTANT CHANGE HERE ---
# Import your Google Sheets handler functions
# Assuming google_sheets_handler.py is in the same directory as data_optimizer.py
from google_sheets_handler import get_sheet_data, update_sheet_data

# Define your main Google Spreadsheet name
MAIN_SPREADSHEET_NAME = "AI_Content_Optimizer_Data" # This looks correct based on your sheet URL

# Initialize NLTK English stop words
ENGLISH_STOP_WORDS = set(stopwords.words('english'))
ENGLISH_STOP_WORDS.update(["new", "product", "review", "best", "vs", "up", "at", "by", "what", "how", "when", "where", "why", "who",
                           "this", "that", "these", "those", "can", "get", "just", "like", "make", "made", "from", "for", "with",
                           "will", "it", "its", "you", "your", "are", "have", "been", "has", "had", "here", "there", "we", "our",
                           "us", "they", "them", "their", "about", "all", "also", "and", "any", "but", "etc", "etc.", "every", "many",
                           "much", "only", "other", "some", "such", "than", "then", "through", "under", "until", "upon", "would"])

# Initialize stemmer for optional use
stemmer = PorterStemmer()

def preprocess_text(text, apply_stemming=True):
    """
    Cleans and tokenizes text, removing stop words, non-alphabetic characters,
    and optionally applies stemming.
    Returns a list of processed tokens.
    """
    if not isinstance(text, str):
        return []

    # Remove URLs, mentions
    text = re.sub(r'http\S+|www\S+|https\S+|@\w+', '', text, flags=re.MULTILINE)
    # Remove hashtags but keep the word (e.g., #awesome -> awesome)
    text = re.sub(r'#(\w+)', r'\1', text) 
    
    # Remove non-alphabetic characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    
    tokens = word_tokenize(text)
    
    # Remove stop words and short words
    tokens = [word for word in tokens if word not in ENGLISH_STOP_WORDS and len(word) > 2]
    
    # Optional: Apply stemming
    if apply_stemming:
        tokens = [stemmer.stem(word) for word in tokens]
        
    return tokens

def clean_and_update_sheet(worksheet_name, text_columns, apply_stemming=True):
    """
    Loads data from a Google Sheet worksheet, cleans specified text columns,
    and updates the sheet with new 'cleaned_<column_name>' columns.

    Args:
        worksheet_name (str): The name of the Google Sheet worksheet (e.g., "youtube product content").
        text_columns (list): A list of column names to clean.
        apply_stemming (bool): Whether to apply stemming during preprocessing.
    """
    print(f"Cleaning data for worksheet: '{worksheet_name}' in spreadsheet '{MAIN_SPREADSHEET_NAME}'")
    df = get_sheet_data(MAIN_SPREADSHEET_NAME, worksheet_name)

    if df is not None and not df.empty:
        # Drop unnamed columns that sometimes appear after reading from sheets
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        for col in text_columns:
            if col in df.columns:
                print(f"  - Cleaning column: '{col}'")
                # Apply preprocessing and convert list of tokens back to string for storage
                df[f'cleaned_{col}'] = df[col].apply(lambda x: ' '.join(preprocess_text(x, apply_stemming)))
            else:
                print(f"  - Warning: Column '{col}' not found in '{worksheet_name}'. Skipping.")
        
        # Update the Google Sheet with the new cleaned columns
        update_sheet_data(df, MAIN_SPREADSHEET_NAME, worksheet_name)
        print(f"Successfully cleaned and updated worksheet: '{worksheet_name}'")
    else:
        print(f"Could not load data or worksheet '{worksheet_name}' is empty. Skipping cleaning.")


def get_optimization_insights(num_keywords=5, num_themes=3, platform_focus=None, apply_stemming=True):
    """
    Analyzes collected marketing data (from Google Sheets) to extract optimization insights
    for content generation, using cleaned text where available.

    Args:
        num_keywords (int): Number of top trending keywords to extract.
        num_themes (int): Number of top engagement themes/topics to extract.
        platform_focus (str, optional): Focus insights on a specific platform ('twitter', 'youtube', 'reddit', 'google_trends').
                                        If None, uses insights from all platforms.
        apply_stemming (bool): Whether preprocessing should apply stemming for keyword/theme extraction.

    Returns:
        str: A formatted string containing data-driven insights for the LLM.
    """
    all_processed_keywords = []
    all_processed_themes = []

    print("\n--- Analyzing data for optimization insights ---")

    # --- 1. Process Google Trends Data ---
    if platform_focus in [None, 'google_trends']:
        # Corrected worksheet name
        gt_queries_df = get_sheet_data(MAIN_SPREADSHEET_NAME, "GoogleTrends_Related_Queries")
        if not gt_queries_df.empty and 'query' in gt_queries_df.columns:
            # Prioritize cleaned_query if it exists
            query_col = 'cleaned_query' if 'cleaned_query' in gt_queries_df.columns else 'query'
            for query in gt_queries_df[query_col].dropna():
                all_processed_keywords.extend(preprocess_text(query, apply_stemming))
            print(f"  Processed {len(gt_queries_df)} GoogleTrends_Related_Queries.")
        
        # Corrected worksheet name
        gt_interest_df = get_sheet_data(MAIN_SPREADSHEET_NAME, "GoogleTrends_Related_Queries")
        if not gt_interest_df.empty and 'keyword_searched' in gt_interest_df.columns:
            # Prioritize cleaned_keyword if it exists
            keyword_col = 'cleaned_keyword_searched' if 'cleaned_keyword_searched' in gt_interest_df.columns else 'keyword_searched'
            for keyword in gt_interest_df[keyword_col].dropna():
                all_processed_keywords.extend(preprocess_text(keyword, apply_stemming))
            print(f"  Processed {len(gt_interest_df)} GoogleTrends_Related_Queries.")


    # --- 2. Process Twitter Data ---
    if platform_focus in [None, 'twitter']:
        # Corrected worksheet name
        twitter_df = get_sheet_data(MAIN_SPREADSHEET_NAME, "Twitter_marketing_tweets")
        if not twitter_df.empty:
            # Prioritize cleaned text if available, otherwise use original
            text_col = 'cleaned_Tweet' if 'cleaned_Tweet' in twitter_df.columns else 'Tweet'

            if text_col in twitter_df.columns:
                for tweet_text in twitter_df[text_col].dropna():
                    all_processed_themes.extend(preprocess_text(tweet_text, apply_stemming))
                
                # Process hashtags from original text for dedicated keyword extraction
                if 'Tweet' in twitter_df.columns:
                    for original_tweet_text in twitter_df['Tweet'].dropna():
                        hashtags = re.findall(r'#(\w+)', original_tweet_text)
                        all_processed_keywords.extend([stemmer.stem(tag.lower()) if apply_stemming else tag.lower() 
                                                       for tag in hashtags if tag.lower() not in ENGLISH_STOP_WORDS])

                if 'public_metrics.like_count' in twitter_df.columns and text_col in twitter_df.columns:
                    top_tweets = twitter_df.sort_values(by='public_metrics.like_count', ascending=False).head(50)
                    for tweet_text in top_tweets[text_col].dropna():
                        all_processed_themes.extend(preprocess_text(tweet_text, apply_stemming))
                print(f"  Processed {len(twitter_df)} Twitter tweets.")


    # --- 3. Process YouTube Data ---
    if platform_focus in [None, 'youtube']:
        # Corrected worksheet name
        youtube_df = get_sheet_data(MAIN_SPREADSHEET_NAME, "YouTube_Product_Content")
        if not youtube_df.empty:
            title_col = 'cleaned_video_title' if 'cleaned_video_title' in youtube_df.columns else 'title'
            desc_col = 'cleaned_video_description' if 'cleaned_video_description' in youtube_df.columns else 'description'
            
            if title_col in youtube_df.columns:
                for title in youtube_df[title_col].dropna():
                    all_processed_keywords.extend(preprocess_text(title, apply_stemming))
                    all_processed_themes.extend(preprocess_text(title, apply_stemming))

            if desc_col in youtube_df.columns:
                for desc in youtube_df[desc_col].dropna():
                    all_processed_themes.extend(preprocess_text(desc, apply_stemming))

            if 'view_count' in youtube_df.columns and title_col in youtube_df.columns:
                top_videos = youtube_df.sort_values(by='view_count', ascending=False).head(50)
                for title in top_videos[title_col].dropna():
                    all_processed_themes.extend(preprocess_text(title, apply_stemming))
                print(f"  Processed {len(youtube_df)} YouTube videos.")


    # --- 4. Process Reddit Data ---
    if platform_focus in [None, 'reddit']:
        # Corrected worksheet name
        reddit_df = get_sheet_data(MAIN_SPREADSHEET_NAME, "Reddit_Product_Content")
        if not reddit_df.empty:
            title_col = 'cleaned_title' if 'cleaned_title' in reddit_df.columns else 'title'
            selftext_col = 'cleaned_selftext' if 'cleaned_selftext' in reddit_df.columns else 'selftext'

            if title_col in reddit_df.columns:
                for title in reddit_df[title_col].dropna():
                    all_processed_keywords.extend(preprocess_text(title, apply_stemming))
                    all_processed_themes.extend(preprocess_text(title, apply_stemming))
            
            if selftext_col in reddit_df.columns:
                for text in reddit_df[selftext_col].dropna():
                    all_processed_themes.extend(preprocess_text(text, apply_stemming))
            
            if 'score' in reddit_df.columns and title_col in reddit_df.columns:
                top_posts = reddit_df.sort_values(by='score', ascending=False).head(50)
                for title in top_posts[title_col].dropna():
                    all_processed_themes.extend(preprocess_text(title, apply_stemming))
            print(f"  Processed {len(reddit_df)} Reddit posts.")

    # --- Consolidate Keywords and Themes ---
    top_keywords_final = [kw for kw, _ in Counter(all_processed_keywords).most_common(num_keywords)]

    # For themes, we can use a higher threshold or different processing if needed
    top_themes_candidates = [word for word, count in Counter(all_processed_themes).most_common(num_themes * 2) if count > 3]
    # Filter themes to ensure they are distinct from top keywords if necessary
    top_themes_final = [theme for theme in top_themes_candidates if theme not in top_keywords_final][:num_themes]


    # --- Construct Insight String ---
    insights_str = "\n\n--- Data-Driven Content Optimization Insights ---\n"
    if top_keywords_final:
        insights_str += f"Based on recent trends and high engagement, consider these effective keywords: {', '.join(top_keywords_final)}\n"
    if top_themes_final:
        insights_str += f"Popular themes and topics that resonate with the audience: {', '.join(top_themes_final)}\n"
    
    if not top_keywords_final and not top_themes_final:
        insights_str += "No significant optimization insights found from available data.\n"

    insights_str += "--------------------------------------------------\n"
    
    print("--- Finished analyzing data ---")
    return insights_str.strip()

# Example Usage:
if __name__ == "__main__":
    print("Starting data cleaning and optimization process...")
    
    # --- Step 1: Clean Data and Update Google Sheets ---
    # Define which worksheets (within MAIN_SPREADSHEET_NAME) and which columns within them need cleaning
    # THESE NOW MATCH YOUR GOOGLE SHEET TAB NAMES EXACTLY
    sheets_to_clean = {
        "Twitter_marketing_tweets": ['Tweet'], # Corrected from 'twitter_marketing_tweets'
        "YouTube_Product_Content": ['title', 'description'], # Corrected from 'youtube_product_content'
        "Reddit_Product_Content": ['title', 'selftext'], # Corrected from 'reddit_product_content'
        "GoogleTrends_Related_Queries": ['query', 'keyword_searched'], # Corrected from 'google_trends_related_queries'
    }

    for worksheet_name, cols in sheets_to_clean.items():
        clean_and_update_sheet(worksheet_name, cols, apply_stemming=True) # Apply stemming during cleaning

    # --- Step 2: Generate Optimization Insights from Cleaned Data ---
    print("\nGenerating optimization insights from cleaned data...")
    insights_all = get_optimization_insights(num_keywords=7, num_themes=5, apply_stemming=True)
    print("\nInsights (All Platforms):")
    print(insights_all)

    insights_twitter = get_optimization_insights(platform_focus='twitter', num_keywords=5, num_themes=3, apply_stemming=True)
    print("\nInsights (Twitter Focus):")
    print(insights_twitter)