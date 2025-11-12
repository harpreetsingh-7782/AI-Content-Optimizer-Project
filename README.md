# AI-Based Automated Content Marketing Optimizer

## Infosys Springboard Internship 6.0 Project - Module 1

### Project Title
AI Based Automated Content Marketing Optimizer

### Problem Statement
To develop an advanced AI system that generates and optimizes marketing content by analyzing audience engagement and trends to create high-impact campaigns. Leveraging LLMs for content creation and sentiment analysis, with integrations to social media APIs, Google Sheets for performance metrics, and Slack for team collaborations, the platform will suggest content variations, predict viral potential, and automate A/B testing. This will enable marketing teams to produce targeted, data-driven content faster, boost audience reach, and maximize ROI on digital campaigns.

This project seeks to develop an advanced AI system that generates and optimizes marketing content by analyzing audience engagement and trends to create high-impact campaigns. Leveraging LLMs like OpenAI GPT, **Google Gemini**, and Meta
LLaMA for content creation and sentiment analysis...

● Content Generation and Optimization Engine
  * Creates marketing content using LLMs (**Google Gemini 2.0 Flash implemented**).
  * Optimizes based on trends and engagement data. (To be enhanced in Module 3)

---

## Module 1: Introduction and Initial Training

### Objective
Set up the project infrastructure, introduce team members to the tools (LLMs like OpenAI GPT, Meta LLaMA), and gather initial data for training models.

### Accomplished Tasks (Milestone 1)

This module successfully established the core data collection and notification infrastructure. The following tasks have been completed:

1.  **Social Media API Integration & Data Extraction:**
    *   **Twitter/X:** Integrated with the Twitter API (v2) to extract marketing content related to new product launches, technology trends, and industry-specific innovations. Data collected includes tweet text, engagement metrics (#likes, #retweets, #comments, #impressions), author information, hashtags, and URLs.
    *   **YouTube:** Integrated with the YouTube Data API (v3) to extract product-centric video content. Data collected includes video titles, descriptions, channel information, and engagement statistics (views, likes, comments).
    *   **Reddit:** Integrated with the Reddit API via PRAW to extract product-related posts and discussions from relevant subreddits. Data collected includes post titles, self-text, URLs, author, subreddit, score, and comment counts.
    *   **Facebook/Instagram:** Attempted integration with the Facebook Graph API. However, due to Meta's strict API access requirements (e.g., verified business portfolio, formal App Review process for `pages_show_list`, `pages_read_engagement` permissions), direct broad content extraction from these platforms was deemed infeasible within the scope of this virtual internship. The project focuses on leveraging other robust social media data sources.

2.  **Google Trends Data Integration:**
    *   Integrated with Google Trends using the `pytrends` library to collect "Interest Over Time" data for a diverse set of product and technology keywords.
    *   Also extracted "Related Queries" and "Related Topics" for content ideation and trend identification.

3.  **Google Sheets Integration (Performance Metrics Storage):**
    *   Developed a robust `upload_to_sheets.py` utility that automatically connects to Google Sheets using a service account.
    *   All extracted data from Twitter, YouTube, Reddit, and Google Trends is automatically uploaded and organized into dedicated worksheets within a central Google Sheet (`AI_Content_Optimizer_Data`). This ensures a centralized, accessible, and auto-updating repository for performance metrics.
    *   **Link to Google Sheet:** [https://docs.google.com/spreadsheets/d/1aAdsgz9AagAOxkRSoxdaIaJ6N76U8G1xb4mPC-_h5HE/edit?usp=sharing]
4.  **Slack Integration (Team Collaborations):**
    *   Integrated with Slack using Incoming Webhooks to send automated notifications about data collection status, detected trends, or other critical updates to a designated Slack channel.
    *   Enables real-time communication and alerts for the marketing team.
    *   **Example Notification:** `Urgent: New trending product detected on YouTube! Check the 'YouTube_Product_Content' sheet.`
    *   **Slack Invite link:** [https://join.slack.com/t/infosysspring-7m32270/shared_invite/zt-3h12ctq9c-DSZkMIDzuFazAGsZf3_DFw]
  
5. **Run Data Extractors:**
    You can run each extractor individually:
    ```bash
    python twitter_data_extractor.py
    python youtube_data_extractor.py
    python reddit_data_extractor.py
    python google_trends_extractor.py
    ```
    Each script will collect data, save it locally as a CSV, and then upload it to the designated worksheets in your `AI_Content_Optimizer_Data` Google Sheet, sending Slack notifications where configured.

---

## Module 2:  Core Content Generation Engine using Google Gemini

● Milestone 2: Weeks 3-4 - Module 1: Content Generation and Optimization Engine
  * Objective: Successfully built a foundational system for generating and optimizing marketing content.
  * Tasks:
    *   **Implemented initial content drafting capabilities using Google Gemini 2.0 Flash models (`content_generator.py`).**
    *   **Integrated content generation with Google Sheets for structured data logging (`upload_to_sheets.py`).**
    *   **Enabled real-time team collaboration updates via Slack notifications upon new content generation (`slack_notifier.py`).**
    *   *Initial exploration of optimization algorithms and data utilization completed; further development deferred to Module 3.*

### **Project Structure (Module 1-2)**

The repository is organized as follows:

AI-Content-Optimizer/

├── .gitignore        A                  # Specifies files and directories to be ignored by Git.

├── README.md                           # This comprehensive project overview.

├── requirements.txt                    # Lists all Python package dependencies.

├── credentials.py.example              # Example file for API keys.

├── service_account.json.example        # Example file for Google Service Account credentials.

├── slack_notifier.py                   # Module for sending Slack notifications.

├── upload_to_sheets.py                 # Utility for uploading DataFrames to Google Sheets.

├── check_gemini_models.py              # Utility script to check available Gemini models. (Optional, if you created this)

├── content_generator.py                # Core module for generating marketing content using LLMs (Google Gemini 2.0 Flash).

├── google_trends_extractor.py          # Script for extracting data from Google Trends.

├── reddit_data_extractor.py            # Script for collecting posts from Reddit.

├── twitter_data_extractor.py           # Script for fetching data from Twitter/X.

└── youtube_data_extractor.py           # Script for extracting data from YouTube.

---

### **Next Steps (Beyond Module 1-2)**
*   **Content Optimization & A/B Testing:** Developing logic to suggest content variations and predict viral potential.
*   **Predictive Analytics for Viral Potential:** Utilize machine learning models, trained on historical content performance, sentiment, and trend data, to predict the viral potential and overall campaign performance of new content variations.

---

### **Author**
Harpreet Singh

LinkedIn Profile : [https://www.linkedin.com/in/harpreet-singh-4baa7626a]
