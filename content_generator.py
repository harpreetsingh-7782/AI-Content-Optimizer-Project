import google.generativeai as genai
import pandas as pd # Import pandas
import os
import random
from datetime import datetime # Import datetime for timestamping

# Load API Key from credentials.py
try:
    from credentials import GEMINI_API_KEY
    genai.configure(api_key=GEMINI_API_KEY)
except ImportError:
    print("Error: GEMINI_API_KEY not found in credentials.py. Please add it.")
    exit()
except AttributeError:
    print("Error: GEMINI_API_KEY is not set in credentials.py.")
    exit()

# Import the Google Sheets uploader
try:
    from upload_to_sheets import upload_to_google_sheet
except ImportError:
    print("Warning: upload_to_sheets.py not found. Google Sheets upload will be skipped.")
    upload_to_google_sheet = None # Set to None if import fails

# --- Slack Notification Integration ---
    # Attempt to import the send_slack_notification function
    try:
        from slack_notifier import send_slack_notification
    except ImportError:
        print("Warning: slack_notifier.py not found. Slack notifications will be skipped.")
        send_slack_notification = None

def generate_marketing_content_gemini(product_info, content_type="tweet", tone="engaging", keywords=None):
    """
    Generates marketing content using Google's Gemini models based on product information.

    Args:
        product_info (str): A detailed description of the product, its features, and benefits.
        content_type (str): The type of content to generate (e.g., "tweet", "short ad copy", "blog post intro", "social media post").
        tone (str): The desired tone for the content (e.g., "engaging", "professional", "humorous", "informative", "playful").
        keywords (list): Optional list of keywords to include in the content.

    Returns:
        tuple: (str, dict) A tuple containing the generated marketing content and a dictionary
               of generation details for logging, or (error_message, None) if an error occurs.
    """
    
    prompt_parts = [
        f"Generate a {tone} {content_type} for the following product, aiming for maximum audience engagement and positive reception.",
        f"Product Description: {product_info}"
    ]
    if keywords:
        prompt_parts.append(f"Ensure to include these keywords: {', '.join(keywords)}.")
    
    if content_type == "tweet":
        prompt_parts.append("Keep it concise, ideally under 280 characters, and use relevant hashtags. Ensure content is positive and brand-safe.")
    elif content_type == "short ad copy":
        prompt_parts.append("Keep it under 60 words and highly persuasive. Ensure content is positive and brand-safe.")
    elif content_type == "blog post introduction":
        prompt_parts.append("Write a compelling introduction, around 150-200 words, that hooks the reader. Ensure content is positive and brand-safe.")
    elif content_type == "social media post":
        prompt_parts.append("Craft an engaging post suitable for platforms like Instagram or Facebook, including emojis if appropriate. Ensure content is positive and brand-safe.")

    full_prompt = "\n".join(prompt_parts)
    
    model_name = "models/gemini-2.0-flash" 

    generation_details = {
        "timestamp": datetime.now().isoformat(),
        "product_info_input": product_info,
        "content_type_requested": content_type,
        "tone_requested": tone,
        "keywords_used": ", ".join(keywords) if keywords else "",
        "model_used": model_name,
        "generated_content": "", # To be filled
        "status": "Failed",      # To be updated
        "error_message": ""      # To be filled on error
    }

    try:
        print(f"Generating {content_type} with Gemini model '{model_name}'...")
        model = genai.GenerativeModel(model_name)
        
        generation_config = {
            "temperature": 0.6,
            "max_output_tokens": 150 if content_type == "tweet" else 400,
        }
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config,
        )
        
        if not response.text:
            error_msg = f"Content generation was blocked. Finish Reason: {response.candidates[0].finish_reason}"
            if hasattr(response, 'prompt_feedback'):
                error_msg += f" Prompt Feedback: {response.prompt_feedback}"
            if hasattr(response.candidates[0], 'safety_ratings'):
                error_msg += f" Safety Ratings: {response.candidates[0].safety_ratings}"
            print(error_msg)
            
            generation_details["error_message"] = error_msg
            return "Content generation blocked by safety filters.", generation_details
        
        generated_text = response.text.strip()
        print("Content generated successfully.")
        
        generation_details["generated_content"] = generated_text
        generation_details["status"] = "Success"
        
        return generated_text, generation_details

    except Exception as e:
        error_msg = f"Gemini API Error or unexpected error: {e}"
        print(error_msg)
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
            error_msg += f" Prompt feedback from error: {e.response.prompt_feedback}"
            print(f"Prompt feedback from error: {e.response.prompt_feedback}")
            
        generation_details["error_message"] = error_msg
        return f"Error generating content: {e}", generation_details

