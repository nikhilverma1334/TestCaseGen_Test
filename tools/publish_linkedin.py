import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def upload_image(access_token, person_id, image_path):
    """Uploads an image to LinkedIn and returns the asset URN."""
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        return None

    # Step 1: Initialize image upload
    url = "https://api.linkedin.com/rest/images?action=initializeUpload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202602",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "initializeUploadRequest": {
            "owner": f"urn:li:person:{person_id}"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"ERROR: Image initialization failed: {response.text}")
            return None
        
        upload_data = response.json()["value"]
        upload_url = upload_data["uploadUrl"]
        image_urn = upload_data["image"]

        # Step 2: Upload the binary
        with open(image_path, "rb") as f:
            upload_response = requests.put(upload_url, data=f, headers={"Authorization": f"Bearer {access_token}"})
            if upload_response.status_code != 201:
                print(f"ERROR: Image binary upload failed: {upload_response.status_code}")
                return None
        
        print(f"SUCCESS: Image uploaded. Asset: {image_urn}")
        return image_urn
    except Exception as e:
        print(f"EXCEPTION during image upload: {e}")
        return None

def publish_to_linkedin():
    # Load content with explicit UTF-8 encoding
    try:
        with open(".tmp/content.json", "r", encoding="utf-8") as f:
            content = json.load(f)
    except FileNotFoundError:
        print("ERROR: .tmp/content.json not found.")
        return

    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_id = os.getenv("LINKEDIN_PERSON_URN")

    if not access_token or not person_id:
        print("ERROR: Missing access token or Person URN.")
        return

    # Upload image if it exists
    image_path = ".tmp/post_image.jpg"
    image_urn = upload_image(access_token, person_id, image_path)

    # Prepare Post Body - Strip non-ASCII to prevent "â€™" style artifacts
    # and simplify formatting for readability
    post_text = f"{content['hook']}\n\n{content['body']}\n\n{content['takeaway']}\n\n{content['question']}"
    # Replace smart quotes with standard quotes
    post_text = post_text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2013', '-').replace('\u2014', '--')

    url = "https://api.linkedin.com/rest/posts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202602",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    payload = {
        "author": f"urn:li:person:{person_id}",
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    if image_urn:
        payload["content"] = {
            "media": {
                "title": "Autonomous Testing 2026",
                "id": image_urn
            }
        }

    print("Publishing to LinkedIn with Image...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print(f"SUCCESS: Post Published! URN: {response.headers.get('x-restli-id')}")
        else:
            print(f"ERROR: Failed to post: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION during publishing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    publish_to_linkedin()
