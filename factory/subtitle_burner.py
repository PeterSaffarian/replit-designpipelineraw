"""
Subtitle burning module for adding styled subtitles to videos using FFmpeg.

This module handles burning SRT subtitle files into videos with professional
Netflix-style formatting and positioning.
"""

import os
import subprocess
from typing import Optional


def burn_subtitles_to_video(
    video_path: str,
    srt_path: str,
    output_path: str,
    font_name: str = "Arial",
    font_size: int = 12,
    font_color: str = "&H00FFFFFF",  # White
    outline_color: str = "&H00000000",  # Black
    outline_width: int = 2,
    alignment: int = 2  # Bottom center
) -> Optional[str]:
    """
    Burn styled subtitles into a video using FFmpeg.
    
    Creates professional Netflix-style subtitles with white text, black outline,
    and bottom center positioning.
    
    Args:
        video_path (str): Path to the input video file
        srt_path (str): Path to the SRT subtitle file
        output_path (str): Path where the subtitled video will be saved
        font_name (str): Font family name (default: Arial)
        font_size (int): Font size in points (default: 20)
        font_color (str): Text color in BGR format (default: white)
        outline_color (str): Outline color in BGR format (default: black)
        outline_width (int): Outline thickness in pixels (default: 2)
        alignment (int): Subtitle position (2=bottom center, 6=top center)
    
    Returns:
        str: Path to the subtitled video file, or None on failure
    """
    print(f"SUBTITLE_BURN: Adding subtitles to video...")
    print(f"SUBTITLE_BURN: Video: {video_path}")
    print(f"SUBTITLE_BURN: Subtitles: {srt_path}")
    print(f"SUBTITLE_BURN: Style: {font_name} {font_size}pt, alignment={alignment}")
    
    # Validate input files
    if not os.path.exists(video_path):
        print(f"SUBTITLE_BURN: Error - Video file not found: {video_path}")
        return None
    
    if not os.path.exists(srt_path):
        print(f"SUBTITLE_BURN: Error - SRT file not found: {srt_path}")
        return None
    
    try:
        # Build the subtitle style string for FFmpeg
        subtitle_style = (
            f"FontName={font_name},"
            f"FontSize={font_size},"
            f"PrimaryColour={font_color},"
            f"OutlineColour={outline_color},"
            f"Outline={outline_width},"
            f"Alignment={alignment},"
            f"BorderStyle=1"  # Outline style
        )
        
        # Build FFmpeg command for subtitle burning
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", video_path,                    # Input video
            "-vf", f"subtitles={srt_path}:force_style='{subtitle_style}'",  # Subtitle filter
            "-c:a", "copy",                      # Copy audio without re-encoding
            "-y",                                # Overwrite output file
            output_path                          # Output path
        ]
        
        print(f"SUBTITLE_BURN: Running FFmpeg subtitle burning...")
        
        # Execute FFmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for subtitle burning
        )
        
        if result.returncode == 0:
            print(f"SUBTITLE_BURN: ✅ Subtitles burned successfully!")
            print(f"SUBTITLE_BURN: Output saved to: {output_path}")
            return output_path
        else:
            print(f"SUBTITLE_BURN: ❌ FFmpeg failed with return code {result.returncode}")
            print(f"SUBTITLE_BURN: Error output: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"SUBTITLE_BURN: ❌ FFmpeg timeout - subtitle burning took too long")
        return None
    except Exception as e:
        print(f"SUBTITLE_BURN: ❌ Error during subtitle burning: {e}")
        return None


def create_subtitled_video(
    video_path: str,
    srt_path: str,
    project_path: str,
    style: str = "netflix"
) -> Optional[str]:
    """
    Create a subtitled version of a video with predefined styling.
    
    This is a convenience function that applies common subtitle styles.
    
    Args:
        video_path (str): Path to the input video file
        srt_path (str): Path to the SRT subtitle file
        project_path (str): Project directory for output file
        style (str): Predefined style ("netflix", "youtube", "minimal")
    
    Returns:
        str: Path to the subtitled video file, or None on failure
    """
    print(f"SUBTITLE_BURN: Creating subtitled video with '{style}' style...")
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_filename = f"{base_name}_subtitled.mp4"
    output_path = os.path.join(project_path, output_filename)
    
    # Define style presets
    style_presets = {
        "netflix": {
            "font_name": "Arial",
            "font_size": 12,
            "font_color": "&H00FFFFFF",    # White
            "outline_color": "&H00000000", # Black
            "outline_width": 2,
            "alignment": 2  # Bottom center
        },
        "youtube": {
            "font_name": "Liberation Sans",
            "font_size": 12,
            "font_color": "&H00FFFFFF",    # White
            "outline_color": "&H00000000", # Black
            "outline_width": 1,
            "alignment": 2  # Bottom center
        },
        "minimal": {
            "font_name": "Arial",
            "font_size": 16,
            "font_color": "&H00FFFFFF",    # White
            "outline_color": "&H00000000", # Black
            "outline_width": 1,
            "alignment": 2  # Bottom center
        }
    }
    
    # Get style settings
    if style not in style_presets:
        print(f"SUBTITLE_BURN: Unknown style '{style}', using 'netflix' default")
        style = "youtube"
    
    settings = style_presets[style]
    
    # Apply subtitle burning with selected style
    return burn_subtitles_to_video(
        video_path=video_path,
        srt_path=srt_path,
        output_path=output_path,
        **settings
    )


def get_video_info(video_path: str) -> dict:
    """
    Get basic information about a video file using FFprobe.
    
    Args:
        video_path (str): Path to the video file
    
    Returns:
        dict: Video information including duration, resolution, etc.
    """
    info = {
        'duration': 0.0,
        'width': 0,
        'height': 0,
        'fps': 0.0,
        'valid': False
    }
    
    try:
        # Get video duration
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            info['duration'] = float(result.stdout.strip())
        
        # Get video resolution and fps
        cmd = [
            "ffprobe", "-v", "quiet", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "csv=p=0", video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            parts = result.stdout.strip().split(',')
            if len(parts) >= 3:
                info['width'] = int(parts[0])
                info['height'] = int(parts[1])
                # Parse frame rate (e.g., "30/1" -> 30.0)
                fps_parts = parts[2].split('/')
                if len(fps_parts) == 2:
                    info['fps'] = float(fps_parts[0]) / float(fps_parts[1])
        
        info['valid'] = True
        print(f"SUBTITLE_BURN: Video info - {info['width']}x{info['height']}, {info['duration']:.1f}s, {info['fps']:.1f}fps")
        
    except Exception as e:
        print(f"SUBTITLE_BURN: Error getting video info: {e}")
    
    return info