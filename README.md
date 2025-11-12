# AI-Based Automated Content Marketing Optimizer

## Infosys Springboard Internship 6.0 Project - Module 1

### Project Title
AI Based Automated Content Marketing Optimizer

### Problem Statement
To develop an advanced AI system that generates and optimizes marketing content by analyzing audience engagement and trends to create high-impact campaigns. Leveraging LLMs for content creation and sentiment analysis, with integrations to social media APIs, Google Sheets for performance metrics, and Slack for team collaborations, the platform will suggest content variations, predict viral potential, and automate A/B testing. This will enable marketing teams to produce targeted, data-driven content faster, boost audience reach, and maximize ROI on digital campaigns.

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

### **Project Structure (Module 1)**

The repository is organized as follows:

AI-Content-Optimizer/

├── .gitignore                          # Specifies files and directories to be ignored by Git.

├── README.md                           # This comprehensive project overview.

├── requirements.txt                    # Lists all Python package dependencies.

├── credentials.py.example              # Example file for API keys.

├── service_account.json.example        # Example file for Google Service Account credentials.

├── slack_notifier.py                   # Module for sending Slack notifications.

├── upload_to_sheets.py                 # Utility for uploading DataFrames to Google Sheets.

├── google_trends_extractor.py          # Script for extracting data from Google Trends.

├── reddit_data_extractor.py            # Script for collecting posts from Reddit.

├── twitter_data_extractor.py           # Script for fetching data from Twitter/X.

└── youtube_data_extractor.py           # Script for extracting data from YouTube.

---

### **Next Steps (Beyond Module 1)**
*   **Data Cleaning and Preprocessing:** Preparing the raw data for LLM ingestion.
*   **Sentiment Analysis:** Applying NLTK or more advanced models to gauge audience sentiment.
*   **LLM Integration:** Using OpenAI GPT or Meta LLaMA for content generation, summarization, and idea generation.
*   **Content Optimization & A/B Testing:** Developing logic to suggest content variations and predict viral potential.
*   **Dashboarding:** Creating visualizations of performance metrics.

---

### **Author**
Harpreet Singh

