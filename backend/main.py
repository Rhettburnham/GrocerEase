import os
import time
import json
import base64
import openai
import RPi.GPIO as GPIO
from hx711 import HX711
from mimetypes import guess_type
from statistics import mode, StatisticsError

# Set your OpenAI API key
openai.api_key = "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"

# --- Capture Image ---
def capture_image(filename="capture.jpg"):
    command = f"libcamera-still -o {filename} --vflip --hflip"
    os.system(command)
    print(f"Image captured and saved as {filename}")

# --- Encode Image ---
def encode_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    with open(image_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded}"

# --- Identify Food ---
def identify_food(image_path):
    data_url = encode_image_to_data_url(image_path)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify the food in 1-3 words, no full sentences."},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ],
            }
        ],
        max_tokens=10
    )
    return response["choices"][0]["message"]["content"].strip()

# --- Get Weight Mode ---
def get_weight(duration_sec=2):
    GPIO.setwarnings(False)
    hx = HX711(dout_pin=5, pd_sck_pin=6)

    readings = []
    start_time = time.time()

    while time.time() - start_time < duration_sec:
        raw_val = hx._read()
        processed_val = round((raw_val - 17000) / 100, 2)
        readings.append(processed_val)
        time.sleep(0.1)

    try:
        return mode(readings)
    except StatisticsError:
        return None

# --- Main Process ---
def main():
    input("Press 'y' then Enter to capture and analyze item...\n")

    # 1. Capture image
    image_path = "capture.jpg"
    capture_image(image_path)

    # 2. Get weight
    print("Measuring weight...")
    weight = get_weight()
    if weight is None:
        print("No unique weight mode found.")
        return
    print(f"Weight: {weight} g")

    # 3. Identify item
    print("Identifying item from image...")
    item_name = identify_food(image_path)
    print(f"Identified: {item_name}")

    # 4. Save to JSON
    output = {
        "image_path": image_path,
        "item": item_name,
        "weight": weight
    }

    json_path = "item_log.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as file:
            data = json.load(file)
    else:
        data = []

    data.append(output)
    with open(json_path, "w") as file:
        json.dump(data, file, indent=4)

    print("Saved to item_log.json")

if __name__ == "__main__":
    main()
