import os
from elevenlabs.client import ElevenLabs

# --- Configuration and Initialization ---
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY") 

# Initialize the client
if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your_elevenlabs_api_key_here":
    print("AUDIO GEN: Warning - ELEVENLABS_API_KEY is not set. The script will not be able to generate audio.")
    client = None
else:
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- Main Function ---

def generate(
    text: str,
    output_path: str,
    voice: str = "xZVrOjUURog02K298cjt", # A default voice ID
    model: str = "eleven_multilingual_v2"
) -> str:
    """
    Generate TTS audio from text using the ElevenLabs API and save it as an MP3.

    Args:
        text (str): The text to convert to speech.
        output_path (str): The full path where the audio file will be saved.
        voice (str): The ID of the voice to use.
        model (str): The ID of the model to use.

    Returns:
        str: The path to the saved audio file, or an empty string on failure.
    """
    print("AUDIO GEN: Generating audio...")
    if not client:
        print("AUDIO GEN: Error - ElevenLabs client is not initialized. Please set your API key.")
        return ""

    try:
        # Generate the audio stream from the API
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice,
            model_id=model
        )

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write the streamed audio chunks to the output file
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        print(f"AUDIO GEN: Successfully saved audio to {output_path}")
        return output_path

    except Exception as e:
        print(f"AUDIO GEN: An error occurred during audio generation: {e}")
        return ""


if __name__ == "__main__":
    # This is a direct test block for the audio generator.

    print("--- RUNNING DIRECT TEST FOR AUDIO GENERATOR ---")

    if not client:
        print("ERROR: Please replace 'your_elevenlabs_api_key_here' in the script with your actual key to run this test.")
    else:
        test_text = "Hello, this is a test of the text-to-speech audio generation system."

        # Ensure the storage directory exists for the test output
        os.makedirs("storage/audio", exist_ok=True)
        test_output_path = "storage/audio/test_output_audio.mp3"

        generate(test_text, test_output_path)

# This allows other scripts to import the 'generate' function easily.
__all__ = ["generate"]
