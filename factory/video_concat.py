# factory/video_concat.py
# Utility for concatenating video segments using FFmpeg

import os
import subprocess
import json
from typing import List, Optional

def get_video_info(video_path: str) -> Optional[dict]:
    """Get video codec and resolution information using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
        if video_stream:
            return {
                'codec': video_stream.get('codec_name'),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '30/1'))  # Convert fraction to float
            }
        return None
    except Exception as e:
        print(f"VIDEO_CONCAT: Error getting video info for {video_path}: {e}")
        return None

def videos_compatible(video_files: List[str]) -> bool:
    """Check if all videos have compatible properties for fast concatenation."""
    if len(video_files) < 2:
        return True
    
    first_info = get_video_info(video_files[0])
    if not first_info:
        return False
    
    for video in video_files[1:]:
        info = get_video_info(video)
        if not info:
            return False
        
        # Check key properties for compatibility
        if (info['codec'] != first_info['codec'] or 
            info['width'] != first_info['width'] or 
            info['height'] != first_info['height']):
            return False
    
    return True

def concat_videos_demuxer(video_files: List[str], output_file: str) -> bool:
    """
    Fast concatenation using concat demuxer (no re-encoding).
    Only works when videos have identical properties.
    """
    try:
        # Create file list for ffmpeg
        concat_list_path = os.path.join(os.path.dirname(output_file), 'concat_list.txt')
        
        with open(concat_list_path, 'w') as f:
            for video in video_files:
                # Use relative paths to avoid issues with special characters
                rel_path = os.path.relpath(video, os.path.dirname(concat_list_path))
                f.write(f"file '{rel_path}'\n")
        
        print(f"VIDEO_CONCAT: Using fast demuxer concatenation")
        
        # Run ffmpeg command
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite output file
            '-f', 'concat', '-safe', '0',
            '-i', concat_list_path,
            '-c', 'copy',  # Copy streams without re-encoding
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Clean up
        try:
            os.remove(concat_list_path)
        except:
            pass
        
        print(f"VIDEO_CONCAT: Successfully concatenated {len(video_files)} videos to {output_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"VIDEO_CONCAT: FFmpeg error during demuxer concatenation: {e.stderr}")
        return False
    except Exception as e:
        print(f"VIDEO_CONCAT: Error in demuxer concatenation: {e}")
        return False

def concat_videos_filter(video_files: List[str], output_file: str) -> bool:
    """
    Concatenation using concat filter (with re-encoding).
    Works with videos of different properties but slower.
    """
    try:
        print(f"VIDEO_CONCAT: Using filter concatenation (re-encoding)")
        
        # Build input arguments
        inputs = []
        for video in video_files:
            inputs.extend(['-i', video])
        
        # Build filter complex string
        filter_parts = []
        for i in range(len(video_files)):
            filter_parts.append(f'[{i}:v][{i}:a]')
        
        filter_complex = ''.join(filter_parts) + f'concat=n={len(video_files)}:v=1:a=1[outv][outa]'
        
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite output file
        ] + inputs + [
            '-filter_complex', filter_complex,
            '-map', '[outv]', '-map', '[outa]',
            '-vsync', 'vfr',  # Handle different frame rates
            '-c:v', 'libx264',  # Ensure consistent video codec
            '-c:a', 'aac',      # Ensure consistent audio codec
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"VIDEO_CONCAT: Successfully concatenated {len(video_files)} videos to {output_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"VIDEO_CONCAT: FFmpeg error during filter concatenation: {e.stderr}")
        return False
    except Exception as e:
        print(f"VIDEO_CONCAT: Error in filter concatenation: {e}")
        return False

def concatenate_videos(video_files: List[str], output_file: str, force_re_encode: bool = False) -> bool:
    """
    Smart video concatenation - uses fast method when possible, filter method when needed.
    
    Args:
        video_files (List[str]): List of video file paths to concatenate
        output_file (str): Path for the final concatenated video
        force_re_encode (bool): Force re-encoding even if videos are compatible
    
    Returns:
        bool: True if concatenation succeeded, False otherwise
    """
    try:
        if not video_files:
            print("VIDEO_CONCAT: No video files provided")
            return False
        
        if len(video_files) == 1:
            # Single file - just copy it
            import shutil
            shutil.copy2(video_files[0], output_file)
            print(f"VIDEO_CONCAT: Single file copied to {output_file}")
            return True
        
        print(f"VIDEO_CONCAT: Concatenating {len(video_files)} video files")
        
        # Check if videos are compatible for fast concatenation
        if not force_re_encode and videos_compatible(video_files):
            print("VIDEO_CONCAT: Videos are compatible - using fast concatenation")
            return concat_videos_demuxer(video_files, output_file)
        else:
            print("VIDEO_CONCAT: Videos are incompatible or re-encoding forced - using filter concatenation")
            return concat_videos_filter(video_files, output_file)
        
    except Exception as e:
        print(f"VIDEO_CONCAT: Error in concatenate_videos: {e}")
        return False

def concatenate_runway_segments(segments_info: dict, output_file: str) -> bool:
    """
    Concatenate Runway video segments into a final video.
    
    Args:
        segments_info (dict): Dictionary containing segment information from runway.py
        output_file (str): Path for the final concatenated video
    
    Returns:
        bool: True if concatenation succeeded, False otherwise
    """
    try:
        if not segments_info or 'segments' not in segments_info:
            print("VIDEO_CONCAT: Invalid segments information provided")
            return False
        
        segments = segments_info['segments']
        video_files = [segment['path'] for segment in segments if os.path.exists(segment['path'])]
        
        if not video_files:
            print("VIDEO_CONCAT: No valid segment files found")
            return False
        
        print(f"VIDEO_CONCAT: Concatenating {len(video_files)} Runway segments")
        
        success = concatenate_videos(video_files, output_file)
        
        if success:
            print(f"VIDEO_CONCAT: Runway segments successfully concatenated to {output_file}")
        
        return success
        
    except Exception as e:
        print(f"VIDEO_CONCAT: Error concatenating Runway segments: {e}")
        return False