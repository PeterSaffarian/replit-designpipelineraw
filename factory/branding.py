"""
Video Branding Module - Clean implementation for intro/outro slides.

Font and Size Configuration:
- You can customize fonts by changing the font paths in BRANDING_CONFIG
- Size ratios can be adjusted in the BRANDING_CONFIG dictionary  
- Positioning can be modified in the LAYOUT_CONFIG
"""

import os
import json
import subprocess
from typing import Optional, Tuple
from openai import OpenAI

# CUSTOMIZABLE BRANDING CONFIGURATION
BRANDING_CONFIG = {
    'fonts': {
        'primary': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-BoldOblique.ttf',      # Main font for titles and text
        'secondary': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',        # Backup font (lighter weight)
    },
    'size_ratios': {
        'logo_ratio': 3,            # Logo = min(width,height) / logo_ratio
        'title_height_ratio': 15,   # Title font = height / title_height_ratio  
        'title_width_ratio': 20,    # Title font = width / title_width_ratio (backup)
        'presents_ratio': 20,       # "KiaOra presents" = height / presents_ratio
        'outro_text_ratio': 25      # "Follow us" = height / outro_text_ratio
    },
    'colors': {
        'text': 'black',
        'background': 'white'
    }
}

LAYOUT_CONFIG = {
    'logo_y_ratio': 6,         # Logo Y = height / logo_y_ratio
    'presents_y_ratio': 2,     # "KiaOra presents" Y = height / presents_y_ratio  
    'title_y_ratio': 0.75,     # Title Y = height * title_y_ratio
    'outro_text_y_ratio': 0.6  # Outro text Y = height * outro_text_y_ratio
}

