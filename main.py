from fasthtml.common import *
from page.components import create_page
from page.gallery_components import (
    get_gallery_carousel_styles,
    get_gallery_carousel_scripts,
    portfolio_carousel_section,
    before_after_carousel_section,
    instagram_section as instagram_section_module
)
from page.sections import (
    hero_section, welcome_section, pricing_section, why_astra_section,
    reviews_section, instagram_section, awards_section, trusted_by_section,
    about_hero_section, our_story_section, our_commitment_section, why_choose_section
)
from page.services import (
    home_staging_services_page,
    real_estate_staging_page,
    our_differences_page
)
from page.contact import contact_page
from page.staging_inquiry import staging_inquiry_page
from page.reserve import reserve_page
from page.design import design_page
# 3D model routes
from tools.model_3d.api_routes import register_test_routes
from tools.model_3d.inpainting import test_inpainting_page
from page.areas import AREAS, AREA_PAGE_FUNCTIONS
from page.blog_listing import blog_listing_page, load_blog_metadata
from page.signin import signin_page
from page.portal import portal_page
# Item Management and Zoho Sync pages
from page.item_management import item_management_app_export
from page.zoho_sync import zoho_sync_app_export
from tools.zoho_sync.database import db as zoho_db
from tools.zoho_sync.zoho_api import zoho_api
from tools.zoho_sync.image_downloader import image_downloader
from tools.zoho_sync.sync_service import sync_service
from tools.zoho_sync.write_service import write_service
from tools.zoho_sync.page_sync_service import PageSyncService
import asyncio
from starlette.staticfiles import StaticFiles
from starlette.responses import Response, JSONResponse, RedirectResponse
import sqlite3
from tools.instagram import get_cached_posts
from tools.google_reviews import fetch_google_reviews
from tools.email_service import send_inquiry_emails
from tools.user_db import (
    create_user, authenticate_user, get_user_by_session,
    create_session, delete_session, get_or_create_google_user,
    get_all_users, update_user,
    save_staging, get_user_stagings, get_staging_by_id, delete_staging
)
from starlette.requests import Request
import httpx
import hashlib
import json
import os
import stripe
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')

# Session cookie name
SESSION_COOKIE_NAME = 'astra_session'

app, rt = fast_app(live=True)

# Cache for proxied images
_image_cache = {}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount Item Management and Zoho Sync sub-apps
app.mount("/item_management", item_management_app_export)
app.mount("/zoho_sync", zoho_sync_app_export)

# Background sync task handle
_background_tasks = []
_sync_running = False
_page_sync_service = None

async def background_page_sync():
    """
    Background page sync using Playwright (0 API calls).
    Polls the Zoho report every 30 seconds and syncs modified items.
    """
    global _page_sync_service
    _page_sync_service = PageSyncService(poll_interval_seconds=30)
    await _page_sync_service.initialize()

    while True:
        try:
            result = await _page_sync_service.sync_once()
            if result.get('records_synced', 0) > 0:
                print(f"[Page Sync] Synced {result['records_synced']} records (0 API calls)")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Page Sync] Error: {e}")

        await asyncio.sleep(30)

async def background_zoho_read_sync():
    """
    Smart background sync that checks Item_Report_Sync every 30 seconds.
    Only uses API credits when actual changes are detected.
    """
    global _sync_running
    while True:
        try:
            await asyncio.sleep(30)  # 30 seconds
            if not _sync_running:
                _sync_running = True
                result = await sync_service.smart_sync_check()
                if result.get('changes_detected'):
                    print(f"[Smart Sync] Synced {result.get('records_synced', 0)} changed records")
                # Don't print anything if no changes (to avoid log spam)
                _sync_running = False
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Smart Sync] Error: {e}")
            _sync_running = False

async def background_zoho_write_sync():
    """Background task for writing changes to Zoho (every 30 seconds)"""
    while True:
        try:
            await asyncio.sleep(30)  # 30 seconds
            result = await write_service.process_pending_updates()
            if result['processed'] > 0 or result['failed'] > 0:
                print(f"[Background Sync] Write: {result['processed']} synced, {result['failed']} failed")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Background Sync] Write error: {e}")

# Startup/shutdown events for Zoho Sync database
@app.on_event("startup")
async def startup():
    """Initialize database connection on startup"""
    await zoho_db.connect()

    # Initialize write service tables
    await write_service.init_tables()

    # Start background sync tasks
    # Use page sync (0 API calls) instead of API-based read sync
    page_sync_task = asyncio.create_task(background_page_sync())
    write_task = asyncio.create_task(background_zoho_write_sync())
    _background_tasks.extend([page_sync_task, write_task])
    print("[Background Sync] Started page sync (30s, 0 API calls) and write (30s) sync tasks")

@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    global _page_sync_service

    # Cancel background tasks
    for task in _background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Close page sync service (Playwright browser)
    if _page_sync_service:
        await _page_sync_service.close()

    await zoho_db.disconnect()
    await zoho_api.close()
    await image_downloader.close()


