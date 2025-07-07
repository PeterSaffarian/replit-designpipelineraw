"""
Fallback video-audio merging using FFmpeg when Sync.so is unavailable.

This module provides basic video-audio synchronization using FFmpeg as a backup
when the Sync.so lip-sync service is experiencing issues.
"""

import os
import subprocess
from typing import Optional


def merge_video_audio_ffmpeg(
    video_path: str,
    audio_path: str,
    output_path: str,
    trim_video: bool = True
) -> Optional[str]:
    """
    Merges video and audio using FFmpeg as fallback when Sync.so is unavailable.
    
    This is a basic merge operation that synchronizes video length with audio length.
    It doesn't provide lip-sync capabilities but ensures the video plays with the audio.
    
    Args:
        video_path (str): Path to the input video file
        audio_path (str): Path to the input audio file  
        output_path (str): Path where the merged video will be saved
        trim_video (bool): Whether to trim video to match audio duration
    
    Returns:
        str: Path to the merged video file, or None on failure
    """
    print(f"VIDEO_AUDIO_MERGE: Merging video and audio using FFmpeg fallback...")
    print(f"VIDEO_AUDIO_MERGE: Video: {video_path}")
    print(f"VIDEO_AUDIO_MERGE: Audio: {audio_path}")
    
    # Validate input files
    if not os.path.exists(video_path):
        print(f"VIDEO_AUDIO_MERGE: Error - Video file not found: {video_path}")
        return None
    
    if not os.path.exists(audio_path):
        print(f"VIDEO_AUDIO_MERGE: Error - Audio file not found: {audio_path}")
        return None
    
    try:
        if trim_video:
            # Get audio duration and trim video to match
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", video_path,    # Input video
                "-i", audio_path,    # Input audio
                "-c:v", "libx264",   # Video codec
                "-c:a", "aac",       # Audio codec
                "-map", "0:v:0",     # Use video from first input
                "-map", "1:a:0",     # Use audio from second input
                "-shortest",         # End when shortest stream ends
                "-y",                # Overwrite output file
                output_path
            ]
        else:
            # Simple merge without trimming
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", video_path,    # Input video
                "-i", audio_path,    # Input audio
                "-c:v", "copy",      # Copy video codec (faster)
                "-c:a", "aac",       # Audio codec
                "-map", "0:v:0",     # Use video from first input
                "-map", "1:a:0",     # Use audio from second input
                "-y",                # Overwrite output file
                output_path
            ]
        
        print(f"VIDEO_AUDIO_MERGE: Running FFmpeg merge...")
        
        # Execute FFmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"VIDEO_AUDIO_MERGE: ✅ Video and audio merged successfully!")
            print(f"VIDEO_AUDIO_MERGE: Output saved to: {output_path}")
            return output_path
        else:
            print(f"VIDEO_AUDIO_MERGE: ❌ FFmpeg failed with return code {result.returncode}")
            print(f"VIDEO_AUDIO_MERGE: Error output: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"VIDEO_AUDIO_MERGE: ❌ FFmpeg timeout - merge took too long")
        return None
    except Exception as e:
        print(f"VIDEO_AUDIO_MERGE: ❌ Error during merge: {e}")
        return None


def get_media_duration(file_path: str) -> Optional[float]:
    """Get duration of audio/video file in seconds using FFprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return None
    except Exception:
        return None