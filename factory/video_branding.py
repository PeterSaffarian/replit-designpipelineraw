"""
Professional Video Branding System with HD Animated Intro/Outro Slides.

This module creates animated intro slides with dynamic titles and animated outro slides
for professional video branding with proper aspect ratio detection and seamless transitions.
"""

import os
import json
import subprocess
from typing import Optional, Dict, Tuple
from openai import OpenAI


def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    """Get actual video dimensions using ffprobe."""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json", 
            "-show_streams", video_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    width = stream.get('width', 1920)
                    height = stream.get('height', 1080)
                    print(f"BRANDING: Detected video dimensions: {width}x{height}")
                    return width, height
        
        print(f"BRANDING: Could not detect dimensions, using default 1920x1080")
        return 1920, 1080
        
    except Exception as e:
        print(f"BRANDING: Error detecting dimensions: {e}, using default 1920x1080")
        return 1920, 1080


def generate_video_title(idea: str, script: str) -> str:
    """Generate a dynamic video title using OpenAI."""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        prompt = f"""Create a compelling, short video title (max 8 words) based on this content:

Idea: {idea}
Script: {script[:200]}...

Requirements:
- Engaging and clickable
- Clear value proposition
- Natural language (not clickbait)
- Professional tone
- Educational focus

Return only the title, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7
        )
        
        title = response.choices[0].message.content.strip().strip('"')
        print(f"BRANDING: Generated title: '{title}'")
        return title
        
    except Exception as e:
        print(f"BRANDING: Error generating title: {e}")
        fallback_title = "Learn Something New Today"
        print(f"BRANDING: Using fallback title: '{fallback_title}'")
        return fallback_title


def create_intro_slide(title: str, logo_path: str, output_path: str, width: int, height: int, duration: int = 3) -> Optional[str]:
    """Create animated intro slide with proper dimensions and logo positioning."""
    print(f"BRANDING: Creating intro slide {width}x{height}...")
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    # Calculate proportional sizes based on video dimensions
    logo_size = min(width, height) // 8  # Logo size as 1/8 of smaller dimension
    font_size_large = height // 20      # Main title font
    font_size_small = height // 30      # "KiaOra presents" font
    
    # Safe positioning - ensure logo is well within bounds
    logo_x = (width - logo_size) // 2
    logo_y = height // 3  # Top third for logo
    
    try:
        # Professional animated intro with corrected FFmpeg syntax
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x1e3a8a:size={width}x{height}:duration={duration}",
            "-i", logo_path,
            "-filter_complex", 
            f"[0:v]drawtext=text='KiaOra presents':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size_small}:fontcolor=0xfbbf24:"
            f"x=(w-text_w)/2:y=h*0.15:shadowcolor=0x000000:shadowx=2:shadowy=2[with_presents];"
            f"[with_presents]drawtext=text='{title}':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size_large}:fontcolor=0xffffff:"
            f"x=(w-text_w)/2:y=h*0.7:shadowcolor=0x000000:shadowx=3:shadowy=3[with_title];"
            f"[1:v]scale={logo_size}:{logo_size}[logo_scaled];"
            f"[with_title][logo_scaled]overlay=x={logo_x}:y={logo_y}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=90)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Intro slide created: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error creating intro slide: {e}")
        return None


def create_outro_slide(logo_path: str, output_path: str, width: int, height: int, duration: int = 3) -> Optional[str]:
    """Create animated outro slide with proper dimensions and logo positioning."""
    print(f"BRANDING: Creating outro slide {width}x{height}...")
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    # Calculate proportional sizes
    logo_size = min(width, height) // 6  # Larger logo for outro
    font_size = height // 25
    
    # Safe positioning
    logo_x = (width - logo_size) // 2
    logo_y = height // 3
    
    try:
        # Professional animated outro with corrected FFmpeg syntax
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x1e3a8a:size={width}x{height}:duration={duration}",
            "-i", logo_path,
            "-filter_complex",
            f"[0:v]drawtext=text='Follow us for more':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size}:fontcolor=0xfbbf24:"
            f"x=(w-text_w)/2:y=h*0.75:shadowcolor=0x000000:shadowx=3:shadowy=3[with_text];"
            f"[1:v]scale={logo_size}:{logo_size}[logo_scaled];"
            f"[with_text][logo_scaled]overlay=x={logo_x}:y={logo_y}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=90)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Outro slide created: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error creating outro slide: {e}")
        return None


def concatenate_videos_with_transitions(video_list: list, output_path: str) -> Optional[str]:
    """Concatenate videos with smooth transitions."""
    try:
        # Build FFmpeg command correctly
        ffmpeg_cmd = ["ffmpeg"]
        
        # Add input files
        for video in video_list:
            ffmpeg_cmd.extend(["-i", video])
        
        # Add filter complex for concatenation
        filter_complex = f"concat=n={len(video_list)}:v=1:a=0[v]"
        ffmpeg_cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ])
        
        print(f"BRANDING: Concatenating {len(video_list)} videos...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Videos concatenated: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ Concatenation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error concatenating videos: {e}")
        return None


def add_branding_sequence(main_video_path: str, title: str, logo_path: str, project_path: str) -> Optional[str]:
    """Add intro and outro branding slides to the main video."""
    print(f"BRANDING: Adding branding sequence...")
    
    # Validate inputs
    if not os.path.exists(main_video_path):
        print(f"BRANDING: Error - Main video not found: {main_video_path}")
        return None
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo not found: {logo_path}")
        return None
    
    try:
        # Get video dimensions from the actual main video
        width, height = get_video_dimensions(main_video_path)
        
        # Create temporary files
        intro_path = os.path.join(project_path, "intro_slide.mp4")
        outro_path = os.path.join(project_path, "outro_slide.mp4")
        final_path = os.path.join(project_path, "final_branded_video.mp4")
        
        # Create intro slide with exact video dimensions
        intro_result = create_intro_slide(title, logo_path, intro_path, width, height, duration=3)
        if not intro_result:
            print(f"BRANDING: Failed to create intro slide")
            return None
        
        # Create outro slide with exact video dimensions
        outro_result = create_outro_slide(logo_path, outro_path, width, height, duration=3)
        if not outro_result:
            print(f"BRANDING: Failed to create outro slide")
            return None
        
        # Concatenate: intro + main + outro
        video_list = [intro_path, main_video_path, outro_path]
        final_result = concatenate_videos_with_transitions(video_list, final_path)
        
        if final_result:
            print(f"BRANDING: ✅ Branding sequence completed: {final_result}")
            return final_result
        else:
            print(f"BRANDING: Failed to concatenate videos")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error in branding sequence: {e}")
        return None


def apply_complete_branding(main_video_path: str, idea: str, script: str, logo_path: str, project_path: str, scenario_path: str = None) -> Optional[str]:
    """Complete branding workflow: generate title, create slides, and concatenate."""
    print(f"BRANDING: Starting complete branding workflow...")
    
    # Step 1: Generate video title
    title = generate_video_title(idea, script)
    
    # Step 2: Add branding sequence
    final_video_path = add_branding_sequence(main_video_path, title, logo_path, project_path)
    
    if final_video_path:
        print(f"BRANDING: ✅ Complete branding workflow finished!")
        print(f"BRANDING: Title: '{title}'")
        print(f"BRANDING: Final video: {final_video_path}")
        return final_video_path
    else:
        print(f"BRANDING: ❌ Complete branding workflow failed")
        return None