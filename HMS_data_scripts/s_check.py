import os

# --- CONFIG ---
DATA_DIR = "HearMyShip_Data"

def run_consistency_check():
    mismatches = []
    total_checked = 0

    print(f"🔍 Checking folder/file consistency in: {DATA_DIR}...")

    # Iterate through every folder
    for root, dirs, files in os.walk(DATA_DIR):
        if not files:
            continue
            
        # Get the current folder name (e.g., "Motorboat_16.08.23_catamaran")
        folder_name = os.path.basename(root).lower()
        
        for f in files:
            total_checked += 1
            # Extract the prefix of the file (e.g., "yacht" from "yacht_001.wav")
            file_prefix = f.split('_')[0].lower()
            
            # CHECK: Does the folder name contain the file's label?
            # We check if "yacht" is anywhere in "motorboat_16.08.23_catamaran"
            if file_prefix not in folder_name:
                mismatches.append({
                    'file': f,
                    'file_label': file_prefix,
                    'folder': folder_name,
                    'path': os.path.join(root, f)
                })

    # --- REPORTING ---
    print("\n" + "="*50)
    print("📊 CONSISTENCY REPORT")
    print("="*50)
    print(f"Total Files Scanned: {total_checked}")
    print(f"Inconsistent Files:  {len(mismatches)}")
    print("="*50)

    if mismatches:
        print("\n🚩 TOP 10 INCONSISTENCIES FOUND:")
        # Show unique folder/label conflicts
        seen_conflicts = set()
        count = 0
        for m in mismatches:
            conflict_id = f"{m['file_label']} inside {m['folder']}"
            if conflict_id not in seen_conflicts and count < 150:
                print(f"❌ Label '{m['file_label'].upper()}' found in folder '{m['folder']}'")
                seen_conflicts.add(conflict_id)
                count += 1
        
        print(f"\nWould you like to generate a full 'mismatches.txt' log? (y/n)")
    else:
        print("🎉 All files match their folder labels!")

if __name__ == "__main__":
    if os.path.exists(DATA_DIR):
        run_consistency_check()
    else:
        print("❌ Data directory not found.")