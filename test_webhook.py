import json
import requests

# Simulated payload from Supabase
payload = {
    "type": "INSERT",
    "table": "jaya_draws",
    "schema": "public",
    "record": {
        "lottery_name": "govisetha",
        "draw_no": 4373,
        "date": "Thursday March 12, 2026",
        "letter": "Y",
        "numbers": [35, 43, 46, 76],
        "prize_structure": None,
        "created_at": "2026-03-12 17:25:38.234564+00:00"
    },
    "old_record": None
}

headers = {"Content-Type": "application/json"}
print("Sending test webhook payload to http://127.0.0.1:8000/webhook/supabase-draw-event ...")

try:
    response = requests.post("http://127.0.0.1:8000/webhook/supabase-draw-event", json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
