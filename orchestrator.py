import os
import json
import pandas as pd
import requests
import time
from datetime import datetime

# --- Import all our project modules ---
# It's good practice to wrap imports in a try-except block for clearer error messages
try:
    from creative_studio import artwork_designer, artwork_builder, artwork_checker, script_writer, producer
    from factory import audio_gen, video_gen, assembly, subtitle_generator, subtitle_burner, branding
except ImportError as e:
    print(f"FATAL ERROR: A required module could not be imported: {e}")
    print("Please ensure you are running the orchestrator from the project's root directory.")
    exit()

# --- Configuration ---
INPUTS_DIR = "inputs"
STORAGE_DIR = "storage"
SCHEMAS_DIR = "schemas"
HERO_IMAGE_NAME = "hero.png"
IDEAS_FILE_NAME = "ideas.csv"
TEMPLATE_FILE_NAME = "runway_scenario_template.json"
HERO_FILE_NAME = "hero.png"  # Expected hero image file name
INTRO_VIDEO_NAME = "intro.mp4"  # Expected intro video file name  
OUTRO_VIDEO_NAME = "outro.mp4"  # Expected outro video file name
MAX_ARTWORK_RETRIES = 3  # Maximum attempts to generate acceptable artwork


# --- Helper Functions ---

def setup_project_structure():
    """Ensures all top-level directories for the project exist."""
    print("ORCHESTRATOR: Setting up main project directories...")
    for dir_name in [INPUTS_DIR, STORAGE_DIR, SCHEMAS_DIR]:
        os.makedirs(dir_name, exist_ok=True)
    print("ORCHESTRATOR: Main directories are ready.")

