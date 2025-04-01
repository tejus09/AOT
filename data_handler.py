import os
import json
import glob
from typing import Dict, List, Tuple, Optional
import shutil
from config import INPUT_DIR, OUTPUT_DIR, PROGRESS_FILE

def get_all_samples() -> List[str]:
    """Get all JSON files from input directory"""
    json_files = glob.glob(os.path.join(INPUT_DIR, "*.json"))
    return sorted(json_files)

def get_image_path(json_path: str) -> str:
    """Get the corresponding image path for a JSON file"""
    base_name = os.path.basename(json_path)
    image_name = os.path.splitext(base_name)[0] + ".jpg"
    return os.path.join(INPUT_DIR, image_name)

def load_json_data(json_path: str) -> Dict:
    """Load JSON data from file"""
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Return empty dict if JSON is invalid
        return {}

def save_json_data(data: Dict, target_path: str) -> str:
    """Save JSON data to the specified path
    
    Args:
        data: The JSON data to save
        target_path: Path where to save the data
        
    Returns:
        str: The path where the data was saved
    """
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Write the data to the file
    with open(target_path, 'w') as f:
        json.dump(data, f, indent=4)  # Add indentation for better readability
    
    return target_path

def load_progress() -> Dict:
    """Load verification progress"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"verified": [], "pending": get_all_samples()}
    else:
        # Initialize with all samples as pending
        return {"verified": [], "pending": get_all_samples()}

def save_progress(progress: Dict) -> None:
    """Save verification progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def mark_as_verified(sample_id: str) -> None:
    """Mark a sample as verified in the progress tracker"""
    progress = load_progress()
    
    if sample_id in progress["pending"]:
        progress["pending"].remove(sample_id)
        
    if sample_id not in progress["verified"]:
        progress["verified"].append(sample_id)
    
    save_progress(progress)

def get_verification_stats() -> Dict:
    """Get verification statistics"""
    progress = load_progress()
    total = len(progress["verified"]) + len(progress["pending"])
    
    return {
        "total": total,
        "verified": len(progress["verified"]),
        "pending": len(progress["pending"]),
        "progress_percentage": (len(progress["verified"]) / total * 100) if total > 0 else 0
    }

def export_dataset_stats() -> Dict:
    """Export statistics about the dataset and verification"""
    all_verified_jsons = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json') and f != os.path.basename(PROGRESS_FILE)]
    stats = {}
    
    # Load all verified JSON files
    verified_data = []
    for json_file in all_verified_jsons:
        with open(os.path.join(OUTPUT_DIR, json_file), 'r') as f:
            try:
                data = json.load(f)
                verified_data.append(data)
            except:
                continue
    
    # Count attributes
    attribute_counts = {}
    for attr in ["label", "orientation", "brand_name", "vehicle_color", "itype", "type", "special_type"]:
        attribute_counts[attr] = {}
        
    for data in verified_data:
        for attr in attribute_counts.keys():
            if attr in data:
                val = data[attr]
                if val in attribute_counts[attr]:
                    attribute_counts[attr][val] += 1
                else:
                    attribute_counts[attr][val] = 1
    
    stats["attribute_counts"] = attribute_counts
    stats["verification_stats"] = get_verification_stats()
    
    return stats 