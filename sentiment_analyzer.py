# sentiment_analyzer.py
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

# Ensure VADER lexicon is downloaded and configured
NLTK_DATA_PATH = os.path.join(os.path.expanduser("~"), "nltk_data") 
if NLTK_DATA_PATH not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_PATH)

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    print(f"Downloading 'vader_lexicon' to {NLTK_DATA_PATH}...")
    nltk.download('vader_lexicon', download_dir=NLTK_DATA_PATH)

# Import your Google Sheets handler functions
# Assuming google_sheets_handler.py is in the same directory
from google_sheets_handler import get_sheet_data, update_sheet_data

# Define your main Google Spreadsheet name
MAIN_SPREADSHEET_NAME = "AI_Content_Optimizer_Data" # <--- CONFIRM THIS IS YOUR MAIN SPREADSHEET NAME

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using NLTK's VADER.
    Returns the sentiment label (Positive, Negative, Neutral) and the compound score.
    """
    if not isinstance(text, str) or not text.strip(): # Handle non-string or empty text
        return 'N/A', 0.0

    vs = analyzer.polarity_scores(text)
    compound_score = vs['compound']

    if compound_score >= 0.05:
        return 'Positive', compound_score
    elif compound_score <= -0.05:
        return 'Negative', compound_score
    else:
        return 'Neutral', compound_score

def process_sentiment_for_worksheet(worksheet_name, text_column):
    """
    Retrieves data from a Google Sheet worksheet, performs sentiment analysis
    on a specified text column, and updates the worksheet with sentiment scores.

    Args:
        worksheet_name (str): The name of the worksheet within MAIN_SPREADSHEET_NAME.
        text_column (str): The name of the column containing text to analyze.
    """
    print(f"\n--- Processing sentiment for worksheet: '{worksheet_name}' (column: '{text_column}') ---")
    df = get_sheet_data(MAIN_SPREADSHEET_NAME, worksheet_name)

    if df is not None and not df.empty:
        # Drop unnamed columns that sometimes appear after reading from sheets
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        if text_column in df.columns:
            # Apply sentiment analysis
            df[['sentiment_label', 'sentiment_score']] = df[text_column].apply(lambda x: pd.Series(analyze_sentiment(x)))
            
            # Update the Google Sheet with the new sentiment columns
            update_sheet_data(df, MAIN_SPREADSHEET_NAME, worksheet_name)
            print(f"Successfully analyzed sentiment and updated worksheet: '{worksheet_name}'")
        else:
            print(f"ERROR: Text column '{text_column}' not found in worksheet '{worksheet_name}'. Skipping sentiment analysis.")
    else:
        print(f"Could not load data or worksheet '{worksheet_name}' is empty. Skipping sentiment analysis.")

if __name__ == "__main__":
    print("Starting sentiment analysis process...")

    # Define the worksheets and their respective text columns for sentiment analysis
    # IMPORTANT: Use the EXACT worksheet names from your Google Sheet tabs (case and spaces matter!)
    worksheets_to_analyze = {
        "Twitter_marketing_tweets": 'Tweet',  # For tweets
        "YouTube_Product_Content": 'title', # For video titles (primary text for sentiment)
        "YouTube_Product_Content": 'description', # Could also analyze descriptions
        "YouTube_Product_Content": 'channel_title',
        # You might also have a 'comments' column in YouTube data if you extracted that
        "Reddit_Product_Content": 'title',   # For Reddit post titles
        "Reddit_Product_Content": 'selftext', # Could also analyze selftext
    }

    for ws_name, col_name in worksheets_to_analyze.items():
        process_sentiment_for_worksheet(ws_name, col_name)

    print("\nSentiment analysis process completed.")