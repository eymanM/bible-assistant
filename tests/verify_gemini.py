
import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from constants import GEMINI_MODEL_NAME

# Load env variables
load_dotenv()

def verify_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment variables.")
        return

    print(f"Testing Gemini model: {GEMINI_MODEL_NAME}")
    try:
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL_NAME,
            google_api_key=api_key,
            temperature=0,
        )
        response = llm.invoke("Hello, are you Gemini?")
        print("Response received:")
        print(response.content)
        print("SUCCESS: Gemini model is working.")
    except Exception as e:
        print(f"ERROR: Failed to invoke Gemini model: {e}")

if __name__ == "__main__":
    verify_gemini()
