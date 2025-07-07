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
    """Create a test transparent PNG logo."""
    print("Creating test logo...")
    
    # Create a transparent logo with text
    img = Image.new('RGBA', (200, 100), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Draw a simple logo with text and shape
    draw.rectangle([10, 10, 190, 90], fill=(0, 123, 255, 180), outline=(0, 100, 200, 255), width=3)
    draw.text((50, 35), "LOGO", fill=(255, 255, 255, 255))
    
    logo_path = "/tmp/test_logo.png"
    img.save(logo_path)
    print(f"Test logo saved to: {logo_path}")
    return logo_path

def create_test_video():
    """Create a simple test video using FFmpeg."""
    print("Creating test video...")
    
    video_path = "/tmp/test_video.mp4"
    
    # Create a simple 5-second test video with color bars
    import subprocess
    cmd = [
        "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=5:size=640x480:rate=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"Test video created: {video_path}")
            return video_path
        else:
            print(f"Failed to create test video: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error creating test video: {e}")
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
    output_path = "/tmp/watermarked_video.mp4"
    
    print(f"\nTesting watermark application...")
    result = add_logo_watermark(
        input_video_path=video_path,
        logo_path=logo_path,
        output_path=output_path,
        position="bottom-right",
        opacity=0.3,
        scale=100
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
    
    # Cleanup test files
    for file_path in [logo_path, video_path, output_path, branded_result]:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up: {file_path}")
    
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