from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import os

# --- 1. Initialize pytrends ---
pytrends = TrendReq(hl='en-US', tz=330) # hl=host language, tz=timezone (330 for India, 360 for US Central, etc.)

# --- 2. Define Search Parameters ---
GOOGLE_TRENDS_KEYWORDS = [
    "new product",
    "product launch",
    "AI trends",
    "wearable technology",
    "electric vehicle",
    "sustainable fashion",
    "food innovation",
    "medtech",
    "smart device",
    "bluetooth headphones",
    "smartwatch",
    "plant-based food",
    "digital health",
    "generative AI",
    "AI chatbots",
    "quantum computing",
    "immersive tech",
    "eco friendly products"
]

# Timeframe for "Interest Over Time"
# Examples: 'today 1-H', 'today 5-y', '2016-12-14 2017-01-25'
TIMEFRAME = 'today 3-m' # Last 3 months for recent trends

# Geo location (leave empty for worldwide)
# Examples: 'US', 'IN' (India), 'GB' (United Kingdom)
GEO = 'IN' # Let's target India for example, change to '' for worldwide

def get_interest_over_time(keywords, timeframe=TIMEFRAME, geo=GEO):
    """
    Fetches Google Trends 'Interest Over Time' for a list of keywords.
    Google Trends allows a maximum of 5 keywords per request.
    """
    all_interest_data = []
    
    # Split keywords into chunks of 5
    keyword_chunks = [keywords[i:i + 5] for i in range(0, len(keywords), 5)]

    print(f"Fetching Google Trends 'Interest Over Time' for {len(keywords)} keywords ({TIMEFRAME}, Geo: {GEO})...")

    for chunk in keyword_chunks:
        print(f"  Requesting data for: {', '.join(chunk)}")
        try:
            pytrends.build_payload(chunk, cat=0, timeframe=timeframe, geo=geo)
            df = pytrends.interest_over_time()
            if not df.empty:
                # Remove the 'isPartial' column if it exists
                if 'isPartial' in df.columns:
                    df = df.drop(columns=['isPartial'])
                df['geo'] = geo
                df['timeframe'] = timeframe
                all_interest_data.append(df)
            else:
                print(f"    No data returned for keywords: {', '.join(chunk)}")
            time.sleep(random.randint(5, 10)) # Be polite to Google Trends
        except Exception as e:
            print(f"    Error fetching interest over time for {', '.join(chunk)}: {e}")
            print("    Waiting longer due to potential rate limit or error...")
            time.sleep(random.randint(30, 60)) # Longer wait for errors

    if all_interest_data:
        # Concatenate all dataframes. The 'date' column will be the index.
        # Ensure the 'date' column is explicitly reset for sheets upload.
        combined_df = pd.concat(all_interest_data, axis=1)
        # Drop duplicate columns that might arise from concat (e.g., if a keyword chunk overlaps somehow, though it shouldn't with slicing)
        combined_df = combined_df.loc[:,~combined_df.columns.duplicated()].copy()
        
        # Move geo and timeframe columns to the front and ensure 'date' is a column
        if 'geo' in combined_df.columns and 'timeframe' in combined_df.columns:
            cols = ['geo', 'timeframe'] + [col for col in combined_df.columns if col not in ['geo', 'timeframe']]
            combined_df = combined_df[cols]
        
        # Reset index to make 'date' a regular column for CSV/Sheets
        combined_df = combined_df.reset_index()
        combined_df.rename(columns={'index': 'date'}, inplace=True)
        
        return combined_df
    return pd.DataFrame()

def get_related_queries_and_topics(keywords, timeframe=TIMEFRAME, geo=GEO):
    """
    Fetches Google Trends 'Related Queries' and 'Related Topics' for individual keywords.
    This works best for single keywords.
    """
    all_related_queries = []
    all_related_topics = []

    print(f"\nFetching Google Trends 'Related Queries' and 'Related Topics' for {len(keywords)} keywords ({TIMEFRAME}, Geo: {GEO})...")

    for keyword in keywords:
        print(f"  Requesting related data for: '{keyword}'")
        try:
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo)
            
            # Related Queries
            related_queries_dict = pytrends.related_queries()
            if related_queries_dict and keyword in related_queries_dict and related_queries_dict[keyword]['top'] is not None:
                df_queries = related_queries_dict[keyword]['top']
                df_queries['keyword_searched'] = keyword
                df_queries['query_type'] = 'top'
                df_queries['geo'] = geo
                df_queries['timeframe'] = timeframe
                all_related_queries.append(df_queries)
            else:
                print(f"    No top related queries found for '{keyword}'")

            # Related Topics
            related_topics_dict = pytrends.related_topics()
            if related_topics_dict and keyword in related_topics_dict and related_topics_dict[keyword]['top'] is not None:
                df_topics = related_topics_dict[keyword]['top']
                df_topics['keyword_searched'] = keyword
                df_topics['topic_type'] = 'top'
                df_topics['geo'] = geo
                df_topics['timeframe'] = timeframe
                all_related_topics.append(df_topics)
            else:
                print(f"    No top related topics found for '{keyword}'")
                
            time.sleep(random.randint(10, 20)) # Be more polite for related queries/topics

        except Exception as e:
            print(f"    Error fetching related data for '{keyword}': {e}")
            print("    Waiting longer due to potential rate limit or error...")
            time.sleep(random.randint(60, 120)) # Even longer wait for errors

    if all_related_queries:
        combined_queries_df = pd.concat(all_related_queries, ignore_index=True)
        return combined_queries_df, pd.concat(all_related_topics, ignore_index=True) if all_related_topics else pd.DataFrame()
    return pd.DataFrame(), pd.DataFrame()


