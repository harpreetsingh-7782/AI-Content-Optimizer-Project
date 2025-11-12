import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import os
import logging

# Suppress Prophet's verbose logging if you don't want to see all the Stan output
logging.getLogger('prophet').setLevel(logging.WARNING)

# --- Configuration ---
GOOGLE_TRENDS_INTEREST_PATH = "google_trends_interest_over_time.csv"
FORECAST_PERIOD_DAYS = 30 # Forecast 30 days into the future

def load_google_trends_data(file_path):
    """
    Loads and preprocesses Google Trends interest over time data for Prophet.
    Expected columns: 'date', 'keyword1', 'keyword2', ...
    """
    if not os.path.exists(file_path):
        print(f"Error: Google Trends data file not found at {file_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        # Ensure 'date' column exists and is in datetime format
        if 'date' not in df.columns:
            print(f"Error: 'date' column not found in {file_path}")
            return pd.DataFrame()
        df['date'] = pd.to_datetime(df['date'])
        return df
    except pd.errors.EmptyDataError:
        print(f"Warning: {file_path} is empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading or processing {file_path}: {e}")
        return pd.DataFrame()

def forecast_keyword_interest(keyword, df_trends, forecast_days=FORECAST_PERIOD_DAYS, plot_results=True):
    """
    Forecasts future interest for a given keyword using Prophet.

    Args:
        keyword (str): The keyword column name in the DataFrame to forecast.
        df_trends (pd.DataFrame): DataFrame containing 'date' and keyword interest data.
        forecast_days (int): Number of days into the future to forecast.
        plot_results (bool): Whether to display a plot of the forecast.

    Returns:
        pd.DataFrame: A DataFrame with the forecast, including 'ds', 'yhat', 'yhat_lower', 'yhat_upper'.
    """
    if df_trends.empty or keyword not in df_trends.columns:
        print(f"Cannot forecast for '{keyword}': DataFrame is empty or keyword column missing.")
        return pd.DataFrame()

    # Prepare data for Prophet: requires 'ds' (datestamp) and 'y' (value) columns
    # Prophet doesn't like column names with spaces, so let's clean it up if necessary.
    prophet_df = df_trends[['date', keyword]].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_df['y'] = pd.to_numeric(prophet_df['y'], errors='coerce') # Ensure y is numeric
    prophet_df = prophet_df.dropna(subset=['y']) # Drop rows where y is NaN

    if prophet_df.empty:
        print(f"After preprocessing, no valid data to forecast for '{keyword}'.")
        return pd.DataFrame()

    print(f"Training Prophet model for '{keyword}'...")
    model = Prophet(
        seasonality_mode='additive', # Can be 'additive' or 'multiplicative'
        changepoint_prior_scale=0.05, # Adjust to control trend flexibility
        daily_seasonality=False # Google Trends data is usually daily/weekly, no need for daily if it's weekly/monthly
    )
    # Add custom seasonality if your data has it (e.g., weekly, if it's not daily data)
    # model.add_seasonality(name='weekly', period=7, fourier_order=3) # Example
    
    model.fit(prophet_df)
    
    # Create future dataframe for forecasting
    future = model.make_future_dataframe(periods=forecast_days)
    
    # Make predictions
    forecast = model.predict(future)
    
    print(f"Forecast generated for '{keyword}'.")

    if plot_results:
        fig = model.plot(forecast)
        plt.title(f'Google Trends Interest Forecast for "{keyword}"')
        plt.xlabel('Date')
        plt.ylabel('Interest Score')
        plt.show()
        
        # Plot components (trend, seasonality)
        fig_comp = model.plot_components(forecast)
        plt.suptitle(f'Forecast Components for "{keyword}"', y=1.02) # Adjust title position
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap
        plt.show()

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Trend Prediction with Prophet ---")

    # Load your Google Trends data
    trends_df = load_google_trends_data(GOOGLE_TRENDS_INTEREST_PATH)

    if not trends_df.empty:
        # Get all keyword columns (excluding 'date')
        keywords_to_forecast = [col for col in trends_df.columns if col != 'date']

        if not keywords_to_forecast:
            print("No keyword columns found in Google Trends data to forecast.")
        else:
            for keyword in keywords_to_forecast:
                print(f"\n--- Forecasting for Keyword: '{keyword}' ---")
                forecast_result = forecast_keyword_interest(keyword, trends_df, plot_results=True)
                
                if not forecast_result.empty:
                    print(f"Forecast for '{keyword}' (next {FORECAST_PERIOD_DAYS} days):")
                    print(forecast_result.tail()) # Show last few forecast dates
                    
                    # You could save this forecast to a CSV or upload to Google Sheets
                    # For example:
                    # forecast_output_path = f"google_trends_forecast_{keyword.replace(' ', '_')}.csv"
                    # forecast_result.to_csv(forecast_output_path, index=False)
                    # print(f"Forecast saved to {forecast_output_path}")

                else:
                    print(f"Failed to generate forecast for '{keyword}'.")
    else:
        print("No Google Trends data loaded. Please ensure google_trends_interest_over_time.csv exists and is populated.")
    
    print("\n--- Trend Prediction Complete ---")