import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# =========================
# 🔹 PART 1: Fetch Twitter Data
# =========================

# Replace with your actual Bearer Token from Twitter API
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIjX4wEAAAAAzrYlRpqjR3ii57Rh5aOuLvvXUp0%3DFTzBHkelvHmgxvRLBEECa8DqtotPHxnWelwXivXaNnzNqYIMdR"

# Define search query and endpoint
query = "marketing OR digital marketing OR content marketing lang:en -is:retweet"
url = "https://api.twitter.com/2/tweets/search/recent"

headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
params = {
    "query": query,
    "tweet.fields": "created_at,public_metrics,text",
    "max_results": 10
}

print("🔍 Fetching tweets...")
response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    raise Exception(f"Twitter API Error: {response.status_code} - {response.text}")

tweets_data = response.json().get("data", [])
if not tweets_data:
    print("⚠️ No tweets found.")
else:
    print(f"✅ Retrieved {len(tweets_data)} tweets.")

# Extract and save to CSV
tweet_list = []
for tweet in tweets_data:
    metrics = tweet.get("public_metrics", {})
    tweet_list.append({
        "Tweet": tweet.get("text"),
        "Likes": metrics.get("like_count"),
        "Retweets": metrics.get("retweet_count"),
        "Created_At": tweet.get("created_at")
    })

df = pd.DataFrame(tweet_list)
csv_file = "marketing_tweets.csv"
df.to_csv(csv_file, index=False)
print(f"💾 Saved tweets to {csv_file}")

# =========================
# 🔹 PART 2: Upload to Google Sheets
# =========================

# Define Google API scope
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

SHEET_NAME = "Marketing Tweets Data"

# Try to open existing Google Sheet
try:
    spreadsheet = client.open(SHEET_NAME)
    sheet = spreadsheet.sheet1
    print("📄 Existing Google Sheet found, updating data...")
except gspread.SpreadsheetNotFound:
    spreadsheet = client.create(SHEET_NAME)
    sheet = spreadsheet.sheet1
    print("🆕 Created new Google Sheet.")

# Clear and update data
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Successfully uploaded marketing_tweets.csv to Google Sheets!")
print("🔗 Sheet URL:", f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
print(f"⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
