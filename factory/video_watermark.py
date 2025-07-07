"""
Video watermarking module for adding logo overlays to final videos.

This module handles adding transparent logo overlays to completed videos
with configurable positioning, opacity, and sizing.
"""

import os
import subprocess
from typing import Optional


def add_logo_watermark(
    input_video_path: str,
    logo_path: str,
    output_path: str,
    position: str = "bottom-right",
    opacity: float = 0.3,
    scale: int = 150
) -> Optional[str]:
    """
    Adds a transparent logo watermark to a video.
    
    Args:
        input_video_path (str): Path to the input video file
        logo_path (str): Path to the transparent PNG logo file
        output_path (str): Path where the watermarked video will be saved
        position (str): Logo position - "top-left", "top-right", "bottom-left", "bottom-right"
        opacity (float): Logo opacity (0.0 to 1.0, where 0.3 = 30% visible)
        scale (int): Logo width in pixels (height auto-calculated to maintain aspect ratio)
    
    Returns:
        str: Path to the watermarked video file, or None on failure
    """
    print(f"VIDEO WATERMARK: Adding logo watermark to video...")
    print(f"VIDEO WATERMARK: Input: {input_video_path}")
    print(f"VIDEO WATERMARK: Logo: {logo_path}")
    print(f"VIDEO WATERMARK: Position: {position}, Opacity: {opacity*100}%, Scale: {scale}px")
    
    # Validate input files
    if not os.path.exists(input_video_path):
        print(f"VIDEO WATERMARK: Error - Input video not found: {input_video_path}")
        return None
    
    if not os.path.exists(logo_path):
        print(f"VIDEO WATERMARK: Error - Logo file not found: {logo_path}")
        return None
    
    try:
        # Define position coordinates
        position_map = {
            "top-left": "10:10",
            "top-right": f"main_w-overlay_w-10:10",
            "bottom-left": f"10:main_h-overlay_h-10",
            "bottom-right": f"main_w-overlay_w-10:main_h-overlay_h-10"
        }
        
        if position not in position_map:
            print(f"VIDEO WATERMARK: Error - Invalid position: {position}")
            return None
        
        overlay_position = position_map[position]
        
        # Build FFmpeg command for watermarking
        # This command:
        # 1. Scales the logo to specified width (maintaining aspect ratio)
        # 2. Applies opacity/transparency
        # 3. Overlays at specified position
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_video_path,  # Input video
            "-i", logo_path,         # Input logo
            "-filter_complex", 
            f"[1:v]scale={scale}:-1,format=rgba,colorchannelmixer=aa={opacity}[logo];"
            f"[0:v][logo]overlay={overlay_position}",
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",            # Overwrite output file if exists
            output_path
        ]
        
        print(f"VIDEO WATERMARK: Running FFmpeg command...")
        
        # Execute FFmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"VIDEO WATERMARK: ✅ Watermark applied successfully!")
            print(f"VIDEO WATERMARK: Output saved to: {output_path}")
            return output_path
        else:
            print(f"VIDEO WATERMARK: ❌ FFmpeg failed with return code {result.returncode}")
            print(f"VIDEO WATERMARK: Error output: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"VIDEO WATERMARK: ❌ FFmpeg timeout - video processing took too long")
        return None
    except Exception as e:
        print(f"VIDEO WATERMARK: ❌ Error during watermarking: {e}")
        return None


def apply_final_branding(
    final_video_path: str,
    logo_path: str,
    project_path: str
) -> Optional[str]:
    """
    Applies company branding to the final video while preserving the original.
    
    This is a convenience function that creates a branded version of the final video
    while keeping the original intact.
    
    Args:
        final_video_path (str): Path to the final lip-synced video
        logo_path (str): Path to the logo file (should be transparent PNG)
        project_path (str): Project directory path for output
    
    Returns:
        str: Path to the branded video file, or None on failure
    """
    print(f"VIDEO WATERMARK: Applying final branding...")
    
    # Generate branded video filename
    base_name = os.path.splitext(os.path.basename(final_video_path))[0]
    branded_filename = f"{base_name}_branded.mp4"
    branded_path = os.path.join(project_path, branded_filename)
    
    # Apply watermark with default settings (bottom-right, 30% opacity, 150px wide)
    return add_logo_watermark(
        input_video_path=final_video_path,
        logo_path=logo_path,
        output_path=branded_path,
        position="bottom-right",
        opacity=0.3,
        scale=150
    )