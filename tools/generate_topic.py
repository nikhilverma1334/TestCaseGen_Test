import os
import json
import requests
import sys
from dotenv import load_dotenv

# Force UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

load_dotenv()

def generate_topic():
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = """
You are a senior QA architect and industry expert advocate for software testers in 2026.
Your task is to generate ONLY ONE topic about:
"AI Powered Software Testing in 2026"

Constraints:
- Focus on how AI solves real pain points for manual and automation testers (e.g., flaky tests, repetitive regression, documentation debt).
- The angle must EMPOWER the tester, showing how AI makes them "QA Leads" rather than obsolete.
- Choose a structural shift that actually improves the quality of life for a testing professional.
- The topic must be bold, specific, and advocate for the human tester's value in an AI-world.

Output MUST be valid JSON format:
{
    "title": "Empowering Title for Testers",
    "thesis": "Tester-centric thesis of value",
    "rationale": ["Pain point solved", "Efficiency gain", "New skill unlocked", "Strategic value", "Quality impact"]
}
"""

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            topic_data = json.loads(content)
            
            # Save to temporary intermediate file
            os.makedirs(".tmp", exist_ok=True)
            with open(".tmp/topic.json", "w", encoding="utf-8") as f:
                json.dump(topic_data, f, indent=4)
            
            print("SUCCESS: Topic Generated and saved to .tmp/topic.json")
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    generate_topic()
