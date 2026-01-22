"""
Test API routes for inpainting testing - separated from main.py for cleaner codebase.
To use during development, import and register these routes in main.py.

Usage in main.py (for development):
    from tools.test.test_api_routes import register_test_routes
    register_test_routes(rt)
"""

import base64
import io
import json
from pathlib import Path
from datetime import datetime
from starlette.responses import Response, JSONResponse
from starlette.requests import Request


def register_test_routes(rt):
    """Register all test API routes with the FastHTML router"""

    @rt('/api/temp-image/{image_id}')
    async def serve_temp_image(image_id: str):
        """Serve temporary test images for external APIs"""
        temp_dir = Path('static/temp_images')
        image_path = temp_dir / f"{image_id}.png"

        if not image_path.exists():
            return Response(content=b'Image not found', status_code=404)

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            return Response(
                content=image_data,
                media_type='image/png',
                headers={'Cache-Control': 'public, max-age=3600'}
            )
        except Exception as e:
            print(f"Error serving temp image: {e}")
            return Response(content=b'Error loading image', status_code=500)

    @rt('/api/test-inpainting', methods=['POST'])
    async def test_inpainting(request: Request):
        """
        Decor8.ai furniture removal API endpoint

        Request body:
            {
                "image": "base64-encoded image",
                "method": 5 (kept for compatibility)
            }

        Returns:
            {
                "success": true,
                "result": {...}
            }
        """
        from PIL import Image
        from tools.test.image_vacate_test import InpaintingTester, image_to_base64

        try:
            data = await request.json()
            image_data = data.get('image', '')

            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Initialize tester
            tester = InpaintingTester()

            # Set the public base URL (use public IP instead of localhost)
            tester.base_url = 'http://174.89.176.147:5001'

            # Run Decor8.ai method
            result = tester.method_5_decor8ai(image)

            # Convert PIL image to base64 for response
            result_base64 = None
            if 'result' in result:
                result_image = result.pop('result')
                result_base64 = image_to_base64(result_image)
                result['result_base64'] = result_base64

                # Save before/after pair to history (as files, not base64)
                try:
                    import uuid
                    timestamp = datetime.now()
                    timestamp_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
                    unique_id = uuid.uuid4().hex[:8]

                    # Save both images to areas folder
                    areas_dir = Path('static/images/areas')
                    areas_dir.mkdir(parents=True, exist_ok=True)

                    input_filename = f"{unique_id}_{timestamp_str}_before.png"
                    input_path = areas_dir / input_filename
                    input_bytes = base64.b64decode(image_data)
                    with open(input_path, 'wb') as f:
                        f.write(input_bytes)

                    output_filename = f"{unique_id}_{timestamp_str}_after.png"
                    output_path = areas_dir / output_filename
                    output_bytes = base64.b64decode(result_base64)
                    with open(output_path, 'wb') as f:
                        f.write(output_bytes)

                    # Update history file with URLs
                    history_file = Path('tools/model_3d/inpainting_history.json')
                    history = []
                    if history_file.exists():
                        with open(history_file, 'r') as f:
                            history = json.load(f)

                    # Add new entry with URLs
                    history.append({
                        'timestamp': timestamp.isoformat(),
                        'input_url': f'/static/images/areas/{input_filename}',
                        'output_url': f'/static/images/areas/{output_filename}',
                        'processing_time': result.get('processing_time', 0),
                        'source': 'api_test'
                    })

                    # Keep only last 20 entries
                    history = history[-20:]

                    with open(history_file, 'w') as f:
                        json.dump(history, f, indent=2)

                    print(f"Saved: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"Failed to save history: {e}")
                    import traceback
                    traceback.print_exc()

            return JSONResponse({
                'success': True,
                'method': 5,
                'result': result
            })

        except Exception as e:
            print(f"Test inpainting error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    @rt('/api/inpainting-history')
    def get_inpainting_history():
        """Get all saved before/after image pairs"""
        try:
            history_file = Path('tools/model_3d/inpainting_history.json')
            if not history_file.exists():
                return JSONResponse({'history': []})

            with open(history_file, 'r') as f:
                history = json.load(f)

            return JSONResponse({'history': history})
        except Exception as e:
            print(f"Error loading history: {e}")
            return JSONResponse({'error': str(e)}, status_code=500)

    # =========================================================================
    # BACKGROUND REMOVAL ENDPOINTS
    # =========================================================================

    @rt('/api/remove-background', methods=['POST'])
    async def remove_background(request: Request):
        """
        Remove background from furniture image using selected method.

        Request body:
            {
                "image": "base64-encoded image",
                "method": "rembg" | "removebg" | "photoroom"
            }

        Returns:
            {
                "success": true,
                "result_base64": "...",
                "processing_time": 1.23
            }
        """
        import time
        from PIL import Image

        try:
            data = await request.json()
            image_data = data.get('image', '')
            method = data.get('method', 'rembg')

            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            start_time = time.time()
            result_image = None
            method_info = ""

            if method == 'rembg':
                result_image, method_info = await remove_bg_rembg(image)
            elif method == 'removebg':
                result_image, method_info = await remove_bg_removebg(image_bytes)
            elif method == 'photoroom':
                result_image, method_info = await remove_bg_photoroom(image_bytes)
            else:
                return JSONResponse({'success': False, 'error': f'Unknown method: {method}'}, status_code=400)

            processing_time = time.time() - start_time

            # Convert result to base64
            buffered = io.BytesIO()
            result_image.save(buffered, format="PNG")
            result_base64 = base64.b64encode(buffered.getvalue()).decode()

            return JSONResponse({
                'success': True,
                'result_base64': result_base64,
                'processing_time': processing_time,
                'method': method,
                'info': method_info
            })

        except Exception as e:
            print(f"Background removal error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    # =========================================================================
    # 2D TO 3D CONVERSION ENDPOINTS
    # =========================================================================

    @rt('/api/convert-to-3d', methods=['POST'])
    async def convert_to_3d(request: Request):
        """
        Convert 2D image to 3D model using selected method.

        Request body:
            {
                "image": "base64-encoded image (preferably with transparent background)",
                "method": "sam3d" | "sharp" | "triposr"
            }

        Returns:
            {
                "success": true,
                "model_url": "/path/to/model.glb",
                "model_base64": "...",
                "processing_time": 5.67,
                "format": "glb"
            }
        """
        import time
        from PIL import Image

        try:
            data = await request.json()
            image_data = data.get('image', '')
            method = data.get('method', 'sam3d')
            prompt = data.get('prompt', None)  # Optional text guidance
            negative_prompt = data.get('negative_prompt', None)
            # Tripo3D specific parameters
            pbr = data.get('pbr', True)
            enable_image_autofix = data.get('enable_image_autofix', True)
            orientation = data.get('orientation', 'align_image')

            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            start_time = time.time()
            result = None

            if method == 'sam3d':
                result = await convert_3d_sam3d(image, image_bytes)
            elif method == 'sharp':
                result = await convert_3d_sharp(image, image_bytes)
            elif method == 'triposr':
                result = await convert_3d_triposr(image_bytes)
            elif method == 'tripo3d':
                result = await convert_3d_tripo3d(
                    image_bytes,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    pbr=pbr,
                    enable_image_autofix=enable_image_autofix,
                    orientation=orientation
                )
            else:
                return JSONResponse({'success': False, 'error': f'Unknown method: {method}'}, status_code=400)

            processing_time = time.time() - start_time

            # Save to 3D model history
            input_thumbnail_url = None
            input_original_url = None
            try:
                import uuid
                from datetime import datetime
                timestamp = datetime.now()
                unique_id = uuid.uuid4().hex[:8]

                # Save input image thumbnail and original
                thumbnail_dir = Path('static/models/thumbnails')
                thumbnail_dir.mkdir(parents=True, exist_ok=True)
                thumbnail_filename = f"{unique_id}_input.png"
                original_filename = f"{unique_id}_original.png"
                thumbnail_path = thumbnail_dir / thumbnail_filename
                original_path = thumbnail_dir / original_filename

                # Save thumbnail (small, for button icon)
                thumb = image.copy()
                thumb.thumbnail((200, 200))
                thumb.save(thumbnail_path, 'PNG')

                # Save original image (full size, for modal display)
                image.save(original_path, 'PNG')

                input_thumbnail_url = f'/static/models/thumbnails/{thumbnail_filename}'
                input_original_url = f'/static/models/thumbnails/{original_filename}'

                # Update history file
                history_file = Path('tools/model_3d/model3d_history.json')
                history = []
                if history_file.exists():
                    with open(history_file, 'r') as f:
                        history = json.load(f)

                history.append({
                    'timestamp': timestamp.isoformat(),
                    'input_thumbnail': input_thumbnail_url,
                    'input_original': input_original_url,
                    'model_url': result.get('model_url'),
                    'format': result.get('format', 'glb'),
                    'method': method,
                    'processing_time': processing_time,
                    'info': result.get('info', '')
                })

                # Keep only last 20 entries
                history = history[-20:]

                with open(history_file, 'w') as f:
                    json.dump(history, f, indent=2)

                print(f"Saved 3D model: {result.get('model_url')}")
            except Exception as e:
                print(f"Failed to save 3D history: {e}")

            return JSONResponse({
                'success': True,
                'model_url': result.get('model_url'),
                'model_base64': result.get('model_base64'),
                'processing_time': processing_time,
                'format': result.get('format', 'glb'),
                'method': method,
                'info': result.get('info', ''),
                'input_thumbnail': input_thumbnail_url,
                'input_original': input_original_url
            })

        except Exception as e:
            print(f"3D conversion error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    @rt('/api/model3d-history')
    def get_model3d_history():
        """Get all saved 3D model conversions"""
        try:
            history_file = Path('tools/model_3d/model3d_history.json')
            if not history_file.exists():
                return JSONResponse({'history': []})

            with open(history_file, 'r') as f:
                history = json.load(f)

            return JSONResponse({'history': history})
        except Exception as e:
            print(f"Error loading 3D history: {e}")
            return JSONResponse({'error': str(e)}, status_code=500)

    @rt('/api/delete-model3d', methods=['POST'])
    async def delete_model3d(request: Request):
        """
        Delete a 3D model from history and optionally delete the files.

        Request body:
            {
                "index": 0,  // Index in the history array
                "model_url": "/static/models/xxx.glb"  // For verification
            }

        Returns:
            {"success": true}
        """
        try:
            data = await request.json()
            index = data.get('index')
            model_url = data.get('model_url')

            if index is None:
                return JSONResponse({'success': False, 'error': 'Index is required'}, status_code=400)

            history_file = Path('tools/model_3d/model3d_history.json')
            if not history_file.exists():
                return JSONResponse({'success': False, 'error': 'No history file found'}, status_code=404)

            with open(history_file, 'r') as f:
                history = json.load(f)

            if index < 0 or index >= len(history):
                return JSONResponse({'success': False, 'error': 'Invalid index'}, status_code=400)

            # Verify the model URL matches (optional safety check)
            item = history[index]
            if model_url and item.get('model_url') != model_url:
                return JSONResponse({'success': False, 'error': 'Model URL mismatch'}, status_code=400)

            # Try to delete the actual files
            try:
                # Delete the GLB model file
                if item.get('model_url'):
                    model_path = Path('.' + item['model_url'])  # Convert /static/... to ./static/...
                    if model_path.exists():
                        model_path.unlink()
                        print(f"Deleted model file: {model_path}")

                # Delete the thumbnail
                if item.get('input_thumbnail'):
                    thumb_path = Path('.' + item['input_thumbnail'])
                    if thumb_path.exists():
                        thumb_path.unlink()
                        print(f"Deleted thumbnail: {thumb_path}")

                # Delete the original image
                if item.get('input_original'):
                    original_path = Path('.' + item['input_original'])
                    if original_path.exists():
                        original_path.unlink()
                        print(f"Deleted original: {original_path}")
            except Exception as file_error:
                print(f"Warning: Could not delete files: {file_error}")
                # Continue even if file deletion fails

            # Remove from history
            history.pop(index)

            # Save updated history
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)

            print(f"Deleted 3D model at index {index}")
            return JSONResponse({'success': True})

        except Exception as e:
            print(f"Delete 3D model error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    # =========================================================================
    # MODEL STATE PERSISTENCE ENDPOINTS
    # =========================================================================

    @rt('/api/model-state', methods=['POST'])
    async def save_model_state_endpoint(request: Request):
        """
        Save or update a 3D model's placement state.

        Request body:
            {
                "background_image": "/static/images/areas/xxx.jpg",
                "model_url": "/static/models/xxx.glb",
                "position_x": 0.5,
                "position_y": -0.3,
                "position_z": 0,
                "scale": 1.2,
                "rotation_y": 0.5,
                "tilt": 0.1745,
                "brightness": 2.5,
                "staging_id": 123  // optional
            }

        Returns:
            {"success": true, "id": 1}
        """
        from tools.user_db import save_model_state

        try:
            data = await request.json()
            background_image = data.get('background_image')
            model_url = data.get('model_url')

            if not background_image or not model_url:
                return JSONResponse({'success': False, 'error': 'background_image and model_url are required'}, status_code=400)

            state = {
                'position_x': data.get('position_x', 0),
                'position_y': data.get('position_y', 0),
                'position_z': data.get('position_z', 0),
                'scale': data.get('scale', 1),
                'rotation_y': data.get('rotation_y', 0),
                'tilt': data.get('tilt', 0.1745),
                'brightness': data.get('brightness', 2.5)
            }

            staging_id = data.get('staging_id')

            result = save_model_state(background_image, model_url, state, staging_id)
            return JSONResponse(result)

        except Exception as e:
            print(f"Save model state error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    @rt('/api/model-state')
    async def get_model_state_endpoint(request: Request):
        """
        Get the saved state for a specific model on a background image.

        Query params:
            ?background_image=/static/images/areas/xxx.jpg&model_url=/static/models/xxx.glb

        Returns:
            {
                "position_x": 0.5,
                "position_y": -0.3,
                "position_z": 0,
                "scale": 1.2,
                "rotation_y": 0.5,
                "tilt": 0.1745,
                "brightness": 2.5
            }
            or null if not found
        """
        from tools.user_db import get_model_state

        try:
            background_image = request.query_params.get('background_image')
            model_url = request.query_params.get('model_url')

            if not background_image or not model_url:
                return JSONResponse({'error': 'background_image and model_url query params are required'}, status_code=400)

            state = get_model_state(background_image, model_url)
            return JSONResponse(state)

        except Exception as e:
            print(f"Get model state error: {e}")
            return JSONResponse({'error': str(e)}, status_code=500)

    @rt('/api/model-state', methods=['DELETE'])
    async def delete_model_state_endpoint(request: Request):
        """
        Delete a saved model state.

        Query params:
            ?background_image=/static/images/areas/xxx.jpg&model_url=/static/models/xxx.glb

        Returns:
            {"success": true}
        """
        from tools.user_db import delete_model_state

        try:
            background_image = request.query_params.get('background_image')
            model_url = request.query_params.get('model_url')

            if not background_image or not model_url:
                return JSONResponse({'success': False, 'error': 'background_image and model_url query params are required'}, status_code=400)

            result = delete_model_state(background_image, model_url)
            return JSONResponse(result)

        except Exception as e:
            print(f"Delete model state error: {e}")
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    @rt('/api/models-for-background')
    async def get_all_models_endpoint(request: Request):
        """
        Get all saved models for a specific background image.

        Query params:
            ?background_image=/static/images/areas/xxx.jpg

        Returns:
            [
                {
                    "model_url": "/static/models/xxx.glb",
                    "instance_id": 0,
                    "position_x": 0.5,
                    ...
                },
                ...
            ]
        """
        from tools.user_db import get_all_models_for_background

        try:
            background_image = request.query_params.get('background_image')

            if not background_image:
                return JSONResponse({'error': 'background_image query param is required'}, status_code=400)

            models = get_all_models_for_background(background_image)
            return JSONResponse(models)

        except Exception as e:
            print(f"Get all models error: {e}")
            return JSONResponse({'error': str(e)}, status_code=500)

    @rt('/api/save-all-models', methods=['POST'])
    async def save_all_models_endpoint(request: Request):
        """
        Save all model instances for a background image.
        Replaces all existing models with the new set.

        Request body:
            {
                "background_image": "/static/images/areas/xxx.jpg",
                "model_url": "/static/models/xxx.glb",
                "models": [
                    {
                        "position_x": 0.5,
                        "position_y": -0.3,
                        "position_z": 0,
                        "scale": 1.2,
                        "rotation_y": 0.5,
                        "tilt": 0.1745,
                        "brightness": 2.5
                    },
                    ...
                ],
                "staging_id": 123  // optional
            }

        Returns:
            {"success": true, "count": 2}
        """
        from tools.user_db import save_all_model_states

        try:
            data = await request.json()
            background_image = data.get('background_image')
            model_url = data.get('model_url')
            models = data.get('models', [])

            if not background_image or not model_url:
                return JSONResponse({'success': False, 'error': 'background_image and model_url are required'}, status_code=400)

            staging_id = data.get('staging_id')

            result = save_all_model_states(background_image, model_url, models, staging_id)
            return JSONResponse(result)

        except Exception as e:
            print(f"Save all models error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    @rt('/api/tripo-balance')
    async def get_tripo_balance():
        """Get Tripo3D account balance and credits"""
        import os
        import httpx

        try:
            api_key = os.getenv('TRIPO_API_KEY')
            if not api_key:
                return JSONResponse({'error': 'TRIPO_API_KEY not set in environment'}, status_code=500)

            base_url = "https://api.tripo3d.ai/v2/openapi"
            headers = {"Authorization": f"Bearer {api_key}"}

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{base_url}/user/balance",
                    headers=headers
                )

                if response.status_code != 200:
                    return JSONResponse({'error': f'API error: {response.status_code}'}, status_code=500)

                data = response.json()
                if data.get("code") != 0:
                    return JSONResponse({'error': 'Failed to fetch balance'}, status_code=500)

                return JSONResponse({
                    'success': True,
                    'balance': data.get('data', {})
                })

        except Exception as e:
            print(f"Error fetching Tripo3D balance: {e}")
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

    print("Test API routes registered: /api/temp-image, /api/test-inpainting, /api/inpainting-history, /api/remove-background, /api/convert-to-3d, /api/model3d-history, /api/model-state, /api/models-for-background, /api/save-all-models, /api/tripo-balance")


# =========================================================================
# BACKGROUND REMOVAL IMPLEMENTATIONS
# =========================================================================

async def remove_bg_rembg(image):
    """Remove background using rembg (local, free)"""
    try:
        from rembg import remove
        result = remove(image)
        return result, "rembg (u2net model)"
    except ImportError:
        # Fallback: return image with simple threshold-based removal
        print("rembg not installed. Install with: pip3 install rembg")
        raise Exception("rembg not installed. Run: pip3 install rembg[gpu]")


async def remove_bg_removebg(image_bytes):
    """Remove background using Remove.bg API"""
    import os
    import httpx

    api_key = os.getenv('REMOVEBG_API_KEY')
    if not api_key:
        raise Exception("REMOVEBG_API_KEY not set in environment")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': ('image.png', image_bytes, 'image/png')},
            data={'size': 'auto'},
            headers={'X-Api-Key': api_key},
            timeout=60.0
        )

        if response.status_code == 200:
            from PIL import Image
            result_image = Image.open(io.BytesIO(response.content))
            return result_image, "Remove.bg API"
        else:
            raise Exception(f"Remove.bg API error: {response.status_code} - {response.text}")


async def remove_bg_photoroom(image_bytes):
    """Remove background using Photoroom API"""
    import os
    import httpx

    api_key = os.getenv('PHOTOROOM_API_KEY')
    if not api_key:
        raise Exception("PHOTOROOM_API_KEY not set in environment")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://sdk.photoroom.com/v1/segment',
            files={'image_file': ('image.png', image_bytes, 'image/png')},
            headers={'x-api-key': api_key},
            timeout=60.0
        )

        if response.status_code == 200:
            from PIL import Image
            result_image = Image.open(io.BytesIO(response.content))
            return result_image, "Photoroom API"
        else:
            raise Exception(f"Photoroom API error: {response.status_code} - {response.text}")


# =========================================================================
# 2D TO 3D CONVERSION IMPLEMENTATIONS
# =========================================================================

async def convert_3d_sam3d(image, image_bytes):
    """Convert to 3D using TripoSR via Hugging Face Space (renamed from SAM3D)"""
    # SAM3D doesn't actually exist for single-image 3D reconstruction
    # Using TripoSR HF Space instead as it's the best free option
    return await convert_3d_triposr_hf(image, image_bytes)


async def convert_3d_sharp(image, image_bytes):
    """Convert to 3D using TripoSR via Hugging Face Space (renamed from SHARP)"""
    # Apple SHARP is for multi-view reconstruction, not single image
    # Using TripoSR HF Space instead
    return await convert_3d_triposr_hf(image, image_bytes)


async def convert_3d_triposr(image_bytes):
    """Convert to 3D using TripoSR - tries multiple providers"""
    from PIL import Image
    image = Image.open(io.BytesIO(image_bytes))

    # Try providers in order of preference
    errors = []

    # Option 1: Try Replicate API (if API key available)
    import os
    replicate_token = os.getenv('REPLICATE_API_TOKEN')
    if replicate_token:
        try:
            result = await convert_3d_replicate(image_bytes, replicate_token)
            return result
        except Exception as e:
            errors.append(f"Replicate: {e}")

    # Option 2: Try HuggingFace Space
    try:
        result = await convert_3d_triposr_hf(image, image_bytes)
        return result
    except Exception as e:
        errors.append(f"HuggingFace: {e}")

    # All options failed
    raise Exception(f"All 3D conversion methods failed: {'; '.join(errors)}")


async def convert_3d_replicate(image_bytes, api_token):
    """Convert to 3D using Replicate API (TripoSR model)"""
    import uuid
    import httpx
    import asyncio

    model_id = uuid.uuid4().hex[:8]
    model_dir = Path('static/models')
    model_dir.mkdir(parents=True, exist_ok=True)

    # Convert image to base64 data URL
    image_b64 = base64.b64encode(image_bytes).decode()
    image_url = f"data:image/png;base64,{image_b64}"

    async with httpx.AsyncClient(timeout=180.0) as client:
        # Start prediction
        response = await client.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {api_token}",
                "Content-Type": "application/json"
            },
            json={
                "version": "e0d3fe8abce3ba86497ea3530d9eae59af7b2231b6c82bedfc32b0732d35ec3a",
                "input": {
                    "image_path": image_url,
                    "do_remove_background": False,  # Disabled - assume image already has clean/transparent background
                    "foreground_ratio": 0.9,
                    "mc_resolution": 256
                }
            }
        )

        if response.status_code != 201:
            raise Exception(f"Replicate API error: {response.status_code} - {response.text}")

        prediction = response.json()
        prediction_id = prediction["id"]

        # Poll for completion
        for _ in range(120):  # Max 2 minutes
            await asyncio.sleep(1)

            status_response = await client.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers={"Authorization": f"Token {api_token}"}
            )

            result = status_response.json()

            if result["status"] == "succeeded":
                # Download the GLB file
                output_url = result["output"]
                if isinstance(output_url, list):
                    output_url = output_url[0]

                glb_response = await client.get(output_url)
                output_path = model_dir / f"{model_id}.glb"

                with open(output_path, 'wb') as f:
                    f.write(glb_response.content)

                return {
                    'model_url': f'/static/models/{model_id}.glb',
                    'format': 'glb',
                    'info': 'TripoSR (Replicate API) - Real 3D mesh'
                }

            elif result["status"] == "failed":
                raise Exception(f"Replicate prediction failed: {result.get('error', 'Unknown error')}")

        raise Exception("Replicate prediction timed out")


