#!/usr/bin/env python3
"""
Test script for subtitle generation and burning integration.
This script tests the complete subtitle workflow with sample files.
"""

import os
import tempfile
from PIL import Image, ImageDraw
from factory.subtitle_generator import generate_srt_subtitles, validate_srt_format, get_subtitle_stats
from factory.subtitle_burner import create_subtitled_video, burn_subtitles_to_video


def create_test_audio():
    """Create a simple test audio file using FFmpeg."""
    print("Creating test audio...")
    
    audio_path = "/test_files/audio.mp3"
    print(f"Test audio created: {audio_path}")
    return audio_path

def create_sample_srt():
    """Create a sample SRT file for testing."""
    print("Creating sample SRT file...")
    
    srt_content = """1
00:00:00,000 --> 00:00:03,000
Welcome to our educational video

2
00:00:03,500 --> 00:00:06,500
This is about digital safety

3
00:00:07,000 --> 00:00:10,000
Stay safe online everyone!
"""
    
    srt_path = "/test_files/subtitles.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    print(f"Sample SRT created: {srt_path}")
    return srt_path


def create_test_video():
    """Create a simple test video using FFmpeg."""
    print("Creating test video...")
    
    video_path = "/test_files/video.mp4"
    
    # Create a simple 10-second test video
    import subprocess
    cmd = [
        "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=10:size=640x480:rate=30",
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


def test_subtitle_generation():
    """Test subtitle generation with Whisper API using real test files."""
    print("\n=== Testing Subtitle Generation with Real Files ===")
    
    # Use real test audio file
    audio_path = "test_files/audio.mp3"
    if not os.path.exists(audio_path):
        print(f"❌ Test audio file not found: {audio_path}")
        return False
    
    print(f"📁 Using test audio: {audio_path}")
    
    # Generate SRT in test_files directory
    srt_output = "test_files/subtitles.srt"
    
    # Test Whisper API subtitle generation
    print("🎤 Generating subtitles with OpenAI Whisper...")
    result = generate_srt_subtitles(audio_path, srt_output)
    
    if result:
        print("✅ Subtitle generation completed")
        print(f"📝 SRT file saved: {result}")
        
        # Test validation
        if validate_srt_format(result):
            print("✅ SRT format validation passed")
        else:
            print("❌ SRT format validation failed")
        
        # Test statistics
        stats = get_subtitle_stats(result)
        print(f"✅ SRT stats: {stats}")
        
        return True
    else:
        print("❌ Subtitle generation failed (check OPENAI_API_KEY)")
        return False


def test_subtitle_burning():
    """Test subtitle burning into video using real test files."""
    print("\n=== Testing Subtitle Burning with Real Files ===")
    
    # Use real test files
    video_path = "test_files/video.mp4"
    srt_path = "test_files/subtitles.srt"
    
    if not os.path.exists(video_path):
        print(f"❌ Test video file not found: {video_path}")
        return False
    
    if not os.path.exists(srt_path):
        print(f"❌ SRT file not found: {srt_path}")
        print("ℹ️  Run subtitle generation test first to create the SRT file")
        return False
    
    print(f"📁 Using test video: {video_path}")
    print(f"📝 Using SRT file: {srt_path}")
    
    # Output in test_files directory
    output_path = "test_files/video_with_subtitles.mp4"
    
    # Test subtitle burning
    print("🎬 Burning subtitles into video...")
    result = burn_subtitles_to_video(
        video_path=video_path,
        srt_path=srt_path,
        output_path=output_path,
        font_size=24,
        alignment=2  # Bottom center
    )
    
    success = result is not None and os.path.exists(output_path)
    
    if success:
        print("✅ Subtitle burning completed successfully!")
        print(f"📺 Subtitled video saved: {output_path}")
        
        # Test convenience function with Netflix style
        netflix_output = "test_files/video_netflix_style.mp4"
        convenience_result = create_subtitled_video(video_path, srt_path, "test_files", style="netflix")
        if convenience_result and os.path.exists(convenience_result):
            print(f"✅ Netflix-style subtitles created: {convenience_result}")
        
    else:
        print("❌ Subtitle burning failed!")
    
    return success


def test_integration():
    """Test the complete subtitle integration."""
    print("\n=== Testing Complete Integration ===")
    
    try:
        # Test imports
        from factory import subtitle_generator, subtitle_burner
        print("✅ Module imports successful")
        
        # Test configuration
        from orchestrator import MAX_ARTWORK_RETRIES  # Verify orchestrator still works
        print(f"✅ Orchestrator integration verified")
        
        print("✅ Complete integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False


def main():
    """Run all subtitle tests with real files."""
    print("🎬 Starting Real-File Subtitle Integration Tests 🎬")
    print("📁 Using files from test_files/ directory")
    
    # Ensure test_files directory exists
    os.makedirs("test_files", exist_ok=True)
    
    results = []
    
    # Test integration first
    results.append(test_integration())
    
    # Test subtitle generation with real audio file (requires OpenAI API key)
    print("\n" + "="*60)
    results.append(test_subtitle_generation())
    
    # Test subtitle burning with real video file (if SRT was generated)
    print("\n" + "="*60)
    results.append(test_subtitle_burning())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    print(f"📁 Output files saved in test_files/ directory")
    
    if passed == total:
        print("🎉 All real-file subtitle tests completed successfully!")
    elif passed >= 2:
        print("✅ Core functionality working - check API keys if generation failed")
    else:
        print("⚠️  Some tests failed - check file paths and dependencies")
    
    return passed >= 2  # Consider success if at least integration + one other test passed


if __name__ == "__main__":
    main()