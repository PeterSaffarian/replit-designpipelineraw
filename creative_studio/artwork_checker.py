"""
Artwork Quality Checker using OpenAI multimodal model.

This module evaluates generated artwork to ensure it meets quality standards
before proceeding to video generation. It checks for AI hallucinations,
anatomical errors, unclear visuals, and other quality issues.
"""

import json
import base64
from typing import Dict, Optional
from .models import call_text_model


def _read_image_bytes(image_path: str) -> Optional[bytes]:
    """Reads an image file and returns its content as bytes."""
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"ARTWORK CHECKER: Error reading image: {e}")
        return None


def check_artwork_quality(artwork_path: str, original_prompt: str) -> Dict[str, str]:
    """
    Evaluates artwork quality using OpenAI's multimodal model.
    
    This function examines generated artwork to determine if it meets quality
    standards for video generation. It checks for AI hallucinations, anatomical
    errors, unclear visuals, spelling mistakes, and other issues.
    
    Args:
        artwork_path (str): Path to the generated artwork image.
        original_prompt (str): The prompt that was used to generate the artwork.
    
    Returns:
        Dict with 'status' (Pass/Fail) and optional 'feedback' for improvements.
        Returns {'status': 'Fail', 'feedback': 'Error message'} on failure.
    """
    print("ARTWORK CHECKER: Starting quality evaluation...")
    
    # Read the artwork image
    image_bytes = _read_image_bytes(artwork_path)
    if not image_bytes:
        return {
            'status': 'Fail',
            'feedback': 'Could not read artwork image file'
        }
    
    # Create the quality checking prompt
    system_prompt = """You are an artwork quality checker for video generation. Your job is to examine AI-generated artwork and decide if it passes quality standards or needs to be regenerated.

You should FAIL artwork that has:
- Anatomical errors (extra limbs, distorted body parts, wrong proportions)
- AI hallucinations or artifacts
- Unclear or confusing visual elements
- Spelling mistakes or garbled text
- Poor composition that would look bad in video
- Elements that don't match the intended prompt
- the placement of elements is too chaotic 
- the aspect ration and size of the image is not appropriate for instagram stories
- or not suitable for AI video generation.
- if a screen or device is presente, they need to make sence (e.g. no screen on the back of a laptop or phone)
- also the character should have a well defined mouth to be used for video and lip-syncing

You should PASS artwork that:
- Has clear, well-composed visuals
- Matches the intended prompt well
- Has proper anatomy and realistic elements
- Would work well as a base for video generation
- Has good visual clarity and focus

Respond with JSON only in this exact format:
{
    "status": "Pass" or "Fail",
    "feedback": "Brief specific feedback if status is Fail, or congratulatory note if Pass"
}"""

    user_prompt = f"""Please evaluate this artwork for quality standards.

ORIGINAL PROMPT GIVEN TO ARTWORK GENERATOR:
{original_prompt}

PURPOSE: This artwork will be used as the base image for video generation, so it needs to be clear, well-composed, and free of AI artifacts.

Please examine the attached artwork and determine if it passes quality standards or needs to be regenerated.
Be realistic.
"""

    try:
        # Call OpenAI's multimodal model (gpt-4o)
        response = call_text_model(
            model_name="gpt-4o",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            image_bytes=image_bytes
        )
        
        if not response:
            return {
                'status': 'Fail',
                'feedback': 'No response from quality checker model'
            }
        
        # Parse the JSON response (handle markdown code blocks if present)
        try:
            # Remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]  # Remove ```json
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]  # Remove ```
            clean_response = clean_response.strip()
            
            result = json.loads(clean_response)
            
            # Validate the response format
            if 'status' not in result:
                return {
                    'status': 'Fail',
                    'feedback': 'Invalid response format from quality checker'
                }
            
            # Ensure status is valid
            if result['status'] not in ['Pass', 'Fail']:
                return {
                    'status': 'Fail',
                    'feedback': 'Invalid status value from quality checker'
                }
            
            # Add default feedback if missing
            if 'feedback' not in result:
                if result['status'] == 'Pass':
                    result['feedback'] = 'Artwork meets quality standards'
                else:
                    result['feedback'] = 'Quality issues detected'
            
            print(f"ARTWORK CHECKER: Evaluation complete - Status: {result['status']}")
            if result['status'] == 'Fail':
                print(f"ARTWORK CHECKER: Feedback: {result['feedback']}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"ARTWORK CHECKER: Failed to parse JSON response: {e}")
            print(f"ARTWORK CHECKER: Raw response: {response}")
            return {
                'status': 'Fail',
                'feedback': 'Could not parse quality checker response'
            }
            
    except Exception as e:
        print(f"ARTWORK CHECKER: Error during quality check: {e}")
        return {
            'status': 'Fail',
            'feedback': f'Quality check failed: {str(e)}'
        }