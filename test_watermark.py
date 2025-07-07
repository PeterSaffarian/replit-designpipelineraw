#!/usr/bin/env python3
"""
Test script for video watermarking functionality.
This script creates sample video and logo files to test the watermarking system.
"""

import os
import tempfile
from PIL import Image, ImageDraw
from factory.video_watermark import add_logo_watermark, apply_final_branding

def create_test_logo():

    print("get test logo...")
    logo_path = "test_files/logo.png"

    if os.path.exists(logo_path):    
        return logo_path

    else:
        print("❌ NO TEST LOGO FOUND")
        return None

def create_test_video():
    
    print("get test video...")

    video_path = "test_files/video.mp4"

    if os.path.exists(video_path):
        return video_path
    else:
        print("❌ NO TEST VIDEO FOUND")
        return None

def test_watermarking():
    """Test the video watermarking functionality."""
    print("\n=== Testing Video Watermarking ===")
    
    # Create test assets
    logo_path = create_test_logo()
    video_path = create_test_video()
    
    if not video_path:
        print("❌ Cannot test watermarking without test video")
        return False
    
    # Test watermarking
    output_path = "test_files/watermarked_video.mp4"
    
    print(f"\nTesting watermark application...")
    result = add_logo_watermark(
        input_video_path=video_path,
        logo_path=logo_path,
        output_path=output_path,
        position="top-left",
        opacity=0.7,
        scale=150
    )
    
    success = result is not None and os.path.exists(output_path)
    
    if success:
        print("✅ Watermarking test completed successfully!")
        print(f"Original video: {video_path}")
        print(f"Watermarked video: {output_path}")
    else:
        print("❌ Watermarking test failed!")
    
    # Test the convenience function
    print(f"\nTesting apply_final_branding function...")
    branded_result = apply_final_branding(video_path, logo_path, "/tmp")
    
    if branded_result and os.path.exists(branded_result):
        print(f"✅ Final branding test successful: {branded_result}")
    else:
        print("❌ Final branding test failed!")
    
    # # Cleanup test files
    # for file_path in [logo_path, video_path, output_path, branded_result]:
    #     if file_path and os.path.exists(file_path):
    #         os.remove(file_path)
    #         print(f"Cleaned up: {file_path}")
    
    return success

def main():
    """Run the watermarking test."""
    try:
        success = test_watermarking()
        if success:
            print("\n✅ All watermarking tests passed!")
        else:
            print("\n❌ Some watermarking tests failed!")
        return success
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return False

if __name__ == "__main__":
    main()