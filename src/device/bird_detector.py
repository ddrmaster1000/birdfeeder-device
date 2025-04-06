"""Bird detection module using ViT."""
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BirdDetector:
    def __init__(self):
        """Initialize the bird detector with ViT."""
        model_name = "google/vit-base-patch16-224"
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        
        # Bird-related class indices in ImageNet
        self.bird_class_indices = {
            7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 80,
            81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97,
            98, 99, 100, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137,
            138, 139, 140, 141, 142, 143, 144, 145, 146, 448
        }

    def detect_bird(self, image_path: Path) -> tuple[bool, Path | None]:
        """
        Detect if a bird is present in the image and return cropped thumbnail if found.
        Returns (is_bird_present, thumbnail_path)
        """
        image = Image.open(image_path)
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        logits = outputs.logits
        # model predicts one of the 1000 ImageNet classes
        predicted_class_idx = logits.argmax(-1).item()
        predicted_class = self.model.config.id2label[predicted_class_idx]
        logger.info(f"Predicted class: {predicted_class}")
        
        # Check if predicted class is bird-related
        is_bird = predicted_class_idx in self.bird_class_indices
        
        if is_bird:
            # Create thumbnail from original image
            thumbnail_size = (224, 224)
            thumbnail = image.copy()
            thumbnail.thumbnail(thumbnail_size)
            
            # Save thumbnail
            thumbnail_path = image_path.parent / f"{image_path.stem}_thumb{image_path.suffix}"
            thumbnail.save(thumbnail_path)
            return True, thumbnail_path
        
        return False, None