# ============================================================================
# AVAILABLE FONTS ON SYSTEM:
# Copy any of these paths to BRANDING_CONFIG['fonts']['primary'] or ['secondary']
# ============================================================================
#
# === SANS SERIF FONTS (Clean, Modern Look) ===
# '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'           # DejaVu Sans Regular - Clean, readable
# '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'      # DejaVu Sans Bold ⭐ RECOMMENDED - Professional, strong
#
# === SERIF FONTS (Traditional, Elegant Look) ===  
# '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'          # DejaVu Serif Regular - Classical, readable
# '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'     # DejaVu Serif Bold ⭐ GREAT FOR HEADLINES - Elegant, formal
#
# === MONOSPACE FONTS (Technical, Code-like Look) ===
# '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'       # DejaVu Sans Mono Regular - Tech, minimal
# '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'  # DejaVu Sans Mono Bold ⭐ PERFECT FOR TECH CONTENT
#
# === ITALIC/SLANTED VARIATIONS ===
# '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf'     # Mono Italic - Creative tech look
# '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-BoldOblique.ttf' # Mono Bold Italic - Strong + creative
#
# === QUICK STYLE GUIDE ===
# 🎯 Business/Professional:   DejaVu Sans Bold (current default works great)
# 🎭 Creative/Artistic:       DejaVu Serif Bold 
# 💻 Technology/Coding:       DejaVu Sans Mono Bold
# 📚 Educational/Academic:    DejaVu Serif Bold
# 🚀 Modern/Startup:         DejaVu Sans Bold
#
# === EXAMPLE USAGE ===
# For modern clean look:    BRANDING_CONFIG['fonts']['primary'] = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
# For traditional look:     BRANDING_CONFIG['fonts']['primary'] = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'  
# For technical/tech look:  BRANDING_CONFIG['fonts']['primary'] = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
# For creative tech look:   BRANDING_CONFIG['fonts']['primary'] = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-BoldOblique.ttf'
#
# === HOW TO CHANGE ===
# 1. Pick a font path from above
# 2. Update BRANDING_CONFIG['fonts']['primary'] = 'your_chosen_path'
# 3. Test with: python test_branding_workflow.py
# ============================================================================


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
- Maximum 20 characters (to fit on slide)
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
    
    # Size calculations using configuration
    logo_size = min(width, height) // BRANDING_CONFIG['size_ratios']['logo_ratio']
    title_font = min(height // BRANDING_CONFIG['size_ratios']['title_height_ratio'], 
                     width // BRANDING_CONFIG['size_ratios']['title_width_ratio'])
    presents_font = height // BRANDING_CONFIG['size_ratios']['presents_ratio']
    
    # Positioning using configuration
    logo_x = (width - logo_size) // 2
    logo_y = height // LAYOUT_CONFIG['logo_y_ratio']
    presents_y = height // LAYOUT_CONFIG['presents_y_ratio']
    title_y = int(height * LAYOUT_CONFIG['title_y_ratio'])
    
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi", "-i", f"color=white:size={width}x{height}:duration=4",
            "-i", logo_path,
            "-filter_complex",
            # KiaOra presents text with fade-in effect (0-1 seconds)
            f"[0:v]drawtext=text='KiaOra presents':"
            f"fontfile={BRANDING_CONFIG['fonts']['primary']}:"
            f"fontsize={presents_font}:fontcolor={BRANDING_CONFIG['colors']['text']}:"
            f"alpha='if(lt(t,1),t,1)':"
            f"x=(w-text_w)/2:y={presents_y}[with_presents];"
            
            # Title text with fade-in effect (0-1 seconds)
            f"[with_presents]drawtext=text='{title_text}':"
            f"fontfile={BRANDING_CONFIG['fonts']['primary']}:"
            f"fontsize={title_font}:fontcolor={BRANDING_CONFIG['colors']['text']}:"
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
    
    # Size calculations using configuration
    logo_size = min(width, height) // BRANDING_CONFIG['size_ratios']['logo_ratio']
    font_size = height // BRANDING_CONFIG['size_ratios']['outro_text_ratio']
    
    # Positioning using configuration
    logo_x = (width - logo_size) // 2
    logo_y = height // LAYOUT_CONFIG['logo_y_ratio']
    text_y = int(height * LAYOUT_CONFIG['outro_text_y_ratio'])
    
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi", "-i", f"color=white:size={width}x{height}:duration=3",
            "-i", logo_path,
            "-filter_complex",
            # Text with fade-in effect (0-1 seconds)
            f"[0:v]drawtext=text='{text_display}':"
            f"fontfile={BRANDING_CONFIG['fonts']['primary']}:"
            f"fontsize={font_size}:fontcolor={BRANDING_CONFIG['colors']['text']}:"
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
            # Get main video dimensions to use as target
            probe_cmd = ["ffprobe", "-v", "quiet", "-select_streams", "v:0", 
                        "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", video_list[1]]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            try:
                main_width, main_height = map(int, probe_result.stdout.strip().split('x'))
                target_size = f"{main_width}x{main_height}"
            except:
                target_size = "720x1280"  # fallback
            
            print(f"Scaling intro/outro to match main video: {target_size}")
            
            # Scale intro and outro to match main video, then add audio
            intro_scaled = output_path.replace('.mp4', '_intro_scaled.mp4')
            outro_scaled = output_path.replace('.mp4', '_outro_scaled.mp4')
            
            print("Scaling and adding audio to intro...")
            intro_result = subprocess.run([
                "ffmpeg", "-i", video_list[0], 
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-filter_complex", f"[0:v]scale={main_width}:{main_height}:force_original_aspect_ratio=decrease,pad={main_width}:{main_height}:(ow-iw)/2:(oh-ih)/2[v]",
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-c:a", "aac", "-shortest", "-y", intro_scaled
            ], capture_output=True, text=True, timeout=60)
            
            if intro_result.returncode != 0:
                print(f"Failed to scale intro: {intro_result.stderr}")
                return None
            
            print("Scaling and adding audio to outro...")
            outro_result = subprocess.run([
                "ffmpeg", "-i", video_list[2],
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", 
                "-filter_complex", f"[0:v]scale={main_width}:{main_height}:force_original_aspect_ratio=decrease,pad={main_width}:{main_height}:(ow-iw)/2:(oh-ih)/2[v]",
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-c:a", "aac", "-shortest", "-y", outro_scaled
            ], capture_output=True, text=True, timeout=60)
            
            if outro_result.returncode != 0:
                print(f"Failed to scale outro: {outro_result.stderr}")
                return None
            
            # Now concatenate all three with fade transitions
            print("Concatenating intro + main + outro with smooth fade transitions...")
            
            # Get actual video durations for proper fade timing
            # Get intro duration
            probe_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", 
                        "-of", "csv=p=0", intro_scaled]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            try:
                intro_duration = float(probe_result.stdout.strip())
            except:
                intro_duration = 5.0  # fallback
            
            # Get main video duration
            probe_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", 
                        "-of", "csv=p=0", video_list[1]]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            try:
                main_duration = float(probe_result.stdout.strip())
            except:
                main_duration = 10.0  # fallback
            
            # Get outro duration
            probe_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", 
                        "-of", "csv=p=0", outro_scaled]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            try:
                outro_duration = float(probe_result.stdout.strip())
            except:
                outro_duration = 5.0  # fallback
            fade_duration = 0.5  # 0.5 second cross-fade transitions
            
            # Now concatenate the scaled videos with fade transitions
            print(f"Video durations - Intro: {intro_duration:.1f}s, Main: {main_duration:.1f}s, Outro: {outro_duration:.1f}s")
            print("Concatenating scaled videos with fade transitions...")
            
            # Check if main video has audio stream
            probe_cmd = ["ffprobe", "-v", "quiet", "-select_streams", "a", "-show_entries", "stream=codec_name", "-of", "csv=p=0", video_list[1]]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            main_has_audio = bool(probe_result.stdout.strip())
            
            if main_has_audio:
                # Standard concatenation with audio from all three videos
                concat_result = subprocess.run([
                    "ffmpeg", "-i", intro_scaled, "-i", video_list[1], "-i", outro_scaled,
                    "-filter_complex", 
                    f"[0:v]fade=out:st={intro_duration-fade_duration}:d={fade_duration}[v0];"
                    f"[1:v]fade=in:st=0:d={fade_duration},fade=out:st={main_duration-fade_duration}:d={fade_duration}[v1];"
                    f"[2:v]fade=in:st=0:d={fade_duration}[v2];"
                    f"[v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac",
                    "-pix_fmt", "yuv420p", "-y", output_path
                ], capture_output=True, text=True, timeout=120)
            else:
                # Main video has no audio - use video-only concat with silent audio
                print("Main video has no audio stream - using video-only concatenation with silent audio")
                concat_result = subprocess.run([
                    "ffmpeg", "-i", intro_scaled, "-i", video_list[1], "-i", outro_scaled,
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-filter_complex", 
                    f"[0:v]fade=out:st={intro_duration-fade_duration}:d={fade_duration}[v0];"
                    f"[1:v]fade=in:st=0:d={fade_duration},fade=out:st={main_duration-fade_duration}:d={fade_duration}[v1];"
                    f"[2:v]fade=in:st=0:d={fade_duration}[v2];"
                    f"[v0][v1][v2]concat=n=3:v=1:a=0[v];"
                    f"[0:a][3:a][2:a]concat=n=3:v=0:a=1[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac",
                    "-pix_fmt", "yuv420p", "-y", output_path
                ], capture_output=True, text=True, timeout=120)
            
            # Cleanup temp files
            try:
                if os.path.exists(intro_scaled):
                    os.unlink(intro_scaled)
                    print(f"Cleaned up: {intro_scaled}")
                if os.path.exists(outro_scaled):
                    os.unlink(outro_scaled)
                    print(f"Cleaned up: {outro_scaled}")
            except Exception as e:
                print(f"Warning: Could not clean up temp files: {e}")
            
            if concat_result.returncode != 0:
                print(f"FFmpeg concatenation error: {concat_result.stderr}")
                return None
                
        else:
            # Fallback for other cases - video-only concatenation (Runway segments have no audio)
            ffmpeg_cmd = ["ffmpeg"]
            for video in video_list:
                ffmpeg_cmd.extend(["-i", video])
            
            # Use video-only concat filter since Runway videos don't have audio
            ffmpeg_cmd.extend([
                "-filter_complex", f"concat=n={len(video_list)}:v=1:a=0[v]",
                "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", output_path
            ])
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"FFmpeg concatenation error: {result.stderr}")
                return None
        
        return output_path if os.path.exists(output_path) else None
        
    except Exception as e:
        print(f"Concatenation exception: {e}")
        return None


