import os
import json
from typing import Dict, List, Optional
import datetime

def get_timestamp() -> str:
    """Get current timestamp string"""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def create_backup(file_path: str) -> str:
    """Create a backup of a file"""
    if not os.path.exists(file_path):
        return None
        
    backup_dir = os.path.join(os.path.dirname(file_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    base_name = os.path.basename(file_path)
    backup_path = os.path.join(backup_dir, f"{get_timestamp()}_{base_name}")
    
    with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
        dst.write(src.read())
    
    return backup_path

def generate_report(stats: Dict, output_file: str = None) -> str:
    """Generate a report of the annotation progress and statistics"""
    if output_file is None:
        output_file = f"AOT_report_{get_timestamp()}.txt"
    
    with open(output_file, 'w') as f:
        f.write("# AOT (AttributeannOtationTool) Report\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write verification statistics
        verification_stats = stats["verification_stats"]
        f.write("## Verification Progress\n")
        f.write(f"Total samples: {verification_stats['total']}\n")
        f.write(f"Verified: {verification_stats['verified']} ({verification_stats['progress_percentage']:.2f}%)\n")
        f.write(f"Pending: {verification_stats['pending']}\n\n")
        
        # Write attribute statistics
        f.write("## Attribute Statistics\n")
        attribute_counts = stats["attribute_counts"]
        
        for attr, counts in attribute_counts.items():
            f.write(f"\n### {attr.capitalize()}\n")
            
            # Sort by count (descending)
            sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_items:
                percentage = (count / verification_stats['verified']) * 100 if verification_stats['verified'] > 0 else 0
                f.write(f"- {value}: {count} ({percentage:.2f}%)\n")
    
    return output_file 