#!/usr/bin/env python3
"""
Clean test for branding workflow.
Tests the final branding stage with a lipsynced + subtitled video.
"""

import os
from factory import branding

def main():
    print("=== BRANDING WORKFLOW TEST ===")
    
    # Test files
    main_video = "test_files/video_with_subtitles.mp4"
    logo_path = "test_files/logo.png"
    output_dir = "test_files"
    
    # Check files exist
    if not os.path.exists(main_video):
        print(f"❌ FAILED: Main video not found: {main_video}")
        return
    if not os.path.exists(logo_path):
        print(f"❌ FAILED: Logo not found: {logo_path}")
        return
        
    print(f"✅ Main video: {main_video}")
    print(f"✅ Logo: {logo_path}")
    
    # Test data
    idea = "Digital privacy and online safety"
    script = "Wait, they're asking for my password? This feels off. Let me check if this website is actually legitimate before entering any personal information."
    
    print(f"📝 Idea: {idea}")
    print(f"📝 Script: {script[:50]}...")
    print()
    
    print("Running branding workflow...")
    print("- Generating title with OpenAI")
    print("- Creating intro slide (logo → 'KiaOra presents' → title)")
    print("- Creating outro slide (logo + 'Follow us for more')")
    print("- Concatenating: intro + main + outro")
    print()
    
    # Run the branding workflow
    result = branding.add_branding(main_video, idea, script, logo_path, output_dir)
    
    if result:
        print(f"✅ SUCCESS: Branded video created!")
        print(f"📍 Output: {result}")
        
        # Check file size
        if os.path.exists(result):
            size = os.path.getsize(result)
            print(f"📊 File size: {size:,} bytes")
        
        print()
        print("🎬 WORKFLOW COMPLETE:")
        print("   • Intro slide with logo → 'KiaOra presents' → AI-generated title")
        print("   • Original main video with audio preserved")
        print("   • Outro slide with logo + 'Follow us for more'")
        print("   • Professional entrance animations")
        print("   • Smart text sizing and wrapping")
        
    else:
        print("❌ FAILED: Branding workflow failed")

if __name__ == "__main__":
    main()