async def convert_3d_triposr_hf(image, image_bytes):
    """
    Convert 2D image to 3D using TripoSR on Hugging Face Spaces.
    This generates ACTUAL 3D geometry, not just a textured plane.
    """
    import uuid
    import tempfile
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    model_id = uuid.uuid4().hex[:8]
    model_dir = Path('static/models')
    model_dir.mkdir(parents=True, exist_ok=True)

    def call_triposr_space():
        """Call TripoSR HF Space synchronously (run in thread pool)"""
        from gradio_client import Client, handle_file
        import tempfile
        import shutil

        # Save image to temp file for gradio client
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            image.save(tmp, format='PNG')
            tmp_path = tmp.name

        try:
            # Try multiple spaces in case one is down
            spaces_to_try = [
                "stabilityai/TripoSR",
                "hysts/TripoSR",  # Community fork
            ]

            last_error = None
            for space_name in spaces_to_try:
                try:
                    # Connect to TripoSR Space
                    client = Client(space_name)

                    # Call the prediction endpoint
                    result = client.predict(
                        handle_file(tmp_path),  # Input image
                        True,  # Remove background
                        0.5,   # Foreground ratio
                        256,   # Marching cubes resolution
                        api_name="/run"
                    )

                    # Result is typically a path to the generated .glb file
                    if result and isinstance(result, str) and Path(result).exists():
                        output_path = model_dir / f"{model_id}.glb"
                        shutil.copy(result, output_path)
                        return {
                            'model_url': f'/static/models/{model_id}.glb',
                            'format': 'glb',
                            'info': f'TripoSR ({space_name}) - Real 3D mesh'
                        }
                    elif result and isinstance(result, (list, tuple)):
                        for item in result:
                            if isinstance(item, str) and (item.endswith('.glb') or item.endswith('.obj')):
                                if Path(item).exists():
                                    ext = Path(item).suffix
                                    output_path = model_dir / f"{model_id}{ext}"
                                    shutil.copy(item, output_path)
                                    return {
                                        'model_url': f'/static/models/{model_id}{ext}',
                                        'format': ext[1:],
                                        'info': f'TripoSR ({space_name}) - Real 3D mesh'
                                    }
                except Exception as e:
                    last_error = e
                    continue

            raise last_error or Exception("All HuggingFace spaces failed")

        finally:
            try:
                Path(tmp_path).unlink()
            except:
                pass

    # Run the blocking gradio client call in a thread pool
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, call_triposr_space)

    return result


