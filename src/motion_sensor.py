"""Motion sensor module supporting both Windows simulation and Raspberry Pi GPIO."""
import platform
import time
import random

class BaseMotionSensor:
    """Base class for motion sensors."""
    def check_motion(self) -> bool:
        """Check if motion is currently detected."""
        raise NotImplementedError

    def cleanup(self):
        """Clean up resources."""
        pass

class WindowsMotionSensor(BaseMotionSensor):
    """Simulated motion sensor for Windows testing."""
    def __init__(self):
        """Initialize simulated motion sensor."""
        self.last_motion = time.time()
        self.motion_interval = 5  # Simulate motion every 5 seconds

    def check_motion(self) -> bool:
        """Simulate motion detection."""
        current_time = time.time()
        if current_time - self.last_motion > self.motion_interval:
            # 90% chance of detecting motion when interval has passed
            if random.random() < 0.9:
                self.last_motion = current_time
                return True
        return False

class RaspberryPiMotionSensor(BaseMotionSensor):
    """Hardware motion sensor implementation for Raspberry Pi."""
    def __init__(self, pin: int = 17):
        """Initialize motion sensor on specified GPIO pin."""
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.pin = pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
        except ImportError:
            raise ImportError("RPi.GPIO is required for Raspberry Pi motion sensor")

    def check_motion(self) -> bool:
        """Check if motion is currently detected."""
        return self.GPIO.input(self.pin) == self.GPIO.HIGH

    def cleanup(self):
        """Clean up GPIO resources."""
        self.GPIO.cleanup(self.pin)

def create_motion_sensor(pin: int = 17) -> BaseMotionSensor:
    """Factory function to create appropriate motion sensor based on platform."""
    if platform.system() == "Windows":
        return WindowsMotionSensor()
    else:
        return RaspberryPiMotionSensor(pin)
