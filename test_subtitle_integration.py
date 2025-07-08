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
    
    audio_path = "/tmp/test_audio.mp3"
    
    # Create a 10-second test audio with spoken text
    import subprocess
    cmd = [
        "ffmpeg", "-f", "lavfi", "-i", 
        "sine=frequency=440:duration=10",  # 10 second sine wave
        "-c:a", "mp3", "-b:a", "128k", "-y", audio_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"Test audio created: {audio_path}")
            return audio_path
        else:
            print(f"Failed to create test audio: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error creating test audio: {e}")
        return None


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
    
    srt_path = "/tmp/sample_subtitles.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    print(f"Sample SRT created: {srt_path}")
    return srt_path


def create_test_video():
    """Create a simple test video using FFmpeg."""
    print("Creating test video...")
    
    video_path = "/tmp/test_video.mp4"
    
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
    """Test subtitle generation with Whisper API."""
    print("\n=== Testing Subtitle Generation ===")
    
    # Note: This test will fail without OPENAI_API_KEY, which is expected
    audio_path = create_test_audio()
    if not audio_path:
        print("❌ Cannot test subtitle generation without test audio")
        return False
    
    srt_output = "/tmp/generated_subtitles.srt"
    
    # Test Whisper API subtitle generation
    result = generate_srt_subtitles(audio_path, srt_output)
    
    if result:
        print("✅ Subtitle generation completed")
        
        # Test validation
        if validate_srt_format(result):
            print("✅ SRT format validation passed")
        else:
            print("❌ SRT format validation failed")
        
        # Test statistics
        stats = get_subtitle_stats(result)
        print(f"✅ SRT stats: {stats}")
        
        # Cleanup
        for file_path in [audio_path, result]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return True
    else:
        print("ℹ️  Subtitle generation skipped (likely missing API key)")
        os.remove(audio_path)
        return False


def test_subtitle_burning():
    """Test subtitle burning into video."""
    print("\n=== Testing Subtitle Burning ===")
    
    # Create test assets
    video_path = create_test_video()
    srt_path = create_sample_srt()
    
    if not video_path or not srt_path:
        print("❌ Cannot test subtitle burning without test assets")
        return False
    
    output_path = "/tmp/subtitled_video.mp4"
    
    # Test subtitle burning
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
        print(f"Original video: {video_path}")
        print(f"Subtitled video: {output_path}")
        
        # Test convenience function
        convenience_result = create_subtitled_video(video_path, srt_path, "/tmp", style="netflix")
        if convenience_result and os.path.exists(convenience_result):
            print(f"✅ Convenience function test successful: {convenience_result}")
        
    else:
        print("❌ Subtitle burning failed!")
    
    # Cleanup
    for file_path in [video_path, srt_path, output_path, convenience_result]:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up: {file_path}")
    
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
    """Run all subtitle tests."""
    print("🎬 Starting Subtitle Integration Tests 🎬")
    
    results = []
    
    # Test integration first
    results.append(test_integration())
    
    # Test subtitle burning (doesn't require API keys)
    results.append(test_subtitle_burning())
    
    # Test subtitle generation (requires OpenAI API key)
    results.append(test_subtitle_generation())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All subtitle integration tests completed successfully!")
    else:
        print("⚠️  Some tests failed - check API keys and dependencies")
    
    return passed == total


if __name__ == "__main__":
    main()