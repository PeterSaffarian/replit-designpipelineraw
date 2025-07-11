# factory/runway.py
# A Python library for interacting with the Runway ML API.
# This file centralizes API calls and will be imported by video_gen.py.

import os
import base64
import time
import cv2
import requests
import tempfile
from typing import List, Dict, Optional, cast, Literal
from runwayml import RunwayML

# --- Configuration ---
API_KEY = os.environ.get("RUNWAY_API_KEY", "").strip()

def _get_client() -> RunwayML:
    """Initialize and return Runway client."""
    if not API_KEY:
        raise ValueError("Runway API key is not configured. Set RUNWAY_API_KEY environment variable.")
    return RunwayML(api_key=API_KEY)

def _download_video(url: str, local_path: str) -> bool:
    """Download video from URL to local path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"RUNWAY: Error downloading video from {url}: {e}")
        return False

def _extract_last_frame(video_path: str) -> Optional[str]:
    """
    Extract the last frame from a video file and return path to saved image.
    Returns None if extraction fails.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"RUNWAY: Could not open video file: {video_path}")
            return None
        
        # Get total frame count
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            print(f"RUNWAY: Invalid frame count in video: {video_path}")
            cap.release()
            return None
        
        # Jump to the last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print(f"RUNWAY: Could not read last frame from video: {video_path}")
            return None
        
        # Save frame as temporary image
        temp_dir = os.path.dirname(video_path)
        frame_filename = f"last_frame_{int(time.time())}.jpg"
        frame_path = os.path.join(temp_dir, frame_filename)
        
        success = cv2.imwrite(frame_path, frame)
        if not success:
            print(f"RUNWAY: Could not save frame to: {frame_path}")
            return None
        
        print(f"RUNWAY: Extracted last frame to: {frame_path}")
        return frame_path
        
    except Exception as e:
        print(f"RUNWAY: Error extracting last frame from {video_path}: {e}")
        return None