def download_file(url: str, local_path: str):
    """Downloads a file from a URL and saves it to a local path."""
    print(f"  -> Downloading file from {url}...")
    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  -> Successfully saved file to {local_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  -> Error downloading file: {e}")
        return False

# --- Main Pipeline Logic ---

def run_pipeline_for_idea(idea_text, idea_number, idea_name):
    """
    Executes the full content generation pipeline for a single idea.
    Returns a dictionary summarizing the result for the final report.
    """
    # 1. Setup project folder and JSON tracker
    date_str = datetime.now().strftime("%Y%m%d")
    sanitized_name = "".join(c for c in idea_name if c.isalnum() or c in " _-").rstrip()
    project_folder_name = f"{idea_number}_{sanitized_name}_{date_str}"
    project_path = os.path.join(STORAGE_DIR, project_folder_name)
    os.makedirs(project_path, exist_ok=True)

    print(f"\n{'='*60}\n🚀 Processing Idea #{idea_number}: '{idea_name}'\n   '{idea_text}'\n   Project Folder: {project_path}\n{'='*60}")
    print(time.ctime())

    # This dictionary will track the progress and final result for this specific idea
    status_report = {
        "idea_name": idea_name,
        "idea_text": idea_text,
        "project_folder": project_path,
        "status": "IN_PROGRESS",
        "failed_at_step": None,
        "final_video_path": None,
        "assets": {}
    }

    tracker_path = os.path.join(project_path, "tracker.json")

    def save_tracker():
        with open(tracker_path, 'w') as f:
            json.dump(status_report, f, indent=4)

    save_tracker()

    try:
        # --- Step 2: Artwork Designer ---
        print("\n--- [Step 1/7] Creative Studio: Designing Artwork ---")
        print("   Your idea is with our designer...")
        hero_image_path = os.path.join(INPUTS_DIR, HERO_FILE_NAME)
        artwork_prompt = artwork_designer.design_artwork_prompt(idea_text, hero_image_path)
        if not artwork_prompt:
            raise RuntimeError("Failed to design artwork prompt.")
        print("   ✅ Designer has completed the design brief:")
        print(f"      \"\"\"{artwork_prompt}\"\"\"")
        status_report['assets']['artwork_prompt'] = artwork_prompt
        save_tracker()

        # --- Step 3: Artwork Builder with Quality Check ---
        print("\n--- [Step 2/7] Creative Studio: Building Artwork ---")
        print("   Our artist is now creating your design...")
        print(time.ctime())
        
        artwork_path = os.path.join(project_path, "artwork.png")
        generated_artwork_path = None
        artwork_retry_count = 0
        
        while artwork_retry_count < MAX_ARTWORK_RETRIES:
            attempt_num = artwork_retry_count + 1
            print(f"   📝 Artwork generation attempt {attempt_num}/{MAX_ARTWORK_RETRIES}...")
            print(time.ctime())
            
            # Generate artwork
            generated_artwork_path = artwork_builder.build_artwork(artwork_prompt, hero_image_path, artwork_path)
            if not generated_artwork_path:
                print(f"   ❌ Artwork generation failed on attempt {attempt_num}")
                print(time.ctime())
                artwork_retry_count += 1
                continue
            
            print(f"   🎨 Artwork created! Now checking quality...")
            print(time.ctime())
            
            # Check artwork quality
            quality_result = artwork_checker.check_artwork_quality(generated_artwork_path, artwork_prompt)

            print("quality_result: ")
            print(quality_result)
            print(time.ctime())
            
            if quality_result['status'] == 'Pass':
                print(f"   ✅ Artwork passed quality check! {quality_result.get('feedback', '')}")
                print(f"   📍 Final artwork saved: {generated_artwork_path}")
                break
            else:
                print(f"   ❌ Artwork failed quality check: {quality_result.get('feedback', 'Quality issues detected')}")
                artwork_retry_count += 1
                if artwork_retry_count < MAX_ARTWORK_RETRIES:
                    print(f"   🔄 Retrying artwork generation...")
                    print(time.ctime())
                else:
                    print(f"   ⚠️  Maximum retries reached. Using last generated artwork.")
                    print(time.ctime())
        
        if not generated_artwork_path:
            raise RuntimeError("Failed to generate artwork after all retry attempts.")
        
        status_report['assets']['artwork_path'] = generated_artwork_path
        status_report['assets']['artwork_retry_count'] = artwork_retry_count
        save_tracker()

        # --- Step 4: Script Writer ---
        print("\n--- [Step 3/7] Creative Studio: Writing Script ---")
        print(time.ctime())
        script = script_writer.write_script(idea_text, generated_artwork_path)
        if not script:
            raise RuntimeError("Failed to write script.")
        print(f"   ✅ Script complete: \"{script}\"")
        print(time.ctime())
        status_report['assets']['script'] = script
        save_tracker()

        # --- Step 5: Audio Generation ---
        print("\n--- [Step 4/9] Factory: Generating Voiceover ---")
        print(time.ctime())
        audio_path = os.path.join(project_path, "audio.mp3")
        generated_audio_path = audio_gen.generate(script, audio_path)
        if not generated_audio_path:
            raise RuntimeError("Failed to generate audio.")
        print(f"   ✅ Audio generated and saved to {generated_audio_path}")
        print(time.ctime())
        status_report['assets']['audio_path'] = generated_audio_path
        save_tracker()

        # --- Step 6: Subtitle Generation ---
        print("\n--- [Step 5/9] Factory: Generating Subtitles ---")
        print(time.ctime())
        srt_path = os.path.join(project_path, "subtitles.srt")
        generated_srt_path = subtitle_generator.generate_srt_subtitles(generated_audio_path, srt_path)
        if generated_srt_path:
            print(f"   ✅ Subtitles generated and saved to {generated_srt_path}")
            print(time.ctime())
            status_report['assets']['srt_path'] = generated_srt_path
            # Get subtitle statistics
            srt_stats = subtitle_generator.get_subtitle_stats(generated_srt_path)
            status_report['assets']['subtitle_stats'] = srt_stats
        else:
            print(f"   ⚠️  Subtitle generation failed, continuing without subtitles")
            print(time.ctime())
            status_report['assets']['srt_path'] = None
        save_tracker()

        # --- Step 7: Producer ---
        print("\n--- [Step 6/9] Creative Studio: Producing Scenario ---")
        print(time.ctime())
        template_path = os.path.join(SCHEMAS_DIR, TEMPLATE_FILE_NAME)
        scenario_path = os.path.join(project_path, "scenario.json")
        generated_scenario_path = producer.produce_scenario(script, generated_audio_path, generated_artwork_path, template_path, scenario_path)
        if not generated_scenario_path:
            raise RuntimeError("Failed to produce scenario.")
        print(f"   ✅ Video scenario produced and saved to {generated_scenario_path}")
        print(time.ctime())
        status_report['assets']['scenario_path'] = generated_scenario_path
        save_tracker()

        # --- Step 8: Raw Video Generation ---
        print("\n--- [Step 7/9] Factory: Generating Raw Video ---")
        print(time.ctime())
        video_gen_result = video_gen.generate(generated_scenario_path, project_path)
        if not video_gen_result or 'videos' not in video_gen_result:
            raise RuntimeError("Failed to generate raw video.")
        
        # Handle different provider results
        video_info = video_gen_result['videos'][0]
        provider = video_info.get('provider', 'kling')
        raw_video_url = video_info.get('url')
        
        print(f"   ✅ Raw video generated using {provider.title()} provider.")
        print(time.ctime())
        status_report['assets']['raw_video_url'] = raw_video_url
        status_report['assets']['video_provider'] = provider
        
        # Handle local file vs remote URL
        if raw_video_url.startswith('file://'):
            # Runway generates local files
            raw_video_path = raw_video_url.replace('file://', '')
            status_report['assets']['raw_video_local_path'] = raw_video_path
        else:
            # Kling generates remote URLs - download them
            raw_video_path = os.path.join(project_path, "raw_video.mp4")
            download_file(raw_video_url, raw_video_path)
            status_report['assets']['raw_video_local_path'] = raw_video_path
        
        save_tracker()

        # --- Step 9: Assembly (Lipsync) ---
        print("\n--- [Step 8/9] Factory: Assembling Final Video ---")
        print(time.ctime())
        
        # For Runway videos (local files), we need to upload to get a public URL for Sync.so
        if raw_video_url.startswith('file://'):
            print("   📤 Uploading Runway video to get public URL for lip-sync...")
            print(time.ctime())
            from factory.assembly import _upload_file_for_url
            public_video_url = _upload_file_for_url(raw_video_path)
            if not public_video_url:
                raise RuntimeError("Failed to upload Runway video for lip-sync processing.")
            print(f"   ✅ Video uploaded successfully: {public_video_url}")
            print(time.ctime())
        else:
            # Kling videos already have public URLs
            public_video_url = raw_video_url
        
        final_video_url = assembly.generate(public_video_url, generated_audio_path)
        if not final_video_url:
            raise RuntimeError("Failed to assemble final video with Sync.so.")
        print(f"   ✅ Lip-sync complete.")
        print(time.ctime())
        status_report['assets']['final_video_url'] = final_video_url
        final_video_path = os.path.join(project_path, "final_video.mp4")
        download_file(final_video_url, final_video_path)
        status_report['assets']['final_video_path'] = final_video_path
        save_tracker()

        # --- Step 10: Subtitle Burning ---
        print("\n--- [Step 9/9] Factory: Adding Subtitles to Video ---")
        print(time.ctime())
        working_video_path = final_video_path  # Start with lip-synced video
        
        if generated_srt_path and os.path.exists(generated_srt_path):
            print(f"   📝 Burning subtitles into video...")
            print(time.ctime())
            subtitled_video_path = subtitle_burner.create_subtitled_video(
                final_video_path, generated_srt_path, project_path, style="netflix"
            )
            
            if subtitled_video_path:
                print(f"   ✅ Subtitles burned successfully!")
                print(f"   📍 Subtitled video: {subtitled_video_path}")
                print(time.ctime())
                status_report['assets']['subtitled_video_path'] = subtitled_video_path
                working_video_path = subtitled_video_path  # Use subtitled version for logo
            else:
                print(f"   ⚠️  Subtitle burning failed, using original video")
                print(time.ctime())
        else:
            print(f"   ℹ️  No subtitles available, skipping subtitle burning")
            print(time.ctime())

        # --- Step 10: Logo Watermarking ---
        print("\n--- [Step 10/12] Factory: Adding Logo Watermark ---")
        print(time.ctime())
        logo_path = os.path.join(INPUTS_DIR, "logo.png")
        
        if os.path.exists(logo_path):
            print(f"   🏷️  Adding logo watermark to main video...")
            print(time.ctime())
            watermarked_video_path = os.path.join(project_path, "watermarked_video.mp4")
            result = branding.add_logo_watermark(
                working_video_path, logo_path, watermarked_video_path, 
                position="top-left", opacity=0.7, scale=0.12  # Customize as needed
            )
            
            if result:
                print(f"   ✅ Logo watermark applied successfully!")
                print(f"   📍 Watermarked video: {result}")
                print(time.ctime())
                status_report['assets']['watermarked_video_path'] = result
                working_video_path = result  # Use watermarked version for branding
            else:
                print(f"   ⚠️  Logo watermarking failed, using previous version")
                print(time.ctime())
        else:
            print(f"   ℹ️  Logo file not found (logo.png), skipping watermark step")
            print(f"   📁  Place logo.png in {INPUTS_DIR} to enable logo watermarking")
            print(time.ctime())

        # --- Step 11: Video Branding ---
        print("\n--- [Step 11/13] Factory: Adding Intro/Outro Branding ---")
        print(time.ctime())
        intro_video_path = os.path.join(INPUTS_DIR, "intro.mp4")
        outro_video_path = os.path.join(INPUTS_DIR, "outro.mp4")
        
        if os.path.exists(intro_video_path) and os.path.exists(outro_video_path):
            print(f"   🎬  Adding intro/outro with title overlay...")
            print(time.ctime())
            branded_video_path = branding.add_branding(
                working_video_path, idea_text, script, intro_video_path, outro_video_path, project_path
            )
            
            if branded_video_path:
                print(f"   ✅ Intro/outro branding applied successfully!")
                print(f"   📍 Branded video: {branded_video_path}")
                print(time.ctime())
                status_report['assets']['branded_video_path'] = branded_video_path
                working_video_path = branded_video_path  # Use branded version for final step
            else:
                print(f"   ⚠️  Failed to apply intro/outro branding, using previous version")
                print(time.ctime())
        else:
            print(f"   ℹ️  Pre-made intro/outro videos not found (intro.mp4, outro.mp4), skipping branding step")
            print(f"   📁  Place intro.mp4 and outro.mp4 in {INPUTS_DIR} to enable branding")
            print(time.ctime())

        # --- Step 12: Final Wrap-up ---
        print("\n--- [Final Step] Pipeline Complete ---")
        print(time.ctime())

        # --- Final Success ---
        status_report['status'] = "SUCCESS"
        save_tracker()
        print(f"\n🎉🎉🎉 SUCCESS! Pipeline complete for '{idea_name}'. 🎉🎉🎉")
        print(f"Final video saved at: {final_video_path}")
        print(time.ctime())

    except Exception as e:
        # If any step fails, record the error
        failed_step = status_report['status']
        print(f"\n❌❌❌ ERROR! Pipeline failed for '{idea_name}' at step: {failed_step} ❌❌❌")
        print(f"   Reason: {e}")
        print(time.ctime())
        status_report['status'] = "FAILED"
        status_report['failed_at_step'] = str(e)
        save_tracker()

    return status_report


# --- Main Execution ---

def main():
    """Main function to start the orchestrator."""
    setup_project_structure()
    run_summary = []
    
    print(time.ctime())
    print("\nWelcome to the Automated Video Content Pipeline!")
    choice = input("What's your idea? (Or type 'file' to read from ideas.csv): ").strip()

    if choice.lower() == 'file':
        ideas_path = os.path.join(INPUTS_DIR, IDEAS_FILE_NAME)
        try:
            ideas_df = pd.read_csv(ideas_path)
            print(f"ORCHESTRATOR: Found {len(ideas_df)} ideas in '{IDEAS_FILE_NAME}'. Processing now...")
            for index, row in ideas_df.iterrows():
                result = run_pipeline_for_idea(
                    idea_text=row['idea'],
                    idea_number=row['number'],
                    idea_name=row['name']
                )
                run_summary.append(result)
                time.sleep(5) # Add a small delay between runs
        except FileNotFoundError:
            print(f"ERROR: ideas.csv not found at '{ideas_path}'")
        except KeyError as e:
            print(f"ERROR: Missing required column in ideas.csv: {e}")
    else:
        # Run for a single, user-provided idea
        result = run_pipeline_for_idea(
            idea_text=choice,
            idea_number="custom",
            idea_name="custom_idea"
        )
        run_summary.append(result)

    # Save the final summary report
    summary_path = os.path.join(STORAGE_DIR, f"run_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(summary_path, 'w') as f:
        json.dump(run_summary, f, indent=4)

    print(f"\n{'='*60}\nORCHESTRATOR: All tasks complete. A summary of the run has been saved to:\n{summary_path}\n{'='*60}")
    print(time.ctime())


if __name__ == '__main__':
    main()
