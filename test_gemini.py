import os
from dotenv import load_dotenv
from google import genai

# Load the private API key from .env
load_dotenv()

# Check that the key exists without displaying it
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

# Connect to Gemini
client = genai.Client()

# Send one small test question
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="In one sentence, what is an HTTP 503 error?"
)

print("Gemini connection successful!")
print(response.text)