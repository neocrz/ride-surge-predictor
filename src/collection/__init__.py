import socket
import json
import time
import os
import base64
import datetime
import threading
import requests 

# Adjusting import to match the new structure
from config.routes import routes

# CONFIGURATION
SERVER_ADDR = ('127.0.0.1', 8766)
# paths relative to (main.py)
RAW_DIR = os.path.join(os.getcwd(), "data", "raw")
INTERVAL_MINUTES = 15

# WEATHER CONFIGURATION (Santos)
LATITUDE = -23.9549098
LONGITUDE = -46.3868865

# Global state for communication between listener thread and main collection loop
screenshot_received = threading.Event()
latest_timestamp = None

def get_current_weather():
    """
    Open-Meteo API forecast.
    """
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,precipitation,weather_code"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            return {
                "temperature": current.get("temperature_2m"),
                "precipitation": current.get("precipitation"),
                "weather_code": current.get("weather_code")
            }
    except Exception as e:
        print(f"| Error fetching weather data: {e}")
        
    # Return None for values on failure to avoid breaking the script
    return {"temperature": None, "precipitation": None, "weather_code": None}

def listen_for_responses(sock):
    """
    Listens continuously on the persistent socket connection.
    Saves the incoming WebP screenshot.
    """
    global latest_timestamp
    try:
        f = sock.makefile('r', encoding='utf-8')
        for line in f:
            if not line: break
            try:
                data = json.loads(line.strip())
                if data.get("action") == "screenshot_result":
                    img_data = data.get("data").split(",")[1]
                    
                    # Generate the timestamp when the screenshot is received
                    latest_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(RAW_DIR, f"uber_raw_{latest_timestamp}.webp")
                    
                    with open(image_path, "wb") as file:
                        file.write(base64.b64decode(img_data))
                    
                    screenshot_received.set() # Signal main thread to proceed
            except Exception as e:
                print(f"| Error parsing bridge response: {e}")
    except Exception as e:
        print(f"|FATAL| Listener thread disconnected: {e}")

def run_job(sock):
    """Runs a single iteration of navigating, taking screenshots, and saving metadata."""
    print(f"\nCycle started at {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Get weather
    weather_data = get_current_weather()
    print(f"|🌤️| Current Weather - Temp: {weather_data['temperature']}°C | Rain: {weather_data['precipitation']}mm")
    
    for route in routes:
        print(f"| Route: {route['from']} -> {route['to']}")
        screenshot_received.clear()

        try:
            # 1. Navigate
            nav_msg = {"action": "navigate", "url": route['url']}
            sock.sendall((json.dumps(nav_msg) + '\n').encode('utf-8'))
            
            # 2. Wait for page load
            time.sleep(15)

            # 3. Request Screenshot
            ss_msg = {"action": "screenshot"}
            sock.sendall((json.dumps(ss_msg) + '\n').encode('utf-8'))

            # 4. Wait for listener to save file and signal us back
            if screenshot_received.wait(timeout=15):
                # The listener just saved the webp and updated `latest_timestamp`
                # Now we dump the matching json metadata
                metadata = {
                    "timestamp": latest_timestamp,
                    "route": route,
                    "weather": weather_data
                }
                
                json_path = os.path.join(RAW_DIR, f"uber_raw_{latest_timestamp}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4, ensure_ascii=False)
                
                print(f"| Raw data saved successfully: uber_raw_{latest_timestamp}.(webp/json)")
            else:
                print("| Timeout: Bridge did not return screenshot.")
                
        except Exception as e:
            print(f"| Error communicating with browser during route: {e}")
            
        time.sleep(2)

def run_collection():
    """Main entry point for the collection methodology."""
    # 1. Establish persistent socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(SERVER_ADDR)
        print("| Connected to browser bridge.")
    except ConnectionRefusedError:
        print("| Connection failed. Is the browser extension/server running?")
        return

    # 2. Start listener thread
    threading.Thread(target=listen_for_responses, args=(sock,), daemon=True).start()

    print(f"Starting collection automation: Every {INTERVAL_MINUTES} minutes.")
    
    # 3. Loop forever scheduling collection jobs
    try:
        while True:
            start_time = time.time()
            
            run_job(sock)
            
            # Calculate precise sleep to maintain rhythm
            elapsed = time.time() - start_time
            sleep_duration = max(0, (INTERVAL_MINUTES * 60) - elapsed)
            
            print(f"[#] Cycle complete. Sleeping {round(sleep_duration/60, 2)} minutes...")
            time.sleep(sleep_duration)
    except KeyboardInterrupt:
        print("\n[!] Script stopped by user.")
    finally:
        sock.close()