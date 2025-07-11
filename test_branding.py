#!/usr/bin/env python3
"""
Test script for pre-made video branding workflow.
Process: Generate title → Add to intro → Concatenate all videos → Output
"""

import os
from factory.branding import generate_title, add_title_overlay, concatenate_videos

def test_branding_workflow():
    """Test the complete pre-made video branding workflow."""
    
    print("Pre-Made Video Branding Test")
    print("=" * 30)
    
    # Test configuration
    idea = "Digital Privacy and Security Best Practices"
    script = "Learn essential techniques to protect your personal data online and stay safe from cyber threats."
    
    intro_video = "test_files/intro.mp4"
    main_video = "test_files/video_with_subtitles.mp4" 
    outro_video = "test_files/outro.mp4"
    output_dir = "test_files"
    
    # Check files exist
    files = [intro_video, main_video, outro_video]
    missing = [f for f in files if not os.path.exists(f)]
    
    if missing:
        print(f"Missing files: {missing}")
        return False
    
    print(f"Content: {idea}")
    print(f"Files: intro.mp4 + main video + outro.mp4")
    print()
    
    # Step 1: Generate title
    print("Step 1: Generate Video Title")
    title = generate_title(idea, script)
    print(f"Generated: '{title}'")
    print()
    
    # Step 2: Add title to intro
    print("Step 2: Add Title to Intro Video")
    intro_with_title = os.path.join(output_dir, "intro_with_title.mp4")
    overlay_result = add_title_overlay(intro_video, title, intro_with_title)
    
    if not overlay_result:
        print("Failed to add title overlay")
        return False
    
    print(f"Title added to intro: {overlay_result}")
    print()
    
    # Step 3: Concatenate videos
    print("Step 3: Concatenate All Videos")
    final_output = os.path.join(output_dir, "final_branded_video.mp4")
    video_list = [intro_with_title, main_video, outro_video]
    
    concat_result = concatenate_videos(video_list, final_output)
    
    if not concat_result:
        print("Failed to concatenate videos")
        return False
    
    file_size = os.path.getsize(concat_result) / (1024 * 1024)  # MB
    print(f"Final video: {concat_result}")
    print(f"Size: {file_size:.1f} MB")
    print()
    
    # Cleanup
    try:
        if os.path.exists(intro_with_title):
            os.unlink(intro_with_title)
            print("Cleaned up temporary files")
    except:
        pass
    
    print("Workflow completed successfully!")
    return True

if __name__ == "__main__":
    success = test_branding_workflow()
    if not success:
        exit(1)