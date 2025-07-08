"""
Professional Video Branding System with Stunning HD Animated Intro/Outro Slides.

Creates beautiful, animated intro/outro slides with proper text fitting, large logos,
smooth animations, and professional design following the aesthetic guide.
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
        
        print(f"BRANDING: Could not detect dimensions, using default 720x1280")
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
        fallback_title = "Learn Something New"
        print(f"BRANDING: Using fallback title: '{fallback_title}'")
        return fallback_title


def create_stunning_intro_slide(title: str, logo_path: str, output_path: str, width: int, height: int, duration: int = 4) -> Optional[str]:
    """Create stunning animated intro slide following the aesthetic guide."""
    print(f"BRANDING: Creating stunning intro slide {width}x{height}...")
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    # Calculate responsive sizes - much larger logo and proper text sizing
    logo_size = min(width, height) // 3  # Much larger logo (1/3 of smaller dimension)
    font_size_title = height // 12       # Larger title font
    font_size_presents = height // 18    # Larger "presents" font
    
    # Beautiful positioning following aesthetic guide
    logo_x = (width - logo_size) // 2
    logo_y = height // 4  # Upper area for logo
    
    try:
        # Create stunning ANIMATED intro with working FFmpeg syntax
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0xb8a4ff:size={width}x{height}:duration={duration}",  # Beautiful light purple
            "-i", logo_path,
            "-filter_complex", 
            # Beautiful gradient background with animated waves
            f"[0:v]geq=r='180+40*sin(Y/40+T*2)':g='164+40*sin(Y/40+T*2)':b='255+20*sin(Y/40+T*2)'[gradient];"
            
            # ANIMATED "KiaOra presents" with slide down effect
            f"[gradient]drawtext=text='KiaOra presents':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size_presents}:fontcolor=0x2d1b69:"
            f"x=(w-text_w)/2:y='h*0.15-30+30*if(lt(t,1),t,1)':"  # Slide down
            f"shadowcolor=0x000000:shadowx=2:shadowy=2[with_presents];"
            
            # ANIMATED main title with slide up effect
            f"[with_presents]drawtext=text='{title}':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size_title}:fontcolor=0x000000:"
            f"x=(w-text_w)/2:y='h*0.65+50*max(0,1-t/2)':"  # Slide up
            f"shadowcolor=0x333333:shadowx=2:shadowy=2:"
            f"box=1:boxcolor=0xffffff@0.9:boxborderw=15[with_title];"
            
            # ANIMATED large logo with position movement
            f"[1:v]scale={logo_size}:{logo_size}[logo_base];"
            f"[with_title][logo_base]overlay=x={logo_x}:y='320+20*sin(2*t)'",  # Gentle float animation
            
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Stunning intro slide created: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error creating intro slide: {e}")
        return None


def create_stunning_outro_slide(logo_path: str, output_path: str, width: int, height: int, duration: int = 4) -> Optional[str]:
    """Create stunning animated outro slide following the aesthetic guide."""
    print(f"BRANDING: Creating stunning outro slide {width}x{height}...")
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    # Large logo and proper text sizing
    logo_size = min(width, height) // 3  # Large logo
    font_size = height // 15
    
    # Centered positioning
    logo_x = (width - logo_size) // 2
    logo_y = height // 3
    
    try:
        # Create stunning ANIMATED outro with working FFmpeg syntax
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0xb8a4ff:size={width}x{height}:duration={duration}",  # Same beautiful purple
            "-i", logo_path,
            "-filter_complex",
            # Beautiful gradient background matching intro
            f"[0:v]geq=r='180+40*sin(Y/40+T*2)':g='164+40*sin(Y/40+T*2)':b='255+20*sin(Y/40+T*2)'[gradient];"
            
            # ANIMATED "Follow us for more" with bounce effect
            f"[gradient]drawtext=text='Follow us for more':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size}:fontcolor=0x2d1b69:"
            f"x=(w-text_w)/2:y='h*0.75+15*sin(6*t)':"  # Bounce animation
            f"shadowcolor=0x333333:shadowx=2:shadowy=2:"
            f"box=1:boxcolor=0xffffff@0.9:boxborderw=15[with_text];"
            
            # ANIMATED logo with rotation effect
            f"[1:v]scale={logo_size}:{logo_size}[logo_base];"
            f"[logo_base]rotate='sin(t*2)*PI/12'[logo_rotating];"
            f"[with_text][logo_rotating]overlay=x={logo_x}:y={logo_y}",
            
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Stunning outro slide created: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error creating outro slide: {e}")
        return None


def concatenate_videos_with_transitions(video_list: list, output_path: str) -> Optional[str]:
    """Concatenate videos with smooth crossfade transitions."""
    try:
        print(f"BRANDING: Concatenating {len(video_list)} videos with transitions...")
        
        # Build FFmpeg command for smooth concatenation
        ffmpeg_cmd = ["ffmpeg"]
        
        # Add all input files
        for video in video_list:
            ffmpeg_cmd.extend(["-i", video])
        
        # Create smooth crossfade transitions between segments
        if len(video_list) == 3:  # intro + main + outro
            filter_complex = (
                "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=3.5[v01];"
                "[v01][2:v]xfade=transition=fade:duration=0.5:offset=0[v]"
            )
        else:
            # Fallback to simple concatenation
            filter_complex = f"concat=n={len(video_list)}:v=1:a=0[v]"
        
        ffmpeg_cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ])
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Videos concatenated with transitions: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ Concatenation failed, trying simple concat: {result.stderr}")
            
            # Fallback to simple concatenation without transitions
            ffmpeg_cmd_simple = ["ffmpeg"]
            for video in video_list:
                ffmpeg_cmd_simple.extend(["-i", video])
            
            ffmpeg_cmd_simple.extend([
                "-filter_complex", f"concat=n={len(video_list)}:v=1:a=0[v]",
                "-map", "[v]",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-y",
                output_path
            ])
            
            result = subprocess.run(ffmpeg_cmd_simple, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print(f"BRANDING: ✅ Videos concatenated (simple): {output_path}")
                return output_path
            else:
                print(f"BRANDING: ❌ Simple concatenation also failed: {result.stderr}")
                return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error concatenating videos: {e}")
        return None


def add_stunning_branding_sequence(main_video_path: str, title: str, logo_path: str, project_path: str) -> Optional[str]:
    """Add stunning intro and outro branding slides to the main video."""
    print(f"BRANDING: Adding stunning branding sequence...")
    
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
        intro_path = os.path.join(project_path, "stunning_intro.mp4")
        outro_path = os.path.join(project_path, "stunning_outro.mp4")
        final_path = os.path.join(project_path, "final_branded_video.mp4")
        
        # Create stunning intro slide with exact video dimensions
        intro_result = create_stunning_intro_slide(title, logo_path, intro_path, width, height, duration=4)
        if not intro_result:
            print(f"BRANDING: Failed to create stunning intro slide")
            return None
        
        # Create stunning outro slide with exact video dimensions
        outro_result = create_stunning_outro_slide(logo_path, outro_path, width, height, duration=4)
        if not outro_result:
            print(f"BRANDING: Failed to create stunning outro slide")
            return None
        
        # Concatenate: intro + main + outro with smooth transitions
        video_list = [intro_path, main_video_path, outro_path]
        final_result = concatenate_videos_with_transitions(video_list, final_path)
        
        if final_result:
            print(f"BRANDING: ✅ Stunning branding sequence completed!")
            print(f"BRANDING: Final video: {final_result}")
            return final_result
        else:
            print(f"BRANDING: Failed to concatenate videos")
            return None
            
    except Exception as e:
        print(f"BRANDING: ❌ Error in branding sequence: {e}")
        return None


def apply_complete_branding(main_video_path: str, idea: str, script: str, logo_path: str, project_path: str, scenario_path: str = None) -> Optional[str]:
    """Complete stunning branding workflow: generate title, create beautiful slides, and concatenate."""
    print(f"BRANDING: Starting complete stunning branding workflow...")
    
    # Step 1: Generate short video title (max 6 words for vertical video)
    title = generate_video_title(idea, script)
    
    # Step 2: Add stunning branding sequence
    final_video_path = add_stunning_branding_sequence(main_video_path, title, logo_path, project_path)
    
    if final_video_path:
        print(f"BRANDING: ✅ Complete stunning branding workflow finished!")
        print(f"BRANDING: Title: '{title}'")
        print(f"BRANDING: Final video: {final_video_path}")
        return final_video_path
    else:
        print(f"BRANDING: ❌ Complete branding workflow failed")
        return None