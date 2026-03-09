import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    # Using user specified model
    model = "gemini-3-flash-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Hello"}]}]
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Gemini Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Gemini API: Connection Success")
        else:
            print(f"❌ Gemini API: Failed - {response.text}")
    except Exception as e:
        print(f"❌ Gemini API: Error - {str(e)}")

def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # User specified model
    model = "openai/gpt-oss-120b"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello"}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Groq Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Groq API: Connection Success")
        else:
            print(f"❌ Groq API: Failed - {response.text}")
    except Exception as e:
        print(f"❌ Groq API: Error - {str(e)}")

def test_image_gen():
    # Testing Pollinations.ai (Free, High Quality)
    prompt = "A futuristic software testing laboratory in 2026, cinematic lighting, 8k"
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Image Gen (Pollinations): Connection Success")
        else:
            print(f"❌ Image Gen: Failed - {response.status_code}")
    except Exception as e:
        print(f"❌ Image Gen: Error - {str(e)}")

if __name__ == "__main__":
    print("--- 🔗 Phase 2: Link Verification ---")
    test_gemini()
    test_groq()
    test_image_gen()