@rt('/api/instagram-image/{image_id}')
async def instagram_image_proxy(image_id: str):
    """Proxy Instagram images to avoid CORS issues"""
    # Get all cached posts and find the matching image
    posts = get_cached_posts()

    for post in posts:
        # Create a hash of the image URL to match
        url_hash = hashlib.md5(post.get('image_url', '').encode()).hexdigest()[:16]
        if url_hash == image_id:
            image_url = post.get('image_url')
            break
    else:
        return Response(content=b'Image not found', status_code=404)

    # Check cache first
    if image_id in _image_cache:
        cached = _image_cache[image_id]
        return Response(
            content=cached['data'],
            media_type=cached['content_type'],
            headers={'Cache-Control': 'public, max-age=86400'}
        )

    # Fetch the image from Instagram
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.instagram.com/",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, headers=headers, timeout=10.0, follow_redirects=True)

            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'image/jpeg')
                image_data = response.content

                # Cache the image
                _image_cache[image_id] = {
                    'data': image_data,
                    'content_type': content_type
                }

                return Response(
                    content=image_data,
                    media_type=content_type,
                    headers={'Cache-Control': 'public, max-age=86400'}
                )
            else:
                return Response(content=b'Failed to fetch image', status_code=502)
    except Exception as e:
        print(f"Error proxying image: {e}")
        return Response(content=b'Error fetching image', status_code=500)


def get_proxied_image_url(image_url: str) -> str:
    """Generate a proxied URL for an Instagram image"""
    url_hash = hashlib.md5(image_url.encode()).hexdigest()[:16]
    return f"/api/instagram-image/{url_hash}"


@rt('/api/contact', methods=['POST'])
async def contact_api(request: Request):
    """Handle contact form submission - sends confirmation and notification emails"""
    try:
        data = await request.json()

        customer_data = {
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'subject': data.get('subject', 'General Inquiry'),
            'message': data.get('message', '')
        }

        # Validate required fields
        if not customer_data['name'] or not customer_data['email'] or not customer_data['message']:
            return Response(
                content=json.dumps({'success': False, 'error': 'Missing required fields'}),
                media_type='application/json',
                status_code=400
            )

        # Send emails to sales@astrastaging.com
        result = send_inquiry_emails(customer_data)

        return Response(
            content=json.dumps({'success': result['success']}),
            media_type='application/json'
        )

    except Exception as e:
        print(f"Contact form error: {e}")
        return Response(
            content=json.dumps({'success': False, 'error': str(e)}),
            media_type='application/json',
            status_code=500
        )


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

def get_current_user(request: Request):
    """Get current user from session cookie"""
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_token:
        return None
    return get_user_by_session(session_token)


@rt('/api/auth/signin', methods=['POST'])
async def auth_signin(request: Request):
    """Handle email/password sign in"""
    try:
        data = await request.json()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return JSONResponse({'success': False, 'error': 'Email and password required'}, status_code=400)

        result = authenticate_user(email, password)

        if not result['success']:
            return JSONResponse({'success': False, 'error': result.get('error', 'Authentication failed')}, status_code=401)

        # Create session
        user = result['user']
        session_token = create_session(user['id'])

        response = JSONResponse({'success': True, 'user': user})
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            samesite='lax',
            secure=False  # Set to True in production with HTTPS
        )
        return response

    except Exception as e:
        print(f"Sign in error: {e}")
        return JSONResponse({'success': False, 'error': 'Sign in failed'}, status_code=500)


@rt('/api/auth/register', methods=['POST'])
async def auth_register(request: Request):
    """Handle user registration"""
    try:
        data = await request.json()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')

        if not first_name or not last_name or not email or not password:
            return JSONResponse({'success': False, 'error': 'All required fields must be filled'}, status_code=400)

        if len(password) < 8:
            return JSONResponse({'success': False, 'error': 'Password must be at least 8 characters'}, status_code=400)

        result = create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone or None,
            password=password,
            user_role='customer'
        )

        if not result['success']:
            return JSONResponse({'success': False, 'error': result.get('error', 'Registration failed')}, status_code=400)

        # Create session
        user = result['user']
        session_token = create_session(user['id'])

        response = JSONResponse({'success': True, 'user': user})
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            samesite='lax',
            secure=False  # Set to True in production with HTTPS
        )
        return response

    except Exception as e:
        print(f"Registration error: {e}")
        return JSONResponse({'success': False, 'error': 'Registration failed'}, status_code=500)


