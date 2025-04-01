#!/usr/bin/env python3
"""
Setup script for AOT (AttributeannOtationTool)
This script ensures the necessary directory structure exists.
"""

import os
import sys
import shutil

# Define the directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(ROOT_DIR), "unpadded_data"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(ROOT_DIR), "verified_data"))

def ensure_directory(dir_path):
    """Ensure a directory exists, create it if it doesn't"""
    if not os.path.exists(dir_path):
        print(f"Creating directory: {dir_path}")
        os.makedirs(dir_path)
    else:
        print(f"Directory already exists: {dir_path}")

def main():
    """Main setup function"""
    print("Setting up AOT (AttributeannOtationTool)...")
    
    # Ensure directories exist
    ensure_directory(INPUT_DIR)
    ensure_directory(OUTPUT_DIR)
    
    # Check if input directory has any JSON files
    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    if not json_files:
        print(f"WARNING: No JSON files found in {INPUT_DIR}. Please add your data files.")
    else:
        print(f"Found {len(json_files)} JSON files in input directory.")
    
    print("\nSetup complete! You can now run the tool with 'python app.py'")

if __name__ == "__main__":
    main() 