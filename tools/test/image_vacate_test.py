"""
Image Vacating Test Script
Compares 4 different inpainting methods for furniture/object removal

New methods (2025):
1. Replicate LaMa API - Fast, cheap, cloud-based
2. ClipDrop API - High quality, cloud-based
3. Flux Fill Schnell - Best quality, cloud-based
4. Simple LaMa (local) - Lightweight local processing
"""

import time
import numpy as np
from PIL import Image
import cv2
from pathlib import Path
from typing import Dict, Tuple, Optional
import io
import base64
import os


class InpaintingTester:
    """Compare different inpainting methods for object removal"""

    def __init__(self):
        self._lama_model = None
        # API keys from environment
        self.replicate_token = os.getenv('REPLICATE_API_TOKEN', '')
        self.clipdrop_key = os.getenv('CLIPDROP_API_KEY', '')
        # Base URL for generating public image URLs (set by main.py)
        self.base_url = 'http://localhost:5001'

    def _load_lama_model(self):
        """Lazy load the Simple LaMa model (for method 4)"""
        if self._lama_model is not None:
            return self._lama_model

        try:
            from simple_lama_inpainting import SimpleLama
            self._lama_model = SimpleLama()
            return self._lama_model
        except ImportError as e:
            raise ImportError(
                "simple-lama-inpainting not installed. "
                "Install with: pip3 install simple-lama-inpainting"
            ) from e

    def _create_auto_mask(self, image: Image.Image) -> Image.Image:
        """
        Create an automatic mask for furniture/object detection
        Uses adaptive thresholding and edge detection
        """
        # Convert to numpy array
        img_np = np.array(image)

        # Convert to grayscale
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Dilate to expand detected regions
        mask = cv2.dilate(mask, kernel, iterations=2)

        return Image.fromarray(mask)

    def method_1_replicate_lama(
        self,
        image: Image.Image,
        mask: Optional[Image.Image] = None
    ) -> Dict[str, any]:
        """
        Method 1: Replicate LaMa API
        Speed: ~1 second, Cost: $0.00022, Quality: High
        """
        start_time = time.time()

        try:
            import replicate

            if not self.replicate_token:
                raise ValueError("REPLICATE_API_TOKEN not set in environment")

            # Auto-create mask if not provided
            if mask is None:
                mask = self._create_auto_mask(image)

            # Convert images to file-like objects
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)

            mask_bytes = io.BytesIO()
            mask.convert('L').save(mask_bytes, format='PNG')
            mask_bytes.seek(0)

            # Run Replicate API - Using Bria Eraser (SOTA object removal)
            # NOTE: Costs $0.04 per image, requires billing setup
            output = replicate.run(
                "bria/eraser",
                input={
                    "image": image_bytes,
                    "mask": mask_bytes
                }
            )

            # Download result
            import requests
            response = requests.get(output)
            result = Image.open(io.BytesIO(response.content))

            processing_time = time.time() - start_time

            return {
                'name': 'Replicate LaMa API',
                'result': result,
                'processing_time': processing_time,
                'estimated_cost': '$0.00022',
                'quality_rating': '8/10',
                'description': '⚡ Fastest & cheapest - Cloud API, ~1 sec, excellent for production'
            }

        except Exception as e:
            return {
                'error': f'Replicate API error: {str(e)}',
                'name': 'Replicate LaMa API',
                'processing_time': time.time() - start_time,
                'estimated_cost': '$0.00022',
                'quality_rating': 'N/A',
                'description': 'API Error - Check REPLICATE_API_TOKEN'
            }

    def method_2_clipdrop(
        self,
        image: Image.Image,
        mask: Optional[Image.Image] = None
    ) -> Dict[str, any]:
        """
        Method 2: ClipDrop Cleanup API
        Speed: 2-4 seconds, Cost: Contact sales, Quality: High
        """
        start_time = time.time()

        try:
            import requests

            if not self.clipdrop_key:
                raise ValueError("CLIPDROP_API_KEY not set in environment")

            # Auto-create mask if not provided
            if mask is None:
                mask = self._create_auto_mask(image)

            # Convert images to bytes
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)

            mask_bytes = io.BytesIO()
            mask.convert('L').save(mask_bytes, format='PNG')
            mask_bytes.seek(0)

            # Call ClipDrop API
            response = requests.post(
                'https://clipdrop-api.co/cleanup/v1',
                files={
                    'image_file': ('image.png', image_bytes, 'image/png'),
                    'mask_file': ('mask.png', mask_bytes, 'image/png')
                },
                headers={'x-api-key': self.clipdrop_key}
            )

            if response.status_code == 200:
                result = Image.open(io.BytesIO(response.content))
            else:
                raise Exception(f"API returned status {response.status_code}: {response.text}")

            processing_time = time.time() - start_time

            return {
                'name': 'ClipDrop Cleanup API',
                'result': result,
                'processing_time': processing_time,
                'estimated_cost': 'Contact sales',
                'quality_rating': '8.5/10',
                'description': '🎨 High quality - Well-documented, 2-4 sec, free tier available'
            }

        except Exception as e:
            return {
                'error': f'ClipDrop API error: {str(e)}',
                'name': 'ClipDrop Cleanup API',
                'processing_time': time.time() - start_time,
                'estimated_cost': 'Contact sales',
                'quality_rating': 'N/A',
                'description': 'API Error - Check CLIPDROP_API_KEY'
            }

    def method_3_flux_fill(
        self,
        image: Image.Image,
        mask: Optional[Image.Image] = None
    ) -> Dict[str, any]:
        """
        Method 3: Flux Fill Schnell (via Replicate)
        Speed: 2-5 seconds, Cost: $0.003, Quality: Best
        """
        start_time = time.time()

        try:
            import replicate

            if not self.replicate_token:
                raise ValueError("REPLICATE_API_TOKEN not set in environment")

            # Auto-create mask if not provided
            if mask is None:
                mask = self._create_auto_mask(image)

            # Convert images to file-like objects
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)

            mask_bytes = io.BytesIO()
            mask.convert('L').save(mask_bytes, format='PNG')
            mask_bytes.seek(0)

            # Run Replicate Flux Fill API (schnell variant for speed)
            output = replicate.run(
                "black-forest-labs/flux-fill-dev",
                input={
                    "image": image_bytes,
                    "mask": mask_bytes,
                    "prompt": "empty room, clean background",
                    "num_inference_steps": 28
                }
            )

            # Download result
            import requests
            if isinstance(output, list):
                output = output[0]
            response = requests.get(str(output))
            result = Image.open(io.BytesIO(response.content))

            processing_time = time.time() - start_time

            return {
                'name': 'Flux Fill (Replicate)',
                'result': result,
                'processing_time': processing_time,
                'estimated_cost': '$0.003',
                'quality_rating': '9/10',
                'description': '🏆 Best quality - Handles complex furniture/shadows, 2-5 sec'
            }

        except Exception as e:
            return {
                'error': f'Flux Fill API error: {str(e)}',
                'name': 'Flux Fill (Replicate)',
                'processing_time': time.time() - start_time,
                'estimated_cost': '$0.003',
                'quality_rating': 'N/A',
                'description': 'API Error - Check REPLICATE_API_TOKEN'
            }

    def method_4_simple_lama_local(
        self,
        image: Image.Image,
        mask: Optional[Image.Image] = None
    ) -> Dict[str, any]:
        """
        Method 4: Simple LaMa (Local Processing)
        Speed: 3-5 seconds, Cost: Free, Quality: Good
        Lightweight local model, won't freeze server
        """
        start_time = time.time()

        try:
            # Auto-create mask if not provided
            if mask is None:
                mask = self._create_auto_mask(image)

            # Load model
            lama = self._load_lama_model()

            # Convert image to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert mask to L mode
            if mask.mode != 'L':
                mask = mask.convert('L')

            # Perform inpainting
            result = lama(image, mask)

            processing_time = time.time() - start_time

            return {
                'name': 'Simple LaMa (Local)',
                'result': result,
                'processing_time': processing_time,
                'estimated_cost': '$0.00 (Free)',
                'quality_rating': '7/10',
                'description': '💻 Local processing - No API cost, lightweight, ~3-5 sec'
            }

        except Exception as e:
            return {
                'error': f'Simple LaMa error: {str(e)}',
                'name': 'Simple LaMa (Local)',
                'processing_time': time.time() - start_time,
                'estimated_cost': '$0.00 (Free)',
                'quality_rating': 'N/A',
                'description': 'Error - Install: pip3 install simple-lama-inpainting'
            }

    def method_5_decor8ai(
        self,
        image: Image.Image,
        mask: Optional[Image.Image] = None
    ) -> Dict[str, any]:
        """
        Method 5: Decor8.ai API
        Speed: Fast (synchronous), Cost: Check pricing, Quality: High
        Specifically designed for removing furniture from room images
        """
        start_time = time.time()

        try:
            import requests
            import hashlib
            from pathlib import Path

            decor8_key = os.getenv('DECOR8_API_KEY', '')
            if not decor8_key:
                raise ValueError("DECOR8_API_KEY not set in environment")

            # Decor8.ai requires image URLs, not direct uploads
            # Save image to temp directory and serve it via our endpoint
            temp_dir = Path('static/temp_images')
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Resize image if too large (Decor8.ai works better with smaller images)
            max_dimension = 1920
            if image.width > max_dimension or image.height > max_dimension:
                print(f"Resizing image from {image.width}x{image.height}...")
                ratio = min(max_dimension / image.width, max_dimension / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"Resized to {image.width}x{image.height}")

            # Generate image ID based on content hash (avoid duplicates)
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG', optimize=True)
            img_bytes.seek(0)
            image_hash = hashlib.md5(img_bytes.getvalue()).hexdigest()[:16]
            temp_path = temp_dir / f"{image_hash}.png"

            # Save image to temp directory (only if not already exists)
            if not temp_path.exists():
                image.save(temp_path, format='PNG', optimize=True)

            # Build public URL
            image_url = f"{self.base_url}/api/temp-image/{image_hash}"
            print(f"Image saved, URL: {image_url}")

            # Handle mask if provided
            mask_url = None
            if mask:
                # Resize mask to match image size
                if mask.size != image.size:
                    mask = mask.resize(image.size, Image.Resampling.LANCZOS)

                # Convert mask to grayscale if needed
                if mask.mode != 'L':
                    mask = mask.convert('L')

                # INVERT mask for Decor8.ai (expects black = remove, white = keep)
                import numpy as np
                mask_array = np.array(mask)
                inverted_array = 255 - mask_array
                mask = Image.fromarray(inverted_array.astype('uint8'), mode='L')
                print("Mask inverted for Decor8.ai (black = remove, white = keep)")

                # Save mask with unique hash
                mask_bytes = io.BytesIO()
                mask.save(mask_bytes, format='PNG')
                mask_bytes.seek(0)
                mask_hash = hashlib.md5(mask_bytes.getvalue()).hexdigest()[:16]
                mask_path = temp_dir / f"{mask_hash}_mask.png"

                if not mask_path.exists():
                    mask.save(mask_path, format='PNG')

                mask_url = f"{self.base_url}/api/temp-image/{mask_hash}_mask"
                print(f"Mask saved (inverted), URL: {mask_url}")

            # Build API request payload
            api_payload = {'input_image_url': image_url}
            if mask_url:
                api_payload['mask_image_url'] = mask_url
                print("Calling Decor8.ai API with custom mask for furniture removal...")
            else:
                print("Calling Decor8.ai API for auto furniture removal...")

            # Call Decor8.ai API
            response = requests.post(
                'https://api.decor8.ai/remove_objects_from_room',
                headers={
                    'Authorization': f'Bearer {decor8_key}',
                    'Content-Type': 'application/json'
                },
                json=api_payload,
                timeout=600  # 10 minutes timeout for large/complex images
            )

            print(f"Decor8.ai response status: {response.status_code}")

            if response.status_code != 200:
                error_text = response.text
                print(f"Decor8.ai API error response: {error_text}")
                raise Exception(f"API returned status {response.status_code}: {error_text}")

            data = response.json()
            print(f"Decor8.ai response data: {data}")

            if data.get('error'):
                error_msg = data['error']
                print(f"Decor8.ai returned error: {error_msg}")
                raise Exception(f"Decor8.ai error: {error_msg}")

            # Download result image from Decor8.ai
            result_url = data['info']['image']['url']
            print(f"Result ready: {result_url}")
            result_response = requests.get(result_url)
            result = Image.open(io.BytesIO(result_response.content))

            # Clean up temp file
            try:
                temp_path.unlink()
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temp file {temp_path}: {cleanup_error}")

            processing_time = time.time() - start_time

            return {
                'name': 'Decor8.ai API',
                'result': result,
                'processing_time': processing_time,
                'estimated_cost': 'Check pricing',
                'quality_rating': '9/10',
                'description': '🏠 Purpose-built - Designed specifically for interior design & furniture removal'
            }

        except Exception as e:
            return {
                'error': f'Decor8.ai API error: {str(e)}',
                'name': 'Decor8.ai API',
                'processing_time': time.time() - start_time,
                'estimated_cost': 'Check pricing',
                'quality_rating': 'N/A',
                'description': 'API Error - Check DECOR8_API_KEY'
            }

    def compare_all_methods(
        self,
        image: Image.Image,
        mask: Optional[Image.Image] = None
    ) -> Dict[str, Dict]:
        """
        Run all 5 methods and compare results

        Returns:
            Dictionary with results from all methods
        """
        results = {}

        try:
            print("Running Method 1: Replicate LaMa API...")
            results['method_1'] = self.method_1_replicate_lama(image, mask)
        except Exception as e:
            print(f"Method 1 failed: {e}")
            results['method_1'] = {'error': str(e)}

        try:
            print("Running Method 2: ClipDrop API...")
            results['method_2'] = self.method_2_clipdrop(image, mask)
        except Exception as e:
            print(f"Method 2 failed: {e}")
            results['method_2'] = {'error': str(e)}

        try:
            print("Running Method 3: Flux Fill...")
            results['method_3'] = self.method_3_flux_fill(image, mask)
        except Exception as e:
            print(f"Method 3 failed: {e}")
            results['method_3'] = {'error': str(e)}

        try:
            print("Running Method 4: Simple LaMa (local)...")
            results['method_4'] = self.method_4_simple_lama_local(image, mask)
        except Exception as e:
            print(f"Method 4 failed: {e}")
            results['method_4'] = {'error': str(e)}

        return results


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def base64_to_image(base64_str: str) -> Image.Image:
    """Convert base64 string to PIL Image"""
    image_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_data))


# Example usage
if __name__ == "__main__":
    # Test with a sample image
    tester = InpaintingTester()

    # Load test image (replace with your image path)
    test_image_path = "test_room.jpg"
    if Path(test_image_path).exists():
        image = Image.open(test_image_path)

        # Run comparison
        results = tester.compare_all_methods(image)

        # Print results
        for method_key, result in results.items():
            if 'error' in result:
                print(f"\n{method_key}: ERROR - {result['error']}")
            else:
                print(f"\n{result['name']}:")
                print(f"  Processing Time: {result['processing_time']:.2f}s")
                print(f"  Estimated Cost: {result['estimated_cost']}")
                print(f"  Quality: {result['quality_rating']}")
                print(f"  Description: {result['description']}")

                # Save result
                if 'result' in result:
                    output_path = f"result_{method_key}.png"
                    result['result'].save(output_path)
                    print(f"  Saved to: {output_path}")
    else:
        print(f"Test image not found: {test_image_path}")
        print("Please provide a test image path")
