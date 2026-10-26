
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY was not found in .env")

client = genai.Client(
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

print("Testing Gemini Flash-Lite...")

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="In one sentence, explain an HTTP 503 error.",
        config=types.GenerateContentConfig(
            max_output_tokens=100,
            thinking_config=types.ThinkingConfig(
                thinking_level="minimal"
            )
        )
    )

    print("SUCCESS: Gemini responded.")
    print(response.text)

except Exception as error:
    print("Gemini test failed:", type(error).__name__)
    print(str(error)[:500])
