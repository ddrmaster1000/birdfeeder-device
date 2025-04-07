"""Tests for the bird detector module."""
import pytest
from pathlib import Path
from PIL import Image
import shutil

from bird_detector import BirdDetector

TEST_IMAGES_DIR = Path(__file__).parent / "images"
FINCH_IMAGE_PATH = TEST_IMAGES_DIR / "finch.jpg"
CAT_IMAGE_PATH = TEST_IMAGES_DIR / "cat.jpg"

@pytest.fixture
def bird_detector():
    """Create a BirdDetector instance for testing."""
    return BirdDetector()

@pytest.fixture
def test_bird_image_path(tmp_path):
    """Copy test bird image to a temporary directory."""
    # Copy the test image to temp directory to avoid modifying original
    temp_image_path = tmp_path / "finch.jpg"
    shutil.copy2(FINCH_IMAGE_PATH, temp_image_path)
    return temp_image_path

@pytest.fixture
def test_non_bird_image_path(tmp_path):
    """Copy test non-bird image to a temporary directory."""
    # Copy the test image to temp directory to avoid modifying original
    temp_image_path = tmp_path / "cat.jpg"
    shutil.copy2(CAT_IMAGE_PATH, temp_image_path)
    return temp_image_path

def test_bird_detection(bird_detector, test_bird_image_path):
    """Test bird detection with a real bird image (finch)."""
    # Run detection
    is_bird, thumbnail_path = bird_detector.detect_bird(test_bird_image_path)

    # Since we're using a real bird image, we expect it to be detected
    assert is_bird is True, "Bird detector failed to recognize the finch image"
    assert thumbnail_path is not None
    assert thumbnail_path.exists()
    
    # Verify thumbnail size - width should be 224 and height should maintain aspect ratio
    with Image.open(thumbnail_path) as thumbnail:
        assert thumbnail.size[0] == 224, "Thumbnail width should be 224 pixels"
        assert thumbnail.size[1] > 0, "Thumbnail height should be positive"
    
    # Cleanup
    thumbnail_path.unlink(missing_ok=True)

def test_non_bird_detection(bird_detector, test_non_bird_image_path):
    """Test bird detection with a non-bird image (chain)."""
    # Run detection
    is_bird, thumbnail_path = bird_detector.detect_bird(test_non_bird_image_path)

    # Since we're using a non-bird image, we expect it not to be detected as a bird
    assert is_bird is False, "Bird detector incorrectly identified a chain as a bird"
    assert thumbnail_path is None, "Thumbnail should not be created for non-bird images"
