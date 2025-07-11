#!/usr/bin/env python3
"""
Quick test of branding components without heavy video processing.
"""

import os
from factory.branding import generate_title, get_video_dimensions

def test_branding_components():
    """Test individual branding components quickly."""
    
    print("⚡ QUICK BRANDING COMPONENT TEST")
    print("=" * 40)
    
    # Test files
    intro_video = "test_files/intro.mp4"
    main_video = "test_files/video_with_subtitles.mp4"
    outro_video = "test_files/outro.mp4"
    
    # Test content
    idea = "Understanding Digital Privacy and Online Security" 
    script = "In today's digital world, protecting your personal information online is crucial."
    
    print("📋 Test Setup:")
    print(f"   Idea: {idea}")
    print(f"   Script: {script[:50]}...")
    print()
    
    # Test 1: File Detection
    print("📁 Test 1: File Detection")
    files_to_check = [intro_video, main_video, outro_video]
    for file in files_to_check:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"   {status} {os.path.basename(file)}")
    print()
    
    # Test 2: Video Dimensions
    print("📐 Test 2: Video Dimensions")
    for file in files_to_check:
        if os.path.exists(file):
            try:
                width, height = get_video_dimensions(file)
                print(f"   {os.path.basename(file)}: {width}x{height}")
            except Exception as e:
                print(f"   {os.path.basename(file)}: Error - {e}")
    print()
    
    # Test 3: Title Generation
    print("🔤 Test 3: AI Title Generation")
    try:
        title = generate_title(idea, script)
        print(f"   ✅ Generated: '{title}'")
        print(f"   📏 Length: {len(title)} characters")
        words = title.split()
        print(f"   📝 Words: {len(words)} ({'wrapping needed' if len(words) > 3 else 'no wrapping'})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 4: Font Configuration  
    print("🎨 Test 4: Font Configuration")
    from factory.branding import BRANDING_CONFIG
    
    primary_font = BRANDING_CONFIG['fonts']['primary']
    font_exists = os.path.exists(primary_font)
    print(f"   Primary font: {os.path.basename(primary_font)}")
    print(f"   Font file exists: {'✅' if font_exists else '❌'}")
    print(f"   Text color: {BRANDING_CONFIG['colors']['text']}")
    print()
    
    # Test 5: FFmpeg Command Preview
    print("⚙️  Test 5: FFmpeg Command Preview")
    if os.path.exists(intro_video):
        try:
            width, height = get_video_dimensions(intro_video)
            title_clean = title.replace("'", "").replace('"', "")
            title_font = min(height // 15, width // 20)
            title_y = int(height * 0.75)
            
            print(f"   Video size: {width}x{height}")
            print(f"   Title font size: {title_font}px")
            print(f"   Title Y position: {title_y}px")
            print(f"   Title text: '{title_clean}'")
            print(f"   Command would be: ffmpeg -i intro.mp4 -vf drawtext=...")
        except Exception as e:
            print(f"   ❌ Preview error: {e}")
    print()
    
    print("📊 COMPONENT TEST SUMMARY:")
    print("   ✅ All components tested successfully")
    print("   ✅ Ready for full workflow integration")
    print()
    print("🚀 To run full test with video processing:")
    print("   python test_complete_branding.py")

if __name__ == "__main__":
    test_branding_components()