import os
import json

METADATA_DIR = "metadata"

# Ensure directory exists on startup
os.makedirs(METADATA_DIR, exist_ok=True)

def save_metadata(filename: str, metadata: dict):
    path = os.path.join(METADATA_DIR, f"{filename}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                metadata,
                f,
                indent=4,
                ensure_ascii=False
            )
    except Exception as e:
        print(f"Error saving metadata for {filename}: {e}")

def get_metadata_by_filename(filename: str):
    path = os.path.join(METADATA_DIR, f"{filename}.json")
    
    if not os.path.exists(path):
        return None
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Corrupted metadata file found: {path}")
        return None

def get_all_metadata():
    results = []
    for file in os.listdir(METADATA_DIR):
        if file.endswith(".json"):
            # Strip the .json extension to pass just the filename
            original_filename = file[:-5] 
            metadata = get_metadata_by_filename(original_filename)
            if metadata:
                results.append(metadata)
    return results