# Image Vacate Tool - Documentation

## Overview

The Image Vacate tool uses AI-powered inpainting to remove furniture, decorations, and objects from staging photos while preserving structural elements like walls, floors, windows, and ceilings.

## Features

- **AI-Powered Object Removal**: Uses LaMa (Large Mask Inpainting) for high-quality results
- **Auto-Detection**: Automatically detects and removes furniture/objects (basic implementation)
- **Custom Masks**: Support for manual mask creation for precise control
- **Web Integration**: Fully integrated with the staging design page
- **Real-time Processing**: Process images on-demand with visual feedback

## Installation

### Step 1: Install Dependencies

```bash
# Install the required Python packages
pip3 install -r tools/image_vacate_requirements.txt
```

**Note**: This will install PyTorch, which is a large package (~1-2GB). The installation may take several minutes.

### Step 2: Verify Installation

```bash
# Test the image vacate tool
python3 tools/image_vacate.py --help
```

You should see the help message with available options.

## Usage

### Web Interface (Recommended)

1. Navigate to the Staging Design page: `/design?id=<staging_id>`
2. Select an area with uploaded photos
3. Click the red **"Vacate"** button in the top-right corner of the photo
4. Wait for processing (typically 5-30 seconds depending on image size and hardware)
5. The vacated photo will replace the original in the carousel

### Command Line

```bash
# Basic usage with auto-detection
python3 tools/image_vacate.py input.jpg -o output.jpg --auto

# With custom mask
python3 tools/image_vacate.py input.jpg -m mask.jpg -o output.jpg

# Force CPU usage
python3 tools/image_vacate.py input.jpg -o output.jpg --device cpu
```

### Python API

```python
from tools.image_vacate import ImageVacator

# Initialize the vacator
vacator = ImageVacator(device="auto")  # auto-detect GPU/CPU

# Vacate an image
result = vacator.vacate_image(
    image_input="path/to/image.jpg",
    auto_detect=True,
    output_path="path/to/output.jpg"
)
```

## API Endpoint

The web application exposes a REST API endpoint for image vacating:

**Endpoint**: `POST /api/vacate-photo`

**Request Body**:
```json
{
    "image": "/static/images/areas/photo.jpg",  // or base64-encoded image
    "mask": "base64-encoded-mask",  // optional
    "auto_detect": true,  // use auto-detection if no mask
    "save": true  // save the result to disk
}
```

**Response**:
```json
{
    "success": true,
    "vacated_image": "data:image/jpeg;base64,...",
    "saved_url": "/static/images/vacated/vacated_abc123.jpg"
}
```

## How It Works

### 1. LaMa Inpainting Model

The tool uses **LaMa (Large Mask Inpainting)**, a state-of-the-art deep learning model published at WACV 2022. LaMa excels at:

- Removing large objects without visible artifacts
- Preserving textures and patterns (walls, floors)
- Handling complex backgrounds
- Maintaining lighting consistency

### 2. Auto-Detection (Basic)

The current auto-detection uses traditional computer vision techniques:

- Adaptive thresholding to detect darker objects
- Morphological operations to clean up the mask
- Works best for furniture against lighter walls

**Future Improvements**:
- Integration with **Segment Anything Model (SAM)** for better object detection
- Custom furniture detection using YOLO or similar models
- Interactive mask editing in the web UI

### 3. Processing Pipeline

```
Input Image → Mask Generation/Loading → LaMa Inpainting → Output Image
```

The model fills in removed areas by:
1. Analyzing surrounding context (walls, floors, textures)
2. Generating plausible content to fill the masked regions
3. Blending seamlessly with existing content

## Performance

### CPU vs GPU

- **CPU**: 10-30 seconds per image (depending on CPU)
- **GPU (CUDA)**: 2-5 seconds per image (with 4GB+ VRAM)

### Image Size

- Recommended: 1920x1440 or smaller
- Larger images will be processed but may take longer
- Output quality is excellent at recommended sizes

## Tips for Best Results

### 1. Photo Quality

- Use well-lit photos with clear visibility
- Avoid heavily shadowed areas
- Higher resolution photos generally produce better results

### 2. Auto-Detection Limitations

The basic auto-detection works best when:
- Furniture is darker than walls/floors
- Clear contrast between objects and background
- Minimal clutter

For complex scenes, consider:
- Taking multiple photos from different angles
- Using manual mask editing (future feature)
- Processing in multiple passes

### 3. Structural Elements

The model automatically preserves:
- Wall textures and colors
- Floor patterns and materials
- Windows and door frames
- Ceiling details
- Lighting fixtures attached to walls/ceilings

## Troubleshooting

### "simple-lama-inpainting not installed" Error

```bash
# Reinstall the dependencies
pip3 install -r tools/image_vacate_requirements.txt
```

### Out of Memory (GPU)

```bash
# Force CPU usage instead
python3 tools/image_vacate.py input.jpg --device cpu
```

Or reduce the image size before processing.

### Poor Results

1. **Too much removed**: The auto-detection may be too aggressive
   - Future: Use manual mask editing
   - Workaround: Pre-process images with better lighting

2. **Visible artifacts**: This can happen with complex scenes
   - Try processing from a different angle
   - Ensure good lighting in original photo
   - Consider using the upcoming manual mask feature

3. **Wrong objects removed**: Auto-detection limitations
   - Future: Interactive object selection with SAM
   - Workaround: Use custom masks (advanced users)

## Future Enhancements

### Planned Features

1. **Interactive Mask Editing**
   - Draw/erase on photos to specify what to remove
   - Real-time mask preview
   - Brush size controls

2. **SAM Integration**
   - Click-to-select objects
   - Automatic furniture segmentation
   - Multi-object removal in one pass

3. **3D Furniture Placement**
   - After vacating, place 3D furniture models
   - Drag-and-drop interface
   - Realistic rendering with shadows

4. **Batch Processing**
   - Process multiple photos at once
   - Queue system for long operations
   - Progress tracking

5. **Undo/Redo**
   - Keep original photos
   - Revert to previous states
   - Compare before/after side-by-side

## Technical Details

### Libraries Used

- **simple-lama-inpainting**: Wrapper for LaMa model
- **PyTorch**: Deep learning framework
- **OpenCV**: Image processing and mask operations
- **Pillow (PIL)**: Image loading/saving
- **NumPy**: Numerical operations

### Model Information

- **Architecture**: LaMa (Large Mask Inpainting)
- **Paper**: "Resolution-robust Large Mask Inpainting with Fourier Convolutions" (WACV 2022)
- **Strengths**:
  - Handles large missing regions
  - Preserves fine details and textures
  - Fast inference
  - Robust to resolution changes

### File Structure

```
tools/
├── image_vacate.py              # Main image vacating module
├── image_vacate_requirements.txt # Python dependencies
└── IMAGE_VACATE_README.md       # This file

static/images/
└── vacated/                     # Vacated images stored here
```

## Support & Feedback

For issues or feature requests related to the Image Vacate tool, please:

1. Check this documentation first
2. Verify dependencies are installed correctly
3. Test with different images to isolate the issue
4. Report bugs with example images (if possible)

## References

- [LaMa Paper](https://arxiv.org/abs/2109.07161)
- [simple-lama-inpainting](https://github.com/enesmsahin/simple-lama-inpainting)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Segment Anything Model (SAM)](https://segment-anything.com/)