async def create_placeholder_3d(image, info):
    """Create a placeholder 3D billboard from the 2D image"""
    import uuid

    # Create a simple GLB with the image as a texture on a plane
    # This is a minimal placeholder - in production, use actual 3D reconstruction

    model_id = uuid.uuid4().hex[:8]
    model_dir = Path('static/models')
    model_dir.mkdir(parents=True, exist_ok=True)

    # Save image as texture
    texture_path = model_dir / f"{model_id}_texture.png"
    image.save(texture_path, 'PNG')

    # For demo, return the texture URL (frontend can create a simple plane)
    return {
        'model_url': f'/static/models/{model_id}_texture.png',
        'model_base64': None,
        'format': 'texture',  # Indicates this is just a texture, not a real 3D model
        'info': info,
        'texture_url': f'/static/models/{model_id}_texture.png'
    }


async def convert_3d_tripo3d(image_bytes, prompt=None, negative_prompt=None, pbr=True, enable_image_autofix=True, orientation='align_image'):
    """
    Convert 2D image to 3D using Tripo3D Pro API.
    This uses the official Tripo3D API for high-quality 3D model generation.

    API Flow:
    1. Upload image -> get file_token
    2. Create task (image_to_model) -> get task_id
    3. Poll task until complete -> get model URL
    4. Download GLB file

    Parameters:
    - pbr: Enable PBR materials (default: True)
    - enable_image_autofix: Optimize input image (default: True)
    - orientation: 'align_image' or 'default' (default: align_image)
    - prompt: Text guidance for generation
    - negative_prompt: What to avoid
    """
    import os
    import uuid
    import httpx
    import asyncio

    api_key = os.getenv('TRIPO_API_KEY')
    if not api_key:
        raise Exception("TRIPO_API_KEY not set in environment. Get one at https://platform.tripo3d.ai/api-keys")

    model_id = uuid.uuid4().hex[:8]
    model_dir = Path('static/models')
    model_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://api.tripo3d.ai/v2/openapi"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Step 1: Upload the image
        print("Tripo3D: Uploading image...")
        upload_response = await client.post(
            f"{base_url}/upload",
            headers=headers,
            files={"file": ("image.png", image_bytes, "image/png")}
        )

        if upload_response.status_code != 200:
            raise Exception(f"Tripo3D upload error: {upload_response.status_code} - {upload_response.text}")

        upload_data = upload_response.json()
        if upload_data.get("code") != 0:
            raise Exception(f"Tripo3D upload error: {upload_data}")

        file_token = upload_data["data"]["image_token"]
        print(f"Tripo3D: Image uploaded, token: {file_token[:20]}...")

        # Step 2: Create image-to-model task
        print("Tripo3D: Creating 3D generation task...")

        # Build task payload with parameters from UI
        task_payload = {
            "type": "image_to_model",
            "model_version": "v2.5-20250123",  # v2.5 quality version
            "file": {
                "type": "png",
                "file_token": file_token
            },
        }

        # Add optional parameters based on UI settings
        if pbr:
            task_payload["pbr"] = True
        if enable_image_autofix:
            task_payload["enable_image_autofix"] = True
        if orientation and orientation != 'default':
            task_payload["orientation"] = orientation

        # Add prompt if provided
        if prompt:
            task_payload["prompt"] = prompt
            print(f"Tripo3D: Using prompt: {prompt}")
        if negative_prompt:
            task_payload["negative_prompt"] = negative_prompt

        task_response = await client.post(
            f"{base_url}/task",
            headers={**headers, "Content-Type": "application/json"},
            json=task_payload
        )

        if task_response.status_code != 200:
            raise Exception(f"Tripo3D task creation error: {task_response.status_code} - {task_response.text}")

        task_data = task_response.json()
        if task_data.get("code") != 0:
            raise Exception(f"Tripo3D task creation error: {task_data}")

        task_id = task_data["data"]["task_id"]
        print(f"Tripo3D: Task created, id: {task_id}")

        # Step 3: Poll for task completion
        print("Tripo3D: Waiting for 3D model generation...")
        for attempt in range(180):  # Max 3 minutes
            await asyncio.sleep(2)  # Poll every 2 seconds

            status_response = await client.get(
                f"{base_url}/task/{task_id}",
                headers=headers
            )

            status_data = status_response.json()
            if status_data.get("code") != 0:
                raise Exception(f"Tripo3D status error: {status_data}")

            task_info = status_data["data"]
            status = task_info["status"]
            progress = task_info.get("progress", 0)

            print(f"Tripo3D: Status={status}, Progress={progress}%")

            if status == "success":
                # Step 4: Download the model
                output = task_info.get("output", {})
                print(f"Tripo3D: Output keys: {output.keys() if output else 'None'}")
                print(f"Tripo3D: Full output: {output}")

                # Try different possible keys for model URL
                model_url = output.get("model") or output.get("mesh") or output.get("glb") or output.get("pbr_model") or output.get("base_model")

                if not model_url:
                    raise Exception("Tripo3D: No model URL in successful task output")

                print(f"Tripo3D: Downloading model from {model_url[:50]}...")
                model_response = await client.get(model_url)

                if model_response.status_code != 200:
                    raise Exception(f"Tripo3D: Failed to download model: {model_response.status_code}")

                output_path = model_dir / f"{model_id}.glb"
                with open(output_path, 'wb') as f:
                    f.write(model_response.content)

                print(f"Tripo3D: Model saved to {output_path}")

                return {
                    'model_url': f'/static/models/{model_id}.glb',
                    'format': 'glb',
                    'info': 'Tripo3D Pro API - High quality 3D mesh'
                }

            elif status == "failed":
                raise Exception(f"Tripo3D: Task failed - {task_info.get('error', 'Unknown error')}")

            elif status == "banned":
                raise Exception("Tripo3D: Task banned - content policy violation")

            elif status == "cancelled":
                raise Exception("Tripo3D: Task was cancelled")

        raise Exception("Tripo3D: Task timed out after 3 minutes")
