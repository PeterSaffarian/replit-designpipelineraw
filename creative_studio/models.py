import os
import google.generativeai as genai
from openai import OpenAI
from typing import Optional
import base64

# --- Configuration and Initialization ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Use a placeholder if the key is not set, to avoid errors on import
# The functions themselves will raise an error if the key is needed and missing.
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# --- Model Abstraction Functions ---

def call_text_model(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    image_bytes: Optional[bytes] = None
) -> str:
    """
    Calls a specified text generation model (Gemini or GPT) that can optionally
    understand images. This is used for designing prompts and writing scripts.
    """
    print(f"MODEL: Calling text model '{model_name}'...")

    try:
        if 'gemini' in model_name.lower():
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is not set in the .env file.")
            model = genai.GenerativeModel(model_name)

            content = [user_prompt]
            if image_bytes:
                content.insert(0, {"mime_type": "image/png", "data": image_bytes})
            response = model.generate_content(
                content,
                generation_config=genai.types.GenerationConfig(temperature=0.7),
                system_instruction=system_prompt
            )
            return response.text
        elif 'gpt' in model_name.lower():
            if not openai_client:
                raise ValueError("OPENAI_API_KEY is not set in the .env file.")
            messages = [{"role": "system", "content": system_prompt}]
            user_content = [{"type": "text", "text": user_prompt}]
            if image_bytes:
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
            messages.append({"role": "user", "content": user_content})
            response = openai_client.chat.completions.create(model=model_name, messages=messages, temperature=0.7)
            return response.choices[0].message.content
        else:
            raise ValueError(f"Unsupported text model: {model_name}")
    except Exception as e:
        print(f"MODEL: An error occurred while calling {model_name}: {e}")
        return ""


def call_image_model(
    model_name: str,
    prompt: str,
    ref_image_bytes: bytes
) -> bytes:
    """
    Generates an image by calling a vision model with an image generation tool.

    This function uses the 'Responses API' to provide both a text prompt and a
    reference image, allowing the model to generate a new image in context.

    Args:
        model_name (str): The name of the vision model to use (e.g., 'gpt-4o').
        prompt (str): The detailed text prompt for the image.
        ref_image_bytes (bytes): The raw byte data of the reference image.

    Returns:
        bytes: The raw byte data of the generated PNG image.
    """
    print(f"MODEL: Calling '{model_name}' with image generation tool...")

    if not openai_client:
        raise ValueError("OPENAI_API_KEY is not set in the .env file.")
    if not ref_image_bytes:
        raise ValueError("A reference image is required for this function.")

    try:
        base64_image = base64.b64encode(ref_image_bytes).decode('utf-8')

        request_message = {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{base64_image}"
                }
            ]
        }

        response = openai_client.responses.create(
            model=model_name,
            input=[request_message],
            tools=[{"type": "image_generation"}]
        )

        # CORRECTED THIS LINE: Access 'result' directly on the 'output' object.
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]

        if image_data:
            image_base64 = image_data[0]
            print("MODEL: Successfully received image data from the tool.")
            return base64.b64decode(image_base64)
        else:
            print("MODEL: The model did not return an image. It may have responded with text instead.")
            text_response = [output.text.content for output in response.output if output.type == "text"]
            if text_response:
                print(f"MODEL: Text response received: {text_response[0]}")
            return b''

    except Exception as e:
        print(f"MODEL: An error occurred while calling {model_name} with image tool: {e}")
        return b''