def add_title_overlay(intro_video_path: str, title: str, output_path: str) -> Optional[str]:
    """Add title text overlay to pre-made intro video."""
    try:
        # Get video dimensions
        width, height = get_video_dimensions(intro_video_path)
        
        # Clean title text and convert to uppercase like your examples
        title_clean = title.replace("'", "").replace('"', "").replace(":", "").replace(";", "")
        title_upper = title_clean.upper()  # Match "HOW TO SPOT A SCAM" style
        
        # Smart text wrapping to maximize font size while fitting in box
        words = title_upper.split()
        
        # Intelligent line breaking for maximum readability
        if len(words) >= 4:
            # For 4+ words, try to balance lines
            mid = len(words) // 2
            title_line1 = ' '.join(words[:mid])
            title_line2 = ' '.join(words[mid:])
        elif len(words) == 3:
            # For 3 words, put 2 on first line, 1 on second
            title_line1 = ' '.join(words[:2])
            title_line2 = words[2]
        elif len(words) == 2:
            # For 2 words, each on its own line for bigger font
            title_line1 = words[0]
            title_line2 = words[1]
        else:
            # Single word stays on one line
            title_line1 = title_upper
            title_line2 = ""
        
        # Create final text with proper line breaks
        if title_line2:
            # Fix the "n" issue by using text parameter instead of embedding line breaks
            title_text = f"{title_line1}"  # We'll handle multi-line differently
            title_text_line2 = f"{title_line2}"
            use_multiline = True
        else:
            title_text = title_line1
            use_multiline = False
        
        # Even larger font size to fill the dotted box better
        title_font = min(height // 12, width // 16)  # Increased size to use available space
        
        # Position title to center within the dotted box area
        # Based on your screenshot, the box center is around 30% from top
        title_y = int(height * 0.30)
        
        # Adjust horizontal positioning - box appears to be left of center
        title_x_offset = int(width * 0.39)  # Shift left from center (50% would be center)
        
        # Get intro video duration to show text for full duration
        try:
            duration_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", intro_video_path]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, timeout=10)
            if duration_result.returncode == 0:
                intro_duration = float(duration_result.stdout.strip())
                # Show text from 1 second to end of video
                text_end_time = intro_duration
            else:
                # Fallback to 5 seconds if duration detection fails
                text_end_time = 5.0
        except:
            text_end_time = 5.0
        
        # Create FFmpeg command with proper multi-line text handling
        if use_multiline:
            # For multi-line text, use multiple drawtext filters
            line_spacing = title_font * 1.2  # 120% of font size for line spacing
            line1_y = title_y - (line_spacing // 2)  # First line above center
            line2_y = title_y + (line_spacing // 2)  # Second line below center
            
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", intro_video_path,
                "-vf",
                f"drawtext=text='{title_text}':"
                f"fontfile={BRANDING_CONFIG['fonts']['secondary']}:"
                f"fontsize={title_font}:fontcolor=white:"
                f"x={title_x_offset}-(text_w/2):y={line1_y}:"
                f"shadowcolor=black:shadowx=2:shadowy=2:"
                f"enable='between(t,1,{text_end_time})',"
                f"drawtext=text='{title_text_line2}':"
                f"fontfile={BRANDING_CONFIG['fonts']['secondary']}:"
                f"fontsize={title_font}:fontcolor=white:"
                f"x={title_x_offset}-(text_w/2):y={line2_y}:"
                f"shadowcolor=black:shadowx=2:shadowy=2:"
                f"enable='between(t,1,{text_end_time})'",
                "-c:a", "copy", "-y", output_path
            ]
        else:
            # Single line text
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", intro_video_path,
                "-vf",
                f"drawtext=text='{title_text}':"
                f"fontfile={BRANDING_CONFIG['fonts']['secondary']}:"
                f"fontsize={title_font}:fontcolor=white:"
                f"x={title_x_offset}-(text_w/2):y={title_y}:"
                f"shadowcolor=black:shadowx=2:shadowy=2:"
                f"enable='between(t,1,{text_end_time})'",
                "-c:a", "copy", "-y", output_path
            ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"Title overlay FFmpeg error: {result.stderr}")
            return None
        return output_path
    except Exception as e:
        print(f"Title overlay error: {e}")
        return None


def add_logo_watermark(video_path: str, logo_path: str, output_path: str, 
                      position: str = "top-left", opacity: float = 0.7, 
                      scale: float = 0.1) -> Optional[str]:
    """
    Add a logo watermark to a video using FFmpeg.
    
    Args:
        video_path (str): Path to the input video
        logo_path (str): Path to the logo image
        output_path (str): Path for the output video
        position (str): Logo position ("top-left", "top-right", "bottom-left", "bottom-right", "center")
        opacity (float): Logo opacity (0.0 to 1.0)
        scale (float): Logo scale relative to video width (0.05 = 5% of video width)
    
    Returns:
        str: Path to watermarked video or None on failure
    """
    if not os.path.exists(video_path) or not os.path.exists(logo_path):
        print(f"WATERMARK: Input files not found - Video: {video_path}, Logo: {logo_path}")
        return None
    
    try:
        # Get video dimensions for positioning
        width, height = get_video_dimensions(video_path)
        logo_size = int(width * scale)
        
        # Calculate position coordinates
        margin = 20  # 20px margin from edges
        positions = {
            "top-left": f"{margin}:{margin}",
            "top-right": f"main_w-overlay_w-{margin}:{margin}",
            "bottom-left": f"{margin}:main_h-overlay_h-{margin}",
            "bottom-right": f"main_w-overlay_w-{margin}:main_h-overlay_h-{margin}",
            "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2"
        }
        
        overlay_position = positions.get(position, positions["top-left"])
        
        # FFmpeg command with logo overlay
        ffmpeg_cmd = [
            "ffmpeg", "-i", video_path, "-i", logo_path,
            "-filter_complex",
            f"[1:v]scale={logo_size}:{logo_size}[logo];"
            f"[0:v][logo]overlay={overlay_position}:format=auto,format=yuv420p[v]",
            "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-c:a", "copy",
            "-y", output_path
        ]
        
        print(f"WATERMARK: Adding logo at {position} with {opacity} opacity...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"WATERMARK: FFmpeg error: {result.stderr}")
            return None
            
        print(f"WATERMARK: Successfully added logo watermark: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"WATERMARK: Error adding logo watermark: {e}")
        return None


def add_branding(main_video_path: str, idea: str, script: str, intro_video_path: str, outro_video_path: str, output_dir: str) -> Optional[str]:
    """
    Main branding workflow with pre-made videos:
    1. Generate title using OpenAI
    2. Add title overlay to intro video
    3. Concatenate: intro_with_title + main + outro
    """
    if not os.path.exists(main_video_path) or not os.path.exists(intro_video_path) or not os.path.exists(outro_video_path):
        print(f"ERROR: Missing files - main: {os.path.exists(main_video_path)}, intro: {os.path.exists(intro_video_path)}, outro: {os.path.exists(outro_video_path)}")
        return None
    
    try:
        # Generate title using OpenAI
        title = generate_title(idea, script)
        print(f"Generated title: '{title}'")
        
        # Create output paths
        intro_with_title_path = os.path.join(output_dir, "intro_with_title.mp4")
        final_path = os.path.join(output_dir, "branded_video.mp4")
        
        # Add title overlay to intro video
        print("Adding title overlay to intro video...")
        if not add_title_overlay(intro_video_path, title, intro_with_title_path):
            print("ERROR: Failed to add title overlay to intro")
            return None
        print(f"Title overlay added: {intro_with_title_path}")
        
        # Concatenate: intro_with_title + main + outro
        print("Concatenating videos...")
        video_list = [intro_with_title_path, main_video_path, outro_video_path]
        result = concatenate_videos(video_list, final_path)
        
        # Clean up temporary intro file
        try:
            if os.path.exists(intro_with_title_path):
                os.unlink(intro_with_title_path)
                print(f"Cleaned up: {intro_with_title_path}")
        except Exception:
            pass
        
        return result
        
    except Exception as e:
        print(f"Branding workflow error: {e}")
        return None
    
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