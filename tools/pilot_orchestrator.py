import subprocess
import os
import json
import sys
from datetime import datetime

# Force UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

def run_step(name, script):
    print(f"--- Running Step: {name} ---")
    result = subprocess.run(["python", script], capture_output=True, text=True, encoding="utf-8")
    
    # Defensive printing of stdout - ASCII only for Windows
    if result.stdout:
        print(result.stdout.encode('ascii', errors='ignore').decode('ascii'))
            
    if result.returncode == 0:
        return True
    else:
        print(f"ERROR in {name}:")
        if result.stderr:
            print(result.stderr.encode('ascii', errors='ignore').decode('ascii'))
        return False

def update_progress(status, notes):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"| {now} | Daily Automation | {status} | {notes} |\n"
    progress_path = "progress.md"
    if os.path.exists(progress_path):
        with open(progress_path, "a", encoding="utf-8") as f:
            f.write(log_line)

def generate_dashboard():
    print("--- Generating Dashboard ---")
    history_dir = "history"
    os.makedirs(history_dir, exist_ok=True)
    
    # Save current post to history
    now_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        if os.path.exists(".tmp/content.json"):
            with open(".tmp/content.json", "r", encoding="utf-8") as f:
                current_content = json.load(f)
            
            # Copy latest image to history
            import shutil
            if os.path.exists(".tmp/post_image.jpg"):
                img_name = f"image_{now_ts}.jpg"
                shutil.copy(".tmp/post_image.jpg", f"{history_dir}/{img_name}")
                current_content["image_path"] = img_name
            
            with open(f"{history_dir}/post_{now_ts}.json", "w", encoding="utf-8") as f:
                json.dump(current_content, f, indent=4)
    except Exception as e:
        print(f"Warning: Could not save to history: {e}")

    # Build the HTML
    try:
        posts = []
        # Load all history
        for file in sorted(os.listdir(history_dir), reverse=True):
            if file.startswith("post_") and file.endswith(".json"):
                with open(os.path.join(history_dir, file), "r", encoding="utf-8") as f:
                    p = json.load(f)
                    # Convert internal YYYYMMDD into DD/MM/YYYY
                    raw_date = file.split("_")[1] # e.g. 20260309
                    fmt_date = f"{raw_date[6:8]} {datetime.strptime(raw_date[4:6], '%m').strftime('%b')} {raw_date[0:4]}"
                    p["display_date"] = fmt_date
                    posts.append(p)

        posts_html = ""
        for p in posts:
            img_src = f"../history/{p.get('image_path', '')}" if p.get('image_path') else ""
            posts_html += f"""
            <div class="post-card">
                <div class="card-status">PUBLISHED</div>
                <img src="{img_src}" alt="Post Media" class="card-img">
                <div class="card-body">
                    <div class="card-date">{p.get('display_date', 'Unknown')}</div>
                    <h2 class="card-hook">{p['hook']}</h2>
                    <p class="card-text">{p['body'].replace('\n', '<br>')}</p>
                    <div class="card-footer">
                        <span class="takeaway-badge">Key Takeaway</span>
                        <p class="takeaway-text">{p['takeaway']}</p>
                    </div>
                </div>
            </div>
            """

        upcoming_date = (datetime.now().timestamp() + 86400)
        upcoming_fmt = datetime.fromtimestamp(upcoming_date).strftime("%d %b %Y")

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QA Pilot | Content Intelligence Dashboard</title>
    <style>
        :root {{
            --bg: #0b0f19;
            --card-bg: #161b22;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.4);
            --text-main: #e6edf3;
            --text-dim: #8b949e;
            --border: #30363d;
        }}
        * {{ box-sizing: border-box; transition: all 0.2s ease; }}
        body {{
            margin: 0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.6;
            overflow-x: hidden;
        }}
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 60px;
            background: rgba(11, 15, 25, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .logo {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -1px; color: var(--text-main); }}
        .logo span {{ color: var(--accent); }}
        .status-pill {{
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid var(--accent);
            text-transform: uppercase;
        }}
        .main-container {{ max-width: 1400px; margin: 40px auto; padding: 0 40px; }}
        .hero {{ margin-bottom: 60px; border-left: 4px solid var(--accent); padding-left: 30px; }}
        .hero h1 {{ font-size: 2.5rem; margin: 0; font-weight: 900; letter-spacing: -0.04em; }}
        .hero p {{ color: var(--text-dim); font-size: 1.1rem; margin-top: 10px; }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 40px;
        }}

        .post-card {{
            background: var(--card-bg);
            border-radius: 20px;
            border: 1px solid var(--border);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        .post-card:hover {{
            transform: translateY(-10px);
            border-color: var(--accent);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }}
        .card-status {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px);
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 800;
            color: var(--accent);
            z-index: 10;
        }}
        .card-img {{
            width: 100%;
            height: 240px;
            object-fit: cover;
            border-bottom: 1px solid var(--border);
        }}
        .card-body {{ padding: 30px; flex-grow: 1; }}
        .card-date {{ color: var(--accent); font-size: 0.85rem; font-weight: 700; margin-bottom: 15px; text-transform: uppercase; }}
        .card-hook {{ font-size: 1.4rem; font-weight: 800; line-height: 1.3; margin-bottom: 20px; color: #fff; }}
        .card-text {{ font-size: 0.95rem; color: var(--text-dim); margin-bottom: 30px; }}
        
        .card-footer {{
            padding-top: 25px;
            border-top: 1px solid var(--border);
        }}
        .takeaway-badge {{
            display: inline-block;
            font-size: 0.65rem;
            font-weight: 900;
            background: var(--accent);
            color: var(--bg);
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .takeaway-text {{ font-weight: 600; font-size: 0.9rem; margin: 0; color: #fff; }}

        .upcoming-card {{
            background: rgba(22, 27, 34, 0.4);
            border: 2px dashed var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 500px;
            text-align: center;
            border-radius: 24px;
        }}
        .upcoming-content h3 {{ font-size: 1.5rem; color: var(--text-dim); margin-bottom: 10px; }}
        .upcoming-content p {{ color: #484f58; font-weight: 600; }}
        
        .footer {{ text-align: center; margin-top: 100px; padding: 40px; border-top: 1px solid var(--border); color: #484f58; font-size: 0.8rem; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">QA<span>PILOT</span></div>
        <div class="status-pill">System Online</div>
    </div>

    <div class="main-container">
        <div class="hero">
            <h1>Content Architecture Hub</h1>
            <p>Empowering the software testing community with AI-driven insights and strategic narratives.</p>
        </div>

        <div class="content-grid">
            <div class="upcoming-card">
                <div class="upcoming-content">
                    <h3>UPCOMING SLOT</h3>
                    <p>Estimated Release: {upcoming_fmt}</p>
                </div>
            </div>
            {posts_html}
        </div>
    </div>

    <div class="footer">
        &copy; 2026 QA PILOT INTELLIGENCE | SENIOR QA ARCHITECT ADVOCACY ENGINE
    </div>
</body>
</html>
        """
        with open(".tmp/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("SUCCESS: Dashboard generated at .tmp/index.html")
    except Exception as e:
        print(f"ERROR: Failed to generate dashboard: {e}")

def main():
    print("Starting B.L.A.S.T. Orchestrator...")
    
    steps = [
        ("Topic Gen", "tools/generate_topic.py"),
        ("Content Gen", "tools/generate_content.py"),
        ("Image Synth", "tools/synthesize_image.py"),
        ("LinkedIn Pub", "tools/publish_linkedin.py")
    ]
    
    overall_success = True
    results_summary = []
    
    for name, script in steps:
        if run_step(name, script):
            results_summary.append(f"{name}: Success")
        else:
            results_summary.append(f"{name}: FAILED")
            overall_success = False
            break
            
    if overall_success:
        generate_dashboard()

    status = "SUCCESS" if overall_success else "FAILED"
    update_progress(status, ", ".join(results_summary))
    print(f"--- Orchestration Finished: {status} ---")

if __name__ == "__main__":
    main()
