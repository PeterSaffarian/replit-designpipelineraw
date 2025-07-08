#!/usr/bin/env python3
"""
Clean test for branding workflow.
Tests the final branding stage with a lipsynced + subtitled video.
"""

import os
from factory.branding import add_branding


def main():
    print("=== BRANDING WORKFLOW TEST ===")
    
    # Test inputs (hardcoded)
    main_video = "test_files/video_with_subtitles.mp4"  # Already lipsynced + subtitled
    logo_path = "test_files/logo.png"
    idea = "Digital privacy and online safety"
    script = "Wait, they're asking for my password? This feels off. Remember, never share personal information over the phone, especially if it seems suspicious. It's always better to hang up and verify from a trusted source."



    output_dir = "test_files"
    
    # Check inputs
    if not os.path.exists(main_video):
        print(f"❌ Main video not found: {main_video}")
        return 1
    
    if not os.path.exists(logo_path):
        print(f"❌ Logo not found: {logo_path}")
        return 1
    
    print(f"✅ Main video: {main_video}")
    print(f"✅ Logo: {logo_path}")
    print(f"📝 Idea: {idea}")
    print(f"📝 Script: {script[:50]}...")
    print()
    
    print("Running branding workflow...")
    print("- Generating title with OpenAI")
    print("- Creating intro slide (logo → 'KiaOra presents' → title)")
    print("- Creating outro slide (logo + 'Follow us for more')")
    print("- Concatenating: intro + main + outro")
    print()
    
    # Run the workflow
    result = add_branding(main_video, idea, script, logo_path, output_dir)
    
    if result:
        print(f"✅ SUCCESS: Branded video created at {result}")
        
        # Check file size
        if os.path.exists(result):
            size = os.path.getsize(result)
            print(f"📊 File size: {size:,} bytes")
        
        # List generated files
        print("\n📁 Generated files:")
        for file in ["intro.mp4", "outro.mp4", "branded_video.mp4"]:
            path = os.path.join(output_dir, file)
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"  ✅ {file}: {size:,} bytes")
            else:
                print(f"  ❌ {file}: not found")
        
        return 0
    else:
        print("❌ FAILED: Branding workflow failed")
        return 1


if __name__ == "__main__":
    exit(main())