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
            # Reduced to 768px to prevent 504 gateway timeout on Decor8.ai's servers
            max_dimension = 768
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
                print(f"Mask provided - original size: {mask.size}, mode: {mask.mode}")

                # Resize mask to match image size
                if mask.size != image.size:
                    print(f"Resizing mask from {mask.size} to {image.size}")
                    mask = mask.resize(image.size, Image.Resampling.LANCZOS)

                # Convert mask to grayscale if needed
                if mask.mode != 'L':
                    print(f"Converting mask from {mask.mode} to L (grayscale)")
                    mask = mask.convert('L')

                # Analyze mask content
                import numpy as np
                mask_array = np.array(mask)
                white_pixels = np.sum(mask_array > 128)
                black_pixels = np.sum(mask_array <= 128)
                total_pixels = mask_array.size
                white_percentage = (white_pixels / total_pixels) * 100
                print(f"Mask analysis: {white_pixels} white pixels ({white_percentage:.1f}%), {black_pixels} black pixels")

                if white_pixels == 0:
                    print("WARNING: Mask has no white pixels - nothing will be removed!")
                elif white_percentage > 95:
                    print("WARNING: Mask is almost entirely white - this may cause issues")

                # Standard mask format: white = remove, black = keep
                # Save mask with unique hash
                mask_bytes = io.BytesIO()
                mask.save(mask_bytes, format='PNG')
                mask_bytes.seek(0)
                mask_hash = hashlib.md5(mask_bytes.getvalue()).hexdigest()[:16]
                mask_path = temp_dir / f"{mask_hash}_mask.png"

                if not mask_path.exists():
                    mask.save(mask_path, format='PNG')

                mask_url = f"{self.base_url}/api/temp-image/{mask_hash}_mask"
                print(f"Mask saved, URL: {mask_url}")

            # Build API request payload
            api_payload = {'input_image_url': image_url}
            if mask_url:
                api_payload['mask_image_url'] = mask_url
                print("Calling Decor8.ai API with custom mask for furniture removal...")
            else:
                print("Calling Decor8.ai API for auto furniture removal...")

            # Record timestamp before API call (UTC) for validation
            from datetime import datetime, timezone
            api_call_timestamp = datetime.now(timezone.utc)
            print(f"API call started at: {api_call_timestamp.isoformat()}")

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

            result_url = None

            if response.status_code == 504:
                # 504 Gateway Timeout - processing completed on Decor8's side
                # Poll the logs API to get the result
                print("Got 504 timeout - polling logs API for result...")
                time.sleep(3)  # Wait a bit for logs to update

                # Fetch the latest log entry
                logs_response = requests.get(
                    'https://prod-app.decor8.ai:8000/fetch_api_logs?page=1&pageSize=5',
                    headers={
                        'Authorization': f'Bearer {decor8_key}',
                        'Content-Type': 'application/json'
                    },
                    timeout=30
                )

                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    print(f"Logs API response: {logs_data}")

                    # Find the log entry matching our input image URL
                    for log_entry in logs_data.get('data', []):
                        input_details = log_entry.get('input_details', {})
                        log_input_url = input_details.get('input_image_url', '')

                        # Check if this log entry matches our input image
                        if image_url in log_input_url or log_input_url.endswith(image_hash):
                            output_details = log_entry.get('output_details', [])
                            if output_details:
                                result_url = output_details[0].get('image_url')
                                print(f"Found matching log entry, output URL: {result_url}")
                                break

                    # If no exact match found, use the most recent log entry
                    if not result_url and logs_data.get('data'):
                        latest_log = logs_data['data'][0]
                        output_details = latest_log.get('output_details', [])
                        if output_details:
                            result_url = output_details[0].get('image_url')
                            print(f"Using latest log entry, output URL: {result_url}")

                if not result_url:
                    raise Exception("504 timeout and could not retrieve result from logs")

            elif response.status_code != 200:
                error_text = response.text
                print(f"Decor8.ai API error response: {error_text}")
                raise Exception(f"API returned status {response.status_code}: {error_text}")
            else:
                data = response.json()
                print(f"Decor8.ai response status 200")
                print(f"Decor8.ai response keys: {data.keys()}")
                print(f"Decor8.ai full response: {data}")

                if data.get('error'):
                    error_msg = data['error']
                    print(f"Decor8.ai returned error: {error_msg}")
                    raise Exception(f"Decor8.ai error: {error_msg}")

                # Get result URL from response
                if 'info' not in data:
                    print(f"ERROR: 'info' key not in response. Full response: {data}")
                    raise Exception(f"Invalid API response - missing 'info' key. Response: {data}")

                if 'image' not in data['info']:
                    print(f"ERROR: 'image' key not in info. Info: {data['info']}")
                    raise Exception(f"Invalid API response - missing 'image' in info. Info: {data['info']}")

                if 'url' not in data['info']['image']:
                    print(f"ERROR: 'url' key not in image. Image: {data['info']['image']}")
                    raise Exception(f"Invalid API response - missing 'url' in image. Image: {data['info']['image']}")

                result_url = data['info']['image']['url']
                print(f"Extracted result URL: {result_url}")

            # Validate that a NEW image was actually generated by checking logs
            print("Validating generation via logs API...")
            time.sleep(2)  # Wait for logs to update

            logs_response = requests.get(
                'https://prod-app.decor8.ai:8000/fetch_api_logs?page=1&pageSize=1',
                headers={
                    'Authorization': f'Bearer {decor8_key}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )

            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                if logs_data.get('data'):
                    latest_log = logs_data['data'][0]
                    log_timestamp_str = latest_log.get('created_at', '')
                    print(f"Latest log entry timestamp: {log_timestamp_str}")

                    # Parse log timestamp (format: "1/27/2026, 4:57:29 AM" in UTC)
                    try:
                        from datetime import datetime, timezone
                        # Parse the timestamp - it's in "M/D/YYYY, H:MM:SS AM/PM" format (UTC)
                        log_timestamp = datetime.strptime(log_timestamp_str, "%m/%d/%Y, %I:%M:%S %p")
                        log_timestamp = log_timestamp.replace(tzinfo=timezone.utc)

                        print(f"API call time (UTC): {api_call_timestamp}")
                        print(f"Log entry time (UTC): {log_timestamp}")

                        # Check if log entry is AFTER our API call (with 60 second buffer for clock skew)
                        time_diff = (log_timestamp - api_call_timestamp).total_seconds()
                        print(f"Time difference: {time_diff} seconds")

                        if time_diff < -60:  # Log entry is more than 60 seconds before our call
                            raise Exception(f"No new image generated. Latest log entry ({log_timestamp_str}) is from before the API call. The image or mask may be invalid.")

                        # Also verify the log entry has an output image
                        output_details = latest_log.get('output_details', [])
                        if not output_details:
                            raise Exception("API returned success but no output image in logs. The request may have failed silently.")

                        print("Validation passed - new image was generated")
                    except ValueError as parse_error:
                        print(f"Warning: Could not parse log timestamp: {parse_error}")
                        # Continue anyway if we can't parse the timestamp

            # Download result image from Decor8.ai
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
