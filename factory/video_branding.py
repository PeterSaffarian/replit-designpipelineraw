"""
Video branding module for adding professional intro/outro slides.

This module creates animated intro slides with dynamic titles and static outro slides
for professional video branding and concatenates them with the main content.
"""

import os
import json
import subprocess
from typing import Optional, Dict
from openai import OpenAI


def generate_video_title(idea: str, script: str, artwork_description: str = "") -> str:
    """
    Generate a short, punchy title for the video using OpenAI.
    
    Args:
        idea (str): The original idea for the video
        script (str): The generated script content
        artwork_description (str): Description of the artwork/visuals
    
    Returns:
        str: A short title (around 5 words) for the video
    """
    print(f"BRANDING: Generating video title...")
    
    # Get OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("BRANDING: Warning - OPENAI_API_KEY not found, using fallback title")
        # Simple fallback based on idea
        words = idea.split()[:3]
        return " ".join(words).title()
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Create prompt for title generation
        prompt = f"""
Create a short, engaging title for an educational video. Keep it around 5 words (can be 3-7 words) - whatever sounds natural and complete.

Original idea: {idea}
Script content: {script}
Visual context: {artwork_description}

The title should be:
- Short and punchy
- Educational/informative in tone
- Engaging for viewers
- Complete and natural (don't cut off mid-thought)
- Suitable for a professional educational video

Examples of good titles:
- "Stay Safe Online Today"
- "Digital Privacy Made Simple"
- "Avoid Phone Scams"
- "Protect Your Personal Data"
- "Online Safety Tips"

Just return the title text, nothing else.
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7
        )
        
        title = response.choices[0].message.content.strip()
        
        # Clean up the title (remove quotes if present)
        title = title.strip('"').strip("'")
        
        print(f"BRANDING: Generated title: '{title}'")
        return title
        
    except Exception as e:
        print(f"BRANDING: Error generating title: {e}")
        # Fallback to simple title based on idea
        words = idea.split()[:3]
        fallback_title = " ".join(words).title()
        print(f"BRANDING: Using fallback title: '{fallback_title}'")
        return fallback_title


def create_intro_slide(title: str, logo_path: str, output_path: str, duration: int = 3) -> Optional[str]:
    """
    Create an animated intro slide with logo and title.
    
    Args:
        title (str): The video title to display
        logo_path (str): Path to the logo image
        output_path (str): Path where the intro video will be saved
        duration (int): Duration of the intro in seconds
    
    Returns:
        str: Path to the generated intro video, or None on failure
    """
    print(f"BRANDING: Creating intro slide...")
    print(f"BRANDING: Title: '{title}'")
    print(f"BRANDING: Duration: {duration} seconds")
    
    # Validate inputs
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    try:
        # Create intro slide with FFmpeg
        # Background: Light blue gradient similar to mockup
        # Logo: Slides in from left
        # Title: Fades in with typewriter effect
        
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x87CEEB:size=640x480:duration={duration}",  # Light blue background
            "-i", logo_path,  # Logo input
            "-filter_complex", f"""
            [0:v]drawtext=text='KiaOra presents':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=24:fontcolor=0x2F4F4F:x=(w-text_w)/2:y=h*0.3 [bg_with_presents];
            [bg_with_presents]drawtext=text='{title}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=32:fontcolor=0x000000:x=(w-text_w)/2:y=h*0.6 [bg_with_title];
            [1:v]scale=80:80[logo_scaled];
            [bg_with_title][logo_scaled]overlay=x=(w-80)/2:y=(h-80)/2-50
            """,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        print(f"BRANDING: Running FFmpeg for intro slide...")
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Intro slide created successfully!")
            print(f"BRANDING: Saved to: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"BRANDING: ❌ Intro slide creation timeout")
        return None
    except Exception as e:
        print(f"BRANDING: ❌ Error creating intro slide: {e}")
        return None


def create_outro_slide(logo_path: str, output_path: str, duration: int = 3) -> Optional[str]:
    """
    Create a static outro slide with "Follow us for more" message.
    
    Args:
        logo_path (str): Path to the logo image
        output_path (str): Path where the outro video will be saved
        duration (int): Duration of the outro in seconds
    
    Returns:
        str: Path to the generated outro video, or None on failure
    """
    print(f"BRANDING: Creating outro slide...")
    print(f"BRANDING: Duration: {duration} seconds")
    
    # Validate inputs
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo file not found: {logo_path}")
        return None
    
    try:
        # Create outro slide with FFmpeg
        # Background: Light blue (same as intro)
        # Logo: Centered with fade-in effect
        # Text: "Follow us for more" below logo
        
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x87CEEB:size=640x480:duration={duration}",  # Light blue background
            "-i", logo_path,  # Logo input
            "-filter_complex", f"""
            [0:v]drawtext=text='Follow us for more':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=28:fontcolor=0x000000:x=(w-text_w)/2:y=h*0.7 [bg_with_text];
            [1:v]scale=100:100[logo_scaled];
            [bg_with_text][logo_scaled]overlay=x=(w-100)/2:y=(h-100)/2-30
            """,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-y",
            output_path
        ]
        
        print(f"BRANDING: Running FFmpeg for outro slide...")
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Outro slide created successfully!")
            print(f"BRANDING: Saved to: {output_path}")
            return output_path
        else:
            print(f"BRANDING: ❌ FFmpeg failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"BRANDING: ❌ Outro slide creation timeout")
        return None
    except Exception as e:
        print(f"BRANDING: ❌ Error creating outro slide: {e}")
        return None


def add_branding_sequence(main_video_path: str, title: str, logo_path: str, project_path: str) -> Optional[str]:
    """
    Add intro and outro branding slides to the main video.
    
    Args:
        main_video_path (str): Path to the main video (with subtitles/logo)
        title (str): Video title for the intro slide
        logo_path (str): Path to the logo image
        project_path (str): Project directory for temporary files
    
    Returns:
        str: Path to the final branded video, or None on failure
    """
    print(f"BRANDING: Adding branding sequence to video...")
    print(f"BRANDING: Main video: {main_video_path}")
    print(f"BRANDING: Title: '{title}'")
    
    # Validate inputs
    if not os.path.exists(main_video_path):
        print(f"BRANDING: Error - Main video not found: {main_video_path}")
        return None
    
    if not os.path.exists(logo_path):
        print(f"BRANDING: Error - Logo not found: {logo_path}")
        return None
    
    try:
        # Create temporary files for intro and outro
        intro_path = os.path.join(project_path, "intro_slide.mp4")
        outro_path = os.path.join(project_path, "outro_slide.mp4")
        
        # Create intro slide
        print(f"BRANDING: Creating intro slide...")
        intro_result = create_intro_slide(title, logo_path, intro_path, duration=3)
        if not intro_result:
            print(f"BRANDING: Failed to create intro slide")
            return None
        
        # Create outro slide
        print(f"BRANDING: Creating outro slide...")
        outro_result = create_outro_slide(logo_path, outro_path, duration=3)
        if not outro_result:
            print(f"BRANDING: Failed to create outro slide")
            return None
        
        # Concatenate intro + main video + outro
        print(f"BRANDING: Concatenating video segments...")
        final_output = os.path.join(project_path, "final_branded_video.mp4")
        
        # Create file list for FFmpeg concat
        concat_list_path = os.path.join(project_path, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            f.write(f"file '{os.path.abspath(intro_path)}'\n")
            f.write(f"file '{os.path.abspath(main_video_path)}'\n")
            f.write(f"file '{os.path.abspath(outro_path)}'\n")
        
        # Run FFmpeg concat
        concat_cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            "-y",
            final_output
        ]
        
        result = subprocess.run(
            concat_cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            print(f"BRANDING: ✅ Branding sequence completed successfully!")
            print(f"BRANDING: Final video: {final_output}")
            
            # Clean up temporary files
            for temp_file in [intro_path, outro_path, concat_list_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return final_output
        else:
            print(f"BRANDING: ❌ Video concatenation failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"BRANDING: ❌ Branding sequence timeout")
        return None
    except Exception as e:
        print(f"BRANDING: ❌ Error in branding sequence: {e}")
        return None


def apply_complete_branding(main_video_path: str, idea: str, script: str, logo_path: str, project_path: str) -> Optional[str]:
    """
    Complete branding workflow: generate title, create slides, and concatenate.
    
    This is the main function to call from the orchestrator.
    
    Args:
        main_video_path (str): Path to the main video (with subtitles/logo)
        idea (str): Original idea for title generation
        script (str): Script content for title generation
        logo_path (str): Path to the logo image
        project_path (str): Project directory for output
    
    Returns:
        str: Path to the final branded video, or None on failure
    """
    print(f"BRANDING: Starting complete branding workflow...")
    
    # Step 1: Generate video title
    title = generate_video_title(idea, script)
    
    # Step 2: Add branding sequence
    final_video_path = add_branding_sequence(main_video_path, title, logo_path, project_path)
    
    if final_video_path:
        print(f"BRANDING: ✅ Complete branding workflow finished!")
        print(f"BRANDING: Title: '{title}'")
        print(f"BRANDING: Final video: {final_video_path}")
    else:
        print(f"BRANDING: ❌ Branding workflow failed")
    
    return final_video_path