import os
import wave
from PIL import Image
from tqdm import tqdm

# --- CONFIG ---
DATA_DIR = "HearMyShip_Data"

def check_files():
    corrupted_count = 0
    empty_count = 0
    valid_count = 0

    # Get a list of all files to check
    all_files = []
    for root, _, files in os.walk(DATA_DIR):
        for f in files:
            all_files.append(os.path.join(root, f))

    print(f"🧐 Auditing {len(all_files)} files for corruption...")

    for file_path in tqdm(all_files):
        # 1. Check for 0-byte files
        if os.path.getsize(file_path) == 0:
            # print(f"Empty: {file_path}")
            os.remove(file_path)
            empty_count += 1
            continue

        # 2. Check Audio Integrity (.wav)
        if file_path.lower().endswith(".wav"):
            try:
                with wave.open(file_path, 'rb') as f:
                    f.getparams() # Attempt to read headers
                valid_count += 1
            except Exception:
                # print(f"Corrupted Audio: {file_path}")
                os.remove(file_path)
                corrupted_count += 1

        # 3. Check Image Integrity (.jpg, .jpeg)
        elif file_path.lower().endswith((".jpg", ".jpeg")):
            try:
                with Image.open(file_path) as img:
                    img.verify() # Verify file integrity
                valid_count += 1
            except Exception:
                # print(f"Corrupted Image: {file_path}")
                os.remove(file_path)
                corrupted_count += 1

    print("\n" + "="*30)
    print("📊 AUDIT RESULTS")
    print("="*30)
    print(f"✅ Valid Files: {valid_count}")
    print(f"🗑️ Empty Files Deleted: {empty_count}")
    print(f"❌ Corrupted Files Deleted: {corrupted_count}")
    print("="*30)
    
    if empty_count > 0 or corrupted_count > 0:
        print("👉 Action: Run your 'download_data.py' again to fetch the missing files.")
    else:
        print("🎉 All files are healthy!")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        print(f"❌ Error: {DATA_DIR} folder not found.")
    else:
        check_files()

def check_completeness(links_file, data_dir):
    from urllib.parse import urlparse, parse_qs
    
    # Extract expected filenames from links.txt
    expected_filenames = set()
    with open(links_file, 'r') as f:
        for line in f:
            if any(ext in line.lower() for ext in ('.wav', '.jpg', '.jpeg')):
                params = parse_qs(urlparse(line.strip()).query)
                fname = params.get('fileName', ['unknown'])[0]
                expected_filenames.add(fname)

    # Check what we actually have
    actual_filenames = set()
    for _, _, files in os.walk(data_dir):
        for f in files:
            actual_filenames.add(f)

    missing = expected_filenames - actual_filenames
    
    print(f"📋 COMPLETENESS CHECK")
    print(f"Expected: {len(expected_filenames)}")
    print(f"Actual:   {len(actual_filenames)}")
    print(f"Missing:  {len(missing)}")
    
    if missing:
        print("\nFirst 5 missing files:")
        for m in list(missing)[:5]:
            print(f" - {m}")

# Usage:
# check_completeness("links.txt", "HearMyShip_Data")