# --- Example Usage ---
if __name__ == "__main__":
    generated_data_records = [] # List to store details of all generated content

    example_product_info = (
        "Introducing the 'LumiCharge Pro' – an all-in-one desk lamp with a built-in wireless charger, "
        "multiple lighting modes (warm, cool, natural), and a smart calendar display. "
        "It's perfect for enhancing productivity and decluttering your workspace. Sleek, minimalist design."
    )

    print("\n--- Generating a Tweet ---")
    tweet_content, tweet_details = generate_marketing_content_gemini(
        example_product_info,
        content_type="tweet",
        tone="exciting",
        keywords=["#LumiChargePro", "#SmartDesk", "#WirelessCharging", "#Productivity", "#TechGadget", "#HomeOffice"]
    )
    print("Generated Tweet:")
    print(tweet_content)
    generated_data_records.append(tweet_details) # Add details to our list

    print("\n--- Generating a Short Ad Copy ---")
    ad_copy, ad_details = generate_marketing_content_gemini(
        example_product_info,
        content_type="short ad copy",
        tone="persuasive",
        keywords=["declutter", "charge", "illuminate", "workspace", "efficiency", "modern design"]
    )
    print("Generated Ad Copy:")
    print(ad_copy)
    generated_data_records.append(ad_details) # Add details to our list

    print("\n--- Generating a Social Media Post (Instagram/Facebook) ---")
    social_post, social_details = generate_marketing_content_gemini(
        example_product_info,
        content_type="social media post",
        tone="friendly",
        keywords=["#WorkspaceGoals", "#TechGadget", "#SmartLiving", "#HomeUpgrade", "#MinimalistDesign", "#Productivity", "#AI"]
    )
    print("Generated Social Media Post:")
    print(social_post)
    generated_data_records.append(social_details) # Add details to our list

    # --- Integrate with Google Sheets ---
    if upload_to_google_sheet:
        print("\n--- Uploading generated content to Google Sheets ---")
        try:
            generated_df = pd.DataFrame(generated_data_records)
            from upload_to_sheets import upload_to_google_sheet
            print("\nAttempting to upload data to Google Sheets...")
            upload_to_google_sheet(generated_df, "AI_Content_Optimizer_Data", "Generated_Marketing_Content")
            print("Successfully uploaded generated content to Google Sheets.")
        except ImportError:
            print("\nWarning: upload_to_sheets.py not found. Skipping Google Sheets upload.")
        except Exception as e:
            print(f"\nError uploading to Google Sheets: {e}")

    else:
        print("\nSkipping Google Sheets upload as 'upload_to_sheets.py' was not found or import failed.")

    # --- Slack Notification Integration ---
    from slack_notifier import send_slack_notification

    if send_slack_notification:
                slack_message = (
                    f":sparkles: New marketing content generated and uploaded! :page_with_curl:\n"
                    f"Product: *LumiCharge Pro*\n"
                    f"Generated {len(generated_data_records)} pieces of content (Tweet, Ad Copy, Social Post).\n"
                    f"Check the Google Sheet here: https://docs.google.com/spreadsheets/d/1aAdsgz9AagAOxkRSoxdaIaJ6N76U8G1xb4mPC-_h5HE/edit?usp=sharing\n" # IMPORTANT: Replace with actual link
                    f"Worksheet: AI_Content_Optimizer_Data\n"
                    f"Check: Generated_Marketing_Content worksheet for the details."
                )
                # MODIFICATION HERE: Add username and icon_emoji
                send_slack_notification(
                    slack_message,
                    username="ContentGenius Bot", # A more specific name for content generation alerts
                    icon_emoji=":bulb:" # A lightbulb emoji to signify new ideas/content
                )
                
    else:
        print("Slack notification function not available.")
    


    
