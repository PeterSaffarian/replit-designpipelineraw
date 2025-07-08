"""
Simple but Beautiful Video Branding System with Animations.
This version prioritizes reliability while still providing beautiful results.
"""

import os
import json
import subprocess
from typing import Optional, Tuple
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
                    width = stream.get('width', 720)
                    height = stream.get('height', 1280)
                    print(f"BRANDING: Detected video dimensions: {width}x{height}")
                    return width, height
        return 720, 1280
    except Exception as e:
        print(f"BRANDING: Error detecting dimensions: {e}, using default 720x1280")
        return 720, 1280


def generate_video_title(idea: str, script: str) -> str:
    """Generate a dynamic video title using OpenAI."""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        prompt = f"""Create a compelling, short video title (max 6 words) based on this content:

Idea: {idea}
Script: {script[:200]}...

Requirements:
- Engaging and clickable
- Clear value proposition  
- Natural language (not clickbait)
- Professional tone
- Educational focus
- MAX 6 WORDS to fit on vertical video

Return only the title, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.7
        )
        
        title = response.choices[0].message.content.strip().strip('"')
        print(f"BRANDING: Generated title: '{title}'")
        return title
        
    except Exception as e:
        print(f"BRANDING: Error generating title: {e}")
        return "Learn Something New"


def create_beautiful_intro_slide(title: str, logo_path: str, output_path: str, width: int, height: int, duration: int = 4) -> Optional[str]:
    """Create beautiful animated intro slide with reliable FFmpeg syntax."""
    print(f"BRANDING: Creating beautiful intro slide {width}x{height}...")
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    # Calculate proper sizes following aesthetic guide
    logo_size = min(width, height) // 3  # Large logo (1/3 of smaller dimension)
    font_size_title = height // 10       # Proper title font
    font_size_presents = height // 16    # "presents" font
    
    # Safe positioning
    logo_x = (width - logo_size) // 2
    logo_y = height // 4
    
    try:
        # Create beautiful intro with working animations
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0xb8a4ff:size={width}x{height}:duration={duration}",  # Beautiful light purple
            "-i", logo_path,
            "-filter_complex", 
            # Beautiful animated gradient background
            f"[0:v]geq=r='180+20*sin(Y/80)':g='164+20*sin(Y/80)':b='255+10*sin(Y/80)'[gradient];"
            
            # "KiaOra presents" text with slide animation
            f"[gradient]drawtext=text='KiaOra presents':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size_presents}:fontcolor=0x2d1b69:"
            f"x=(w-text_w)/2:y='h*0.15+20*sin(2*t)':"  # Gentle float
            f"shadowcolor=0x000000:shadowx=2:shadowy=2[with_presents];"
            
            # Main title with professional styling
            f"[with_presents]drawtext=text='{title}':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size_title}:fontcolor=0x000000:"
            f"x=(w-text_w)/2:y=h*0.65:"
            f"shadowcolor=0x333333:shadowx=3:shadowy=3:"
            f"box=1:boxcolor=0xffffff@0.95:boxborderw=20[with_title];"
            
            # Large animated logo
            f"[1:v]scale={logo_size}:{logo_size}[logo_scaled];"
            f"[with_title][logo_scaled]overlay=x={logo_x}:y='320+15*sin(3*t)'",  # Float animation
            
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "24",  # Reduced framerate for stability
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Beautiful intro slide created: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error creating intro slide: {e}")
        return None


def create_beautiful_outro_slide(logo_path: str, output_path: str, width: int, height: int, duration: int = 4) -> Optional[str]:
    """Create beautiful animated outro slide."""
    print(f"BRANDING: Creating beautiful outro slide {width}x{height}...")
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    # Large logo and proper text sizing
    logo_size = min(width, height) // 3
    font_size = height // 14
    
    # Centered positioning
    logo_x = (width - logo_size) // 2
    logo_y = height // 3
    
    try:
        # Create beautiful animated outro
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0xb8a4ff:size={width}x{height}:duration={duration}",
            "-i", logo_path,
            "-filter_complex",
            # Beautiful gradient background
            f"[0:v]geq=r='180+20*sin(Y/80)':g='164+20*sin(Y/80)':b='255+10*sin(Y/80)'[gradient];"
            
            # "Follow us for more" with bounce
            f"[gradient]drawtext=text='Follow us for more':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size}:fontcolor=0x2d1b69:"
            f"x=(w-text_w)/2:y='h*0.75+10*sin(4*t)':"  # Gentle bounce
            f"shadowcolor=0x333333:shadowx=2:shadowy=2:"
            f"box=1:boxcolor=0xffffff@0.95:boxborderw=15[with_text];"
            
            # Large logo with gentle rotation
            f"[1:v]scale={logo_size}:{logo_size}[logo_base];"
            f"[logo_base]rotate='sin(t)*PI/24'[logo_rotating];"
            f"[with_text][logo_rotating]overlay=x={logo_x}:y={logo_y}",
            
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "24",
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Beautiful outro slide created: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error creating outro slide: {e}")
        return None


def concatenate_videos_simple(video_list: list, output_path: str) -> Optional[str]:
    """Concatenate videos with simple but reliable method."""
    try:
        print(f"BRANDING: Concatenating {len(video_list)} videos...")
        
        # Simple concatenation without complex transitions
        ffmpeg_cmd = ["ffmpeg"]
        for video in video_list:
            ffmpeg_cmd.extend(["-i", video])
        
        ffmpeg_cmd.extend([
            "-filter_complex", f"concat=n={len(video_list)}:v=1:a=0[v]",
            "-map", "[v]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ])
        
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


def apply_beautiful_branding(main_video_path: str, idea: str, script: str, logo_path: str, project_path: str) -> Optional[str]:
    """Complete beautiful branding workflow that works reliably."""
    print(f"BRANDING: Starting beautiful branding workflow...")
    
    if not os.path.exists(main_video_path) or not os.path.exists(logo_path):
        print(f"BRANDING: Error - Required files not found")
        return None
    
    try:
        # Get video dimensions
        width, height = get_video_dimensions(main_video_path)
        
        # Generate title
        title = generate_video_title(idea, script)
        
        # Create slides
        intro_path = os.path.join(project_path, "beautiful_intro.mp4")
        outro_path = os.path.join(project_path, "beautiful_outro.mp4")
        final_path = os.path.join(project_path, "final_beautiful_branded_video.mp4")
        
        # Create intro slide
        intro_result = create_beautiful_intro_slide(title, logo_path, intro_path, width, height)
        if not intro_result:
            return None
        
        # Create outro slide
        outro_result = create_beautiful_outro_slide(logo_path, outro_path, width, height)
        if not outro_result:
            return None
        
        # Concatenate everything
        video_list = [intro_path, main_video_path, outro_path]
        final_result = concatenate_videos_simple(video_list, final_path)
        
        if final_result:
            print(f"BRANDING: ✅ Beautiful branding completed!")
            print(f"BRANDING: Title: '{title}'")
            print(f"BRANDING: Final video: {final_result}")
            return final_result
        else:
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error in branding workflow: {e}")
        return None