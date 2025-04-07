"""Camera module supporting both Windows webcam and Raspberry Pi camera."""
import platform
from pathlib import Path
from datetime import datetime
import time

class BaseCamera:
    """Base class for camera implementations."""
    def capture_image(self, output_dir: Path, file_name: str, event_time: datetime) -> Path:
        """Capture a still image and save it to the specified directory."""
        raise NotImplementedError

    def record_for_duration(self, output_dir: Path, file_name: str, duration_seconds: float, event_time: datetime) -> Path:
        """Record video for a specified duration."""
        raise NotImplementedError

    def cleanup(self):
        """Clean up camera resources."""
        pass

class WindowsCamera(BaseCamera):
    """Windows webcam implementation using OpenCV."""
    def __init__(self):
        """Initialize the webcam."""
        import cv2
        self.cv2 = cv2
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open webcam")
        
        # Set resolution to 1080p if supported
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Allow camera to warm up
        time.sleep(.5)

    def capture_image(self, output_dir: Path, file_name: str, event_time: datetime) -> Path:
        """Capture a still image and save it to the specified directory."""
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture image")
        
        image_path = output_dir / file_name
        self.cv2.imwrite(str(image_path), frame)
        
        return image_path

    def record_for_duration(self, output_dir: Path, file_name: str, duration_seconds: float, event_time: datetime) -> Path:
        """Record video for a specified duration."""
        video_path = output_dir / file_name
        
        # Define the codec and create VideoWriter object
        fourcc = self.cv2.VideoWriter_fourcc(*'mp4v')
        out = self.cv2.VideoWriter(
            str(video_path),
            fourcc,
            30.0,  # fps
            (int(self.cap.get(self.cv2.CAP_PROP_FRAME_WIDTH)),
             int(self.cap.get(self.cv2.CAP_PROP_FRAME_HEIGHT)))
        )

        end_time = time.time() + duration_seconds
        while time.time() < end_time:
            ret, frame = self.cap.read()
            if not ret:
                break
            out.write(frame)

        out.release()
        return video_path

    def cleanup(self):
        """Clean up camera resources."""
        if hasattr(self, 'cap'):
            self.cap.release()

class RaspberryPiCamera(BaseCamera):
    """Raspberry Pi camera implementation using picamera2."""
    def __init__(self):
        """Initialize the camera."""
        try:
            from picamera2 import Picamera2
            self.camera = Picamera2()
            # Configure camera for 1080p resolution
            self.config = self.camera.create_still_configuration(
                main={"size": (1920, 1080)},
                lores={"size": (640, 480)},
                display="lores"
            )
            self.camera.configure(self.config)
            self.camera.start()
            # Allow camera to warm up
            time.sleep(2)
        except ImportError:
            raise ImportError("picamera2 is required for Raspberry Pi camera")

    def capture_image(self, output_dir: Path, file_name: str, event_time: datetime) -> Path:
        """Capture a still image and save it to the specified directory."""
        image_path = output_dir / file_name
        self.camera.capture_file(str(image_path))
        return image_path

    def record_for_duration(self, output_dir: Path, file_name: str, duration_seconds: float, event_time: datetime) -> Path:
        """Record video for a specified duration."""
        video_path = output_dir / file_name
        self.camera.start_recording(str(video_path))
        time.sleep(duration_seconds)
        self.camera.stop_recording()
        return video_path

    def cleanup(self):
        """Clean up camera resources."""
        self.camera.stop()

def create_camera() -> BaseCamera:
    """Factory function to create appropriate camera based on platform."""
    if platform.system() == "Windows":
        return WindowsCamera()
    else:
        return RaspberryPiCamera()
