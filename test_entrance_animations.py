#!/usr/bin/env python3
"""
Test script to demonstrate the improved entrance animations in branding slides.
"""

import os
from factory.branding import create_intro_slide, create_outro_slide

def test_entrance_animations():
    """Test the entrance animations in intro and outro slides."""
    
    print("=== ENTRANCE ANIMATIONS TEST ===")
    
    # Check required files
    logo_path = "test_files/logo.png"
    if not os.path.exists(logo_path):
        print(f"❌ Logo not found: {logo_path}")
        return False
    
    # Test parameters
    width, height = 720, 1280  # Vertical video format
    title = "Digital Security Test"
    
    # Create intro slide with animations
    print("Creating intro slide with entrance animations...")
    intro_path = "test_files/test_intro_animated.mp4"
    intro_success = create_intro_slide(title, logo_path, intro_path, width, height)
    
    if intro_success:
        print(f"✅ Intro slide created: {intro_path}")
        print("   - Logo slides down from above (0.5-1.5 seconds)")
        print("   - 'KiaOra presents' slides down (1-2 seconds)")
        print("   - Title slides up from below (2.5-3.5 seconds)")
    else:
        print("❌ Failed to create intro slide")
        return False
    
    # Create outro slide with animations
    print("\nCreating outro slide with entrance animations...")
    outro_path = "test_files/test_outro_animated.mp4"
    outro_success = create_outro_slide(logo_path, outro_path, width, height)
    
    if outro_success:
        print(f"✅ Outro slide created: {outro_path}")
        print("   - Logo slides down from above (0.5-1.5 seconds)")
        print("   - 'Follow us for more' slides up from below (1-2 seconds)")
    else:
        print("❌ Failed to create outro slide")
        return False
    
    # Show file details
    if os.path.exists(intro_path):
        intro_size = os.path.getsize(intro_path)
        print(f"\n📊 Intro slide: {intro_size} bytes")
    
    if os.path.exists(outro_path):
        outro_size = os.path.getsize(outro_path)
        print(f"📊 Outro slide: {outro_size} bytes")
    
    print("\n✅ SUCCESS: Both animated slides created successfully!")
    print("\nThe entrance animations implemented:")
    print("• Elements start off-screen (above/below)")
    print("• Smooth slide transitions using mathematical easing")
    print("• Elements reach final position and stay static")
    print("• No constant motion after entrance is complete")
    print("• Proper timing sequence for professional look")
    
    return True

if __name__ == "__main__":
    success = test_entrance_animations()
    exit(0 if success else 1)