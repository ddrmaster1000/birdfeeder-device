"""Main program for the Bird Feeder device."""
from pathlib import Path
import time
import logging
import argparse
from datetime import datetime

from motion_sensor import create_motion_sensor
from camera import create_camera
from bird_detector import BirdDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "bird_feeder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BirdFeederDevice:
    def __init__(self, test_image_path=None):
        """Initialize the bird feeder device components."""
        # Create output directories
        logger.info("Initializing BirdFeederDevice...")
        self.base_dir = Path(__file__).parent / "data"
        self.base_dir.mkdir(exist_ok=True)

        # Initialize components
        self.motion_sensor = create_motion_sensor()
        self.camera = create_camera()
        self.bird_detector = BirdDetector()
        
        # Store test image path if provided
        self.test_image_path = test_image_path

    def process_motion_event(self):
        """Process a motion detection event."""
        logger.info(f"Motion detected at {datetime.now()}")
        
        # Capture image or use test image
        if self.test_image_path:
            image_path = Path(self.test_image_path)
            logger.info(f"Using test image: {image_path}")
        else:
            # Capture image using camera
            image_path = self.camera.capture_image(self.base_dir)
            logger.info(f"Captured image: {image_path}")

        # Detect birds in the image
        bird_detected = self.bird_detector.detect_bird(image_path)
        
        if bird_detected:
            logger.info("Bird detected! Recording video...")
            # Record video for a specified duration
            video_path = self.camera.record_for_duration(self.base_dir, duration_seconds=10)
            logger.info(f"Recorded video: {video_path}")
        
        return bird_detected

    def run(self):
        """Run the continuous monitoring loop."""
        logger.info("Starting Bird Feeder Device...")
        logger.info("Monitoring for birds...")
        
        if self.test_image_path:
            # If a test image is provided, process it once and exit
            self.process_motion_event()
        else:
            # Normal continuous monitoring mode
            while True:
                # Check PIR sensor every second
                if self.motion_sensor.check_motion():
                    self.process_motion_event()
                time.sleep(1)  # Low-power state between checks

def main():
    """Main entry point."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Bird Feeder Device")
    parser.add_argument(
        "-t", "--test-image", 
        type=str, 
        help="Path to a test image to process instead of using camera"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize device with optional test image
    device = BirdFeederDevice(test_image_path=args.test_image)
    device.run()

if __name__ == "__main__":
    main()
