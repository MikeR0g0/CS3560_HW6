from google import genai
from google.genai import types
# from PIL import Image

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# $env:GEMINI_API_KEY = "AIzaSyAaYBzsoTQ6IXMse6AvSjBUlNkjp9NB5Lk"
client = genai.Client()

# prompt = input("What do you want to ask Gemini? ")

# response = client.models.generate_content(
#     model="gemini-3-flash-preview", 
#     contents=prompt,
#     config = types.GenerateContentConfig(thinking_config = types.ThinkingConfig(thinking_level = "high")
#     ),
# )
# print(response.text)

# --- STEP 1: Define a function declaration ---
# This describes the function's name, purpose, and parameters to the model.
set_light_values_declaration = {
    "name": "set_light_values",
    "description": "Sets the brightness and color temperature of a light.",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {
                "type": "integer",
                "description": "Light level from 0 to 100. Zero is off and 100 is full brightness"
            },
            "color_temp": {
                "type": "string",
                "enum": ["daylight", "cool", "warm"],
                "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`."
            },
        },
        "required": ["brightness", "color_temp"],
    },
}

# The actual mock function to be executed by your application
def set_light_values(brightness: int, color_temp: str) -> dict:
    print(f"\n>>> Executing set_light_values(brightness={brightness}, color_temp='{color_temp}')")
    return {"brightness": brightness, "colorTemperature": color_temp}

# --- STEP 2: Call the model with function declarations ---
tools = types.Tool(function_declarations=[set_light_values_declaration])
config = types.GenerateContentConfig(tools=[tools])

# User prompt that triggers the function call
user_prompt = "Turn the lights down to a romantic level"
contents = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

print(f"Sending prompt to model: '{user_prompt}'")
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=contents,
    config=config,
)

# --- STEP 3: Execute function code ---
# Check if the model requested a function call
first_part = response.candidates[0].content.parts[0]
if first_part.function_call:
    tool_call = first_part.function_call
    print(f"Model suggests calling: {tool_call.name}")
    
    if tool_call.name == "set_light_values":
        # Parse arguments and call the actual function
        result = set_light_values(**tool_call.args)
        print(f"Function execution result: {result}")

        # --- STEP 4: Create user friendly response ---
        # 1. Create a response part with the function output
        function_response_part = types.Part.from_function_response(
            name=tool_call.name,
            response={"result": result},
        )

        # 2. Add the model's previous turn (the call) and the tool output to history
        contents.append(response.candidates[0].content)
        contents.append(types.Content(role="tool", parts=[function_response_part]))

        # 3. Call the model again to generate the final natural language answer
        final_response = client.models.generate_content(
            model="gemini-3-flash-preview",
            config=config,
            contents=contents,
        )
        
        print("\nFinal Model Response:")
        print(final_response.text)
else:
    print("No function call was suggested by the model.")
    print(response.text)