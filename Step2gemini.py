import os
from google import genai
from google.genai import types
from PIL import Image 

# --- CONFIGURATION ---
API_KEY = 'AIzaSyA-APS9pKrd0E5s64PVxiVlVafjlWdfHsI'
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3-flash-preview" 

# --- 1. DEFINE 5+ TOOLS ---

def set_light_brightness(level: int):
    """Sets the smart light brightness level between 0 and 100."""
    print(f"[TOOL] Lights set to {level}%")
    return {"status": "success", "brightness": level}

def get_weather(city: str):
    """Retrieves the current weather for a specific city."""
    print(f"[TOOL] Fetching weather for {city}...")
    return {"city": city, "temp": "22°C", "condition": "Sunny"}

def add_to_todo(task: str):
    """Adds a task item to the user's to-do list."""
    print(f"[TOOL] Added '{task}' to-do list.")
    return {"status": "added", "item": task}

def set_thermostat(temp: float):
    """Sets the home thermostat to a target temperature in Celsius."""
    print(f"[TOOL] Thermostat set to {temp}°C")
    return {"status": "updated", "temperature": temp}

def generate_and_save_image(prompt: str):
    """
    Generates a real image using Imagen 4 based on a text prompt
    and saves it as output.png.
    """
    print(f"[TOOL] Generating Image: {prompt}...")
    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',  
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1)
        )

        output_path = "output.png"

        response.generated_images[0].image.save(location=output_path)

        if os.name == 'nt':
            os.startfile(output_path)

        return {"status": "success", "file_saved": output_path}
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        return {"status": "error", "message": str(e)}

tools_list = [
    set_light_brightness,
    get_weather,
    add_to_todo,
    set_thermostat,
    generate_and_save_image
]

# --- 2. MULTIMODAL ASSISTANT LOGIC ---

def run_assistant(user_text, image_path):
    chat = client.chats.create(
        model=MODEL_ID,
        config=types.GenerateContentConfig(
            tools=tools_list,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False
            )
        )
    )

    # Build multimodal message parts (text + image)
    content_parts = [types.Part.from_text(text=user_text)]

    if os.path.exists(image_path):
        print(f"[SYSTEM] Analyzing Image: {image_path}...")
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        content_parts.append(
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
        )
    else:
        print(f"[ERROR] {image_path} not found. Ensure the image is in the same folder.")
        return

    response = chat.send_message(content_parts)

    print("\n--- Assistant Final Message ---")
    print(response.text)



instruction = """
1. Look at 'input_image.jpg'. What's one thing I should clean? Add it to my todo list.
2. Check the weather in Paris.
3. Generate a 'futuristic office' image to inspire me.
"""

run_assistant(instruction, image_path="input_image.jpg")