
import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import setup_llms, translate_texts

def test_ai_translation():
    load_dotenv()
    print("Setting up LLMs...")
    llm_insights, llm_translate = setup_llms()
    
    if not llm_translate:
        print("FAIL: llm_translate could not be initialized")
        return

    print(f"LLM initialized: {llm_translate.model_name}")
    
    test_texts = ["In the beginning God created the heaven and the earth.", "God is love."]
    print(f"Translating: {test_texts}")
    
    try:
        translated = translate_texts(test_texts, llm_translate)
        print(f"Result: {translated}")
        
        if len(translated) == 2 and translated[0] != test_texts[0]:
            print("PASS: Translation seems to have worked (content changed).")
        else:
            print("FAIL: Translation output identical or mismatch.")
            
    except Exception as e:
        print(f"FAIL: Translation raised exception: {e}")

if __name__ == "__main__":
    test_ai_translation()
