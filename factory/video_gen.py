# factory/video_gen.py
# This script is responsible for executing a single video generation
# project based on a scenario JSON file.

import os
import json
import time
from . import kling # Import from within the same package

# --- Configuration ---
MAX_RETRIES = 3
RETRY_DELAY = 10 

def _load_scenario_data(path: str) -> dict:
    """Loads and validates the scenario data from a JSON file."""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        if 'global_settings' in data and 'opening_scene' in data:
            print("VIDEO GEN: Scenario data loaded and validated.")
            return data
        else:
            print("VIDEO GEN: Error - Scenario is missing required keys.")
            return None
    except Exception as e:
        print(f"VIDEO GEN: Error loading scenario file: {e}")
        return None

def generate(scenario_path: str, assets_base_path: str) -> dict:
    """
    Reads a scenario file and executes the full video generation workflow.

    Args:
        scenario_path (str): The full path to the scenario JSON file.
        assets_base_path (str): The base directory where assets like images are located (e.g., 'storage/images').

    Returns:
        A dictionary containing the final video result, or None on failure.
    """
    print("\n--- Starting Video Generation ---")
    direction = _load_scenario_data(scenario_path)
    if not direction:
        return None

    opening_config = direction.get('opening_scene', {})
    global_config = direction.get('global_settings', {})
    current_result = None

    # --- Step 1: Generate the Opening Scene ---
    if opening_config.get('type') == 'image_to_video':
        print("VIDEO GEN: Generating opening scene from image...")

        # Construct the full path to the image asset
        image_name = opening_config.get('image_source')
        if not image_name:
            print("VIDEO GEN: Error - `image_source` not specified in scenario.")
            return None
        full_image_path = os.path.join(assets_base_path, image_name)

        if not os.path.exists(full_image_path):
            print(f"VIDEO GEN: Error - Asset image not found at {full_image_path}")
            return None

        current_result = kling.image_to_video(
            image_path=full_image_path,
            prompt=opening_config['prompt'],
            model_name=global_config.get('model_name', 'kling-v1'),
            duration=opening_config.get('duration', 5)
        )
    else:
        print(f"VIDEO GEN: Error - Invalid 'type' for opening scene: {opening_config.get('type')}")
        return None

    if not current_result:
        print("VIDEO GEN: Failed to create the opening scene.")
        return None

    # --- Step 2: Chain the Extensions ---
    try:
        current_video_id = current_result['videos'][0]['id']
        print(f"VIDEO GEN: Opening scene created. Starting extensions with Video ID: {current_video_id}")
    except (KeyError, IndexError, TypeError):
        print("VIDEO GEN: Error - Could not find video ID in the opening scene result.")
        return None

    extension_prompts = direction.get('extensions', [])
    for i, prompt in enumerate(extension_prompts):
        print(f"--- Starting Extension {i+1}/{len(extension_prompts)} ---")
        retries = 0
        extension_successful = False

        while retries < MAX_RETRIES:
            print(f"Attempt {retries + 1}/{MAX_RETRIES} for extension {i+1}...")
            extension_result = kling.video_extension(source_video_id=current_video_id, prompt=prompt)

            if extension_result:
                extension_successful = True
                break 

            retries += 1
            if retries < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)

        if not extension_successful:
            print(f"VIDEO GEN: Error - Failed on extension {i+1} after {MAX_RETRIES} retries. Stopping.")
            return current_result # Return the last successful result

        current_result = extension_result
        try:
            current_video_id = current_result['videos'][0]['id']
            print(f"VIDEO GEN: Extension {i+1} successful. New Video ID: {current_video_id}")
        except (KeyError, IndexError, TypeError):
            print("VIDEO GEN: Error - Could not find video ID in extension result. Stopping.")
            return current_result

    print("🎉 --- Video Generation Finished Successfully! --- 🎉")
    return current_result

# This allows other scripts to import the 'generate' function easily.
__all__ = ["generate"]


if __name__ == '__main__':
    # This is a direct test block for the video generator.
    print("--- RUNNING DIRECT TEST FOR VIDEO GENERATOR ---")

    # 1. Define paths for the test
    test_scenario_path = "storage/custom_custom_idea_20250612/scenario.json"
    # The base path for assets referenced inside the scenario (e.g., images)
    assets_dir = "storage/custom_custom_idea_20250612"

    # 2. Check if the test scenario file exists
    if not os.path.exists(test_scenario_path):
        print(f"ERROR: Test scenario not found at '{test_scenario_path}'.")
        print("Please create a test_scenario.json file inside the 'scenarios' directory to run this test.")
    else:
        # 3. Run the generator
        print(f"Attempting to generate video from '{test_scenario_path}'...")
        final_result = generate(test_scenario_path, assets_dir)

        if final_result:
            print("\n--- TEST COMPLETE: Final Video Data ---")
            print(json.dumps(final_result, indent=2))
        else:
            print("\n--- TEST FAILED ---")

