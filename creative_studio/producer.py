import os
import json
import math
from mutagen.mp3 import MP3
from creative_studio.models import call_text_model
from typing import Optional

def _read_image_bytes(image_path: str) -> Optional[bytes]:
    """Reads an image file and returns its content as bytes."""
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"PRODUCER: Error - Artwork image not found at {image_path}")
        return None
    except Exception as e:
        print(f"PRODUCER: Error reading image file: {e}")
        return None

def _get_audio_duration(audio_path: str) -> float:
    """Calculates the duration of an MP3 file in seconds."""
    try:
        audio = MP3(audio_path)
        return audio.info.length
    except Exception as e:
        print(f"PRODUCER: Error reading audio file duration: {e}")
        return 0.0

def _calculate_extensions(audio_duration_seconds: float, opening_duration: int = 10, extension_duration: int = 8) -> int:
    """
    Calculates the number of video extensions needed to cover the audio length.

    Args:
        audio_duration_seconds (float): Total length of the audio.
        opening_duration (int): Duration of the initial static scene.
        extension_duration (int): Duration of each subsequent extension.

    Returns:
        int: The number of extensions required.
    """
    if audio_duration_seconds <= opening_duration:
        return 0

    remaining_length = audio_duration_seconds - opening_duration
    # Always round up to ensure the video is long enough
    required_extensions = math.ceil(remaining_length / extension_duration)
    return required_extensions

def produce_scenario(script: str, audio_path: str, artwork_path: str, template_path: str, output_path: str) -> str:
    """
    Assembles the final scenario JSON file for the video generator.

    Args:
        script (str): The script for the video.
        audio_path (str): Path to the generated audio file.
        artwork_path (str): Path to the generated artwork.
        template_path (str): Path to the scenario_template.json.
        output_path (str): The full path where the generated scenario will be saved.

    Returns:
        str: The path to the saved scenario file, or an empty string on failure.
    """
    print("PRODUCER: Assembling video scenario...")

    # 1. Load the scenario template from the file
    try:
        with open(template_path, 'r') as f:
            scenario_data = json.load(f)
    except Exception as e:
        print(f"PRODUCER: Error loading scenario template: {e}")
        return ""

    # 2. Get audio duration and calculate the number of extensions needed
    audio_duration = _get_audio_duration(audio_path)
    if audio_duration == 0.0:
        return ""
    num_extensions = _calculate_extensions(audio_duration)

    # 3. Read and analyze the artwork image
    artwork_bytes = _read_image_bytes(artwork_path)
    if not artwork_bytes:
        print("PRODUCER: Warning - Could not read artwork image, continuing with text-only context.")
    
    # 4. Define the 'role' for our AI model
    system_prompt = (
        "You are a meticulous AI video production assistant with vision capabilities. Your task is to populate a JSON "
        "template for a video generator by analyzing the provided artwork image. You must follow all instructions precisely. "
        "Your output must be ONLY the raw, valid JSON content, with no explanatory text before or after. "
        "Look carefully at the character, scene, and visual elements in the provided artwork image. Your animation prompts "
        "will be used to animate this specific character and scene. It is important to be aware of the video-generation "
        "machine's limitations. In order to avoid distorted animation, we must avoid sudden huge movements and manage "
        "the animation via precise, gentle prompt instructions that work with the character's pose and environment shown in the image."
    )

    # 5. Define the specific 'task' for our AI model
    user_prompt = (
        "Please populate the provided JSON template based on the following materials and the provided artwork image.\n\n"
        "INSTRUCTIONS:\n"
        f"1. Update the `image_source` field to be exactly this path: '{os.path.basename(artwork_path)}'.\n"
        f"2. Analyze the character, pose, environment, and visual elements in the provided artwork image. Write a new `prompt` "
        f"for the `opening_scene` that creates a 'living photo' effect from this specific image. Consider the character's "
        f"current pose, facial expression, and setting. For example: 'The character maintains their current pose with subtle "
        f"ambient motion, beginning to speak with natural lip movement' or describe what you actually see in the image.\n"
        f"3. Based on both the provided script AND the visual analysis of the artwork, generate exactly {num_extensions} "
        f"simple, sequential motion prompts for the `extensions` array. IMPORTANT: The extensions array must contain "
        f"ONLY text strings, not objects. Each extension should be a simple text description like 'The character continues "
        f"speaking with gentle head movements.' Work naturally with the character's pose and environment shown in the image. "
        f"Describe small, natural progressions that maintain visual consistency with the artwork while showing speaking animation.\n\n"
        f"SCRIPT:\n---\n{script}\n---\n\n"
        "JSON TEMPLATE TO POPULATE:\n"
        f"{json.dumps(scenario_data, indent=4)}"
    )

    # 6. Call the text model with vision to get the populated JSON string
    json_string_output = call_text_model(
        model_name='gpt-4o',
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image_bytes=artwork_bytes  # Now the producer can "see" the artwork
    )

    if not json_string_output:
        print("PRODUCER: Failed to get a response from the model.")
        return ""

    # 7. Save the generated JSON to the output file
    try:
        # The model might sometimes include markdown backticks, so we clean them up.
        cleaned_json_string = json_string_output.strip().replace('```json', '').replace('```', '')
        # Validate and re-format the JSON to ensure it's clean
        final_json_data = json.loads(cleaned_json_string)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(final_json_data, f, indent=4)
        print(f"PRODUCER: Successfully saved scenario to {output_path}")
        return output_path
    except json.JSONDecodeError:
        print("PRODUCER: Error - Model output was not valid JSON.")
        print(f"Raw output received:\n{json_string_output}")
        return ""
    except Exception as e:
        print(f"PRODUCER: Failed to save scenario file. Error: {e}")
        return ""

if __name__ == '__main__':
    print("--- RUNNING DIRECT TEST FOR PRODUCER ---")

    # 1. Define paths and check for necessary files
    os.makedirs("storage/scenarios", exist_ok=True)

    test_audio_path = "storage/audio/test.mp3"
    test_artwork = "storage/images/test.png"
    test_template = "schemas/scenario_template.json"
    test_output = "storage/scenarios/test_scenario.json"
    test_script = "Online security is crucial in protecting your personal information from cyber threats. Always use strong, unique passwords and enable two-factor authentication. Staying vigilant can help keep your data safe and secure in our digital world."

    # Check if all required files for the test exist
    required_files = [test_audio_path, test_artwork, test_template]
    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        print("ERROR: Missing required files for test:")
        for f in missing_files:
            print(f" - {f}")
    else:
        try:
            produce_scenario(test_script, test_audio_path, test_artwork, test_template, test_output)
        except Exception as e:
            print(f"\nAn error occurred during the test run: {e}")

