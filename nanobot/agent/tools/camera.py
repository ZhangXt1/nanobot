"""Camera tool for taking photos."""

import base64
import io
import os
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class CameraTool(Tool):
    """Tool to take photos using the local camera."""

    def __init__(self, workspace: Path | None = None):
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "camera"
    
    @property
    def description(self) -> str:
        return "Take a photo using the local camera and return it as a base64-encoded image, or list available cameras."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'capture' or 'list'",
                    "enum": ["capture", "list"]
                },
                "save_path": {
                    "type": "string",
                    "description": "Optional path to save the photo (only for capture action)"
                },
                "camera_index": {
                    "type": "integer",
                    "description": "Camera index (default: 0 for default camera, only for capture action)"
                }
            },
            "required": []
        }
    
    async def execute(self, action: str = "capture", save_path: str | None = None, camera_index: int = 0, **kwargs: Any) -> str:
        try:
            # Try to import OpenCV
            try:
                import cv2
            except ImportError:
                return "Error: OpenCV not installed. Please run 'pip install opencv-python'"

            if action == "list":
                # List available cameras
                available_cameras = []
                # Try camera indices from 0 to 9
                for i in range(10):
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        # Get camera properties if available
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        available_cameras.append(f"Camera {i} (resolution: {width}x{height})")
                        cap.release()
                    else:
                        cap.release()
                        # Stop searching once we find a gap
                        if i > 0 and not available_cameras:
                            break
                
                if available_cameras:
                    return f"Available cameras:\n" + "\n".join(available_cameras)
                else:
                    return "No cameras found."
            else:
                # Capture photo action
                # Open the camera
                cap = cv2.VideoCapture(camera_index)
                if not cap.isOpened():
                    return f"Error: Could not open camera with index {camera_index}"

                # Capture a frame
                ret, frame = cap.read()
                cap.release()

                if not ret:
                    return "Error: Could not capture frame"

                # Encode the frame as base64
                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = base64.b64encode(buffer).decode('utf-8')

                # Save the image if a path is provided
                if save_path:
                    if self._workspace:
                        save_path = str(self._workspace / save_path)
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    # Save the image
                    cv2.imwrite(save_path, frame)
                    return f"Successfully took photo and saved to {save_path}.\nBase64 encoded image: data:image/jpeg;base64,{image_base64}"
                else:
                    return f"Successfully took photo.\nBase64 encoded image: data:image/jpeg;base64,{image_base64}"
        except Exception as e:
            return f"Error: {str(e)}"