@rt('/api/auth/google', methods=['POST'])
async def auth_google(request: Request):
    """Handle Google sign in"""
    try:
        data = await request.json()
        credential = data.get('credential', '')

        if not credential or not GOOGLE_CLIENT_ID:
            return JSONResponse({'success': False, 'error': 'Google sign in not configured'}, status_code=400)

        # Decode the JWT token from Google (without verification for simplicity)
        # In production, you should verify the token properly
        try:
            # Decode without verification (Google already verified it)
            payload = jwt.decode(credential, options={"verify_signature": False})
        except Exception as e:
            return JSONResponse({'success': False, 'error': 'Invalid Google token'}, status_code=400)

        google_id = payload.get('sub')
        email = payload.get('email')
        first_name = payload.get('given_name', '')
        last_name = payload.get('family_name', '')

        if not google_id or not email:
            return JSONResponse({'success': False, 'error': 'Invalid Google account data'}, status_code=400)

        result = get_or_create_google_user(
            google_id=google_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        if not result['success']:
            return JSONResponse({'success': False, 'error': result.get('error', 'Google sign in failed')}, status_code=400)

        # Create session
        user = result['user']
        session_token = create_session(user['id'])

        response = JSONResponse({'success': True, 'user': {
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'user_role': user['user_role']
        }})
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            samesite='lax',
            secure=False  # Set to True in production with HTTPS
        )
        return response

    except Exception as e:
        print(f"Google sign in error: {e}")
        return JSONResponse({'success': False, 'error': 'Google sign in failed'}, status_code=500)


@rt('/api/auth/signout', methods=['POST'])
async def auth_signout(request: Request):
    """Handle sign out"""
    try:
        session_token = request.cookies.get(SESSION_COOKIE_NAME)
        if session_token:
            delete_session(session_token)

        response = JSONResponse({'success': True})
        response.delete_cookie(SESSION_COOKIE_NAME)
        return response

    except Exception as e:
        print(f"Sign out error: {e}")
        response = JSONResponse({'success': True})
        response.delete_cookie(SESSION_COOKIE_NAME)
        return response


@rt('/api/auth/check')
def auth_check(request: Request):
    """Check if user is authenticated"""
    user = get_current_user(request)
    if user:
        return JSONResponse({
            'authenticated': True,
            'user': {
                'id': user['id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email'],
                'phone': user.get('phone', ''),
                'user_role': user['user_role']
            }
        })
    return JSONResponse({'authenticated': False})


@rt('/api/profile/update', methods=['POST'])
async def profile_update(request: Request):
    """Update current user's profile"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({'success': False, 'error': 'Not authenticated'}, status_code=401)

    try:
        data = await request.json()

        # Update user (only allow updating own profile, keep same role)
        result = update_user(
            user_id=user['id'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            user_role=user['user_role'],  # Keep existing role
            password=data.get('password')
        )

        if result.get('success'):
            return JSONResponse({'success': True})
        else:
            return JSONResponse({'success': False, 'error': result.get('error', 'Update failed')}, status_code=400)

    except Exception as e:
        print(f"Profile update error: {e}")
        return JSONResponse({'success': False, 'error': 'Update failed'}, status_code=500)


# =============================================================================
# STAGING API ENDPOINTS
# =============================================================================

@rt('/api/stagings', methods=['GET'])
def get_stagings(request: Request):
    """Get all stagings for the current user"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({'success': False, 'error': 'Not authenticated'}, status_code=401)

    status = request.query_params.get('status')  # Optional filter: 'quote' or 'confirmed'
    stagings = get_user_stagings(user['id'], status)
    return JSONResponse({'success': True, 'stagings': stagings})


@rt('/api/stagings', methods=['POST'])
async def create_or_update_staging(request: Request):
    """Create or update a staging for the current user"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({'success': False, 'error': 'Not authenticated'}, status_code=401)

    try:
        data = await request.json()
        import sys
        print(f"Staging save request - user_id: {user['id']}, data: {data}", file=sys.stderr)
        result = save_staging(user['id'], data)
        print(f"Staging save result: {result}", file=sys.stderr)

        if result.get('success'):
            return JSONResponse({
                'success': True,
                'staging_id': result['staging_id']
            })
        else:
            return JSONResponse({
                'success': False,
                'error': result.get('error', 'Save failed')
            }, status_code=400)

    except Exception as e:
        print(f"Staging save error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({'success': False, 'error': 'Save failed'}, status_code=500)


@rt('/api/stagings/{staging_id}')
def get_single_staging(request: Request, staging_id: int):
    """Get a single staging by ID"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({'success': False, 'error': 'Not authenticated'}, status_code=401)

    staging = get_staging_by_id(staging_id, user['id'])
    if staging:
        return JSONResponse({'success': True, 'staging': staging})
    return JSONResponse({'success': False, 'error': 'Staging not found'}, status_code=404)


