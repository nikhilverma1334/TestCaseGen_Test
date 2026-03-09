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

def synthesize_image():
    try:
        with open(".tmp/content.json", "r") as f:
            content = json.load(f)
    except FileNotFoundError:
        print("ERROR: .tmp/content.json not found. Run generate_content.py first.")
        return

    concept = content.get("image_concept", "Futuristic technology minimal")
    # Clean up concept for URL
    clean_concept = concept.replace(" ", "%20").replace("\n", "").replace(".", "")
    # Add attraction boosters
    prompt = f"{clean_concept},%20cinematic,%20vibrant%20colors,%20hyper-realistic,%20unreal%20engine%205,%20neon%20lighting,%20masterpiece"
    
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1080&nologo=true"
    
    print(f"📡 Requesting image for: {concept[:50]}...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(".tmp", exist_ok=True)
            with open(".tmp/post_image.jpg", "wb") as f:
                f.write(response.content)
            print("SUCCESS: Image synthesized and saved to .tmp/post_image.jpg")
        else:
            print(f"ERROR: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    synthesize_image()
