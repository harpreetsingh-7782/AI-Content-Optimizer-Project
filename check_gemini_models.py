# check_gemini_models.py

import google.generativeai as genai
import os

try:
    from credentials import GEMINI_API_KEY
    genai.configure(api_key=GEMINI_API_KEY)
except ImportError:
    print("Error: GEMINI_API_KEY not found in credentials.py. Please add it.")
    exit()
except AttributeError:
    print("Error: GEMINI_API_KEY is not set in credentials.py.")
    exit()

def list_available_gemini_models():
    """Lists all available Gemini models and their supported methods."""
    print("Listing available Gemini models...")
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(f"  Model Name: {m.name}")
                print(f"    Description: {m.description}")
                print(f"    Supported Methods: {m.supported_generation_methods}")
                print(f"    Input Token Limit: {m.input_token_limit}")
                print(f"    Output Token Limit: {m.output_token_limit}")
                print("-" * 30)
    except Exception as e:
        print(f"Error listing models: {e}")
        print("Please ensure your GEMINI_API_KEY is correct and active.")
        print("You might also check your Google AI Studio dashboard for any service interruptions or quota limits.")

if __name__ == "__main__":
    list_available_gemini_models()