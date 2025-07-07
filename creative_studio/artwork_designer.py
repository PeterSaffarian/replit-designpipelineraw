import os
from creative_studio.models import call_text_model
from typing import Optional

def _read_image_bytes(image_path: str) -> Optional[bytes]:
    """Reads an image file and returns its content as bytes."""
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ARTWORK DESIGNER: Error - Reference image not found at {image_path}")
        return None
    except Exception as e:
        print(f"ARTWORK DESIGNER: Error reading image file: {e}")
        return None

def design_artwork_prompt(idea: str, ref_image_path: str) -> str:
    """
    Interprets an idea and reference character to generate a detailed prompt for an image model.

    This function uses a vision-capable text model to "look" at the reference character
    and create a scene description that is ready for the artwork_builder.

    Args:
        idea (str): The high-level concept (e.g., "Explain digital privacy").
        ref_image_path (str): The file path to the reference character image.

    Returns:
        str: A detailed, descriptive prompt for the image generation model.
             Returns an empty string if an error occurs.
    """
    print(f"ARTWORK DESIGNER: Designing prompt for idea: '{idea}'")

    # 1. Define the 'role' for our AI model.
    system_prompt = (
        "You are an expert animation prompt designer. Your job is to take a high-level idea "
        "and a reference character image, and create a single, detailed, and descriptive prompt "
        "for an image generation engine like gpt image-1. The prompt should describe a complete scene "
        "that includes the character as the main actor. Focus on visual details: lighting, "
        "camera angle, mood, setting, and character expression. Do not write a story, only the prompt."
        "the reference character image will also be given to the engine as reference alongside your prompt."
        "given the limitations of the video generation machine around working with text, try and make a visual scene and environmnet that can be easily animated."
        "in the scene let's try and avoide using text content on any screen."
        "the goal is to make it a visual (and then later adding voice to make it verbal as well). not text filled"
    )

    # 2. Define the specific 'task' for our AI model.
    user_prompt = (
        f"Here is the high-level idea: '{idea}'.\n\n"
        "Based on this idea and the provided reference character image, create a single, "
        "detailed paragraph to be used as a prompt for an image generator. The prompt should result in "
        "an image in the same animation style as the refrence character for instagram story. Describe the character's appearance based on the scene, "
        "their expression, the environment they are in, and how the overall scene relates to the core idea."
    )

    # 3. Read the reference image into bytes to be sent to the model.
    image_bytes = _read_image_bytes(ref_image_path)
    if not image_bytes:
        print("ARTWORK DESIGNER: Could not proceed without reference image.")
        return ""

    # 4. Call the text model to generate the prompt.
    # We use a powerful vision model like 'gemini-1.5-pro' or 'gpt-4o' for this task.
    # As discussed, we are setting both the system and user prompts here.
    detailed_prompt = call_text_model(
        model_name='gpt-4o',  # This can be changed to 'gpt-4o' etc. gemini-1.5-pro
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image_bytes=image_bytes
    )

    if detailed_prompt:
        print(f"ARTWORK DESIGNER: Successfully generated prompt:\n---\n{detailed_prompt}\n---")
    else:
        print("ARTWORK DESIGNER: Failed to generate a prompt.")

    return detailed_prompt

if __name__ == '__main__':
    # This is a test block to run this file directly.
    # Make sure you have a .env file with your GOOGLE_API_KEY, OPENAI_API_KEY in the project root.
    # Also, ensure you have the 'inputs/reference.png' file as created by the orchestrator.

    # Create dummy files and directories for testing if they don't exist
    if not os.path.exists("inputs"):
        os.makedirs("inputs")
    if not os.path.exists("inputs/reference.png"):
        with open("inputs/reference.png", "w") as f:
            f.write("This is a dummy file.") # A real image file is needed for the model to work.
            print("Created a dummy reference.png. Please replace it with a real image for proper testing.")

    test_idea = "A character educating viewers about the importance of online security."
    test_ref_image = "inputs/reference.png"

    # To run this test, you need the models.py file in the same directory (or in a package).
    # Since we are in creative_studio, it should work if you run this from the project root.
    try:
        # We assume models.py is in the same directory for this direct test run.
        from creative_studio.models import call_text_model
        design_artwork_prompt(test_idea, test_ref_image)
    except ImportError:
        print("\nTo test this file directly, make sure 'models.py' is accessible,")
        print("and run this script from the root 'project/' directory.")
    except Exception as e:
        print(f"An error occurred during the test run: {e}")