LinkedIn Profile : [https://www.linkedin.com/in/harpreet-singh-4baa7626a]

# AI-Based Automated Content Marketing Optimizer

## Project Statement

This project seeks to develop an advanced AI system that generates and optimizes marketing content by analyzing audience engagement and trends to create high-impact campaigns. Leveraging LLMs like OpenAI GPT and Meta LLaMA (and currently implemented Google Gemini) for content creation and sentiment analysis, with integrations to social media APIs, Google Sheets for performance metrics, and Slack for team collaborations, the platform will suggest content variations, predict viral potential, and automate A/B testing. This will enable marketing teams to produce targeted, data-driven content faster, boost audience reach, and maximize ROI on digital campaigns.

## Outcomes

*   Automated content generation with optimized variations for engagement.
*   Predictive analytics for viral potential and campaign performance.
*   Streamlined A/B testing with real-time adjustments.
*   Enhanced ROI through data-driven insights and audience targeting.

## Modules to be Implemented

*   **Content Generation and Optimization Engine:** Creates marketing content using LLMs (e.g., Google Gemini). Optimizes based on trends and engagement data (initial implementation in Module 2, further optimization in Module 3).
*   **Sentiment and Trend Analysis System:** Analyzes audience reactions across social media. Predicts content performance from sentiment signals (planned for Module 3).
*   **Performance Metrics and Slack Integration Hub:** Tracks metrics in Google Sheets and alerts via Slack. Automates reporting and collaboration updates (integrated in Modules 1 & 2).
*   **A/B Testing and Prediction Coach:** Runs automated tests and forecasts outcomes. Provides recommendations for campaign refinements (planned for Module 4).

## Milestones

*   **Milestone 1: Weeks 1-2 - Introduction & Initial Training**
    *   **Objective:** Set up the project infrastructure, introduce team members to the tools, and gather initial data for training models.
    *   **Tasks Achieved:**
        *   Integrated with social media APIs for Twitter/X, YouTube, and Reddit to collect raw marketing content data.
        *   Integrated with Google Trends API for related queries and interest-over-time data.
        *   Established auto-updating data storage in Google Sheets for all collected data.
        *   Set up Slack for team collaboration and automated notifications for data collection.
        *   Successfully extracted data from diverse social media platforms and Google Trends, storing it in dedicated Google Sheet worksheets.
        *   *Note: Facebook/Instagram API integration encountered significant restrictions requiring a verified business and app review, deemed out of scope for the internship. Alternative data sources (Twitter, YouTube, Reddit) provide a robust foundation.*

*   **Milestone 2: Weeks 3-4 - Module 2: Content Generation and Optimization Engine (Initial Implementation)**
    *   **Objective:** Build a foundational system for generating marketing content using Large Language Models and integrate it into the existing pipeline.
    *   **Tasks Achieved:**
        *   Integrated Google Gemini 2.0 Flash model for automated marketing content generation (`content_generator.py`).
        *   Developed a content generation function that can produce various content types (e.g., tweets, ad copy, social media posts) based on product information, tone, and keywords.
        *   Configured the system to automatically upload generated content details (prompt, generated text, metadata) to a dedicated Google Sheet worksheet (`Generated_Marketing_Content`).
        *   Integrated Slack notifications to alert the team when new marketing content has been successfully generated and uploaded to Google Sheets.
        *   *Initial development of data optimization (using `data_optimizer.py`) and trend prediction (`trend_predictor.py`) was started but will be fully implemented and integrated in Milestone 3, focusing on refining content generation based on data insights.*

## Project Structure

The repository is organized as follows:

AI-Content-Optimizer/
├── .gitignore # Specifies files and directories to be ignored by Git (e.g., sensitive credentials, virtual environments, generated data files).
├── README.md # This comprehensive project overview.
├── requirements.txt # Lists all Python package dependencies required for the project.
├── credentials.py.example # An example file demonstrating the structure for API keys and secrets. (Actual 'credentials.py' is git-ignored)
├── service_account.json.example # An example file demonstrating the structure for Google Service Account credentials. (Actual 'service_account.json' is git-ignored)
├── check_gemini_models.py # Utility script to list available Google Gemini models via API.
├── content_generator.py # Core module for generating marketing content using LLMs (Google Gemini).
├── data_optimizer.py # Module for analyzing collected data to extract optimization insights (partially implemented in M2, full integration in M3).
├── google_trends_extractor.py # Script for extracting trending search queries and interest data from Google Trends.
├── reddit_data_extractor.py # Script for collecting product-related posts and discussions from Reddit communities.
├── slack_notifier.py # Python module responsible for sending automated notifications to Slack.
├── trend_predictor.py # Script for time-series forecasting of trends (initial implementation in M2, full integration in M3).
├── twitter_data_extractor.py # Script for fetching marketing content and engagement data from Twitter/X.
├── upload_to_sheets.py # Utility script to facilitate uploading pandas DataFrames to Google Sheets.
└── youtube_data_extractor.py # Script for extracting product review and launch videos, along with statistics, from YouTube.

## Google Sheets Integration Links

All collected and generated data is automatically stored and updated in the following Google Sheets:

*   **Main Data Hub:** [Link to your `AI_Content_Optimizer_Data` Google Sheet]
    *   Worksheet: `Twitter_Marketing_Tweets` (contains tweets data)
    *   Worksheet: `YouTube_Product_Content` (contains YouTube videos data)
    *   Worksheet: `Reddit_Product_Content` (contains Reddit posts data)
    *   Worksheet: `Google_Trends_Related_Queries` (contains Google Trends related queries)
    *   Worksheet: `Google_Trends_Interest_Over_Time` (contains Google Trends interest scores)
    *   Worksheet: `Generated_Marketing_Content` (contains output from the LLM content generator)

**Note:** Please replace `[Link to your AI_Content_Optimizer_Data Google Sheet]` with the actual shareable link to your main Google Sheet.

## Slack Integration

Automated notifications and alerts are sent to a dedicated Slack channel for real-time team collaboration and updates on data collection and content generation processes.

*   **Channel:** `[Your Slack Channel Name, e.g., #ai-marketing-updates]`

---