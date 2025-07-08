"""
Video Transitions using MoviePy - Professional entrance animations and smooth crossfade transitions.

This module replaces the complex FFmpeg filter approach with MoviePy for reliable,
high-quality video transitions and entrance animations.
"""

import os
from typing import Optional, List
import tempfile

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    print("MoviePy not available, falling back to FFmpeg")
    MOVIEPY_AVAILABLE = False

def create_intro_slide_with_animation(title: str, logo_path: str, width: int, height: int, 
                                    duration: float = 5.0) -> Optional[str]:
    """
    Create an animated intro slide with smooth entrance animations using MoviePy.
    
    Args:
        title (str): The video title text
        logo_path (str): Path to the logo image
        width (int): Video width
        height (int): Video height  
        duration (float): Duration of the intro slide
    
    Returns:
        str: Path to the created intro video, or None on failure
    """
    try:
        # Create white background
        background = ColorClip(size=(width, height), color=(255, 255, 255), duration=duration)
        
        # Load and prepare logo
        logo = ImageClip(logo_path).resize(height=width//4).set_duration(duration)
        logo_x = (width - logo.w) // 2
        logo_y = height // 4
        
        # Logo entrance animation: slide down from above
        def logo_position(t):
            if t < 1.0:  # Animation during first second
                progress = t / 1.0
                y = logo_y - 200 + (200 * progress)  # Smooth slide down
                return (logo_x, max(y, logo_y))
            return (logo_x, logo_y)  # Final position
        
        logo_animated = logo.set_position(logo_position)
        
        # "KiaOra presents" text
        presents_text = TextClip("KiaOra presents", 
                               fontsize=width//30, 
                               color='black', 
                               font='Arial-Bold',
                               duration=duration)
        presents_x = (width - presents_text.w) // 2
        presents_y = height // 2
        
        # Presents text entrance animation: slide down after 1.5 seconds
        def presents_position(t):
            if t < 1.5:
                return (presents_x, presents_y - 150)  # Off-screen above
            elif t < 2.5:  # Animation between 1.5-2.5 seconds
                progress = (t - 1.5) / 1.0
                y = presents_y - 150 + (150 * progress)  # Smooth slide down
                return (presents_x, y)
            return (presents_x, presents_y)  # Final position
        
        presents_animated = presents_text.set_position(presents_position)
        
        # Title text
        title_text = TextClip(title,
                            fontsize=width//25,
                            color='black', 
                            font='Arial-Bold',
                            duration=duration)
        title_x = (width - title_text.w) // 2
        title_y = height * 0.7
        
        # Title entrance animation: slide up from below after 3 seconds
        def title_position(t):
            if t < 3.0:
                return (title_x, title_y + 150)  # Off-screen below
            elif t < 4.0:  # Animation between 3-4 seconds
                progress = (t - 3.0) / 1.0
                y = title_y + 150 - (150 * progress)  # Smooth slide up
                return (title_x, y)
            return (title_x, title_y)  # Final position
        
        title_animated = title_text.set_position(title_position)
        
        # Composite all elements
        intro_clip = CompositeVideoClip([
            background,
            logo_animated,
            presents_animated, 
            title_animated
        ])
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix='_intro.mp4')
        intro_clip.write_videofile(temp_path, fps=25, codec='libx264', audio=False, verbose=False, logger=None)
        
        return temp_path
        
    except Exception as e:
        print(f"Error creating intro slide: {e}")
        return None

def create_outro_slide_with_animation(logo_path: str, width: int, height: int,
                                    duration: float = 4.0) -> Optional[str]:
    """
    Create an animated outro slide with smooth entrance animations.
    
    Args:
        logo_path (str): Path to the logo image
        width (int): Video width
        height (int): Video height
        duration (float): Duration of the outro slide
    
    Returns:
        str: Path to the created outro video, or None on failure
    """
    try:
        # Create white background
        background = ColorClip(size=(width, height), color=(255, 255, 255), duration=duration)
        
        # Load and prepare logo
        logo = ImageClip(logo_path).resize(height=width//3).set_duration(duration)
        logo_x = (width - logo.w) // 2
        logo_y = height // 3
        
        # Logo entrance animation: slide down from above
        def logo_position(t):
            if t < 1.0:  # Animation during first second
                progress = t / 1.0
                y = logo_y - 200 + (200 * progress)  # Smooth slide down
                return (logo_x, max(y, logo_y))
            return (logo_x, logo_y)  # Final position
        
        logo_animated = logo.set_position(logo_position)
        
        # "Follow us for more" text
        follow_text = TextClip("Follow us for more",
                             fontsize=width//20,
                             color='black',
                             font='Arial-Bold', 
                             duration=duration)
        follow_x = (width - follow_text.w) // 2
        follow_y = height * 0.7
        
        # Text entrance animation: slide up from below after 1.5 seconds
        def follow_position(t):
            if t < 1.5:
                return (follow_x, follow_y + 150)  # Off-screen below
            elif t < 2.5:  # Animation between 1.5-2.5 seconds
                progress = (t - 1.5) / 1.0
                y = follow_y + 150 - (150 * progress)  # Smooth slide up
                return (follow_x, y)
            return (follow_x, follow_y)  # Final position
        
        follow_animated = follow_text.set_position(follow_position)
        
        # Composite all elements
        outro_clip = CompositeVideoClip([
            background,
            logo_animated,
            follow_animated
        ])
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix='_outro.mp4')
        outro_clip.write_videofile(temp_path, fps=25, codec='libx264', audio=False, verbose=False, logger=None)
        
        return temp_path
        
    except Exception as e:
        print(f"Error creating outro slide: {e}")
        return None

