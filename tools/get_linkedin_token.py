import os
import webbrowser
import requests
import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

# Configuration
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080"
SCOPES = "openid profile w_member_social"

class OAuthHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        if "code" in query_components:
            OAuthHandler.auth_code = query_components["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Success!</h1><p>You can close this window now and return to the terminal.</p>")
        else:
            self.send_response(400)
            self.end_headers()

def get_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ ERROR: LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET missing in .env")
        return

    # 1. Ask user to add Redirect URI
    print("\n--- 🛠️ OAuth Configuration ---")
    print(f"1. Go to: https://www.linkedin.com/developers/apps/{CLIENT_ID}/auth")
    print(f"2. Add '{REDIRECT_URI}' to 'Authorized Redirect URLs'.")
    print("3. Ensure 'Share on LinkedIn' or 'Sign In with LinkedIn' products are enabled.")
    input("\nPress Enter once you have added the Redirect URI...")

    # 2. Build Auth URL
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}"
    )

    print("\n--- 🔗 Authorization ---")
    print("Opening browser for LinkedIn login...")
    webbrowser.open(auth_url)

    # 3. Start Local Server
    server = HTTPServer(("localhost", 8080), OAuthHandler)
    print("Waiting for callback on http://localhost:8080...")
    while OAuthHandler.auth_code is None:
        server.handle_request()

    code = OAuthHandler.auth_code
    print(f"✅ Authorization Code Received: {code[:10]}...")

    # 4. Exchange Code for Token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    print("📡 Exchanging code for Access Token...")
    response = requests.post(token_url, data=payload)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        # 5. Get Person URN (sub)
        print("👤 Fetching your Person URN...")
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        userinfo_headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_res = requests.get(userinfo_url, headers=userinfo_headers)
        
        person_urn = ""
        if userinfo_res.status_code == 200:
            person_urn = userinfo_res.json().get("sub")
            print(f"✅ Person URN Found: {person_urn}")
        
        # 6. Update .env
        with open(".env", "r") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                new_lines.append(f"LINKEDIN_ACCESS_TOKEN={access_token}\n")
            elif line.startswith("LINKEDIN_PERSON_URN="):
                new_lines.append(f"LINKEDIN_PERSON_URN={person_urn}\n")
            else:
                new_lines.append(line)
        
        with open(".env", "w") as f:
            f.writelines(new_lines)
            
        print("\n🎉 SUCCESS! .env file updated with Access Token and Person URN.")
    else:
        print(f"❌ Failed to get token: {response.status_code} - {response.text}")

if __name__ == "__main__":
    get_token()
