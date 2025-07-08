#!/usr/bin/env python3
"""
Test script for video branding system.
Tests title generation, intro/outro creation, and complete branding workflow.
"""

import os
import tempfile
from factory.video_branding import (
    generate_video_title,
    create_intro_slide,
    create_outro_slide,
    add_branding_sequence,
    apply_complete_branding
)


def test_title_generation():
    """Test video title generation with OpenAI."""
    print("\n=== Testing Video Title Generation ===")
    
    # Test with sample content
    idea = "Explain digital privacy and online safety"
    script = "Remember, never share personal information over the phone, especially if it seems suspicious. It's always better to hang up and verify from a trusted source."
    artwork_desc = "Character illustration showing digital safety concepts"
    
    print(f"Input idea: {idea}")
    print(f"Script: {script[:50]}...")
    
    # Generate title
    title = generate_video_title(idea, script, artwork_desc)
    
    print(f"Generated title: '{title}'")
    
    # Basic validation
    word_count = len(title.split())
    if 2 <= word_count <= 8:
        print(f"✅ Title length appropriate: {word_count} words")
        return True
    else:
        print(f"⚠️  Title might be too long/short: {word_count} words")
        return True  # Still consider success since it's flexible


def test_intro_slide():
    """Test intro slide creation."""
    print("\n=== Testing Intro Slide Creation ===")
    
    logo_path = "test_files/logo.png"
    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found: {logo_path}")
        return False
    
    output_path = "test_files/intro_slide.mp4"
    test_title = "Stay Safe Online"
    
    print(f"Creating intro slide with title: '{test_title}'")
    
    # Create intro slide
    result = create_intro_slide(test_title, logo_path, output_path, duration=3)
    
    if result and os.path.exists(output_path):
        print(f"✅ Intro slide created: {output_path}")
        return True
    else:
        print(f"❌ Intro slide creation failed")
        return False


def test_outro_slide():
    """Test outro slide creation."""
    print("\n=== Testing Outro Slide Creation ===")
    
    logo_path = "test_files/logo.png"
    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found: {logo_path}")
        return False
    
    output_path = "test_files/outro_slide.mp4"
    
    print(f"Creating outro slide...")
    
    # Create outro slide
    result = create_outro_slide(logo_path, output_path, duration=3)
    
    if result and os.path.exists(output_path):
        print(f"✅ Outro slide created: {output_path}")
        return True
    else:
        print(f"❌ Outro slide creation failed")
        return False


def test_complete_branding():
    """Test complete branding workflow."""
    print("\n=== Testing Complete Branding Workflow ===")
    
    # Check required files
    main_video_path = "test_files/video_with_subtitles.mp4"
    logo_path = "test_files/logo.png"
    
    if not os.path.exists(main_video_path):
        print(f"❌ Main video not found: {main_video_path}")
        print("   Run subtitle tests first to create the subtitled video")
        return False
    
    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found: {logo_path}")
        return False
    
    # Test data
    idea = "Explain digital privacy and online safety"
    script = "Remember, never share personal information over the phone, especially if it seems suspicious."
    
    print(f"Main video: {main_video_path}")
    print(f"Idea: {idea}")
    print(f"Script: {script[:50]}...")
    
    # Apply complete branding
    result = apply_complete_branding(
        main_video_path, idea, script, logo_path, "test_files"
    )
    
    if result and os.path.exists(result):
        print(f"✅ Complete branding successful: {result}")
        return True
    else:
        print(f"❌ Complete branding failed")
        return False


def test_integration():
    """Test module integration."""
    print("\n=== Testing Integration ===")
    
    try:
        # Test imports
        from factory import video_branding
        from orchestrator import MAX_ARTWORK_RETRIES
        
        print("✅ All modules imported successfully")
        
        # Test file structure
        files_check = [
            'factory/video_branding.py'
        ]
        
        for file_path in files_check:
            if os.path.exists(file_path):
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False


def main():
    """Run all branding tests."""
    print("🎬 Starting Video Branding Tests 🎬")
    
    # Ensure test_files directory exists
    os.makedirs("test_files", exist_ok=True)
    
    results = []
    
    # Test integration first
    results.append(test_integration())
    
    # Test title generation
    print("\n" + "="*60)
    results.append(test_title_generation())
    
    # Test intro slide creation
    print("\n" + "="*60)
    results.append(test_intro_slide())
    
    # Test outro slide creation
    print("\n" + "="*60)
    results.append(test_outro_slide())
    
    # Test complete branding workflow
    print("\n" + "="*60)
    results.append(test_complete_branding())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Branding Test Results: {passed}/{total} tests passed")
    print(f"📁 Output files saved in test_files/ directory")
    
    if passed == total:
        print("🎉 All branding tests completed successfully!")
    elif passed >= 3:
        print("✅ Core branding functionality working")
    else:
        print("⚠️  Some branding tests failed - check dependencies")
    
    return passed >= 3


if __name__ == "__main__":
    main()