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

def generate_content():
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-3-flash-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Load topic from intermediate
    try:
        with open(".tmp/topic.json", "r") as f:
            topic = json.load(f)
    except FileNotFoundError:
        print("ERROR: .tmp/topic.json not found. Run generate_topic.py first.")
        return

    prompt = f"""
You are a specialized LinkedIn strategist for the software testing community.
Input:
- Title: {topic['title']}
- Thesis: {topic['thesis']}
- Rationale: {", ".join(topic['rationale'])}

Your task:
Create a high-engagement LinkedIn post that is ULTRA-SIMPLE to read and STRONGLY SUPPORTS software testers.

Requirements:
1. Hook: 1 short sentence that validates a tester's current struggle or future potential.
2. Structure: 
   - 1-2 sentences per paragraph. Use double line breaks.
   - Use standard bullets.
3. Content: 
   - Transform complex QA jargon into simple value.
   - Emphasize how this AI shift empowers the human tester to do more meaningful work.
   - Use "we" and "us" to build community with fellow testers.
4. Formatting: 
   - Use standard ASCII only.
   - Clear and punchy mobile-first design.
5. Ending: 1 sharp takeaway and 1 community-focused question.

Tone: Supportive, insightful, and visionary. Avoid corporate management-speak.
Target Audience: Software Testers, QA Engineers, and SDETs.

Also provide an Image Suggestion:
- Describe a visually EXHILARATING and ATTRACTIVE image concept.
- Think: "Cyberpunk QA", "Futuristic Lab", "Epic AI Guardian", or "Hyper-clean 3D Abstract".
- High contrast, vibrant colors (electric blue, neon purple, or sleek gold).

Output must be valid JSON:
{{
    "hook": "Sharp Hook",
    "body": "Post body with double line breaks for readability",
    "takeaway": "Simple takeaway for testers",
    "question": "Community question",
    "image_concept": "Vibrant and attractive image description"
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            # Extract the Gemini parts
            try:
                raw_text = result['candidates'][0]['content']['parts'][0]['text']
                # Clean up markdown if Gemini wrapped it in ```json blocks
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()
                
                content_data = json.loads(raw_text)
                with open(".tmp/content.json", "w", encoding="utf-8") as f:
                    json.dump(content_data, f, indent=4)
                print("SUCCESS: Content Generated and saved to .tmp/content.json")
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"ERROR parsing Gemini response: {e}")
                print(f"Raw response: {result}")
                sys.exit(1)
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    generate_content()
