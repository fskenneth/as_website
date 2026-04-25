"""
Portal web routes — sign in, /portal, admin, 3D designer, stagings, client-log.
Extracted from as_website/main.py during the as_webapp split (Phase 2).

Registered on the as_webapp FastHTML app via register(app, rt). Both the
sub-app mounts (/item_management, /zoho_sync) live in as_webapp/main.py
alongside the call to this register().
"""
import sqlite3
import hashlib
import json
import os
from datetime import datetime

import httpx
import jwt
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from page.signin import signin_page
from page.portal import portal_page
from tools.model_3d.api_routes import register_test_routes
from tools.model_3d.inpainting import test_inpainting_page
from tools.user_db import (
    create_user, authenticate_user, get_user_by_session,
    create_session, delete_session, get_or_create_google_user,
    get_all_users, update_user,
    save_staging, get_user_stagings, get_staging_by_id, delete_staging,
)

# Google OAuth + session cookie name. Main.py also defines these for its
# own public-facing needs (e.g. /reserve/ reads cookies); re-declared here
# so this module has no runtime dependency on main.py.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
SESSION_COOKIE_NAME = "astra_session"


def register(app, rt):
    """Register all portal web routes on the given FastHTML app + router."""
    # ==========================================================================
    # get_current_user helper
    # ==========================================================================

    def get_current_user(request: Request):
        """Get current user from session cookie"""
        session_token = request.cookies.get(SESSION_COOKIE_NAME)
        if not session_token:
            return None
        return get_user_by_session(session_token)


    # ==========================================================================
    # /api/auth/* (signin, register, google, signout, check)
    # ==========================================================================

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


    # ==========================================================================
    # /api/profile/update
    # ==========================================================================

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

    # ==========================================================================
    # /api/stagings (GET/POST, DELETE, by id)
    # ==========================================================================

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


    # ==========================================================================
    # /api/inventory-items
    # ==========================================================================

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
                       Item_Width, Item_Depth, Item_Height, COUNT(*) as Item_Count
                FROM Item_Report
                WHERE Item_Name IS NOT NULL AND Item_Name != ''
            """
            params = []

            if item_type:
                # Filter by item name pattern (e.g., "Accent Chair" matches "Accent Chair 01052")
                query += " AND (Item_Type = ? OR Item_Name LIKE ?)"
                params.append(item_type)
                params.append(f"{item_type}%")

            # Group by Item_Name to show only one item per Item_Name and get count
            query += " GROUP BY Item_Name ORDER BY Item_Name"

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
                        'height': height,
                        'count': item['Item_Count']
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


    # ==========================================================================
    # /api/save-default-rotation + get-default-rotation
    # ==========================================================================

    @rt('/api/save-default-rotation', methods=['POST'])
    async def save_default_rotation(request: Request):
        """Save default properties (rotation, brightness, tilt) for a 3D model"""
        try:
            data = await request.json()
            model3d = data.get('model3d')
            rotation = data.get('rotation')
            brightness = data.get('brightness', 3.0)  # Default brightness
            tilt = data.get('tilt', 0.1745)  # Default tilt (~10 degrees)

            if not model3d or rotation is None:
                return JSONResponse({'success': False, 'error': 'Missing model3d or rotation'}, status_code=400)

            # Create table if it doesn't exist (with brightness and tilt columns)
            async with zoho_db._connection.cursor() as cursor:
                await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS model_default_rotations (
                        model3d TEXT PRIMARY KEY,
                        rotation REAL NOT NULL,
                        brightness REAL DEFAULT 3.0,
                        tilt REAL DEFAULT 0.1745,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Migrate existing table if needed - add brightness and tilt columns
                try:
                    # Check if columns exist
                    await cursor.execute("PRAGMA table_info(model_default_rotations)")
                    columns = await cursor.fetchall()
                    column_names = [col[1] for col in columns]

                    if 'brightness' not in column_names:
                        await cursor.execute('ALTER TABLE model_default_rotations ADD COLUMN brightness REAL DEFAULT 3.0')
                        print("Added brightness column to model_default_rotations")

                    if 'tilt' not in column_names:
                        await cursor.execute('ALTER TABLE model_default_rotations ADD COLUMN tilt REAL DEFAULT 0.1745')
                        print("Added tilt column to model_default_rotations")
                except Exception as migrate_error:
                    print(f"Migration check/update: {migrate_error}")

                # Insert or update all properties
                await cursor.execute('''
                    INSERT INTO model_default_rotations (model3d, rotation, brightness, tilt, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(model3d) DO UPDATE SET
                        rotation = excluded.rotation,
                        brightness = excluded.brightness,
                        tilt = excluded.tilt,
                        updated_at = CURRENT_TIMESTAMP
                ''', (model3d, rotation, brightness, tilt))

            await zoho_db._connection.commit()

            return JSONResponse({'success': True, 'model3d': model3d, 'rotation': rotation, 'brightness': brightness, 'tilt': tilt})
        except Exception as e:
            print(f"Error saving default properties: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


    @rt('/api/get-default-rotation/{model3d}')
    async def get_default_rotation(model3d: str):
        """Get default properties (rotation, brightness, tilt) for a 3D model"""
        try:
            async with zoho_db._connection.cursor() as cursor:
                await cursor.execute('''
                    SELECT rotation, brightness, tilt FROM model_default_rotations WHERE model3d = ?
                ''', (model3d,))
                result = await cursor.fetchone()

            if result:
                return JSONResponse({
                    'success': True,
                    'rotation': result[0],
                    'brightness': result[1] if result[1] is not None else 3.0,
                    'tilt': result[2] if result[2] is not None else 0.1745
                })
            else:
                return JSONResponse({'success': False, 'error': 'No default properties found'}, status_code=404)
        except Exception as e:
            print(f"Error getting default properties: {e}")
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


    # ==========================================================================
    # /api/staging-photos/cleanup (portal-only)
    # ==========================================================================

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


    # ==========================================================================
    # /api/save-staging-models + /api/get-staging-models
    # ==========================================================================

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
                        position_x, position_y, position_z, scale, rotation_y, tilt, brightness,
                        item_name, image_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    model.get('brightness', 2.5),
                    model.get('itemName', ''),
                    model.get('imageUrl', '')
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
                       scale, rotation_y, tilt, brightness, item_name, image_url
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
                    'brightness': row[8],
                    'itemName': row[9],
                    'imageUrl': row[10]
                })

            conn.close()
            return JSONResponse({'success': True, 'models': models})

        except Exception as e:
            print(f"Error getting staging models: {e}")
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


    # =============================================================================
    # TEST API ENDPOINTS - MOVED TO tools/test/test_api_routes.py
    # =============================================================================

    # ==========================================================================
    # register_test_routes(rt) (model_3d test API)
    # ==========================================================================

    register_test_routes(rt)

    # ==========================================================================
    # /api/admin/users*
    # ==========================================================================

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


    @rt('/api/admin/users/create', methods=['POST'])
    async def admin_create_user(request: Request):
        """Create a new user (admin only)"""
        user = get_current_user(request)
        if not user or user.get('user_role') != 'admin':
            return JSONResponse({'error': 'Unauthorized'}, status_code=403)

        try:
            data = await request.json()

            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            phone = data.get('phone')
            user_role = data.get('user_role', 'customer')

            if not first_name or not last_name:
                return JSONResponse({'success': False, 'error': 'First and last name are required'}, status_code=400)
            if not email:
                return JSONResponse({'success': False, 'error': 'Email is required'}, status_code=400)
            if not password:
                return JSONResponse({'success': False, 'error': 'Password is required'}, status_code=400)

            result = create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                phone=phone,
                user_role=user_role
            )

            if result['success']:
                return JSONResponse({'success': True, 'user': result['user']})
            else:
                return JSONResponse({'success': False, 'error': result.get('error', 'Create failed')}, status_code=400)

        except Exception as e:
            print(f"Admin create user error: {e}")
            return JSONResponse({'success': False, 'error': 'Create failed'}, status_code=500)


    # =============================================================================
    # STRIPE PAYMENT ENDPOINTS
    # =============================================================================

    # ==========================================================================
    # /api/client-log*
    # ==========================================================================

    @rt('/api/client-log', methods=['POST'])
    async def client_log(req: Request):
        """Receive and store client-side debug logs"""
        try:
            data = await req.json()
            message = data.get('message', '')
            level = data.get('level', 'info')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # Ensure log file directory exists
            DEBUG_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Append to log file
            with open(DEBUG_LOG_FILE, 'a') as f:
                f.write(f"[{timestamp}] [{level.upper()}] {message}\n")

            return JSONResponse({'success': True})
        except Exception as e:
            print(f"Client log error: {e}")
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


    @rt('/api/client-log')
    def get_client_log(req: Request):
        """Read the client debug log (last 100 lines)"""
        try:
            if not DEBUG_LOG_FILE.exists():
                return Response("No logs yet", media_type="text/plain")

            # Read last 100 lines
            with open(DEBUG_LOG_FILE, 'r') as f:
                lines = f.readlines()
                last_lines = lines[-100:] if len(lines) > 100 else lines

            return Response(''.join(last_lines), media_type="text/plain")
        except Exception as e:
            return Response(f"Error reading logs: {e}", media_type="text/plain")


    @rt('/api/client-log/clear', methods=['POST'])
    def clear_client_log(req: Request):
        """Clear the client debug log"""
        try:
            if DEBUG_LOG_FILE.exists():
                DEBUG_LOG_FILE.unlink()
            return JSONResponse({'success': True})
        except Exception as e:
            return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


    # ==========================================================================
    # /test (inpainting test page)
    # ==========================================================================

    @app.get('/test')
    def test():
        """Test page for comparing inpainting methods - live reload disabled"""
        from fasthtml.common import to_xml
        content = test_inpainting_page()
        # Return response without live reload
        return Response(content=to_xml(content), media_type="text/html")

    # ==========================================================================
    # /signin + /portal
    # ==========================================================================

    @rt('/signin')
    def signin(req: Request):
        """Sign in / Register page"""
        # If already signed in, redirect to portal
        user = get_current_user(req)
        if user:
            return RedirectResponse('/', status_code=302)
        return signin_page()


    @rt('/portal')
    def portal(req: Request):
        """Customer-portal page — disabled on portal.astrastaging.com
        (staff host). Redirect to staff home. If we ever bring the
        customer dashboard back, re-enable portal_page(user) here."""
        user = get_current_user(req)
        if not user:
            return RedirectResponse('/signin', status_code=302)
        return RedirectResponse('/', status_code=302)


