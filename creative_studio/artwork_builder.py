import os
from creative_studio.models import call_image_model
from typing import Optional

def _read_image_bytes(image_path: str) -> Optional[bytes]:
    """Reads an image file and returns its content as bytes."""
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ARTWORK BUILDER: Error - Reference image not found at {image_path}")
        return None
    except Exception as e:
        print(f"ARTWORK BUILDER: Error reading image file: {e}")
        return None

def build_artwork(prompt: str, ref_image_path: str, output_path: str) -> str:
    """
    Generates artwork by calling a vision model with an image generation tool,
    using a prompt and a reference image.

    Args:
        prompt (str): The detailed prompt from the artwork_designer.
        ref_image_path (str): The path to the reference image.
        output_path (str): The full path where the generated image will be saved.

    Returns:
        str: The path to the saved artwork file, or an empty string on failure.
    """
    print("ARTWORK BUILDER: Building artwork using Responses API...")

    ref_image_bytes = _read_image_bytes(ref_image_path)
    if not ref_image_bytes:
        print("ARTWORK BUILDER: Could not proceed without reference image.")
        return ""

    # Call our central image model function which now uses the Responses API
    image_bytes = call_image_model(
        model_name='gpt-4o',  # Use a powerful vision model like gpt-4o
        prompt=prompt,
        ref_image_bytes=ref_image_bytes
    )

    if not image_bytes:
        print("ARTWORK BUILDER: Failed to generate image bytes from the model.")
        return ""

    # Save the generated image bytes to the specified output file
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"ARTWORK BUILDER: Successfully saved artwork to {output_path}")
        return output_path
    except Exception as e:
        print(f"ARTWORK BUILDER: Failed to save image file. Error: {e}")
        return ""

if __name__ == '__main__':
    # This is a direct test block for the artwork_builder.
    # It uses a hardcoded prompt to test the image generation directly.

    print("--- RUNNING DIRECT TEST FOR ARTWORK BUILDER ---")

    # 1. Setup paths and test data
    if not os.path.exists("storage/images"):
        os.makedirs("storage/images")
    if not os.path.exists("inputs/reference.png"):
        # You must have a real image here for the test to work
        print("ERROR: Please create a real 'inputs/reference.png' image to run this test.")
    else:
        test_ref_image = "inputs/reference.png"
        test_output = "storage/images/test_artwork_from_builder.png"

        # A high-quality, detailed prompt, similar to what artwork_designer would create.
        test_prompt = "Create an animated scene featuring the character in a modern, sleek office setting with soft, ambient lighting. The character stands confidently in front of a large digital screen displaying graphics related to cybersecurity, such as locks and encrypted codes. She wears a smart casual outfit, with a tailored blazer over her original attire, conveying professionalism. Her expression is focused and engaging, with a slight smile, as if explaining a complex topic clearly. The background includes a desk with a laptop and a few potted plants, adding a touch of warmth. The overall mood is informative and empowering, emphasizing the importance of online security. The composition is designed for an Instagram story, with the character centered and ample space above for text overlays."

        try:
            # 2. Run the build_artwork function with the test data
            print("\nBuilding artwork with hardcoded prompt and reference image...")
            build_artwork(test_prompt, test_ref_image, test_output)

        except ImportError as e:
            print(f"\nIMPORT ERROR: {e}")
            print("To test this file directly, make sure 'models.py' is accessible,")
            print("and run this script from the root 'project/' directory.")
        except Exception as e:
            print(f"\nAn error occurred during the test run: {e}")
