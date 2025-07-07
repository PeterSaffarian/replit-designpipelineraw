#!/usr/bin/env python3
"""
Test script for the artwork quality checker integration.
This script tests the quality checking workflow with a sample image.
"""

import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from creative_studio.artwork_checker import check_artwork_quality

def create_test_artwork():
    """Create a test artwork image for quality checking."""
    print("Creating test artwork...")
    
    # Create a simple test image with text
    img = Image.new('RGB', (512, 512), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Add some text to make it look like artwork
    draw.text((50, 200), "Test Character", fill='darkblue', font=font)
    draw.text((50, 250), "Quality Check Demo", fill='darkblue', font=font)
    
    # Draw a simple character representation
    draw.ellipse([200, 100, 300, 200], fill=(255, 218, 185), outline='black', width=2)  # head
    draw.rectangle([225, 200, 275, 350], fill='red', outline='black', width=2)  # body
    draw.rectangle([200, 320, 220, 400], fill='blue', outline='black', width=2)  # left leg
    draw.rectangle([280, 320, 300, 400], fill='blue', outline='black', width=2)  # right leg
    draw.rectangle([175, 220, 195, 280], fill='green', outline='black', width=2)  # left arm
    draw.rectangle([305, 220, 325, 280], fill='green', outline='black', width=2)  # right arm
    
    # Save to temporary file
    temp_path = "/tmp/test_artwork.png"
    img.save(temp_path)
    print(f"Test artwork saved to: {temp_path}")
    return temp_path

def test_quality_checker():
    """Test the artwork quality checker with a sample image."""
    print("\n=== Testing Artwork Quality Checker ===")
    
    # Create test artwork
    test_image_path = create_test_artwork()
    
    # Test prompt (simulating what would come from artwork_designer)
    test_prompt = "Create an illustration of a friendly character standing upright, wearing colorful clothes. The character should have a simple, clean design suitable for educational content about digital safety."
    
    print(f"\nTesting with prompt: {test_prompt}")
    print(f"Image path: {test_image_path}")
    
    # Run quality check
    result = check_artwork_quality(test_image_path, test_prompt)
    
    print(f"\nQuality Check Results:")
    print(f"Status: {result.get('status', 'Unknown')}")
    print(f"Feedback: {result.get('feedback', 'No feedback')}")
    
    # Cleanup
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"\nCleaned up test file: {test_image_path}")
    
    return result.get('status') == 'Pass'

def main():
    """Run the artwork checker test."""
    try:
        success = test_quality_checker()
        if success:
            print("\n✅ Artwork quality checker test completed successfully!")
        else:
            print("\n❌ Artwork quality checker test failed!")
        return success
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return False

if __name__ == "__main__":
    main()