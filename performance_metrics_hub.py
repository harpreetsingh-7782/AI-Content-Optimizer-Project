# performance_metrics_hub.py
import pandas as pd
from datetime import datetime
import os

# Import Google Sheets and Slack integration functions
from google_sheets_handler import get_sheet_data
from slack_notifier import send_slack_notification # Assuming your slack_notifier has this function

# Define your main Google Spreadsheet name
MAIN_SPREADSHEET_NAME = "AI_Content_Optimizer_Data" # <--- CONFIRM THIS

def generate_sentiment_report_for_worksheet(worksheet_name, text_column, sentiment_label_col='sentiment_label', sentiment_score_col='sentiment_score'):
    """
    Generates a sentiment summary report for a specific worksheet.
    """
    print(f"\n--- Generating sentiment report for worksheet: '{worksheet_name}' ---")
    df = get_sheet_data(MAIN_SPREADSHEET_NAME, worksheet_name)

    if df is not None and not df.empty and sentiment_label_col in df.columns and sentiment_score_col in df.columns:
        # Drop unnamed columns that sometimes appear after reading from sheets
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Ensure sentiment_score is numeric
        df[sentiment_score_col] = pd.to_numeric(df[sentiment_score_col], errors='coerce')
        df.dropna(subset=[sentiment_score_col], inplace=True) # Remove rows where score couldn't be converted

        if df.empty:
            return f"No valid sentiment data found in '{worksheet_name}' for reporting."

        total_entries = len(df)
        avg_sentiment_score = df[sentiment_score_col].mean()

        sentiment_counts = df[sentiment_label_col].value_counts(normalize=True).reindex(['Positive', 'Negative', 'Neutral', 'N/A'], fill_value=0) * 100

        report_message = (
            f"📊 **Sentiment Report for {worksheet_name.replace('_', ' ').title()}**\n"
            f"   - Total analyzed items: `{total_entries}`\n"
            f"   - Average sentiment score: `{avg_sentiment_score:.2f}` (Range: -1 to 1)\n"
            f"   - Positive: `{sentiment_counts.get('Positive', 0):.1f}%`\n"
            f"   - Negative: `{sentiment_counts.get('Negative', 0):.1f}%`\n"
            f"   - Neutral: `{sentiment_counts.get('Neutral', 0):.1f}%`\n"
        )

        # Identify top positive/negative examples (optional, can be memory intensive for large data)
        # For simplicity, let's get the 3 most positive and 3 most negative items
        top_pos = df.nlargest(3, sentiment_score_col)
        top_neg = df.nsmallest(3, sentiment_score_col)

        if not top_pos.empty:
            report_message += "\n⭐ **Top 3 Positive Items:**\n"
            for _, row in top_pos.iterrows():
                content = str(row[text_column])[:100] + "..." if len(str(row[text_column])) > 100 else str(row[text_column])
                report_message += f"   - `{content}` (Score: {row[sentiment_score_col]:.2f})\n"
        
        if not top_neg.empty:
            report_message += "\n🚨 **Top 3 Negative Items:**\n"
            for _, row in top_neg.iterrows():
                content = str(row[text_column])[:100] + "..." if len(str(row[text_column])) > 100 else str(row[text_column])
                report_message += f"   - `{content}` (Score: {row[sentiment_score_col]:.2f})\n"

        return report_message
    else:
        return f"Could not generate report for '{worksheet_name}': Data empty or sentiment columns missing."

def check_for_sentiment_alerts(worksheet_name, sentiment_label_col='sentiment_label', sentiment_score_col='sentiment_score', 
                                negative_threshold=-0.5, negative_count_threshold=5, channel="#marketing-alerts"):
    """
    Checks for critical negative sentiment and sends a Slack alert if thresholds are met.
    """
    print(f"\n--- Checking for sentiment alerts in worksheet: '{worksheet_name}' ---")
    df = get_sheet_data(MAIN_SPREADSHEET_NAME, worksheet_name)

    if df is not None and not df.empty and sentiment_label_col in df.columns and sentiment_score_col in df.columns:
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df[sentiment_score_col] = pd.to_numeric(df[sentiment_score_col], errors='coerce')
        
        # Filter for significantly negative content
        negative_content = df[(df[sentiment_label_col] == 'Negative') & (df[sentiment_score_col] < negative_threshold)]
        
        if len(negative_content) >= negative_count_threshold:
            alert_message = (
                f"🚨 **URGENT SENTIMENT ALERT in {worksheet_name.replace('_', ' ').title()}!**\n"
                f"   - Detected `{len(negative_content)}` items with sentiment scores below `{negative_threshold}`.\n"
                f"   - This indicates a significant negative trend.\n"
                f"   - Please review the latest data in the Google Sheet: [Link to your Google Sheet]\n"
            )
            print(f"Sending Slack alert for {worksheet_name}...")
            send_slack_notification(alert_message, channel)
            return alert_message
        else:
            print(f"No critical negative sentiment detected in '{worksheet_name}'.")
            return None
    else:
        print(f"Skipping alert check for '{worksheet_name}': Data empty or sentiment columns missing.")
        return None

if __name__ == "__main__":
    print("Starting Performance Metrics Hub...")

    # Configuration for reports and alerts
    # IMPORTANT: Use the EXACT worksheet names from your Google Sheet tabs (case and spaces matter!)
    reporting_config = {
        "Twitter_marketing_tweets": {'text_col': 'Tweet', 'slack_channel': "#marketing-reports"},
        "YouTube_Product_Content": {'text_col': 'title', 'slack_channel': "#marketing-reports"},
        "Reddit_Product_Content": {'text_col': 'selftext', 'slack_channel': "#marketing-reports"},
    }

    alert_config = {
        "Twitter_marketing_tweets": {'negative_threshold': -0.3, 'negative_count_threshold': 5, 'slack_channel': "#marketing-alerts"},
        "YouTube_Product_Content": {'negative_threshold': -0.4, 'negative_count_threshold': 3, 'slack_channel': "#marketing-alerts"},
        "Reddit_Product_Content": {'negative_threshold': -0.5, 'negative_count_threshold': 2, 'slack_channel': "#marketing-alerts"},
    }

    # --- Generate and Send Reports ---
    print("\n--- Generating and sending daily reports ---")
    for ws_name, config in reporting_config.items():
        report = generate_sentiment_report_for_worksheet(ws_name, config['text_col'])
        if report:
            print(f"Sending report for {ws_name} to {config['slack_channel']}")
            send_slack_notification(report, config['slack_channel'])
        else:
            print(f"Failed to generate report for {ws_name}.")

    # --- Check for and Send Alerts ---
    print("\n--- Checking for sentiment alerts ---")
    for ws_name, config in alert_config.items():
        check_for_sentiment_alerts(
            ws_name, 
            negative_threshold=config['negative_threshold'], 
            negative_count_threshold=config['negative_count_threshold'], 
            channel=config['slack_channel']
        )
    
    print("\nPerformance Metrics Hub completed.")