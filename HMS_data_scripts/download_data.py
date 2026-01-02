import os
import requests
import time
import random
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs

# --- CONFIGURATION ---
LINKS_FILE = "links.txt"
OUTPUT_DIR = "HearMyShip_Data"
WANTED_EXTENSIONS = ('.wav', '.jpg', '.jpeg')

def get_file_info(url):
    """Parses ScienceDB URL to get the intended filename and folder path."""
    params = parse_qs(urlparse(url).query)
    filename = params.get('fileName', ['unknown'])[0]
    remote_path = params.get('path', [''])[0]
    return filename, remote_path

def run_local_download():
    if not os.path.exists(LINKS_FILE):
        print(f"❌ Error: {LINKS_FILE} not found in this folder.")
        return

    # 1. Filter links locally (No network calls yet)
    with open(LINKS_FILE, "r") as f:
        all_lines = [line.strip() for line in f if line.strip()]
    
    tasks = []
    for url in all_lines:
        fname, r_path = get_file_info(url)
        if fname.lower().endswith(WANTED_EXTENSIONS):
            tasks.append({'url': url, 'fname': fname, 'path': r_path})

    print(f"📦 Total target files: {len(tasks)}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    current_wait = 10 # Initial wait time in seconds when blocked
    
    for task in tqdm(tasks, desc="Overall Progress"):
        # Create local folder structure
        sub_folder = os.path.dirname(task['path']).lstrip('/')
        local_dir = os.path.join(OUTPUT_DIR, sub_folder)
        os.makedirs(local_dir, exist_ok=True)
        local_file = os.path.join(local_dir, task['fname'])

        # SKIP if already exists
        if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
            continue

        # DOWNLOAD LOOP (Handles Retries)
        while True:
            try:
                r = session.get(task['url'], stream=True, timeout=30)
                
                if r.status_code == 200:
                    with open(local_file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    # Success: small random jitter to look human
                    current_wait = 10 
                    time.sleep(random.uniform(0.5, 1.5))
                    break

                elif r.status_code == 429:
                    print(f"\n🛑 Rate Limited. Waiting {current_wait}s...")
                    time.sleep(current_wait)
                    # Exponential Backoff: Double the wait time for next time (up to 10 mins)
                    current_wait = min(current_wait * 2, 600) 
                
                else:
                    print(f"\n⚠️ Server returned {r.status_code} for {task['fname']}. Skipping.")
                    break

            except Exception as e:
                print(f"\n📡 Connection error: {e}. Retrying in 30s...")
                time.sleep(30)

    print("\n✅ All finished! Your data is in the 'HearMyShip_Data' folder.")

if __name__ == "__main__":
    run_local_download()