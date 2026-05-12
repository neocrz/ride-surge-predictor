import os
import json
import csv
import shutil
from glob import glob

from .qwen_agent import process_with_llm
from .validator import extract_json_from_response

RAW_DIR = os.path.join(os.getcwd(), "data", "raw")
INTERIM_DIR = os.path.join(os.getcwd(), "data", "interim")
ARCHIVE_DIR = os.path.join(os.getcwd(), "data", "archive")
CSV_FILE = os.path.join(INTERIM_DIR, "uber_rides_log.csv")

def save_to_csv(timestamp, route_info, weather_data, ride_data):
    """Appends the newly extracted data into the CSV file."""
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write header if file is new
            writer.writerow(['timestamp', 'from', 'to', 'ride_id', 'price', 'wait_time_minutes', 'temperature_celsius', 'precipitation_mm', 'weather_code'])
        
        for item in ride_data:
            writer.writerow([
                timestamp,
                route_info.get('from', ''),
                route_info.get('to', ''),
                item.get('ride_id'),
                item.get('price'),
                item.get('wait_time_minutes'),
                weather_data.get('temperature'),
                weather_data.get('precipitation'),
                weather_data.get('weather_code')
            ])

def run_extraction():
    """Main loop for finding files, passing to LLM, and archiving."""
    print("| Starting extraction process...")
    
    # Find all JSON metadata files in the raw directory
    json_files = glob(os.path.join(RAW_DIR, "*.json"))
    
    if not json_files:
        print("| No raw data found to process. Returning.")
        return

    for json_path in json_files:
        # Get matching WebP image path based on timestamp base name
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        webp_path = os.path.join(RAW_DIR, f"{base_name}.webp")
        
        if not os.path.exists(webp_path):
            print(f"| Missing matching WebP for {json_path}. Skipping.")
            continue
            
        print(f"\n| Processing pair: {base_name}")
        
        # Read Metadata (Weather, Routes, Timestamps)
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        timestamp = metadata.get('timestamp')
        route_info = metadata.get('route', {})
        weather_data = metadata.get('weather', {})
        
        # LLM Inference
        print("    -> Sending image to Ollama...")
        llm_response = process_with_llm(webp_path)
        ride_data = extract_json_from_response(llm_response)
        
        if ride_data:
            # Save merged data to CSV
            save_to_csv(timestamp, route_info, weather_data, ride_data)
            print(f"    | Data extracted and appended to CSV.")
            
            # Move files to Archive to avoid processing them again
            shutil.move(json_path, os.path.join(ARCHIVE_DIR, f"{base_name}.json"))
            shutil.move(webp_path, os.path.join(ARCHIVE_DIR, f"{base_name}.webp"))
            print(f"    | Files moved to data/archive/.")
        else:
            print(f"    | Extraction failed for {base_name}. Files will remain in data/raw/ to retry later.")

    print("\n| Extraction phase completed successfully.")