@rt('/api/stagings/{staging_id}', methods=['DELETE'])
def remove_staging(request: Request, staging_id: int):
    """Delete a staging"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({'success': False, 'error': 'Not authenticated'}, status_code=401)

    result = delete_staging(staging_id, user['id'])
    if result.get('success'):
        return JSONResponse({'success': True})
    return JSONResponse({'success': False, 'error': result.get('error', 'Delete failed')}, status_code=400)


@rt('/api/inventory-items')
def get_inventory_items(item_type: str = ""):
    """Get inventory items filtered by type"""
    import os
    try:
        # Connect directly to the zoho_sync database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "zoho_sync.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT Item_Name, Item_Type, Item_Image, Resized_Image, Item_Color, Item_Style, Model_3D,
                   Item_Width, Item_Depth, Item_Height
            FROM Item_Report
            WHERE Item_Name IS NOT NULL AND Item_Name != ''
        """
        params = []

        if item_type:
            # Filter by item name pattern (e.g., "Accent Chair" matches "Accent Chair 01052")
            query += " AND (Item_Type = ? OR Item_Name LIKE ?)"
            params.append(item_type)
            params.append(f"{item_type}%")

        query += " ORDER BY Item_Name"

        cursor.execute(query, params)
        items = cursor.fetchall()

        # Group by item name and get unique images
        items_data = {}
        for item in items:
            name = item['Item_Name']
            # Get image URL (prefer resized, then original)
            image_url = None

            # Helper to check if URL is valid
            def is_valid_image_url(url):
                if not url or url == 'blank.png' or url.strip() == '':
                    return False
                # Accept both http:// and https:// URLs
                return url.strip().startswith('http://') or url.strip().startswith('https://')

            # Try Resized_Image first, then fall back to Item_Image
            if is_valid_image_url(item['Resized_Image']):
                image_url = item['Resized_Image'].strip()
            elif is_valid_image_url(item['Item_Image']):
                image_url = item['Item_Image'].strip()
            else:
                # Log when no valid image found
                print(f"No valid image for {name}: Resized_Image='{item['Resized_Image']}', Item_Image='{item['Item_Image']}'")

            # Get 3D model filename
            model_3d = item['Model_3D'] if item['Model_3D'] else None

            # Get dimensions (convert to float, default to 0)
            def parse_dimension(val):
                if val:
                    try:
                        return float(val)
                    except:
                        return 0
                return 0

            width = parse_dimension(item['Item_Width'])
            depth = parse_dimension(item['Item_Depth'])
            height = parse_dimension(item['Item_Height'])

            # Get front rotation from Zoho field or saved defaults
            try:
                front_rotation = parse_dimension(item['Front_Rotation']) if item['Front_Rotation'] else None
            except (KeyError, IndexError):
                front_rotation = None

            # If no rotation from Zoho and we have a 3D model, check database for saved default
            if front_rotation is None and model_3d:
                try:
                    saved_cursor = conn.cursor()
                    saved_cursor.execute('''
                        SELECT rotation FROM model_default_rotations WHERE model3d = ?
                    ''', (model_3d,))
                    saved_rotation = saved_cursor.fetchone()
                    if saved_rotation:
                        front_rotation = saved_rotation[0]
                        print(f"Loaded saved rotation for {model_3d}: {front_rotation}")
                except Exception as e:
                    print(f"Error loading saved rotation for {model_3d}: {e}")
                    pass  # Table may not exist yet, that's okay

            if name not in items_data:
                items_data[name] = {
                    'name': name,
                    'type': item['Item_Type'],
                    'images': [],
                    'model_3d': model_3d,
                    'width': width,
                    'depth': depth,
                    'height': height
                }
            elif model_3d and not items_data[name].get('model_3d'):
                # Update model_3d if this record has one and previous didn't
                items_data[name]['model_3d'] = model_3d
                items_data[name]['width'] = width
                items_data[name]['depth'] = depth
                items_data[name]['height'] = height

            # Add unique images only (with their model_3d info and dimensions)
            if image_url and image_url not in [img['url'] if isinstance(img, dict) else img for img in items_data[name]['images']]:
                items_data[name]['images'].append({
                    'url': image_url,
                    'model_3d': model_3d,
                    'width': width,
                    'depth': depth,
                    'height': height,
                    'front_rotation': front_rotation  # Rotation in radians, frontend uses -Math.PI/2 as default if null
                })

        conn.close()
        return JSONResponse({'success': True, 'items': list(items_data.values())})
    except Exception as e:
        print(f"Error getting inventory items: {e}")
        if 'conn' in locals():
            conn.close()
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@rt('/api/save-default-rotation', methods=['POST'])
async def save_default_rotation(request: Request):
    """Save default rotation for a 3D model"""
    try:
        data = await request.json()
        model3d = data.get('model3d')
        rotation = data.get('rotation')

        if not model3d or rotation is None:
            return JSONResponse({'success': False, 'error': 'Missing model3d or rotation'}, status_code=400)

        # Create table if it doesn't exist
        async with zoho_db._connection.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_default_rotations (
                    model3d TEXT PRIMARY KEY,
                    rotation REAL NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insert or update the rotation
            await cursor.execute('''
                INSERT INTO model_default_rotations (model3d, rotation, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(model3d) DO UPDATE SET
                    rotation = excluded.rotation,
                    updated_at = CURRENT_TIMESTAMP
            ''', (model3d, rotation))

        await zoho_db._connection.commit()

        return JSONResponse({'success': True, 'model3d': model3d, 'rotation': rotation})
    except Exception as e:
        print(f"Error saving default rotation: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@rt('/api/get-default-rotation/{model3d}')
async def get_default_rotation(model3d: str):
    """Get default rotation for a 3D model"""
    try:
        async with zoho_db._connection.cursor() as cursor:
            await cursor.execute('''
                SELECT rotation FROM model_default_rotations WHERE model3d = ?
            ''', (model3d,))
            result = await cursor.fetchone()

        if result:
            return JSONResponse({'success': True, 'rotation': result[0]})
        else:
            return JSONResponse({'success': False, 'error': 'No default rotation found'}, status_code=404)
    except Exception as e:
        print(f"Error getting default rotation: {e}")
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@rt('/api/staging-photos', methods=['POST'])
async def upload_staging_photos(request: Request):
    """Upload and compress staging area photos"""
    import base64
    import io
    import uuid
    import os
    from PIL import Image

    try:
        data = await request.json()
        area = data.get('area', 'unknown')
        photos = data.get('photos', [])  # List of base64 images

        if not photos:
            return JSONResponse({'success': False, 'error': 'No photos provided'}, status_code=400)

        saved_urls = []
        target_size = (1920, 1440)  # Target dimensions
        save_dir = 'static/images/areas'

        # Ensure directory exists
        os.makedirs(save_dir, exist_ok=True)

        for i, photo_data in enumerate(photos):
            try:
                # Remove data URL prefix if present
                if ',' in photo_data:
                    photo_data = photo_data.split(',')[1]

                # Decode base64
                image_bytes = base64.b64decode(photo_data)
                image = Image.open(io.BytesIO(image_bytes))

                # Convert to RGB if necessary (for PNG with transparency)
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')

                # Resize maintaining aspect ratio, fitting within target size
                image.thumbnail(target_size, Image.Resampling.LANCZOS)

                # Generate unique filename
                filename = f"{area}_{uuid.uuid4().hex[:8]}.jpg"
                filepath = os.path.join(save_dir, filename)

                # Save with compression
                image.save(filepath, 'JPEG', quality=85, optimize=True)

                # Return URL path
                saved_urls.append(f'/static/images/areas/{filename}')

            except Exception as e:
                print(f"Error processing photo {i}: {e}")
                continue

        if saved_urls:
            return JSONResponse({'success': True, 'urls': saved_urls})
        else:
            return JSONResponse({'success': False, 'error': 'Failed to process photos'}, status_code=500)

    except Exception as e:
        print(f"Photo upload error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@rt('/api/staging-photos/cleanup', methods=['POST'])
async def cleanup_staging_photos(request: Request):
    """Delete orphaned photos that are not associated with any area"""
    import os
    import glob

    try:
        data = await request.json()
        # Get list of all valid photo URLs currently in use
        valid_urls = data.get('valid_urls', [])

        # Extract just the filenames from URLs
        valid_filenames = set()
        for url in valid_urls:
            if url.startswith('/static/images/areas/'):
                filename = url.replace('/static/images/areas/', '')
                valid_filenames.add(filename)

        # Scan the areas folder
        areas_dir = 'static/images/areas'
        if not os.path.exists(areas_dir):
            return JSONResponse({'success': True, 'deleted': 0})

        deleted_count = 0
        for filepath in glob.glob(os.path.join(areas_dir, '*.jpg')):
            filename = os.path.basename(filepath)
            if filename not in valid_filenames:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"Deleted orphaned photo: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

        return JSONResponse({'success': True, 'deleted': deleted_count})

    except Exception as e:
        print(f"Cleanup error: {e}")
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@rt('/api/save-staging-models', methods=['POST'])
async def save_staging_models(request: Request):
    """Save 3D model states for a staging photo"""
    from tools.user_db import get_db_connection

    try:
        data = await request.json()
        staging_id = data.get('stagingId') or 0  # Use 0 instead of NULL
        area = data.get('area')
        photo_index = data.get('photoIndex')
        background_image = data.get('backgroundImage', '')[:100]  # First 100 chars as identifier
        models = data.get('models', [])

        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete existing models for this background (match on background_image only for flexibility)
        cursor.execute("""
            DELETE FROM design_models
            WHERE background_image = ?
        """, (background_image,))

        # Insert new model states
        for model in models:
            cursor.execute("""
                INSERT INTO design_models (
                    staging_id, background_image, model_url, instance_id,
                    position_x, position_y, position_z, scale, rotation_y, tilt, brightness
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                staging_id,
                background_image,
                model.get('modelUrl', ''),
                model.get('instanceId', 0),
                model.get('positionX', 0),
                model.get('positionY', 0),
                model.get('positionZ', 0),
                model.get('scale', 1),
                model.get('rotationY', 0),
                model.get('tilt', 0.1745),
                model.get('brightness', 2.5)
            ))

        conn.commit()
        conn.close()
        return JSONResponse({'success': True})

    except Exception as e:
        print(f"Error saving staging models: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@rt('/api/get-staging-models')
def get_staging_models(staging_id: int = 0, background_image: str = ""):
    """Get 3D model states for a staging photo"""
    from tools.user_db import get_db_connection

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Match on background_image only for flexibility (staging_id may be 0 or NULL)
        cursor.execute("""
            SELECT model_url, instance_id, position_x, position_y, position_z,
                   scale, rotation_y, tilt, brightness
            FROM design_models
            WHERE background_image = ?
            ORDER BY instance_id
        """, (background_image[:100],))

        models = []
        for row in cursor.fetchall():
            models.append({
                'modelUrl': row[0],
                'instanceId': row[1],
                'positionX': row[2],
                'positionY': row[3],
                'positionZ': row[4],
                'scale': row[5],
                'rotationY': row[6],
                'tilt': row[7],
                'brightness': row[8]
            })

        conn.close()
        return JSONResponse({'success': True, 'models': models})

    except Exception as e:
        print(f"Error getting staging models: {e}")
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


# =============================================================================
# TEST API ENDPOINTS - MOVED TO tools/test/test_api_routes.py
# =============================================================================
register_test_routes(rt)


# =============================================================================
# ADMIN API ENDPOINTS
# =============================================================================

@rt('/api/admin/users')
def admin_users(request: Request):
    """Get all users (admin only)"""
    user = get_current_user(request)
    if not user or user.get('user_role') != 'admin':
        return JSONResponse({'error': 'Unauthorized'}, status_code=403)

    users = get_all_users()
    return JSONResponse({'users': users})


@rt('/api/admin/users/update', methods=['POST'])
async def admin_update_user(request: Request):
    """Update a user (admin only)"""
    user = get_current_user(request)
    if not user or user.get('user_role') != 'admin':
        return JSONResponse({'error': 'Unauthorized'}, status_code=403)

    try:
        data = await request.json()
        user_id = data.get('id')

        if not user_id:
            return JSONResponse({'success': False, 'error': 'User ID required'}, status_code=400)

        # Build update fields
        update_fields = {}
        for field in ['first_name', 'last_name', 'email', 'phone', 'user_role', 'password']:
            if field in data and data[field]:
                update_fields[field] = data[field]

        if not update_fields:
            return JSONResponse({'success': False, 'error': 'No fields to update'}, status_code=400)

        result = update_user(user_id, **update_fields)

        if result['success']:
            return JSONResponse({'success': True})
        else:
            return JSONResponse({'success': False, 'error': result.get('error', 'Update failed')}, status_code=400)

    except Exception as e:
        print(f"Admin update user error: {e}")
        return JSONResponse({'success': False, 'error': 'Update failed'}, status_code=500)


# =============================================================================
# STRIPE PAYMENT ENDPOINTS
# =============================================================================

@rt('/api/stripe-config')
def get_stripe_config():
    """Return Stripe publishable key"""
    return JSONResponse({'publishableKey': STRIPE_PUBLISHABLE_KEY})


@rt('/api/create-payment-intent')
async def create_payment_intent(req: Request):
    """Create a Stripe payment intent with customer for staging reservation"""
    try:
        data = await req.json()

        # Extract reservation details
        amount = data.get('amount', 50000)  # Default to $500 in cents
        if isinstance(amount, (int, float)) and amount < 1000:
            # Convert dollars to cents if needed
            amount = int(amount * 100)

        guest_name = data.get('guest_name', '')
        if not guest_name:
            first_name = data.get('firstName', '')
            last_name = data.get('lastName', '')
            guest_name = f"{first_name} {last_name}".strip()

        guest_email = data.get('guest_email', data.get('email', ''))
        guest_phone = data.get('guest_phone', data.get('phone', ''))
        property_address = data.get('property_address', '')
        staging_date = data.get('staging_date', '')

        # Validate guest email is provided
        if not guest_email:
            return JSONResponse({'error': 'Email is required'}, status_code=400)

        print(f"Creating staging payment for: {guest_name} ({guest_email}), Property: {property_address}")

        # Check if customer already exists in Stripe
        existing_customers = stripe.Customer.list(email=guest_email, limit=1)

        if existing_customers.data:
            customer = existing_customers.data[0]
            print(f"Found existing Stripe customer: {customer.id} ({customer.email})")
        else:
            # Create new customer (not a guest) so we can charge them later
            customer = stripe.Customer.create(
                email=guest_email,
                name=guest_name,
                phone=guest_phone,
                metadata={
                    'property_address': property_address,
                    'staging_date': staging_date,
                    'source': 'astra_staging_website'
                }
            )
            print(f"Created new Stripe customer: {customer.id} ({guest_email})")

        # Create payment intent with customer for future charges
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='cad',
            customer=customer.id,
            receipt_email=guest_email,
            description='Astra Staging - Reservation Deposit',
            setup_future_usage='off_session',  # Save payment method for future use
            automatic_payment_methods={'enabled': True},
            metadata={
                'customer_name': guest_name,
                'customer_email': guest_email,
                'customer_phone': guest_phone,
                'property_address': property_address,
                'staging_date': staging_date,
                'type': 'staging_deposit'
            }
        )

        return JSONResponse({
            'clientSecret': intent.client_secret,
            'paymentIntentId': intent.id,
            'customerId': customer.id
        })
    except Exception as e:
        print(f"Stripe error: {str(e)}")
        return JSONResponse({'error': str(e)}, status_code=400)


@rt('/api/confirm-reservation')
async def confirm_reservation(req: Request):
    """Confirm reservation after successful payment"""
    try:
        data = await req.json()
        payment_intent_id = data.get('paymentIntentId')
        customer_id = data.get('customerId')
        form_data = data.get('formData', {})
        deposit_amount = data.get('depositAmount', 500)

        # Verify payment was successful
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status == 'succeeded':
            # Payment successful - log and return success
            print(f"Payment successful for customer {customer_id}, intent {payment_intent_id}")

            # TODO: Send confirmation email, save to database, etc.

            return JSONResponse({
                'success': True,
                'customer_id': customer_id,
                'payment_intent_id': payment_intent_id
            })
        else:
            return JSONResponse({
                'success': False,
                'error': f'Payment not completed. Status: {intent.status}'
            }, status_code=400)
    except Exception as e:
        print(f"Confirmation error: {str(e)}")
        return JSONResponse({'success': False, 'error': str(e)}, status_code=400)


# =============================================================================
# ROUTES
# =============================================================================

@rt('/gallery')
def gallery():
    """Gallery page with Portfolio, Before/After, and Instagram sections"""
    content = Div(
        portfolio_carousel_section(title="Portfolio", alt_bg=False),
        before_after_carousel_section(title="Before and After", alt_bg=True),
        instagram_section_module(alt_bg=False),
        cls="gallery-content"
    )

    # Combine gallery carousel styles with any additional styles
    additional_styles = get_gallery_carousel_styles()
    additional_scripts = get_gallery_carousel_scripts()

    return create_page(
        "Portfolio | Astra Staging",
        content,
        additional_styles=additional_styles,
        additional_scripts=additional_scripts,
        description="View our portfolio of professional home staging projects, before and after transformations, and latest Instagram posts.",
        keywords="home staging portfolio, staging before after, home staging photos, real estate staging gallery"
    )


@rt('/staging-pricing')
def staging_pricing():
    """Staging Pricing page with pricing packages, why astra, portfolio and instagram"""
    content = Div(
        pricing_section(),
        why_astra_section(),
        portfolio_carousel_section(title="Portfolio", alt_bg=True),
        instagram_section_module(alt_bg=False),
        cls="staging-pricing-content"
    )

    # Include gallery carousel styles and scripts
    additional_styles = get_gallery_carousel_styles()
    additional_scripts = get_gallery_carousel_scripts()

    return create_page(
        "Staging Pricing | Astra Staging",
        content,
        additional_styles=additional_styles,
        additional_scripts=additional_scripts,
        description="Professional home staging pricing packages. Starter package from $1,200, Complete package from $1,600. Free consultation in GTA.",
        keywords="home staging pricing, staging cost, staging packages, home staging rates, GTA staging prices"
    )


def get_about_page_styles():
    """CSS styles specific to the about page"""
    return """
    /* About Hero Section */
    .about-hero-section {
        padding: 80px 40px 60px;
        background: var(--bg-secondary);
        text-align: center;
    }
    .about-hero-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(32px, 5vw, 48px);
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 20px;
    }
    .about-hero-subtitle {
        font-size: 20px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 700px;
        margin: 0 auto;
    }
    @media (max-width: 767px) {
        .about-hero-section {
            padding: 60px 20px 40px;
        }
        .about-hero-subtitle {
            font-size: 18px;
        }
    }

    /* Our Story Section */
    .our-story-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }
    .story-text {
        font-size: 18px;
        line-height: 1.8;
        color: var(--color-secondary);
        max-width: 800px;
        margin: 0 auto 20px;
        text-align: justify;
    }
    .story-text:last-child {
        margin-bottom: 0;
    }
    @media (max-width: 767px) {
        .our-story-section {
            padding: 40px 20px;
        }
        .story-text {
            font-size: 16px;
            line-height: 1.7;
        }
    }

    /* Our Commitment Section */
    .our-commitment-section {
        padding: 60px 40px;
        background: var(--bg-secondary);
    }
    .commitment-text {
        font-size: 18px;
        line-height: 1.8;
        color: var(--color-secondary);
        max-width: 800px;
        margin: 0 auto 20px;
        text-align: justify;
    }
    .commitment-text:last-child {
        margin-bottom: 0;
    }
    @media (max-width: 767px) {
        .our-commitment-section {
            padding: 40px 20px;
        }
        .commitment-text {
            font-size: 16px;
            line-height: 1.7;
        }
    }

    /* Why Choose Section */
    .why-choose-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }
    .choose-cards {
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 40px;
        max-width: 960px;
        margin: 0 auto;
    }
    .choose-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        max-width: 280px;
        padding: 30px 20px;
        background: var(--bg-secondary);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .choose-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    [data-theme="dark"] .choose-card:hover {
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.05);
    }
    .choose-icon {
        width: 70px;
        height: 70px;
        margin-bottom: 20px;
        font-size: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .choose-title {
        font-family: 'Inter', sans-serif;
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 15px;
        color: var(--color-primary);
    }
    .choose-description {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
    }
    @media (max-width: 767px) {
        .why-choose-section {
            padding: 40px 20px;
        }
        .choose-cards {
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }
        .choose-card {
            max-width: 100%;
            width: 100%;
            padding: 25px 20px;
        }
        .choose-icon {
            width: 60px;
            height: 60px;
            font-size: 40px;
        }
        .choose-title {
            font-size: 20px;
        }
        .choose-description {
            font-size: 15px;
        }
    }

    /* Override awards section background for about page */
    .about-content .awards-section {
        background: var(--bg-secondary);
    }
    """


@rt('/about-us')
def about_us():
    """About page with company story, commitment, and why choose us"""
    content = Div(
        about_hero_section(),
        our_story_section(),
        our_commitment_section(),
        why_choose_section(),
        awards_section(),
        reviews_section(),
        trusted_by_section(),
        cls="about-content"
    )

    return create_page(
        "About Us | Astra Staging",
        content,
        additional_styles=get_about_page_styles(),
        description="Learn about Astra Staging - your partner in professional home staging services in the Greater Toronto Area. Award-winning, reliable, and affordable.",
        keywords="about astra staging, home staging company, staging services GTA, professional stagers"
    )


# =============================================================================
# SERVICE PAGES
# =============================================================================

@rt('/home-staging-services/')
def home_staging_services():
    """Home Staging Services page"""
    return home_staging_services_page()


@rt('/real-estate-staging/')
def real_estate_staging():
    """Real Estate Staging page"""
    return real_estate_staging_page()


@rt('/our-differences/')
def our_differences():
    """Our Differences page"""
    return our_differences_page()


@rt('/contactus/')
def contactus():
    """Contact page"""
    return contact_page()


@rt('/staging-inquiry/')
def staging_inquiry():
    """Staging Inquiry page for instant quotes"""
    return staging_inquiry_page()


@rt('/reserve/')
def reserve(req: Request):
    """Staging reservation page"""
    user = get_current_user(req)
    return reserve_page(req, user=user)


@rt('/design')
def design(req: Request):
    """Staging design page - visual presentation of staging with areas and items"""
    staging_id = req.query_params.get('id')
    return design_page(req, staging_id=staging_id)


@rt('/test')
def test():
    """Test page for comparing inpainting methods"""
    return test_inpainting_page()


# =============================================================================
# AUTHENTICATION PAGES
# =============================================================================

@rt('/signin')
def signin(req: Request):
    """Sign in / Register page"""
    # If already signed in, redirect to portal
    user = get_current_user(req)
    if user:
        return RedirectResponse('/portal', status_code=302)
    return signin_page()


@rt('/portal')
def portal(req: Request):
    """User portal page"""
    # If not signed in, redirect to signin
    user = get_current_user(req)
    if not user:
        return RedirectResponse('/signin', status_code=302)
    return portal_page(user)


# =============================================================================
# AREA LANDING PAGES (Google Ads)
# =============================================================================

# Register all area landing page routes
for city_name, url_slug in AREAS:
    route_path = f"/home-staging-services-in-{url_slug}/"
    page_func = AREA_PAGE_FUNCTIONS[url_slug]
    rt(route_path)(page_func)


# =============================================================================
# BLOG ROUTES
# =============================================================================

@rt('/blog/')
def blog():
    """Blog listing page"""
    return blog_listing_page()


# Dynamically register blog post routes
def register_blog_routes():
    """Register routes for individual blog posts"""
    import importlib
    blog_posts = load_blog_metadata()

    for post in blog_posts:
        slug = post['slug']
        seo_url = slug.replace('_', '-')
        filename = post['filename']

        # Convert filename to module path (e.g., page/blog/blog_20251201.py -> page.blog.blog_20251201)
        module_path = filename.replace('/', '.').replace('.py', '')

        # Import the module and get the page function
        try:
            module = importlib.import_module(module_path)
            func_name = f"{filename.split('/')[-1].replace('.py', '')}_page"
            page_func = getattr(module, func_name)

            # Register the route
            rt(f"/{seo_url}/")(page_func)
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not load blog post {slug}: {e}")


register_blog_routes()


@rt('/')
def home():
    """Home page with hero banner"""
    content = Div(
        hero_section(),
        welcome_section(),
        why_astra_section(),
        pricing_section(),
        instagram_section(),
        reviews_section(),
        awards_section(),
        trusted_by_section(),
        cls="home-content"
    )
    return create_page("Astra Staging", content, is_homepage=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
