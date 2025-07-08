"""
Video Branding Module - Clean implementation for intro/outro slides.
"""

import os
import json
import subprocess
from typing import Optional, Tuple
from openai import OpenAI


def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    """Get video dimensions using ffprobe."""
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
                    return width, height
        return 720, 1280
    except Exception:
        return 720, 1280


def generate_title(idea: str, script: str) -> str:
    """Generate video title using OpenAI."""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        prompt = f"""Create a short video title for:
Idea: {idea}
Script: {script[:200]}...

Requirements:
- Maximum 4 words (to fit on slide)
- Educational tone
- Clear and engaging
- No quotes or punctuation

Return only the title."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15,
            temperature=0.7
        )
        
        title = response.choices[0].message.content.strip().strip('"\'.,!?')
        
        # Smart truncation if still too long
        words = title.split()
        if len(words) > 4:
            title = ' '.join(words[:4])
        
        return title
    except Exception:
        return "Stay Safe Online"


def create_intro_slide(title: str, logo_path: str, output_path: str, width: int, height: int) -> Optional[str]:
    """Create intro slide: logo first, then 'KiaOra presents', then title."""
    if not os.path.exists(logo_path):
        return None
    
    # Clean title text - remove special characters that break FFmpeg
    title_clean = title.replace("'", "").replace('"', "").replace(":", "").replace(";", "")
    
    # Smart text wrapping for title
    words = title_clean.split()
    if len(words) > 3:  # Only wrap if really long
        # Split into two lines for better fit - proper FFmpeg line break
        mid = len(words) // 2
        title_line1 = ' '.join(words[:mid])
        title_line2 = ' '.join(words[mid:])
        title_text = f"{title_line1}\\\\n{title_line2}"  # Double backslash for FFmpeg
    else:
        title_text = title_clean
    
    # Size calculations with smart font sizing
    logo_size = min(width, height) // 3
    title_font = min(height // 15, width // 20)  # Adaptive font size
    presents_font = height // 20
    
    # Positioning
    logo_x = (width - logo_size) // 2
    logo_y = height // 6
    presents_y = height // 2
    title_y = int(height * 0.75)
    
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi", "-i", f"color=white:size={width}x{height}:duration=4",
            "-i", logo_path,
            "-filter_complex",
            # KiaOra presents text with fade-in effect (0-1 seconds)
            f"[0:v]drawtext=text='KiaOra presents':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={presents_font}:fontcolor=black:"
            f"alpha='if(lt(t,1),t,1)':"
            f"x=(w-text_w)/2:y={presents_y}[with_presents];"
            
            # Title text with fade-in effect (0-1 seconds)
            f"[with_presents]drawtext=text='{title_text}':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={title_font}:fontcolor=black:"
            f"alpha='if(lt(t,1),t,1)':"
            f"x=(w-text_w)/2:y={title_y}[with_title];"
            
            # Scale logo and overlay (no fade - keeps logo visible)
            f"[1:v]scale={logo_size}:{logo_size}[logo_scaled];"
            f"[with_title][logo_scaled]overlay=x={logo_x}:y={logo_y}",
            
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", "3", "-y", output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"Intro slide FFmpeg error: {result.stderr}")
            print(f"Title text was: '{title_text}'")
        return output_path if result.returncode == 0 else None
    except Exception as e:
        print(f"Intro slide exception: {e}")
        return None


def create_outro_slide(logo_path: str, output_path: str, width: int, height: int) -> Optional[str]:
    """Create outro slide with logo and 'Follow us for more'."""
    if not os.path.exists(logo_path):
        return None
    
    # No text wrapping for outro - keep it simple to avoid formatting issues
    text_display = "Follow us for more"
    
    logo_size = min(width, height) // 3
    font_size = min(height // 18, width // 25)  # Smaller adaptive font
    
    logo_x = (width - logo_size) // 2
    logo_y = height // 3
    text_y = int(height * 0.75)  # Move text lower to fit better
    
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi", "-i", f"color=white:size={width}x{height}:duration=3",
            "-i", logo_path,
            "-filter_complex",
            # Text with fade-in effect (0-1 seconds)
            f"[0:v]drawtext=text='{text_display}':"
            f"fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"fontsize={font_size}:fontcolor=black:"
            f"alpha='if(lt(t,1),t,1)':"
            f"x=(w-text_w)/2:y={text_y}[with_text];"
            
            # Scale logo and overlay (no fade - keeps logo visible)
            f"[1:v]scale={logo_size}:{logo_size}[logo_scaled];"
            f"[with_text][logo_scaled]overlay=x={logo_x}:y={logo_y}",
            
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", "3", "-y", output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        return output_path if result.returncode == 0 else None
    except Exception:
        return None


def concatenate_videos(video_list: list, output_path: str) -> Optional[str]:
    """Concatenate videos with audio preservation and smooth transitions."""
    try:
        # Verify all input files exist
        for video in video_list:
            if not os.path.exists(video):
                print(f"ERROR: Input video not found: {video}")
                return None
        
        print(f"Concatenating {len(video_list)} videos...")
        
        if len(video_list) == 3:  # intro + main + outro
            # Add silent audio to intro and outro first
            intro_with_audio = output_path.replace('.mp4', '_intro_audio.mp4')
            outro_with_audio = output_path.replace('.mp4', '_outro_audio.mp4')
            
            print("Adding silent audio to intro...")
            intro_result = subprocess.run([
                "ffmpeg", "-i", video_list[0], 
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", intro_with_audio
            ], capture_output=True, text=True, timeout=60)
            
            if intro_result.returncode != 0:
                print(f"Failed to add audio to intro: {intro_result.stderr}")
                return None
            
            print("Adding silent audio to outro...")
            outro_result = subprocess.run([
                "ffmpeg", "-i", video_list[2],
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", 
                "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", outro_with_audio
            ], capture_output=True, text=True, timeout=60)
            
            if outro_result.returncode != 0:
                print(f"Failed to add audio to outro: {outro_result.stderr}")
                return None
            
            # Now concatenate all three with fade transitions
            print("Concatenating intro + main + outro with smooth fade transitions...")
            
            # Get video durations for proper fade timing
            intro_duration = 3.0  # intro slide duration
            
            # Get main video duration
            probe_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", 
                        "-of", "csv=p=0", video_list[1]]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            try:
                main_duration = float(probe_result.stdout.strip())
            except:
                main_duration = 10.0  # fallback
            
            outro_duration = 3.0  # outro slide duration
            fade_duration = 0.5  # 0.5 second cross-fade
            
            # Create smooth cross-fade transitions between videos
            concat_result = subprocess.run([
                "ffmpeg", "-i", intro_with_audio, "-i", video_list[1], "-i", outro_with_audio,
                "-filter_complex", 
                f"[0:v]fade=out:st={intro_duration-fade_duration}:d={fade_duration}[v0];"
                f"[1:v]fade=in:st=0:d={fade_duration},fade=out:st={main_duration-fade_duration}:d={fade_duration}[v1];"
                f"[2:v]fade=in:st=0:d={fade_duration}[v2];"
                f"[v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[v][a]",
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac",
                "-pix_fmt", "yuv420p", "-y", output_path
            ], capture_output=True, text=True, timeout=120)
            
            # Cleanup temp files
            try:
                if os.path.exists(intro_with_audio):
                    os.unlink(intro_with_audio)
                    print(f"Cleaned up: {intro_with_audio}")
                if os.path.exists(outro_with_audio):
                    os.unlink(outro_with_audio)
                    print(f"Cleaned up: {outro_with_audio}")
            except Exception as e:
                print(f"Warning: Could not clean up temp files: {e}")
            
            if concat_result.returncode != 0:
                print(f"FFmpeg concatenation error: {concat_result.stderr}")
                return None
                
        else:
            # Fallback for other cases - direct concatenation
            ffmpeg_cmd = ["ffmpeg"]
            for video in video_list:
                ffmpeg_cmd.extend(["-i", video])
            
            ffmpeg_cmd.extend([
                "-filter_complex", f"concat=n={len(video_list)}:v=1:a=1[v][a]",
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac",
                "-pix_fmt", "yuv420p", "-y", output_path
            ])
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"FFmpeg concatenation error: {result.stderr}")
                return None
        
        return output_path if os.path.exists(output_path) else None
        
    except Exception as e:
        print(f"Concatenation exception: {e}")
        return None


def add_branding(main_video_path: str, idea: str, script: str, logo_path: str, output_dir: str) -> Optional[str]:
    """
    Main branding workflow:
    1. Generate title
    2. Get video dimensions
    3. Create intro slide
    4. Create outro slide
    5. Concatenate: intro + main + outro
    """
    if not os.path.exists(main_video_path) or not os.path.exists(logo_path):
        print(f"ERROR: Missing files - video: {os.path.exists(main_video_path)}, logo: {os.path.exists(logo_path)}")
        return None
    
    try:
        # Try MoviePy approach first (better animations and transitions)
        from . import video_transitions
        
        print("Using MoviePy for professional animations and smooth transitions...")
        moviepy_result = video_transitions.create_branded_video_moviepy(
            main_video_path, idea, script, logo_path, output_dir
        )
        
        if moviepy_result:
            print(f"SUCCESS: Professional branded video created with MoviePy at {moviepy_result}")
            return moviepy_result
        else:
            print("MoviePy approach failed, falling back to FFmpeg method...")
    
    except Exception as e:
        print(f"MoviePy error: {e}, falling back to FFmpeg method...")
    
    # Fallback to original FFmpeg approach
    try:
        # Get dimensions and generate title
        width, height = get_video_dimensions(main_video_path)
        print(f"Video dimensions: {width}x{height}")
        
        title = generate_title(idea, script)
        print(f"Generated title: '{title}'")
        
        # Create slide paths
        intro_path = os.path.join(output_dir, "intro.mp4")
        outro_path = os.path.join(output_dir, "outro.mp4")
        final_path = os.path.join(output_dir, "branded_video.mp4")
        
        # Create slides
        print("Creating intro slide...")
        if not create_intro_slide(title, logo_path, intro_path, width, height):
            print("ERROR: Failed to create intro slide")
            return None
        print(f"Intro slide created: {intro_path}")
        
        print("Creating outro slide...")
        if not create_outro_slide(logo_path, outro_path, width, height):
            print("ERROR: Failed to create outro slide")
            return None
        print(f"Outro slide created: {outro_path}")
        
        # Concatenate
        print("Concatenating videos...")
        video_list = [intro_path, main_video_path, outro_path]
        result = concatenate_videos(video_list, final_path)
        if result:
            print(f"Final video created: {result}")
        else:
            print("ERROR: Failed to concatenate videos")
        return result
        
    except Exception as e:
        print(f"ERROR: Exception in add_branding: {e}")
        return None