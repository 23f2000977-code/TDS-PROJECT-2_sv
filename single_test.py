import requests
import os
from dotenv import load_dotenv

# Load your email/secret from .env
load_dotenv()

# ==========================================
# 👇 CHANGE THIS URL TO THE ONE YOU WANT TO TEST
# ==========================================
TARGET_URL = "https://p2testingone.vercel.app/q1.html" 
# Other options:
# "https://tds-llm-analysis.s-anand.net/demo"
# "https://tds-llm-analysis.s-anand.net/demo2"
# "https://tdsbasictest.vercel.app/quiz/1"
# "https://p2testingone.vercel.app/q1.html" 
# ==========================================

SERVER_URL = "https://eddywait-tds-project-2-sv.hf.space/solve"
payload = {
    "email": os.getenv("EMAIL"),
    "secret": os.getenv("SECRET"),
    "url": TARGET_URL
}

print(f"🚀 Sending request for: {TARGET_URL}")

try:
    response = requests.post(SERVER_URL, json=payload)
    if response.status_code == 200:
        print("✅ Request Sent! Check your SERVER terminal for the logs.")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Failed to connect: {e}")