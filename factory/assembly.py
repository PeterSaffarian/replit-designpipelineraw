import os
import time
import requests
from sync import Sync
from sync.common import Audio, GenerationOptions, Video
from sync.core.api_error import ApiError

# --- Configuration ---
# Hardcoded Sync.so API key as per the provided snippet.
# For better practice, consider moving this to an environment variable later.
SYNC_API_KEY = os.environ.get("SYNC_API_KEY", "").strip()

# Initialize the client
if not SYNC_API_KEY or SYNC_API_KEY == "your_sync_so_api_key_here":
    print("ASSEMBLY: Warning - SYNC_API_KEY is not set. The script will not be able to run.")
    client = None
else:
    client = Sync(api_key=SYNC_API_KEY).generations

# --- Helper Functions ---

def _upload_file_for_url(local_path: str) -> str:
    """
    Uploads a local file to uguu.se to get a temporary public URL.

    Args:
        local_path (str): The path to the local file to upload.

    Returns:
        The public URL of the uploaded file, or an empty string on failure.
    """
    if not os.path.exists(local_path):
        print(f"ASSEMBLY: Error - Cannot upload file, path does not exist: {local_path}")
        return ""

    file_name = os.path.basename(local_path)
    print(f"ASSEMBLY: Uploading {file_name} to uguu.se for a public URL...")

    upload_url = "https://uguu.se/upload"

    try:
        with open(local_path, 'rb') as f:
            files = {'files[]': (file_name, f)}
            response = requests.post(upload_url, files=files, timeout=60)
            response.raise_for_status()

            data = response.json()
            # Expected response format: {"success":true,"files":[{"url":"...","name":"...","size":...}]}
            if data.get("success") and data.get("files"):
                url = data["files"][0].get("url")
                if url:
                    print(f"ASSEMBLY: Successfully uploaded. URL: {url}")
                    return url

            print(f"ASSEMBLY: uguu.se API did not return a valid file URL. Response: {data}")
            return ""

    except requests.exceptions.RequestException as e:
        print(f"ASSEMBLY: Error uploading file to uguu.se: {e}")
        return ""
    except (KeyError, IndexError, ValueError):
        print(f"ASSEMBLY: Error parsing JSON response from uguu.se. Raw response: {response.text}")
        return ""

# --- Main Function ---

def generate(raw_video_url: str, audio_path: str) -> str:
    """
    Performs lip-sync on a video and returns the URL to the final video.

    Args:
        raw_video_url (str): The public URL to the raw, mute video (from Kling).
        audio_path (str): The local path to the audio file.

    Returns:
        The public URL of the final lip-synced video, or an empty string on failure.
    """
    print("ASSEMBLY: Starting lip sync generation job...")
    if not client:
        print("ASSEMBLY: Error - Sync.so client is not initialized.")
        return ""

    # 1. Upload the local audio file to get a public URL
    public_audio_url = _upload_file_for_url(audio_path)
    if not public_audio_url:
        print("ASSEMBLY: Failed to get public URL for audio, cannot proceed.")
        return ""

    # 2. Submit the job to Sync.so using the URLs
    try:
        response = client.create(
            input=[Video(url=raw_video_url), Audio(url=public_audio_url)],
            model="lipsync-2",
            options=GenerationOptions(sync_mode="cut_off"),
        )
        job_id = response.id
        print(f"ASSEMBLY: Generation submitted successfully, job ID: {job_id}")
    except ApiError as e:
        print(f'ASSEMBLY: Create generation request failed with status {e.status_code} and error {e.body}')
        return ""
    except Exception as e:
        print(f"ASSEMBLY: An unexpected error occurred during job submission: {e}")
        return ""

    # 3. Poll for the result
    while True:
        try:
            print(f'ASSEMBLY: Polling status for generation {job_id}...')
            generation = client.get(job_id)
            status = generation.status
            if status == 'COMPLETED':
                print(f'ASSEMBLY: Generation {job_id} completed successfully.')
                # 4. Return the public URL of the final video
                return generation.output_url
            elif status == 'FAILED':
                print(f'ASSEMBLY: Generation {job_id} failed.')
                return ""
            time.sleep(10)
        except ApiError as e:
            print(f"ASSEMBLY: Error polling job status: {e}")
            return ""
        except Exception as e:
            print(f"ASSEMBLY: An unexpected polling error occurred: {e}")
            return ""


if __name__ == '__main__':
    print("--- RUNNING DIRECT TEST FOR ASSEMBLY ---")

    if not client:
        print("ERROR: Please replace 'your_sync_so_api_key_here' in the script with your actual key.")
    else:
        # For this test, you MUST have a test audio file.
        test_audio = "storage/5_ drink wate_20250613/audio.mp3"
        # The raw video URL would normally come from the video_gen step. We'll use a placeholder.
        # NOTE: This URL must be a real, public video URL for the test to work.
        test_video_url = "https://v21-kling.klingai.com/bs2/upload-ylab-stunt-sgp/se/stream_lake_m2v_extend_video_v15_v16/650ece21-e762-4e85-897f-76f5ffccb92c_raw_video.mp4?x-kcdn-pid=112372"

        if not os.path.exists(test_audio):
            print(f"ERROR: Test audio file not found at '{test_audio}'.")
        else:
            final_url = generate(test_video_url, test_audio)
            if final_url:
                print(f"\n--- TEST COMPLETE ---")
                print(f"Final video URL: {final_url}")
            else:
                print("\n--- TEST FAILED ---")
