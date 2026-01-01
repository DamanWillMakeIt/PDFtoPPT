import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List all available models
models = genai.list_models()

print("Available Gemini Models:\n")
for m in models:
    # print all attributes to see what we have
    print(f"- {m.name}")