def _image_to_data_uri(image_path: str) -> Optional[str]:
    """Convert local image file to data URI format for Runway API."""
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine MIME type based on file extension
        ext = os.path.splitext(image_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif ext == '.png':
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'  # Default fallback
        
        return f"data:{mime_type};base64,{image_data}"
    except Exception as e:
        print(f"RUNWAY: Error converting image to data URI: {e}")
        return None

def _convert_aspect_ratio(aspect_ratio: str) -> str:
    """Convert aspect ratio format to Runway-compatible resolution."""
    # Runway's supported ratios based on their API
    aspect_mapping = {
        "16:9": "1280:720",
        "9:16": "720:1280", 
        "1:1": "960:960",
        "4:3": "1104:832",
        "3:4": "832:1104"
    }
    
    # Valid Runway ratios
    valid_ratios = ["1280:720", "720:1280", "1104:832", "832:1104", "960:960", "1584:672", "1280:768", "768:1280"]
    
    # If already valid, return as-is
    if aspect_ratio in valid_ratios:
        return aspect_ratio
    
    # Map common ratios to valid ones
    return aspect_mapping.get(aspect_ratio, "1280:720")

def image_to_video(image_path: str, prompt: str, model_name: str = "gen4_turbo", 
                  duration: int = 5, aspect_ratio: str = "16:9") -> Optional[Dict]:
    """
    Generates a single video segment from an image using Runway.
    
    Args:
        image_path (str): Path to the input image file
        prompt (str): Text prompt to guide video generation
        model_name (str): Runway model to use (gen4_turbo, gen3a_turbo)
        duration (int): Duration in seconds (5 or 10)
        aspect_ratio (str): Aspect ratio or resolution
    
    Returns:
        Dict with video information or None on failure
    """
    try:
        print(f"RUNWAY: Starting image-to-video generation...")
        print(f"   Image: {image_path}")
        print(f"   Prompt: {prompt}")
        print(f"   Model: {model_name}")
        print(f"   Duration: {duration}s")
        
        client = _get_client()
        
        # Convert image to data URI
        prompt_image = _image_to_data_uri(image_path)
        if not prompt_image:
            print("RUNWAY: Failed to convert image to data URI")
            return None
        
        # Convert aspect ratio and validate
        ratio = _convert_aspect_ratio(aspect_ratio)
        print(f"   Ratio: {ratio}")
        
        # Validate model name
        valid_models = ["gen4_turbo", "gen3a_turbo"]
        if model_name not in valid_models:
            print(f"RUNWAY: Invalid model {model_name}, using gen4_turbo")
            model_name = "gen4_turbo"
        
        # Validate duration
        valid_durations = [5, 10]
        if duration not in valid_durations:
            print(f"RUNWAY: Invalid duration {duration}, using 5 seconds")
            duration = 5
        
        # Generate video with proper type casting
        result = client.image_to_video.create(
            model=cast(Literal["gen3a_turbo", "gen4_turbo"], model_name),
            prompt_image=prompt_image,
            prompt_text=prompt,
            ratio=cast(Literal["1280:720", "720:1280", "1104:832", "832:1104", "960:960", "1584:672", "1280:768", "768:1280"], ratio),
            duration=cast(Literal[5, 10], duration)
        )
        
        # Wait for completion
        print("RUNWAY: Waiting for video generation to complete...")
        output = result.wait_for_task_output()
        
        # Extract URL from the output - handle different response formats
        if output:
            video_url = None
            
            # Try different ways to access the URL based on Runway's response format
            try:
                # Method 1: Direct url attribute
                if hasattr(output, 'url'):
                    video_url = getattr(output, 'url')  # type: ignore
                # Method 2: Output list with URL
                elif hasattr(output, 'output') and output.output:  # type: ignore
                    if isinstance(output.output, list) and len(output.output) > 0:  # type: ignore
                        video_url = output.output[0] if isinstance(output.output[0], str) else None  # type: ignore
                    elif isinstance(output.output, str):  # type: ignore
                        video_url = output.output  # type: ignore
                # Method 3: Try as dictionary
                elif isinstance(output, dict):
                    video_url = output.get('url') or output.get('output')
                # Method 4: String conversion
                else:
                    output_str = str(output)
                    if output_str.startswith('http'):
                        video_url = output_str
            except Exception as attr_error:
                print(f"RUNWAY: Error accessing output attributes: {attr_error}")
            
            if video_url and isinstance(video_url, str) and video_url.startswith('http'):
                print(f"RUNWAY: Video generated successfully: {video_url}")
                return {
                    'id': result.id,
                    'url': video_url,
                    'status': 'completed'
                }
        
        print("RUNWAY: Video generation completed but no URL found in response")
        print(f"RUNWAY: Output type: {type(output)}")
        print(f"RUNWAY: Output content: {output}")
        return None
            
    except Exception as e:
        print(f"RUNWAY: Error in image_to_video: {e}")
        import traceback
        print(f"RUNWAY: Traceback: {traceback.format_exc()}")
        return None

def generate_extended_video(image_path: str, prompts: List[str], model_name: str = "gen4_turbo",
                          segment_durations: Optional[List[int]] = None, segment_duration: int = 5, 
                          aspect_ratio: str = "16:9", temp_dir: Optional[str] = None) -> Optional[Dict]:
    """
    Generate an extended video by chaining multiple segments with frame extraction.
    
    Args:
        image_path (str): Path to the initial reference image
        prompts (List[str]): List of prompts for each segment
        model_name (str): Runway model to use
        segment_durations (List[int], optional): List of durations for each segment. If None, uses segment_duration for all.
        segment_duration (int): Default duration for segments when segment_durations is not provided
        aspect_ratio (str): Video aspect ratio
        temp_dir (str): Directory for temporary files (optional)
    
    Returns:
        Dict with final video information or None on failure
    """
    try:
        if not prompts:
            print("RUNWAY: No prompts provided for video generation")
            return None
        
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
        
        print(f"RUNWAY: Starting extended video generation with {len(prompts)} segments")
        print(f"   Temporary directory: {temp_dir}")
        
        segments = []
        current_reference = image_path
        
        for i, prompt in enumerate(prompts):
            print(f"\n--- RUNWAY: Generating segment {i+1}/{len(prompts)} ---")
            
            # Generate current segment
            segment_result = image_to_video(
                image_path=current_reference,
                prompt=prompt,
                model_name=model_name,
                duration=segment_duration,
                aspect_ratio=aspect_ratio
            )
            
            if not segment_result:
                print(f"RUNWAY: Failed to generate segment {i+1}")
                return None
            
            # Download the segment
            segment_filename = f"segment_{i:03d}.mp4"
            segment_path = os.path.join(temp_dir, segment_filename)
            
            if not _download_video(segment_result['url'], segment_path):
                print(f"RUNWAY: Failed to download segment {i+1}")
                return None
            
            segments.append({
                'path': segment_path,
                'url': segment_result['url'],
                'id': segment_result['id']
            })
            
            # For all segments except the last, extract the final frame for next reference
            if i < len(prompts) - 1:
                print(f"RUNWAY: Extracting last frame from segment {i+1} for next reference")
                last_frame_path = _extract_last_frame(segment_path)
                
                if not last_frame_path:
                    print(f"RUNWAY: Failed to extract last frame from segment {i+1}")
                    return None
                
                current_reference = last_frame_path
                print(f"RUNWAY: Using frame as reference for segment {i+2}: {current_reference}")
        
        print(f"\nRUNWAY: All {len(segments)} segments generated successfully")
        
        # Return information about the segmented video
        # The actual concatenation will be handled by branding.py
        return {
            'segments': segments,
            'total_segments': len(segments),
            'temp_dir': temp_dir,
            'segment_duration': segment_duration,
            'status': 'completed'
        }
        
    except Exception as e:
        print(f"RUNWAY: Error in generate_extended_video: {e}")
        return None

def cleanup_temp_files(temp_dir: str, keep_final: bool = True):
    """Clean up temporary files from video generation."""
    try:
        if not os.path.exists(temp_dir):
            return
        
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            
            # Keep final concatenated video if requested
            if keep_final and filename == "final_video.mp4":
                continue
            
            # Remove temporary files
            if filename.startswith(("segment_", "last_frame_")) or filename.endswith(".txt"):
                try:
                    os.remove(file_path)
                    print(f"RUNWAY: Cleaned up temporary file: {filename}")
                except Exception as e:
                    print(f"RUNWAY: Could not remove {filename}: {e}")
        
    except Exception as e:
        print(f"RUNWAY: Error during cleanup: {e}")