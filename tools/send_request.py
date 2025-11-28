from langchain_core.tools import tool
from shared_store import BASE64_STORE, url_time
import time
import os
import requests
import json
from collections import defaultdict
from typing import Any, Dict, Optional

cache = defaultdict(int)
retry_limit = 3  # Reduced to 3 to fail faster

@tool
def post_request(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
    """
    Send an HTTP POST request. 
    CRITICAL: If the server returns a NEW URL, this tool updates the environment 
    to proceed to that new URL immediately, even if the answer was incorrect.
    """
    # Handling if the answer is a BASE64
    ans = payload.get("answer")
    if isinstance(ans, str) and ans.startswith("BASE64_KEY:"):
        try:
            key = ans.split(":", 1)[1]
            payload["answer"] = BASE64_STORE[key]
        except KeyError:
            return "Error: Image key not found in memory. Please regenerate the image."

    headers = headers or {"Content-Type": "application/json"}
    
    try:
        cur_url = os.getenv("url")
        cache[cur_url] += 1
        
        # Logging (truncated for cleanliness)
        sending = payload.copy()
        if isinstance(payload.get("answer"), str) and len(payload.get("answer", "")) > 100:
            sending["answer"] = payload["answer"][:100] + "...(truncated)"
            
        print(f"\nSending Answer to {url}")

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("Got the response: \n", json.dumps(data, indent=4), '\n')

        # --- CRITICAL LOGIC FIX ---
        server_next_url = data.get("url")
        
        # 1. IF SERVER GIVES A NEW URL -> MOVE ON IMMEDIATELY
        if server_next_url and server_next_url != cur_url:
            print(f"⏩ Server indicated progression to: {server_next_url}")
            os.environ["url"] = server_next_url
            os.environ["offset"] = "0" # Reset timer for new level
            
            # Ensure we don't accidentally retry
            if next_url_time := url_time.get(server_next_url):
                 pass 
            else:
                 url_time[server_next_url] = time.time()
                 
            return data

        # 2. IF SERVER KEEPS US ON SAME URL (or null) -> CHECK RETRY LOGIC
        correct = data.get("correct")
        if not correct:
            delay = time.time() - url_time.get(cur_url, time.time())
            
            # Fail conditions: Too many retries OR Too much time
            if cache[cur_url] >= retry_limit or delay >= 150: 
                print("❌ Retry limit/Time limit reached. Moving on (simulated).")
                # If server didn't give a URL, we might be stuck, but we stop retrying
                return data 
            else:
                # Force the agent to retry locally
                print("🔄 Answer wrong. Retrying...")
                data["url"] = cur_url
                data["message"] = "Incorrect. Try again."
                return data

        # 3. Success case (Correct + Same URL? Unlikely but handle it)
        return data

    except requests.HTTPError as e:
        return f"HTTP Error: {e.response.text}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"