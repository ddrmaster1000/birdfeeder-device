# Bird Feeder Device Program

On-device program for the Bird Feeder system running on Raspberry Pi 5. This program handles motion detection, image/video capture, and bird detection using google/vit-base-patch16-224.

## Requirements

- Raspberry Pi 5
- PIR Motion Sensor (connected to GPIO pin 17)
- Raspberry Pi Camera Module
- Python 3.13 or later

## Installation

1. Connect the PIR motion sensor to GPIO pin 17 and GND
2. Connect the Raspberry Pi Camera Module
3. Install the dependencies:
   ```bash
   python -m pip install -e .
   ```

## Usage

Run the main program:
```bash
python main.py
```

The program will:
1. Create data directories for images and videos
2. Monitor for motion using the PIR sensor
3. When motion is detected:
   - Capture an image
   - Start video recording
   - Run bird detection on the captured image
   - Save a thumbnail if a bird is detected

Press Ctrl+C to exit the program safely.

## Directory Structure

- `data/`
  - `images/` - Captured images and bird thumbnails
  - `videos/` - Recorded videos
- `motion_sensor.py` - Motion detection module
- `camera.py` - Camera handling module
- `bird_detector.py` - Bird detection using Vision Transformer (ViT)
- `main.py` - Main program

## Local Setup
```uv pip install -e .[windows,dev]```

## Testing
```python -m pytest tests/test_bird_detector.py -v```
