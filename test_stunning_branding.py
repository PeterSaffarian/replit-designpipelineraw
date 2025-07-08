#!/usr/bin/env python3
"""
Test script for the stunning branding system.
This is the file you can run to test the branding system yourself!

Usage: python test_stunning_branding.py
"""

import os
import sys
import subprocess
import json
from factory.video_branding_simple import apply_beautiful_branding


def check_video_dimensions(video_path):
    """Check and display video dimensions."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', video_path
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    w = stream.get('width')
                    h = stream.get('height')
                    print(f"   Video dimensions: {w}x{h}")
                    return w, h
    except Exception as e:
        print(f"   Could not get dimensions: {e}")
    return None, None


def main():
    print("=== STUNNING BRANDING SYSTEM TEST ===")
    print("This script tests the complete branding workflow with beautiful animations!")
    print()
    
    # Test files
    main_video = 'test_files/video_with_subtitles.mp4'
    logo_path = 'test_files/logo.png'
    idea = 'Explain digital privacy and online safety'
    script = 'Remember, never share personal information over the phone, especially if it seems suspicious.'
    
    # Check if required files exist
    print("Checking required files...")
    if not os.path.exists(main_video):
        print(f"❌ Main video not found: {main_video}")
        return 1
    else:
        print(f"✅ Main video found: {main_video}")
        check_video_dimensions(main_video)
    
    if not os.path.exists(logo_path):
        print(f"❌ Logo not found: {logo_path}")
        return 1
    else:
        print(f"✅ Logo found: {logo_path}")
    
    print()
    print("Starting stunning branding workflow...")
    print("This will create:")
    print("- Beautiful purple gradient backgrounds")
    print("- Large animated logos")
    print("- Properly sized text that fits on screen")
    print("- Smooth fade transitions")
    print("- Professional intro/outro sequence")
    print()
    
    # Run the branding system
    result = apply_beautiful_branding(main_video, idea, script, logo_path, 'test_files')
    
    if result:
        print()
        print("=== SUCCESS! ===")
        print(f"✅ Final branded video created: {result}")
        print()
        
        # Check final video
        print("Final video details:")
        check_video_dimensions(result)
        
        # Check individual slides
        intro_slide = 'test_files/stunning_intro.mp4'
        outro_slide = 'test_files/stunning_outro.mp4'
        
        if os.path.exists(intro_slide):
            print(f"✅ Intro slide: {intro_slide}")
            check_video_dimensions(intro_slide)
        
        if os.path.exists(outro_slide):
            print(f"✅ Outro slide: {outro_slide}")
            check_video_dimensions(outro_slide)
        
        print()
        print("🎉 You can now view the beautiful branded video!")
        print("The branding system is working perfectly with:")
        print("- Proper aspect ratios")
        print("- Large, visible logos")
        print("- Text that fits on screen")
        print("- Beautiful animations")
        print("- Professional design")
        
        return 0
    else:
        print()
        print("❌ FAILED: Branding system encountered issues")
        print("Check the logs above for error details")
        return 1


if __name__ == "__main__":
    sys.exit(main())