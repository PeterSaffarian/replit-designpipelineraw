# factory/kling.py
# A Python library for interacting with the Kling AI API.
# This file centralizes API calls and will be imported by video_gen.py.

import time
import jwt
import requests
import os
import base64

# --- Configuration ---
ACCESS_KEY = os.environ.get("KLING_ACCESS_KEY", "").strip()
SECRET_KEY = os.environ.get("KLING_SECRET_KEY", "").strip()

API_ROOT = "https://api-singapore.klingai.com/v1"

# --- Private Helper Functions ---

def _generate_jwt_token():
    """Generates a JWT token for API authentication."""
    if not ACCESS_KEY or not SECRET_KEY:
        raise ValueError("Kling API keys are not configured.")

    headers = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": ACCESS_KEY,
        "exp": int(time.time()) + 1800,  # 30-minute validity
        "nbf": int(time.time()) - 5
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256", headers=headers)

def _submit_task(endpoint: str, payload: dict) -> str:
    """A generic function to submit a task to a given endpoint."""
    token = _generate_jwt_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print(f"KLING: Submitting task to {os.path.basename(endpoint)}...")
    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        response_data = resp.json()

        if response_data.get("code") != 0:
            print(f"KLING: API Error: {response_data.get('message')} (Code: {response_data.get('code')})")
            return None

        task_id = response_data.get("data", {}).get("task_id")
        print(f"KLING: Task submitted successfully. Task ID: {task_id}")
        return task_id
    except requests.exceptions.RequestException as e:
        print(f"KLING: Network/Request Error submitting task: {e}")
        return None

def _poll_for_result(task_endpoint_url: str) -> dict:
    """A generic function to poll a task until it's complete."""
    print(f"KLING: Polling for result...")
    while True:
        token = _generate_jwt_token()
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(task_endpoint_url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json().get("data", {})
            status = data.get("task_status")

            if status == "succeed":
                print("KLING: Task succeeded!")
                return data.get("task_result")
            elif status == "failed":
                print(f"KLING: Task failed. Reason: {data.get('task_status_msg')}")
                return None

            print(f"KLING: Status is '{status}'. Waiting 10 seconds...")
            time.sleep(10)
        except requests.exceptions.RequestException as e:
            print(f"KLING: Network/Request Error during polling: {e}")
            return None

# --- Public API Functions ---

def text_to_video(prompt: str, model_name: str = "kling-v1", duration: int = 5, aspect_ratio: str = "16:9", mode: str = "std") -> dict:
    """Generates a video from a text prompt."""
    endpoint = f"{API_ROOT}/videos/text2video"
    payload = {"model_name": model_name, "prompt": prompt, "duration": str(duration), "aspect_ratio": aspect_ratio, "mode": mode}
    task_id = _submit_task(endpoint, payload)
    return _poll_for_result(f"{endpoint}/{task_id}") if task_id else None

def image_to_video(image_path: str, prompt: str, model_name: str = "kling-v1", duration: int = 5) -> dict:
    """Animates a source image based on a prompt."""
    endpoint = f"{API_ROOT}/videos/image2video"
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    payload = {"image": image_data, "model_name": model_name, "prompt": prompt, "duration": str(duration)}
    task_id = _submit_task(endpoint, payload)
    return _poll_for_result(f"{endpoint}/{task_id}") if task_id else None

def video_extension(source_video_id: str, prompt: str) -> dict:
    """Extends a previously generated video."""
    endpoint = f"{API_ROOT}/videos/video-extend"
    payload = {"video_id": source_video_id, "prompt": prompt}
    task_id = _submit_task(endpoint, payload)
    return _poll_for_result(f"{endpoint}/{task_id}") if task_id else None

