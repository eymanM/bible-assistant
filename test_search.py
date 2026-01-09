
import requests
import json
import time

def test_search():
    url = "http://127.0.0.1:5000/search"
    payload = {
        "query": "modlitwa",
        "settings": {
            "language": "pl",
            "commentary": True,
            "oldTestament": True,
            "newTestament": True
        }
    }
    
    print("Sending request...")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, stream=True)
        print(f"Response status: {response.status_code}")
        
        first_chunk_received = False
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Received chunk: {decoded_line[:100]}...") # Print first 100 chars
                if not first_chunk_received:
                    print(f"First chunk received after {time.time() - start_time:.2f} seconds")
                    first_chunk_received = True
                
                if "bible_results" in decoded_line:
                    print("Found bible_results!")
                if "commentary_results" in decoded_line:
                    print("Found commentary_results!")
                    
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_search()
