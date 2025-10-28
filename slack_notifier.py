# slack_notifier.py
import requests
import json
import os

# Load Slack Webhook URL from credentials.py
try:
    from credentials import SLACK_WEBHOOK_URL
except ImportError:
    SLACK_WEBHOOK_URL = None
    print("Warning: SLACK_WEBHOOK_URL not found in credentials.py. Slack notifications will be disabled.")

def send_slack_notification(message, channel=None, username="AI Content Optimizer Bot", icon_emoji=":robot_face:"):
    """
    Sends a message to a Slack channel using an Incoming Webhook.

    Args:
        message (str): The text message to send.
        channel (str, optional): The channel to post to (e.g., "#general"). 
                                 If None, uses the default channel configured for the webhook.
        username (str, optional): The name that will appear as the sender.
        icon_emoji (str, optional): An emoji to use as the bot's icon.
    """
    if not SLACK_WEBHOOK_URL:
        print(f"Slack notification skipped: {message} (Webhook URL not configured)")
        return False

    headers = {'Content-type': 'application/json'}
    
    payload = {
        "text": message,
        "username": username,
        "icon_emoji": icon_emoji,
    }
    if channel:
        payload["channel"] = channel # Override the default channel if specified

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        print(f"Slack notification sent successfully: {message}")
        return True
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while sending Slack notification: {err}")
        print(f"Response text: {response.text}")
        return False
    except requests.exceptions.ConnectionError as err:
        print(f"Connection error occurred while sending Slack notification: {err}")
        return False
    except requests.exceptions.Timeout as err:
        print(f"Timeout error occurred while sending Slack notification: {err}")
        return False
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred while sending Slack notification: {err}")
        return False

if __name__ == "__main__":
    # Example Usage:
    print("Attempting to send a test Slack notification...")
    test_message = "🤖 AI Content Optimizer: *Test notification!* All systems nominal for data collection."
    success = send_slack_notification(test_message)
    if success:
        print("Test notification function called successfully.")
    else:
        print("Test notification failed or was skipped.")

    print("\nAttempting to send a second test notification with custom channel and emoji...")
    second_test_message = "🔔 Urgent: New trending product detected on YouTube! Check the 'YouTube_Product_Content' sheet."
    # If your webhook is configured for #general, you might need to specify a channel like "#marketing-alerts"
    # send_slack_notification(second_test_message, channel="#marketing-alerts", icon_emoji=":bell:")
    # For now, let's just send to the default webhook channel.
    send_slack_notification(second_test_message, icon_emoji=":bell:")