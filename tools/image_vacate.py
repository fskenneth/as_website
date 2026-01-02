"""
Image Vacating Tool - Remove furniture and objects from staging photos

This module provides functionality to remove items (furniture, decor, lamps, etc.)
from interior photos while preserving structural elements (walls, floors, windows, ceilings).

Uses LaMa (Large Mask Inpainting) for high-quality object removal.

Dependencies:
    pip3 install simple-lama-inpainting torch torchvision pillow numpy opencv-python

For GPU acceleration (optional but recommended):
    pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
"""

import os
import io
import base64
from pathlib import Path
from typing import Union, Tuple, Optional
import numpy as np
from PIL import Image
import cv2


class ImageVacator:
    """Handle image vacating operations using LaMa inpainting"""

    def __init__(self, device: str = "auto"):
        """
        Initialize the ImageVacator

        Args:
            device: 'cuda', 'cpu', or 'auto' (auto-detect GPU)
        """
        self.device = self._setup_device(device)
        self.model = None
        self._model_loaded = False

    def _setup_device(self, device: str) -> str:
        """Setup computation device (GPU or CPU)"""
        if device == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    def _load_model(self):
        """Lazy load the LaMa model"""
        if self._model_loaded:
            return

        try:
            # Disable SSL verification for model download
            import ssl
            import certifi
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            from simple_lama_inpainting import SimpleLama
            self.model = SimpleLama()
            self._model_loaded = True
            print(f"✓ LaMa model loaded successfully on {self.device}")
        except ImportError as e:
            raise ImportError(
                "simple-lama-inpainting not installed. "
                "Install with: pip3 install simple-lama-inpainting torch torchvision"
            ) from e

    def vacate_image(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        mask_input: Optional[Union[str, Path, Image.Image, np.ndarray]] = None,
        auto_detect: bool = True,
        output_path: Optional[Union[str, Path]] = None,
        return_base64: bool = False
    ) -> Union[Image.Image, str, Tuple[Image.Image, str]]:
        """
        Remove objects from an image

        Args:
            image_input: Input image (file path, PIL Image, or numpy array)
            mask_input: Optional mask showing what to remove (white=remove, black=keep)
                       If None and auto_detect=True, will try to detect furniture
            auto_detect: If True and no mask provided, auto-detect objects to remove
            output_path: Optional path to save the result
            return_base64: If True, also return base64-encoded image

        Returns:
            PIL Image, or (PIL Image, base64 string) if return_base64=True
        """
        self._load_model()

        # Load input image
        image = self._load_image(image_input)

        # Generate or load mask
        if mask_input is None:
            if auto_detect:
                mask = self._auto_detect_objects(image)
            else:
                raise ValueError("Either provide a mask or set auto_detect=True")
        else:
            mask = self._load_image(mask_input)

        # Ensure mask is binary (0 or 255)
        mask = self._process_mask(mask)

        # Perform inpainting
        result = self._inpaint(image, mask)

        # Save if output path provided
        if output_path:
            result.save(output_path)
            print(f"✓ Vacated image saved to {output_path}")

        # Return result
        if return_base64:
            b64 = self._image_to_base64(result)
            return result, b64
        return result

    def _load_image(self, image_input: Union[str, Path, Image.Image, np.ndarray]) -> Image.Image:
        """Load image from various input types"""
        if isinstance(image_input, Image.Image):
            return image_input.convert('RGB')
        elif isinstance(image_input, np.ndarray):
            return Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
        elif isinstance(image_input, (str, Path)):
            return Image.open(image_input).convert('RGB')
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def _process_mask(self, mask: Image.Image) -> Image.Image:
        """Convert mask to binary format (0 or 255)"""
        # Convert to grayscale
        mask = mask.convert('L')

        # Convert to numpy for processing
        mask_np = np.array(mask)

        # Binarize: anything > 127 becomes 255 (remove), else 0 (keep)
        mask_np = np.where(mask_np > 127, 255, 0).astype(np.uint8)

        return Image.fromarray(mask_np)

    def _auto_detect_objects(self, image: Image.Image) -> Image.Image:
        """
        Auto-detect furniture and objects to remove

        This is a placeholder for more advanced detection.
        For production, you could use:
        - Segment Anything Model (SAM)
        - YOLO for furniture detection
        - Custom-trained furniture segmentation model

        For now, returns a simple mask based on color/brightness
        """
        # Convert to numpy
        img_np = np.array(image)

        # Create a simple mask that targets darker objects (furniture tends to be darker)
        # This is a VERY basic approach - you'll want to improve this
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Use adaptive thresholding to detect objects
        # This will need tuning based on your specific images
        mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 10
        )

        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # For better results, you should integrate SAM or furniture detection
        print("⚠ Using basic auto-detection. For best results, provide a custom mask.")

        return Image.fromarray(mask)

    def _inpaint(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Perform inpainting using LaMa model"""
        # Convert PIL Images to numpy arrays
        image_np = np.array(image)
        mask_np = np.array(mask.convert('L'))

        # Run LaMa inpainting - returns PIL Image directly
        result = self.model(image_np, mask_np)

        # SimpleLama returns a PIL Image directly
        return result

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def create_manual_mask(
        self,
        image_input: Union[str, Path, Image.Image],
        points: list,
        brush_size: int = 50,
        output_path: Optional[Union[str, Path]] = None
    ) -> Image.Image:
        """
        Create a mask by marking points/regions to remove

        Args:
            image_input: Input image
            points: List of (x, y) coordinates to mark for removal
            brush_size: Size of the brush for each point
            output_path: Optional path to save the mask

        Returns:
            PIL Image mask (white=remove, black=keep)
        """
        image = self._load_image(image_input)

        # Create blank mask (all black = keep everything)
        mask = Image.new('L', image.size, 0)
        mask_np = np.array(mask)

        # Draw white circles at each point (white = remove)
        for x, y in points:
            cv2.circle(mask_np, (int(x), int(y)), brush_size, 255, -1)

        mask = Image.fromarray(mask_np)

        if output_path:
            mask.save(output_path)
            print(f"✓ Mask saved to {output_path}")

        return mask


# Convenience functions for quick usage

def vacate_image_simple(
    image_path: str,
    mask_path: Optional[str] = None,
    output_path: str = "vacated_output.jpg"
) -> str:
    """
    Simple function to vacate an image

    Args:
        image_path: Path to input image
        mask_path: Optional path to mask image
        output_path: Path to save result

    Returns:
        Path to output image
    """
    vacator = ImageVacator()
    vacator.vacate_image(
        image_input=image_path,
        mask_input=mask_path,
        auto_detect=(mask_path is None),
        output_path=output_path
    )
    return output_path


def vacate_with_base64(
    image_base64: str,
    mask_base64: Optional[str] = None
) -> Tuple[str, str]:
    """
    Vacate image provided as base64

    Args:
        image_base64: Base64-encoded input image
        mask_base64: Optional base64-encoded mask

    Returns:
        Tuple of (result_image_base64, mask_used_base64)
    """
    # Decode base64 to PIL Image
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data))

    mask = None
    if mask_base64:
        mask_data = base64.b64decode(mask_base64)
        mask = Image.open(io.BytesIO(mask_data))

    # Process
    vacator = ImageVacator()
    result, result_b64 = vacator.vacate_image(
        image_input=image,
        mask_input=mask,
        auto_detect=(mask is None),
        return_base64=True
    )

    return result_b64, mask_base64 or ""


# Command-line interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Remove furniture and objects from images")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-m", "--mask", help="Mask image path (white=remove, black=keep)")
    parser.add_argument("-o", "--output", default="vacated_output.jpg", help="Output image path")
    parser.add_argument("--auto", action="store_true", help="Auto-detect objects if no mask provided")
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"], help="Device to use")

    args = parser.parse_args()

    print(f"Processing {args.input}...")

    vacator = ImageVacator(device=args.device)
    result = vacator.vacate_image(
        image_input=args.input,
        mask_input=args.mask,
        auto_detect=args.auto or (args.mask is None),
        output_path=args.output
    )

    print(f"✓ Done! Result saved to {args.output}")