# --- Main Execution ---
if __name__ == "__main__":
    
    print("--- Starting Google Trends Data Extraction ---")

    # 1. Get Interest Over Time
    interest_over_time_df = get_interest_over_time(GOOGLE_TRENDS_KEYWORDS)
    if not interest_over_time_df.empty:
        csv_path_iot = "google_trends_interest_over_time.csv"
        interest_over_time_df.to_csv(csv_path_iot, index=False)
        print(f"\nSuccessfully extracted Interest Over Time data for {len(GOOGLE_TRENDS_KEYWORDS)} keywords.")
        print(f"Data saved to {csv_path_iot}")
        print("\nFirst 5 rows of Interest Over Time data:")
        print(interest_over_time_df.head())

        # Upload to Google Sheets
        try:
            from upload_to_sheets import upload_to_google_sheet
            print("\nAttempting to upload Interest Over Time data to Google Sheets...")
            upload_to_google_sheet(interest_over_time_df, "AI_Content_Optimizer_Data", "GoogleTrends_Interest_Over_Time")
        except ImportError:
            print("\nWarning: upload_to_sheets.py not found. Skipping Google Sheets upload.")
        except Exception as e:
            print(f"\nError uploading Interest Over Time to Google Sheets: {e}")
    else:
        print("\nNo Interest Over Time data extracted.")

    # 2. Get Related Queries and Topics (using the same keywords)
    related_queries_df, related_topics_df = get_related_queries_and_topics(GOOGLE_TRENDS_KEYWORDS)

    if not related_queries_df.empty:
        csv_path_rq = "google_trends_related_queries.csv"
        related_queries_df.to_csv(csv_path_rq, index=False)
        print(f"\nSuccessfully extracted Related Queries data for {len(GOOGLE_TRENDS_KEYWORDS)} keywords.")
        print(f"Data saved to {csv_path_rq}")
        print("\nFirst 5 rows of Related Queries data:")
        print(related_queries_df.head())

        # Upload to Google Sheets
        try:
            from upload_to_sheets import upload_to_google_sheet
            print("\nAttempting to upload Related Queries data to Google Sheets...")
            upload_to_google_sheet(related_queries_df, "AI_Content_Optimizer_Data", "GoogleTrends_Related_Queries")
        except ImportError:
            print("\nWarning: upload_to_sheets.py not found. Skipping Google Sheets upload.")
        except Exception as e:
            print(f"\nError uploading Related Queries to Google Sheets: {e}")
    else:
        print("\nNo Related Queries data extracted.")

    if not related_topics_df.empty:
        csv_path_rt = "google_trends_related_topics.csv"
        related_topics_df.to_csv(csv_path_rt, index=False)
        print(f"\nSuccessfully extracted Related Topics data for {len(GOOGLE_TRENDS_KEYWORDS)} keywords.")
        print(f"Data saved to {csv_path_rt}")
        print("\nFirst 5 rows of Related Topics data:")
        print(related_topics_df.head())

        # Upload to Google Sheets
        try:
            from upload_to_sheets import upload_to_google_sheet
            print("\nAttempting to upload Related Topics data to Google Sheets...")
            upload_to_google_sheet(related_topics_df, "AI_Content_Optimizer_Data", "GoogleTrends_Related_Topics")
        except ImportError:
            print("\nWarning: upload_to_sheets.py not found. Skipping Google Sheets upload.")
        except Exception as e:
            print(f"\nError uploading Related Topics to Google Sheets: {e}")
    else:
        print("\nNo Related Topics data extracted.")
    
    print("\n--- Google Trends Data Extraction Complete ---")

from slack_notifier import send_slack_notification