def concatenate_with_crossfade(video_paths: List[str], output_path: str,
                             fade_duration: float = 1.0) -> Optional[str]:
    """
    Concatenate videos with smooth crossfade transitions using MoviePy.
    
    Args:
        video_paths (List[str]): List of video file paths to concatenate
        output_path (str): Path for the final output video
        fade_duration (float): Duration of crossfade transitions in seconds
    
    Returns:
        str: Path to the final video, or None on failure
    """
    try:
        if len(video_paths) < 2:
            print("Need at least 2 videos for crossfade")
            return None
        
        # Load all video clips
        clips = []
        for path in video_paths:
            if not os.path.exists(path):
                print(f"Video not found: {path}")
                return None
            clips.append(VideoFileClip(path))
        
        print(f"Concatenating {len(clips)} videos with {fade_duration}s crossfade...")
        
        # Apply crossfade transitions
        final_clips = [clips[0]]  # First clip without fade-in
        
        for i, clip in enumerate(clips[1:], 1):
            # Add crossfade to each subsequent clip
            clip_with_fade = clip.crossfadein(fade_duration)
            final_clips.append(clip_with_fade)
        
        # Concatenate with overlap for smooth transitions
        final_video = concatenate_videoclips(final_clips, padding=-fade_duration)
        
        # Add subtle fade in/out for professional finish
        final_video = final_video.fadein(0.2).fadeout(0.2)
        
        # Write final video
        final_video.write_videofile(
            output_path,
            fps=25,
            codec='libx264',
            audio_codec='aac',
            bitrate="5000k",
            verbose=False,
            logger=None
        )
        
        # Clean up clips
        for clip in clips:
            clip.close()
        final_video.close()
        
        return output_path if os.path.exists(output_path) else None
        
    except Exception as e:
        print(f"Error in video concatenation: {e}")
        return None

def create_branded_video_moviepy(main_video_path: str, idea: str, script: str, 
                                logo_path: str, output_dir: str) -> Optional[str]:
    """
    Main function to create a branded video with MoviePy animations and transitions.
    
    Args:
        main_video_path (str): Path to the main video content
        idea (str): The video idea for title generation
        script (str): The video script for title generation  
        logo_path (str): Path to the logo image
        output_dir (str): Directory for output files
    
    Returns:
        str: Path to the final branded video, or None on failure
    """
    if not MOVIEPY_AVAILABLE:
        print("MoviePy not available")
        return None
        
    try:
        import sys
        sys.path.append('/home/runner/workspace')
        from factory import branding  # Import existing title generation
        
        # Get video dimensions
        main_clip = VideoFileClip(main_video_path)
        width, height = main_clip.size
        main_clip.close()
        
        # Generate title using existing function
        title = branding.generate_title(idea, script)
        print(f"Generated title: '{title}'")
        
        # Create animated intro slide
        print("Creating animated intro slide...")
        intro_path = create_intro_slide_with_animation(title, logo_path, width, height)
        if not intro_path:
            return None
        
        # Create animated outro slide  
        print("Creating animated outro slide...")
        outro_path = create_outro_slide_with_animation(logo_path, width, height)
        if not outro_path:
            return None
        
        # Concatenate with smooth crossfade transitions
        print("Concatenating with smooth crossfade transitions...")
        output_path = os.path.join(output_dir, "branded_video_moviepy.mp4")
        final_video = concatenate_with_crossfade([intro_path, main_video_path, outro_path], 
                                               output_path, fade_duration=1.0)
        
        # Clean up temporary files
        try:
            if intro_path and os.path.exists(intro_path):
                os.unlink(intro_path)
                print(f"Cleaned up: {intro_path}")
            if outro_path and os.path.exists(outro_path):
                os.unlink(outro_path)
                print(f"Cleaned up: {outro_path}")
        except:
            pass
        
        return final_video
        
    except Exception as e:
        print(f"Error creating branded video: {e}")
        return None