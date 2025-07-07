# factory/video_gen.py
# This script is responsible for executing a single video generation
# project based on a scenario JSON file.

import os
import json
import time
from typing import Optional, Dict
from . import kling # Import from within the same package
from . import runway # Import Runway integration
from . import video_concat # Import video concatenation utilities

# --- Configuration ---
MAX_RETRIES = 3
RETRY_DELAY = 10 

def _load_scenario_data(path: str) -> Optional[Dict]:
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

def generate(scenario_path: str, assets_base_path: str) -> Optional[Dict]:
    """
    Reads a scenario file and executes the full video generation workflow.
    Supports both Kling and Runway providers based on scenario configuration.

    Args:
        scenario_path (str): The full path to the scenario JSON file.
        assets_base_path (str): The base directory where assets like images are located (e.g., 'storage/images').

    Returns:
        A dictionary containing the final video result, or None on failure.
    """
    print("\n--- Starting Video Generation ---")
    scenario_data = _load_scenario_data(scenario_path)
    if not scenario_data:
        return None

    global_config = scenario_data.get('global_settings', {})
    opening_config = scenario_data.get('opening_scene', {})
    extension_prompts = scenario_data.get('extensions', [])

    # Determine provider from global settings
    provider = global_config.get('provider', 'kling').lower()
    print(f"VIDEO GEN: Using provider: {provider}")

    # Get image source for the opening scene
    image_name = opening_config.get('image_source')
    if not image_name:
        print("VIDEO GEN: Error - `image_source` not specified in scenario.")
        return None
    
    full_image_path = os.path.join(assets_base_path, image_name)
    if not os.path.exists(full_image_path):
        print(f"VIDEO GEN: Error - Asset image not found at {full_image_path}")
        return None

    # Route to appropriate provider
    if provider == 'runway':
        return _generate_runway_video(scenario_data, full_image_path, assets_base_path)
    else:
        return _generate_kling_video(scenario_data, full_image_path, assets_base_path)

def _generate_kling_video(scenario_data: dict, full_image_path: str, assets_base_path: str) -> Optional[Dict]:
    """Generate video using Kling provider (original method)."""
    global_config = scenario_data.get('global_settings', {})
    opening_config = scenario_data.get('opening_scene', {})
    extension_prompts = scenario_data.get('extensions', [])

    print("VIDEO GEN: Using Kling provider")

    # --- Step 1: Create the Opening Scene ---
    if opening_config.get('type') == 'image_to_video':
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

    extension_result = None
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
            return current_result

        current_result = extension_result if extension_result else current_result
        try:
            current_video_id = current_result['videos'][0]['id']
            print(f"VIDEO GEN: Extension {i+1} successful. New Video ID: {current_video_id}")
        except (KeyError, IndexError, TypeError):
            print("VIDEO GEN: Error - Could not find video ID in extension result. Stopping.")
            return current_result

    print("🎉 --- Kling Video Generation Finished Successfully! --- 🎉")
    return current_result

def _generate_runway_video(scenario_data: dict, full_image_path: str, assets_base_path: str) -> Optional[Dict]:
    """Generate video using Runway provider with chaining method."""
    global_config = scenario_data.get('global_settings', {})
    opening_config = scenario_data.get('opening_scene', {})
    extension_prompts = scenario_data.get('extensions', [])

    print("VIDEO GEN: Using Runway provider")

    # Build complete prompts list (opening + extensions)
    all_prompts = [opening_config.get('prompt', 'A still shot of the character, with subtle ambient motion.')]
    all_prompts.extend(extension_prompts)

    print(f"VIDEO GEN: Generating {len(all_prompts)} segments with Runway")

    # Create temp directory for segments
    temp_dir = os.path.join(assets_base_path, f'temp_segments_{int(time.time())}')
    os.makedirs(temp_dir, exist_ok=True)

    # Generate extended video using Runway's chaining method
    segments_result = runway.generate_extended_video(
        image_path=full_image_path,
        prompts=all_prompts,
        model_name=global_config.get('model_name', 'gen4_turbo'),
        segment_duration=opening_config.get('duration', 5),
        aspect_ratio=global_config.get('aspect_ratio', '16:9'),
        temp_dir=temp_dir
    )

    if not segments_result:
        print("VIDEO GEN: Failed to generate Runway video segments")
        return None

    # Concatenate segments into final video
    print("VIDEO GEN: Concatenating Runway segments...")
    final_video_path = os.path.join(assets_base_path, f'final_runway_video_{int(time.time())}.mp4')
    
    if video_concat.concatenate_runway_segments(segments_result, final_video_path):
        print(f"VIDEO GEN: Runway video successfully created: {final_video_path}")
        
        # Clean up temporary segments but keep final video
        runway.cleanup_temp_files(temp_dir, keep_final=True)
        
        print("🎉 --- Runway Video Generation Finished Successfully! --- 🎉")
        
        # Return in consistent format with Kling
        return {
            'videos': [{
                'id': f"runway_concat_{int(time.time())}",
                'url': f"file://{final_video_path}",
                'path': final_video_path,
                'segments': len(segments_result['segments']),
                'provider': 'runway'
            }],
            'status': 'completed'
        }
    else:
        print("VIDEO GEN: Failed to concatenate Runway segments")
        return None

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

