
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TEXTBEE_API_KEY")
DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID")
BASE_URL = os.getenv(
    "TEXTBEE_BASE_URL",
    "https://api.textbee.dev/api/v1"
)

if not API_KEY or not DEVICE_ID:
    raise ValueError("TextBee credentials are missing in .env")

headers = {
    "x-api-key": API_KEY
}

# Step 1: Verify API key
response = requests.get(
    f"{BASE_URL}/gateway/stats",
    headers=headers,
    timeout=20
)

print("API verification:", response.status_code)

if response.status_code != 200:
    print("Connection failed:", response.text)
    raise SystemExit(1)

print("TextBee API connected successfully!")

# Step 2: Send test SMS to your own number
number = input("Enter your own mobile number (+91XXXXXXXXXX): ")
message = "Test SMS from RakshaAI. TextBee integration is working!"

payload = {
    "recipients": [number],
    "message": message,
    "deviceId": DEVICE_ID
}

response = requests.post(
    f"{BASE_URL}/gateway/send-sms",
    headers={
        **headers,
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=30
)

print("SMS API response:", response.status_code)
print(response.text)
