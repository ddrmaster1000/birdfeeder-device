"""Main program for the Bird Feeder device."""
from pathlib import Path
import time
import logging
import argparse
from datetime import datetime
import re
import boto3
import uuid
import shutil

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
        
        # # Initialize AWS components
        # self.s3_client = boto3.client('s3')
        # self.dynamodb = boto3.resource('dynamodb')
        
        # Store test image path if provided
        self.test_image_path = test_image_path

    def sanitize_filename(filename):
        """Sanitize filename to remove invalid characters for Windows."""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def upload_to_dynamodb(self, table_name, data):
        """Upload data to a DynamoDB table."""
        logger.info(f"Uploading data to DynamoDB table: {table_name}")
        table = self.dynamodb.Table(table_name)
        table.put_item(Item=data)

    def process_motion_event(self):
        """Process a motion detection event."""
        self.event_time = datetime.now()
        logger.info(f"Motion detected at {self.event_time}")
        date_dir = self.base_dir / self.event_time.strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True, parents=True)
        
        # Use a sanitized timestamp for filename with specific format
        original_timestamp = self.event_time.strftime("%Y-%m-%dT%H:%M:%S")
        timestamp = BirdFeederDevice.sanitize_filename(original_timestamp)

        # Capture image or use test image
        if self.test_image_path:
            image_path = Path(self.test_image_path)
            # Ensure the test image path exists
            if not image_path.exists():
                logger.error(f"Test image path does not exist: {image_path}")
                return
            
            # Create a copy of the test image in the date directory
            try:
                shutil.copy2(image_path, date_dir / f"image_{timestamp}.jpg")
                image_path = date_dir / f"image_{timestamp}.jpg"
                logger.info(f"Using test image: {image_path}")
            except (OSError, IOError) as e:
                logger.error(f"Error copying test image: {e}")
                return
        else:
            # Capture image using camera
            try:
                image_path = self.camera.capture_image(output_dir=date_dir, file_name=f"image_{timestamp}.jpg", event_time=self.event_time)
                logger.info(f"Captured image: {image_path}")
            except (OSError, IOError) as e:
                logger.error(f"Error capturing image: {e}")
                return

        # Detect if there is a bird in the image
        bird_detected, thumbnail_path = self.bird_detector.detect_bird(image_path, date_dir / f"thumb_{timestamp}.jpg", date_dir)
        
        if bird_detected:
            logger.info("Bird detected! Recording video...")
            # Record video for a specified duration
            video_path = self.camera.record_for_duration(output_dir=date_dir, file_name=f"video_{timestamp}.mp4", duration_seconds=3, event_time=self.event_time)
            logger.info(f"Recorded video: {video_path}")
        
            # # Upload event Data to DynamoDB
            # table = self.dynamodb.Table('BirdFeederEvents')
            # table.put_item( 
            #     Item={
            #         'id': str(uuid.uuid4()),
            #         'timestamp': str(self.event_time),
            #         'image_path': str(image_path),
            #         'video_path': str(video_path)
            #     }
            # )

            # # Upload files to S3
            # bucket_name = 'bird-feeder-bucket'
            # self.s3_client.upload_file(str(image_path), bucket_name, f"{self.event_time.strftime('%Y-%m-%d')}/{os.path.basename(str(image_path))}")
            # self.s3_client.upload_file(str(thumbnail_path), bucket_name, f"{self.event_time.strftime('%Y-%m-%d')}/{os.path.basename(str(thumbnail_path))}")
            # self.s3_client.upload_file(str(video_path), bucket_name, f"{self.event_time.strftime('%Y-%m-%d')}/{os.path.basename(str(video_path))}")
            
            # # Cleanup
            # image_path.unlink(missing_ok=True)
            # thumbnail_path.unlink(missing_ok=True)
            # video_path.unlink(missing_ok=True)
        return bird_detected

    def run(self):
        """Run the continuous monitoring loop."""
        logger.info("Starting Bird Feeder Device...")
        logger.info("Monitoring for birds...")
        
        if self.test_image_path:
            # If a test image is provided, process it once and exit
            self.process_motion_event()
            return
        else:
            # Normal continuous monitoring mode
            while True:
                # Check PIR sensor every second
                if self.motion_sensor.check_motion():
                    self.process_motion_event()
                time.sleep(1)  
                # TODO: Implement low-power state between checks

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
