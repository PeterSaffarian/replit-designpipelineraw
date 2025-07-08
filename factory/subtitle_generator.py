"""
Subtitle generation using OpenAI Whisper API.

This module generates SRT subtitle files from audio using OpenAI's Whisper API
with proper timing and formatting for video integration.
"""

import os
from typing import Optional
from openai import OpenAI


def generate_srt_subtitles(audio_path: str, output_path: str, language: str = "en") -> Optional[str]:
    """
    Generate SRT subtitle file from audio using OpenAI Whisper API.
    
    Args:
        audio_path (str): Path to the audio file (MP3, WAV, etc.)
        output_path (str): Path where the SRT file will be saved
        language (str): Language code for transcription (default: "en")
    
    Returns:
        str: Path to the generated SRT file, or None on failure
    """
    print(f"SUBTITLE_GEN: Generating subtitles from audio...")
    print(f"SUBTITLE_GEN: Audio: {audio_path}")
    print(f"SUBTITLE_GEN: Output: {output_path}")
    
    # Validate input file
    if not os.path.exists(audio_path):
        print(f"SUBTITLE_GEN: Error - Audio file not found: {audio_path}")
        return None
    
    # Check file size (Whisper API has 25MB limit)
    file_size = os.path.getsize(audio_path)
    if file_size > 25 * 1024 * 1024:  # 25MB in bytes
        print(f"SUBTITLE_GEN: Warning - Audio file is {file_size/1024/1024:.1f}MB (limit: 25MB)")
        print("SUBTITLE_GEN: Skipping subtitle generation for large file")
        return None
    
    # Get OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("SUBTITLE_GEN: Error - OPENAI_API_KEY not found in environment")
        return None
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        print(f"SUBTITLE_GEN: Calling Whisper API for transcription...")
        
        # Generate SRT subtitles using Whisper API
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt",
                language=language,
                prompt="This is an educational video about digital safety and technology topics."
            )
        
        # Save SRT content to file
        with open(output_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(transcript)
        
        print(f"SUBTITLE_GEN: ✅ Subtitles generated successfully!")
        print(f"SUBTITLE_GEN: SRT file saved: {output_path}")
        
        # Validate SRT content
        if len(transcript.strip()) < 10:
            print("SUBTITLE_GEN: Warning - Generated SRT content seems too short")
        
        return output_path
        
    except Exception as e:
        print(f"SUBTITLE_GEN: ❌ Error generating subtitles: {e}")
        return None


def validate_srt_format(srt_path: str) -> bool:
    """
    Validate that the SRT file has proper format and content.
    
    Args:
        srt_path (str): Path to the SRT file
    
    Returns:
        bool: True if SRT format is valid, False otherwise
    """
    if not os.path.exists(srt_path):
        return False
    
    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # Basic validation - check for subtitle markers
        if not content:
            return False
        
        # Look for timestamp patterns (SRT format)
        if "-->" not in content:
            return False
        
        # Check for subtitle numbering
        lines = content.split('\n')
        if len(lines) < 3:
            return False
        
        return True
        
    except Exception:
        return False


def get_subtitle_stats(srt_path: str) -> dict:
    """
    Get basic statistics about the subtitle file.
    
    Args:
        srt_path (str): Path to the SRT file
    
    Returns:
        dict: Statistics including subtitle count, duration, etc.
    """
    stats = {
        'subtitle_count': 0,
        'total_characters': 0,
        'duration_seconds': 0,
        'valid_format': False
    }
    
    if not validate_srt_format(srt_path):
        return stats
    
    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        stats['valid_format'] = True
        stats['total_characters'] = len(content)
        
        # Count subtitle blocks (simple heuristic)
        subtitle_blocks = content.split('\n\n')
        stats['subtitle_count'] = len([block for block in subtitle_blocks if block.strip()])
        
        # Extract last timestamp to estimate duration
        lines = content.strip().split('\n')
        for line in reversed(lines):
            if '-->' in line:
                # Extract end time from timestamp line
                try:
                    end_time = line.split('-->')[1].strip()
                    # Convert HH:MM:SS,mmm to seconds
                    time_parts = end_time.replace(',', '.').split(':')
                    if len(time_parts) == 3:
                        hours = float(time_parts[0])
                        minutes = float(time_parts[1])
                        seconds = float(time_parts[2])
                        stats['duration_seconds'] = hours * 3600 + minutes * 60 + seconds
                except:
                    pass
                break
        
        print(f"SUBTITLE_GEN: SRT Stats - {stats['subtitle_count']} subtitles, {stats['duration_seconds']:.1f}s duration")
        
    except Exception as e:
        print(f"SUBTITLE_GEN: Error analyzing SRT file: {e}")
    
    return stats