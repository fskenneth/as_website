"""
Test page for comparing 3 different inpainting methods
This page will be removed after testing is complete
"""

from fasthtml.common import *


def test_inpainting_page():
    """
    Page for testing and comparing 3 inpainting methods:
    1. LaMa (simple-lama-inpainting) - AI/ML method
    2. OpenCV Navier-Stokes - Traditional CV method
    3. OpenCV Telea - Traditional CV alternative algorithm
    """

    styles = Style("""
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        /* Full-width 3D viewer */
        #convert3DResults {
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
        }

        #convert3DResults h4 {
            padding: 1rem 2rem;
            margin: 0;
        }

        #convert3DResults #3dModelInfo,
        #convert3DResults > div:last-child {
            padding: 0.5rem 2rem;
        }

        #threejsViewer,
        #roomCompositeViewer {
            position: relative;
            left: 50%;
            transform: translateX(-50%);
            width: 100vw !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            border-radius: 0 !important;
            aspect-ratio: 4/3 !important;
        }

        /* Mobile styles */
        @media (max-width: 768px) {
            body {
                padding: 0 !important;
            }

            .container {
                max-width: 100%;
                border-radius: 0;
                padding: 0;
                box-shadow: none;
            }

            .container > h1,
            .container > .subtitle,
            .container > .upload-section,
            .container > .preview-section,
            .container > .btn-group,
            .container > .results-grid,
            .container > .history-section > *:not(#threejsViewer):not(#roomCompositeViewer):not(#convert3DResults) {
                margin-left: 1rem;
                margin-right: 1rem;
            }

            .upload-section,
            .result-card,
            .history-section {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }

        .upload-section {
            background: #f8f9fa;
            border: 3px dashed #dee2e6;
            border-radius: 12px;
            padding: 3rem;
            text-align: center;
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }

        .upload-section:hover {
            border-color: #667eea;
            background: #f0f4ff;
        }

        .upload-section.drag-over {
            border-color: #667eea;
            background: #e7edff;
            transform: scale(1.02);
        }

        #imageInput {
            display: none;
        }

        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .vacate-btn {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            font-size: 1rem;
            border-radius: 8px;
            cursor: pointer;
            margin: 0.5rem;
            transition: all 0.2s ease;
        }

        .vacate-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
        }

        .vacate-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .btn-group {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            margin: 2rem auto;
            gap: 1rem;
        }

        .vacate-btn.method-1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .vacate-btn.method-2 {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }

        .vacate-btn.method-3 {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .vacate-btn.method-4 {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }

        .vacate-btn.method-5 {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        /* Mesh Editor Styles */
        .edit-btn {
            background: #e5e7eb;
            color: #374151;
            border: 1px solid #d1d5db;
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .edit-btn:hover:not(:disabled) {
            background: #d1d5db;
        }
        .edit-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .edit-btn.active, .edit-btn[style*="background: #6366f1"] {
            background: #6366f1 !important;
            color: white !important;
            border-color: #6366f1 !important;
        }
        .edit-btn.danger {
            background: #fee2e2;
            color: #dc2626;
            border-color: #fecaca;
        }
        .edit-btn.danger:hover:not(:disabled) {
            background: #fecaca;
        }
        .edit-btn.small {
            padding: 0.3rem 0.6rem;
            font-size: 0.75rem;
        }
        .mesh-part-item {
            padding: 0.4rem 0.6rem;
            margin: 0.2rem 0;
            background: #fff;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
        }
        .mesh-part-item:hover {
            background: #f3f4f6;
        }
        .mesh-part-item.selected {
            background: #fef3c7;
            border-color: #f59e0b;
        }
        .mesh-part-item .part-name {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .mesh-part-item .part-actions {
            display: flex;
            gap: 0.3rem;
        }
        .mesh-part-item .part-actions button {
            padding: 0.15rem 0.3rem;
            font-size: 0.7rem;
            background: #e5e7eb;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .mesh-part-item .part-actions button:hover {
            background: #d1d5db;
        }

        .preview-section {
            margin: 2rem 0;
            text-align: center;
        }

        .preview-section img {
            max-width: 100%;
            max-height: 400px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .preview-section h3 {
            margin-bottom: 1rem;
            color: #333;
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }

        .result-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .result-card h3 {
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }

        .result-card .method-description {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            min-height: 40px;
        }

        .result-card img {
            width: 100%;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin-top: 1rem;
        }

        .stat-item {
            background: white;
            padding: 0.75rem;
            border-radius: 6px;
            text-align: center;
        }

        .stat-label {
            font-size: 0.8rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }

        .stat-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #333;
        }

        .stat-value.time {
            color: #667eea;
        }

        .stat-value.cost {
            color: #f5576c;
        }

        .stat-value.quality {
            color: #43a047;
        }

        .loading {
            text-align: center;
            padding: 3rem;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #ffebee;
            color: #c62828;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #c62828;
        }

        .success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #2e7d32;
        }

        .hidden {
            display: none;
        }

        .history-section {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #e0e0e0;
        }

        .history-section h2 {
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
        }

        .history-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .history-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .history-item .before-after {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .history-item img {
            width: 100%;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .history-item .label {
            font-size: 0.75rem;
            color: #666;
            text-align: center;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .history-item .timestamp {
            font-size: 0.8rem;
            color: #999;
            text-align: center;
            margin-top: 0.5rem;
        }

        .history-item img {
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .history-item img:hover {
            transform: scale(1.05);
        }

        /* Modal styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.95);
            animation: fadeIn 0.3s ease;
        }

        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            max-width: 95%;
            max-height: 95%;
            object-fit: contain;
            animation: zoomIn 0.3s ease;
        }

        .modal-close {
            position: absolute;
            top: 20px;
            right: 40px;
            color: #fff;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.2s ease;
            z-index: 10000;
        }

        .modal-close:hover {
            color: #ccc;
        }

        .modal-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: #fff;
            font-size: 60px;
            font-weight: bold;
            cursor: pointer;
            padding: 20px;
            user-select: none;
            transition: color 0.2s ease;
        }

        .modal-nav:hover {
            color: #ccc;
        }

        .modal-nav.prev {
            left: 20px;
        }

        .modal-nav.next {
            right: 20px;
        }

        .modal-caption {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: #fff;
            font-size: 1.2rem;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px 20px;
            border-radius: 8px;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes zoomIn {
            from { transform: scale(0.8); }
            to { transform: scale(1); }
        }
    """)

    scripts = Script("""
        let uploadedImage = null;
        let currentImages = [];
        let currentImageIndex = 0;

        function triggerUpload() {
            document.getElementById('imageInput').click();
        }

        function openModal(imageSrc, caption, index) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const modalCaption = document.getElementById('modalCaption');

            modal.classList.add('active');
            modalImg.src = imageSrc;
            modalCaption.textContent = caption;
            currentImageIndex = index;

            // Prevent body scroll
            document.body.style.overflow = 'hidden';
        }

        function closeModal() {
            const modal = document.getElementById('imageModal');
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }

        function navigateModal(direction) {
            currentImageIndex += direction;
            if (currentImageIndex < 0) currentImageIndex = currentImages.length - 1;
            if (currentImageIndex >= currentImages.length) currentImageIndex = 0;

            const img = currentImages[currentImageIndex];
            document.getElementById('modalImage').src = img.src;
            document.getElementById('modalCaption').textContent = img.caption;
        }

        async function loadHistory() {
            try {
                const response = await fetch('/api/inpainting-history');
                const data = await response.json();

                if (data.history && data.history.length > 0) {
                    const historyGrid = document.getElementById('historyGrid');
                    historyGrid.innerHTML = '';
                    currentImages = [];

                    // Display in reverse order (newest first)
                    data.history.reverse().forEach((item, index) => {
                        const historyItem = document.createElement('div');
                        historyItem.className = 'history-item';

                        const timestamp = new Date(item.timestamp).toLocaleString();
                        // Support both URL format (new) and base64 format (legacy)
                        const inputSrc = item.input_url || `data:image/png;base64,${item.input_base64}`;
                        const outputSrc = item.output_url || `data:image/png;base64,${item.output_base64}`;

                        // Add images to navigation array
                        currentImages.push({
                            src: inputSrc,
                            caption: `Before - ${timestamp}`
                        });
                        currentImages.push({
                            src: outputSrc,
                            caption: `After - ${timestamp}`
                        });

                        historyItem.innerHTML = `
                            <div class="before-after">
                                <div>
                                    <div class="label">Before</div>
                                    <img src="${inputSrc}" alt="Before" onclick="openModal('${inputSrc}', 'Before - ${timestamp}', ${index * 2})">
                                </div>
                                <div>
                                    <div class="label">After</div>
                                    <img src="${outputSrc}" alt="After" onclick="openModal('${outputSrc}', 'After - ${timestamp}', ${index * 2 + 1})">
                                </div>
                            </div>
                            <div class="timestamp">${timestamp}</div>
                        `;

                        historyGrid.appendChild(historyItem);
                    });

                    document.getElementById('historySection').classList.remove('hidden');
                } else {
                    document.getElementById('historySection').classList.add('hidden');
                }
            } catch (error) {
                console.error('Failed to load history:', error);
            }
        }

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                handleImageUpload(file);
            }
        }

        function handleImageUpload(file) {
            if (!file.type.startsWith('image/')) {
                showError('Please upload an image file');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedImage = e.target.result;

                // Show preview
                document.getElementById('previewSection').classList.remove('hidden');
                document.getElementById('previewImage').src = uploadedImage;

                // Enable all method buttons
                document.querySelectorAll('.vacate-btn').forEach(btn => btn.disabled = false);

                // Hide results from previous test
                document.getElementById('resultsSection').classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }

        async function vacateImage(methodNum) {
            if (!uploadedImage) {
                showError('Please upload an image first');
                return;
            }

            // Show loading
            document.getElementById('loadingSection').classList.remove('hidden');
            document.getElementById('loadingText').textContent = 'Processing with Method ' + methodNum + '...';

            // Disable all buttons
            document.querySelectorAll('.vacate-btn').forEach(btn => btn.disabled = true);

            try {
                const response = await fetch('/api/test-inpainting', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image: uploadedImage,
                        method: methodNum
                    })
                });

                const data = await response.json();

                if (data.success) {
                    displayResult(methodNum, data.result);
                    // Reload history to show the new entry
                    loadHistory();
                } else {
                    showError(data.error || 'Processing failed');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                document.getElementById('loadingSection').classList.add('hidden');
                document.querySelectorAll('.vacate-btn').forEach(btn => btn.disabled = false);
            }
        }

        function displayResult(methodNum, result) {
            // Show results section
            document.getElementById('resultsSection').classList.remove('hidden');

            const cardId = 'result' + methodNum + 'Card';
            const card = document.getElementById(cardId);

            if (result && !result.error) {
                document.getElementById('result' + methodNum + 'Image').src = 'data:image/png;base64,' + result.result_base64;
                document.getElementById('result' + methodNum + 'Time').textContent = result.processing_time.toFixed(2) + 's';
                document.getElementById('result' + methodNum + 'Cost').textContent = result.estimated_cost;
                document.getElementById('result' + methodNum + 'Quality').textContent = result.quality_rating;
                document.getElementById('result' + methodNum + 'Desc').textContent = result.description;
                // Reset card HTML in case it was showing an error before
                card.querySelector('img').style.display = 'block';
            } else {
                card.innerHTML = '<h3>Method ' + methodNum + '</h3><div class="error">Method ' + methodNum + ' failed: ' + (result?.error || 'Unknown error') + '</div>';
            }
        }

        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = message;
            document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.upload-section'));
            setTimeout(() => errorDiv.remove(), 5000);
        }

        // Initialize drag and drop when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            const uploadSection = document.querySelector('.upload-section');

            if (uploadSection) {
                uploadSection.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadSection.classList.add('drag-over');
                });

                uploadSection.addEventListener('dragleave', () => {
                    uploadSection.classList.remove('drag-over');
                });

                uploadSection.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadSection.classList.remove('drag-over');

                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        handleImageUpload(files[0]);
                    }
                });
            }

            // Load history on page load
            loadHistory();
            load3DHistory();

            // Keyboard navigation for modal
            document.addEventListener('keydown', (e) => {
                const modal = document.getElementById('imageModal');
                if (modal.classList.contains('active')) {
                    if (e.key === 'Escape') {
                        closeModal();
                    } else if (e.key === 'ArrowLeft') {
                        navigateModal(-1);
                    } else if (e.key === 'ArrowRight') {
                        navigateModal(1);
                    }
                }
            });

            // Initialize furniture upload drag and drop
            const furnitureUpload = document.getElementById('furnitureUploadSection');
            if (furnitureUpload) {
                furnitureUpload.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    furnitureUpload.classList.add('drag-over');
                });
                furnitureUpload.addEventListener('dragleave', () => {
                    furnitureUpload.classList.remove('drag-over');
                });
                furnitureUpload.addEventListener('drop', (e) => {
                    e.preventDefault();
                    furnitureUpload.classList.remove('drag-over');
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        handleFurnitureUpload(files[0]);
                    }
                });
            }
        });

        // ========== Furniture to 3D Functions ==========
        let furnitureImage = null;
        let bgRemovedImage = null;
        let current3DModel = null;
        let threeScene = null;
        let threeRenderer = null;
        let threeCamera = null;
        let threeControls = null;

        function triggerFurnitureUpload() {
            document.getElementById('furnitureInput').click();
        }

        function handleFurnitureSelect(event) {
            const file = event.target.files[0];
            if (file) {
                handleFurnitureUpload(file);
            }
        }

        function handleFurnitureUpload(file) {
            if (!file.type.startsWith('image/')) {
                showError('Please upload an image file');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                furnitureImage = e.target.result;
                bgRemovedImage = null; // Reset background removed image

                // Show preview
                document.getElementById('furniturePreviewSection').classList.remove('hidden');
                document.getElementById('furniturePreview').src = furnitureImage;

                // Show both sections (background removal and 3D conversion)
                document.getElementById('bgRemovalSection').classList.remove('hidden');
                document.getElementById('convert3DSection').classList.remove('hidden');

                // Enable buttons
                document.getElementById('removeBgBtn').disabled = false;
                document.getElementById('convertBtn').disabled = false;

                // Hide previous results
                document.getElementById('bgRemovedPreviewSection').classList.add('hidden');
                document.getElementById('convert3DResults').classList.add('hidden');
                document.getElementById('roomPlacementSection').classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }

        async function removeBackground() {
            if (!furnitureImage) {
                showError('Please upload a furniture image first');
                return;
            }

            const bgMethod = document.querySelector('input[name="bgMethod"]:checked').value;

            // Show loading
            document.getElementById('convert3DLoading').classList.remove('hidden');
            document.getElementById('convert3DStatus').textContent = 'Removing background with ' + bgMethod + '...';
            document.getElementById('removeBgBtn').disabled = true;

            try {
                const bgResponse = await fetch('/api/remove-background', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: furnitureImage,
                        method: bgMethod
                    })
                });

                const bgData = await bgResponse.json();
                if (!bgData.success) {
                    throw new Error(bgData.error || 'Background removal failed');
                }

                bgRemovedImage = bgData.result_base64;
                document.getElementById('bgRemovedPreview').src = 'data:image/png;base64,' + bgRemovedImage;
                document.getElementById('bgRemovalPreviewInfo').textContent =
                    `Method: ${bgMethod} | Time: ${bgData.processing_time?.toFixed(2) || '?'}s | ${bgData.info || ''}`;

                // Show result
                document.getElementById('bgRemovedPreviewSection').classList.remove('hidden');

            } catch (error) {
                showError('Background removal error: ' + error.message);
            } finally {
                document.getElementById('convert3DLoading').classList.add('hidden');
                document.getElementById('removeBgBtn').disabled = false;
            }
        }

        async function convertTo3D() {
            if (!furnitureImage) {
                showError('Please upload a furniture image first');
                return;
            }

            const method3D = 'tripo3d';  // Using Tripo3D API only
            const useBgRemovedCheckbox = document.getElementById('useBgRemoved');

            // Determine which image to use
            let imageToConvert = furnitureImage;
            if (useBgRemovedCheckbox.checked && bgRemovedImage) {
                imageToConvert = 'data:image/png;base64,' + bgRemovedImage;
            }

            // Show loading
            document.getElementById('convert3DLoading').classList.remove('hidden');
            document.getElementById('convert3DStatus').textContent = 'Converting to 3D with Tripo3D... (this may take 60-90 seconds)';
            document.getElementById('convertBtn').disabled = true;

            // Start a timer to show progress
            let elapsed = 0;
            const timer = setInterval(() => {
                elapsed++;
                document.getElementById('convert3DStatus').textContent =
                    `Converting to 3D with Tripo3D... ${elapsed}s elapsed`;
            }, 1000);

            try {
                // Use AbortController for timeout (3 minutes max)
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 180000);

                // Get Tripo3D parameters from UI
                const tripo3dParams = {
                    pbr: document.getElementById('tripo3dPbr')?.checked ?? true,
                    enable_image_autofix: document.getElementById('tripo3dAutofix')?.checked ?? true,
                    orientation: document.getElementById('tripo3dOrientation')?.checked ? 'align_image' : 'default',
                    prompt: document.getElementById('tripo3dPrompt')?.value || ''
                };

                const response3D = await fetch('/api/convert-to-3d', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageToConvert,
                        method: method3D,
                        ...tripo3dParams
                    }),
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                const data3D = await response3D.json();
                if (!data3D.success) {
                    throw new Error(data3D.error || '3D conversion failed');
                }

                current3DModel = data3D;
                const usedImage = (useBgRemovedCheckbox.checked && bgRemovedImage) ? 'bg-removed' : 'original';
                document.getElementById('3dModelInfo').textContent =
                    `Method: Tripo3D | Time: ${data3D.processing_time?.toFixed(2) || '?'}s | Format: ${data3D.format || 'glb'} | Source: ${usedImage}`;

                // Show results
                document.getElementById('convert3DResults').classList.remove('hidden');

                // Initialize Three.js viewer
                init3DViewer(data3D.model_url || data3D.model_base64, data3D.format);

                // Show room placement section and populate dropdown
                document.getElementById('roomPlacementSection').classList.remove('hidden');
                populateRoomSelector();

            } catch (error) {
                if (error.name === 'AbortError') {
                    showError('3D conversion timed out. Please try again.');
                } else {
                    showError('3D conversion error: ' + error.message);
                }
            } finally {
                clearInterval(timer);
                document.getElementById('convert3DLoading').classList.add('hidden');
                document.getElementById('convertBtn').disabled = false;
            }
        }

        function init3DViewer(modelData, format) {
            const container = document.getElementById('threejsViewer');
            container.innerHTML = ''; // Clear previous

            // Reset control state since we're creating a new viewer
            showControlButtons = false;
            controlOverlay = null;

            // Check if Three.js is loaded
            if (typeof THREE === 'undefined') {
                loadThreeJS().then(() => setupThreeScene(container, modelData, format));
            } else {
                setupThreeScene(container, modelData, format);
            }
        }

        async function loadThreeJS() {
            // Load Three.js and GLTFLoader from CDN
            await loadScript('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js');
            await loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js');
            await loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js');
            await loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/TransformControls.js');
            await loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/exporters/GLTFExporter.js');
            await loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/utils/BufferGeometryUtils.js');
        }

        function loadScript(src) {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }

        let currentLoadedModel = null;  // Currently selected model for controls
        let allLoadedModels = [];  // All models in the scene
        let isDraggingModel = false;
        let isDraggingRotate = false;
        let isDraggingScale = false;
        let isDraggingBrightness = false;
        let isDraggingTilt = false;
        let lastMouseX = 0;
        let lastMouseY = 0;
        let modelBrightness = 2.5; // Max brightness by default
        let viewerContainer = null;
        let controlOverlay = null;

        // Object contact points (e.g., chair legs)
        let objectContactPoints = [];  // 4 world coordinates on the object that touch floor
        let isDefiningContactPoints = false;
        let contactMarkers = [];  // DOM elements showing contact points
        let userYRotation = 0;  // Track user's Y rotation separately from leveling
        let levelingQuaternion = null;  // Store the initial leveling rotation

        // Visibility toggles
        let showContactMarkers = true;
        let showControlButtons = false;  // Start hidden, show on model click

        // For maintaining constant apparent size when moving in Z
        let modelReferenceZ = 0;  // Z position where baseScale applies
        let modelBaseScale = 1;   // Scale at reference Z position
        const cameraZ = 10;       // Camera Z position (must match camera setup)
        const DEFAULT_TILT = 10 * Math.PI / 180;  // Default tilt angle (10 degrees)
        let modelTilt = DEFAULT_TILT;  // Model X rotation for tilting view angle

        // State persistence
        let currentBackgroundImage = null;  // Track current background image URL
        let saveStateTimeout = null;  // Debounce timer for auto-save

        // Debounced save function for single model (500ms delay)
        function saveModelState() {
            // Now delegates to saveAllModelStates
            saveAllModelStates();
        }

        // Save all model instances to the server
        function saveAllModelStates() {
            console.log('saveAllModelStates called with:', {
                bgImage: currentBackgroundImage,
                modelUrl: current3DModel?.model_url,
                numModels: allLoadedModels.length
            });

            if (!currentBackgroundImage) {
                console.log('saveAllModelStates: No background image');
                return;
            }
            if (!current3DModel?.model_url) {
                console.log('saveAllModelStates: No model URL');
                return;
            }
            if (allLoadedModels.length === 0) {
                console.log('saveAllModelStates: No models to save');
                return;
            }

            if (saveStateTimeout) clearTimeout(saveStateTimeout);
            saveStateTimeout = setTimeout(() => {
                // Collect state from all models - each model has its own rotation stored in userData
                const models = allLoadedModels.map(model => {
                    // Get per-model rotation from userData, fallback to globals for current model
                    const yRot = model.userData.yRotation !== undefined ? model.userData.yRotation :
                                 (model === currentLoadedModel ? userYRotation : 0);
                    const tilt = model.userData.tilt !== undefined ? model.userData.tilt :
                                 (model === currentLoadedModel ? modelTilt : DEFAULT_TILT);
                    return {
                        position_x: model.position.x,
                        position_y: model.position.y,
                        position_z: model.position.z,
                        scale: model.scale.x,
                        rotation_y: yRot,
                        tilt: tilt,
                        brightness: modelBrightness
                    };
                });

                const payload = {
                    background_image: currentBackgroundImage,
                    model_url: current3DModel.model_url,
                    models: models
                };

                console.log('Saving all model states:', payload);

                fetch('/api/save-all-models', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                }).then(r => r.json()).then(result => {
                    if (result.success) {
                        console.log('All model states saved successfully, count:', result.count);
                    } else {
                        console.error('Failed to save model states:', result.error);
                    }
                }).catch(err => console.error('Save all states error:', err));
            }, 500);
        }

        // Load all saved models for a background
        async function loadAllSavedModels(backgroundImage) {
            console.log('loadAllSavedModels called with backgroundImage:', backgroundImage);
            try {
                const params = new URLSearchParams({
                    background_image: backgroundImage
                });
                const response = await fetch(`/api/models-for-background?${params}`);
                if (response.ok) {
                    const models = await response.json();
                    console.log('Loaded models from server:', models);
                    if (Array.isArray(models) && models.length > 0) {
                        return models;
                    }
                }
            } catch (err) {
                console.error('Load all models error:', err);
            }
            return null;
        }

        // Load saved state for a model (kept for backwards compatibility)
        async function loadSavedModelState(backgroundImage, modelUrl) {
            try {
                const params = new URLSearchParams({
                    background_image: backgroundImage,
                    model_url: modelUrl
                });
                const response = await fetch(`/api/model-state?${params}`);
                if (response.ok) {
                    const state = await response.json();
                    if (state && state.position_x !== undefined) {
                        return state;
                    }
                }
            } catch (err) {
                console.error('Load state error:', err);
            }
            return null;
        }

        function setupThreeScene(container, modelData, format) {
            viewerContainer = container;
            const width = window.innerWidth;
            const height = width * (3 / 4); // 4:3 aspect ratio
            container.style.height = height + 'px';

            // Scene
            threeScene = new THREE.Scene();

            // Use 2nd after photo as background if available (index 3 = 2nd after)
            // Fallback to 1st after (index 1), then any after image
            let bgImageSrc = null;
            if (currentImages.length > 3 && currentImages[3].src) {
                bgImageSrc = currentImages[3].src;
            } else if (currentImages.length > 1 && currentImages[1].src) {
                bgImageSrc = currentImages[1].src;
            }

            if (bgImageSrc) {
                currentBackgroundImage = bgImageSrc;  // Track for state persistence
                const textureLoader = new THREE.TextureLoader();
                textureLoader.load(bgImageSrc, (bgTexture) => {
                    threeScene.background = bgTexture;
                }, undefined, (error) => {
                    console.error('Error loading background:', error);
                    threeScene.background = new THREE.Color(0x1a1a2e);
                });
            } else {
                // No background image available - use a default identifier for state persistence
                currentBackgroundImage = 'default_session';
                threeScene.background = new THREE.Color(0x1a1a2e);
            }
            console.log('Background image for state persistence:', currentBackgroundImage);

            // Camera - orthographic to keep leg bottoms on horizontal line when rotating
            const aspect = width / height;
            const frustumSize = 5;
            threeCamera = new THREE.OrthographicCamera(
                frustumSize * aspect / -2,
                frustumSize * aspect / 2,
                frustumSize / 2,
                frustumSize / -2,
                0.1,
                1000
            );
            threeCamera.position.set(0, 0, 10);
            threeCamera.lookAt(0, 0, 0);

            // Renderer
            threeRenderer = new THREE.WebGLRenderer({ antialias: true });
            threeRenderer.setSize(width, height);
            threeRenderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(threeRenderer.domElement);

            // Lights
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            threeScene.add(ambientLight);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(5, 10, 7);
            threeScene.add(directionalLight);

            // Add control overlay UI
            addControlOverlay(container);

            // Load model based on format
            if (format === 'texture') {
                loadTextureAsPlane(modelData);
            } else if (modelData.startsWith('http') || modelData.startsWith('/')) {
                loadGLTFModel(modelData);
            } else {
                const blob = base64ToBlob(modelData, 'model/gltf-binary');
                const url = URL.createObjectURL(blob);
                loadGLTFModel(url);
            }

            // Animation loop
            function animate() {
                requestAnimationFrame(animate);
                threeRenderer.render(threeScene, threeCamera);
                updateControlPositions();
                updateContactMarkerPositions();
            }
            animate();

            // Handle resize
            window.addEventListener('resize', () => {
                const newWidth = window.innerWidth;
                const newHeight = newWidth * (3 / 4); // 4:3 aspect ratio
                container.style.height = newHeight + 'px';
                const newAspect = newWidth / newHeight;
                const frustumSize = 5;
                threeCamera.left = frustumSize * newAspect / -2;
                threeCamera.right = frustumSize * newAspect / 2;
                threeCamera.top = frustumSize / 2;
                threeCamera.bottom = frustumSize / -2;
                threeCamera.updateProjectionMatrix();
                threeRenderer.setSize(newWidth, newHeight);
            });

            // Setup mouse/touch events for model dragging
            setupModelDragEvents(container);
        }

        function getModelScreenPosition() {
            if (!currentLoadedModel || !threeCamera || !viewerContainer) return null;

            // Use model's position as center (not bounding box center)
            // This keeps buttons fixed relative to model center during rotation
            const modelPos = currentLoadedModel.position.clone();

            // Use a fixed offset in world units for button positioning
            // This ensures buttons don't move when model rotates
            const fixedOffset = 1.0;  // Fixed distance in world units

            // Project center and fixed offset points to screen
            const centerScreen = modelPos.clone().project(threeCamera);
            const bottomCenter = new THREE.Vector3(modelPos.x, modelPos.y - fixedOffset, modelPos.z).project(threeCamera);
            const topCenter = new THREE.Vector3(modelPos.x, modelPos.y + fixedOffset, modelPos.z).project(threeCamera);
            const rightCenter = new THREE.Vector3(modelPos.x + fixedOffset, modelPos.y, modelPos.z).project(threeCamera);
            const leftCenter = new THREE.Vector3(modelPos.x - fixedOffset, modelPos.y, modelPos.z).project(threeCamera);

            const rect = viewerContainer.getBoundingClientRect();
            const width = rect.width;
            const height = rect.height;

            return {
                centerX: (centerScreen.x + 1) / 2 * width,
                centerY: (-centerScreen.y + 1) / 2 * height,
                bottomY: (-bottomCenter.y + 1) / 2 * height,
                topY: (-topCenter.y + 1) / 2 * height,
                rightX: (rightCenter.x + 1) / 2 * width,
                leftX: (leftCenter.x + 1) / 2 * width
            };
        }

        function updateControlPositions() {
            if (!controlOverlay || !currentLoadedModel) return;

            const pos = getModelScreenPosition();
            if (!pos) return;

            const rotateCtrl = controlOverlay.querySelector('.rotate-control');
            const scaleCtrl = controlOverlay.querySelector('.scale-control');
            const brightnessCtrl = controlOverlay.querySelector('.brightness-control');
            const tiltCtrl = controlOverlay.querySelector('.tilt-control');
            const tiltResetCtrl = controlOverlay.querySelector('.tilt-reset-control');
            const addModelCtrl = controlOverlay.querySelector('.add-model-control');
            const removeModelCtrl = controlOverlay.querySelector('.remove-model-control');
            const thumbnailCtrl = controlOverlay.querySelector('.thumbnail-control');

            // Use consistent offset from model edges for symmetry
            const buttonOffset = 20;

            // Top row buttons centered as a group: brightness, +, -, thumbnail
            const topRowY = Math.max(pos.topY - buttonOffset, 10);
            if (brightnessCtrl) {
                brightnessCtrl.style.left = (pos.centerX - 65) + 'px';
                brightnessCtrl.style.top = topRowY + 'px';
            }
            if (addModelCtrl) {
                addModelCtrl.style.left = (pos.centerX - 10) + 'px';
                addModelCtrl.style.top = topRowY + 'px';
            }
            if (removeModelCtrl) {
                removeModelCtrl.style.left = (pos.centerX + 30) + 'px';
                removeModelCtrl.style.top = topRowY + 'px';
            }
            if (thumbnailCtrl) {
                thumbnailCtrl.style.left = (pos.centerX + 70) + 'px';
                thumbnailCtrl.style.top = topRowY + 'px';
            }
            // Bottom rotate button - closer to model
            if (rotateCtrl) {
                rotateCtrl.style.left = pos.centerX + 'px';
                rotateCtrl.style.top = Math.min(pos.bottomY - 35, viewerContainer.clientHeight - 50) + 'px';
            }
            // Side buttons - closer to model
            if (scaleCtrl) {
                scaleCtrl.style.left = Math.min(pos.rightX + buttonOffset - 30, viewerContainer.clientWidth - 50) + 'px';
                scaleCtrl.style.top = pos.centerY + 'px';
            }
            if (tiltCtrl) {
                tiltCtrl.style.left = Math.max(pos.leftX - buttonOffset - 6, 10) + 'px';
                tiltCtrl.style.top = pos.centerY + 'px';
            }
            if (tiltResetCtrl) {
                tiltResetCtrl.style.left = Math.max(pos.leftX - buttonOffset - 6, 10) + 'px';
                tiltResetCtrl.style.top = (pos.centerY + 45) + 'px';
            }
        }

        function addControlOverlay(container) {
            // Remove existing overlay if any
            const existingOverlay = container.querySelector('.viewer-controls');
            if (existingOverlay) existingOverlay.remove();

            const overlay = document.createElement('div');
            overlay.className = 'viewer-controls';
            overlay.style.cssText = 'position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 100;';
            controlOverlay = overlay;

            // Rotate control (left-right arrows) - positioned under object (Y rotation)
            const rotateBtn = document.createElement('div');
            rotateBtn.className = 'rotate-control';
            rotateBtn.innerHTML = `<svg width="28" height="20" viewBox="0 0 28 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="4" y1="10" x2="24" y2="10"/>
                <polyline points="8,5 3,10 8,15"/>
                <polyline points="20,5 25,10 20,15"/>
            </svg>`;
            rotateBtn.style.cssText = `
                position: absolute; bottom: 20px; left: 50%; transform: translate(-50%, 0);
                width: 50px; height: 36px; background: rgba(255,255,255,0.9); border-radius: 18px;
                display: none; align-items: center; justify-content: center;
                cursor: ew-resize; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000;
            `;
            rotateBtn.title = 'Drag left/right to rotate (Y axis)';


            // Scale control (up-down arrows) - positioned to right of object
            const scaleControl = document.createElement('div');
            scaleControl.className = 'scale-control';
            scaleControl.innerHTML = '↕';
            scaleControl.style.cssText = `
                position: absolute; right: 20px; top: 50%; transform: translate(0, -50%);
                width: 36px; height: 50px; background: rgba(255,255,255,0.9); border-radius: 18px;
                display: none; align-items: center; justify-content: center; font-size: 24px;
                cursor: ns-resize; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000; font-weight: bold; padding-bottom: 6px;
            `;
            scaleControl.title = 'Drag up/down to resize';

            // Brightness control (sun icon) - positioned above object
            const brightnessControl = document.createElement('div');
            brightnessControl.className = 'brightness-control';
            brightnessControl.innerHTML = '☀';
            brightnessControl.style.cssText = `
                position: absolute; top: 20px; left: 50%; transform: translate(-50%, 0);
                width: 50px; height: 36px; background: rgba(255,255,255,0.9); border-radius: 18px;
                display: none; align-items: center; justify-content: center; font-size: 20px;
                cursor: ew-resize; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000; font-weight: bold;
            `;
            brightnessControl.title = 'Drag left/right to adjust brightness';

            // Tilt control (up-down arrows) - positioned to left of object
            const tiltControl = document.createElement('div');
            tiltControl.className = 'tilt-control';
            tiltControl.innerHTML = '↕';
            tiltControl.style.cssText = `
                position: absolute; left: 20px; top: 50%; transform: translate(0, -50%);
                width: 36px; height: 50px; background: rgba(255,255,255,0.9); border-radius: 18px;
                display: none; align-items: center; justify-content: center; font-size: 24px;
                cursor: ns-resize; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000; font-weight: bold; padding-bottom: 6px;
            `;
            tiltControl.title = 'Drag up/down to tilt object (X rotation)';

            // Tilt reset button (circular arrow) - positioned below tilt control
            const tiltResetBtn = document.createElement('div');
            tiltResetBtn.className = 'tilt-reset-control';
            tiltResetBtn.innerHTML = '↺';
            tiltResetBtn.style.cssText = `
                position: absolute; left: 20px; top: calc(50% + 35px); transform: translate(0, -50%);
                width: 36px; height: 36px; background: rgba(255,255,255,0.9); border-radius: 50%;
                display: none; align-items: center; justify-content: center; font-size: 24px;
                cursor: pointer; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000; font-weight: bold;
            `;
            tiltResetBtn.title = 'Reset tilt to default angle';

            // Add another model button (+ icon) - positioned right of brightness
            const addModelBtn = document.createElement('div');
            addModelBtn.className = 'add-model-control';
            addModelBtn.innerHTML = '+';
            addModelBtn.style.cssText = `
                position: absolute;
                width: 36px; height: 36px; background: rgba(255,255,255,0.9); border-radius: 50%;
                display: none; align-items: center; justify-content: center; font-size: 24px;
                cursor: pointer; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000; font-weight: bold; z-index: 101;
                transform: translate(-50%, 0);
            `;
            addModelBtn.title = 'Add another instance of this model';

            // Remove model button (- icon) - positioned right of add button
            const removeModelBtn = document.createElement('div');
            removeModelBtn.className = 'remove-model-control';
            removeModelBtn.innerHTML = '−';
            removeModelBtn.style.cssText = `
                position: absolute;
                width: 36px; height: 36px; background: rgba(255,255,255,0.9); border-radius: 50%;
                display: none; align-items: center; justify-content: center; font-size: 24px;
                cursor: pointer; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000; font-weight: bold; z-index: 101;
                transform: translate(-50%, 0);
            `;
            removeModelBtn.title = 'Remove current model';

            // Thumbnail button (shows actual thumbnail image) - positioned right of remove button
            const thumbnailBtn = document.createElement('div');
            thumbnailBtn.className = 'thumbnail-control';
            thumbnailBtn.style.cssText = `
                position: absolute;
                width: 36px; height: 36px; background: rgba(255,255,255,0.9); border-radius: 50%;
                display: none; align-items: center; justify-content: center;
                cursor: pointer; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #000; z-index: 101;
                transform: translate(-50%, 0);
                background-size: cover; background-position: center;
                border: 2px solid rgba(255,255,255,0.9);
            `;
            thumbnailBtn.title = 'View original 2D image';

            // Move hint in center
            const moveHint = document.createElement('div');
            moveHint.className = 'move-hint';
            moveHint.innerHTML = '✥ Drag object to move';
            moveHint.style.cssText = `
                position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
                padding: 8px 16px; background: rgba(0,0,0,0.6); border-radius: 20px;
                color: white; font-size: 12px; pointer-events: none;
            `;

            overlay.appendChild(rotateBtn);
            overlay.appendChild(scaleControl);
            overlay.appendChild(brightnessControl);
            overlay.appendChild(tiltControl);
            overlay.appendChild(tiltResetBtn);
            overlay.appendChild(addModelBtn);
            overlay.appendChild(removeModelBtn);
            overlay.appendChild(thumbnailBtn);
            overlay.appendChild(moveHint);
            container.style.position = 'relative';
            container.appendChild(overlay);

            // Rotate control events (Y axis - bottom) - mouse
            rotateBtn.addEventListener('mousedown', (e) => {
                e.preventDefault();
                isDraggingRotate = true;
                lastMouseX = e.clientX;
                rotateBtn.style.background = 'rgba(100,200,255,0.9)';
            });
            // Rotate control events - touch
            rotateBtn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                isDraggingRotate = true;
                lastMouseX = e.touches[0].clientX;
                rotateBtn.style.background = 'rgba(100,200,255,0.9)';
            }, { passive: false });

            // Scale control events - mouse
            scaleControl.addEventListener('mousedown', (e) => {
                e.preventDefault();
                isDraggingScale = true;
                lastMouseY = e.clientY;
                scaleControl.style.background = 'rgba(100,255,100,0.9)';
            });
            // Scale control events - touch
            scaleControl.addEventListener('touchstart', (e) => {
                e.preventDefault();
                isDraggingScale = true;
                lastMouseY = e.touches[0].clientY;
                scaleControl.style.background = 'rgba(100,255,100,0.9)';
            }, { passive: false });

            // Brightness control events - mouse
            brightnessControl.addEventListener('mousedown', (e) => {
                e.preventDefault();
                isDraggingBrightness = true;
                lastMouseX = e.clientX;
                brightnessControl.style.background = 'rgba(255,200,100,0.9)';
            });
            // Brightness control events - touch
            brightnessControl.addEventListener('touchstart', (e) => {
                e.preventDefault();
                isDraggingBrightness = true;
                lastMouseX = e.touches[0].clientX;
                brightnessControl.style.background = 'rgba(255,200,100,0.9)';
            }, { passive: false });

            // Tilt control events - mouse
            tiltControl.addEventListener('mousedown', (e) => {
                e.preventDefault();
                isDraggingTilt = true;
                lastMouseY = e.clientY;
                tiltControl.style.background = 'rgba(200,100,255,0.9)';
            });
            // Tilt control events - touch
            tiltControl.addEventListener('touchstart', (e) => {
                e.preventDefault();
                isDraggingTilt = true;
                lastMouseY = e.touches[0].clientY;
                tiltControl.style.background = 'rgba(200,100,255,0.9)';
            }, { passive: false });

            // Tilt reset button click event
            tiltResetBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (currentLoadedModel) {
                    modelTilt = DEFAULT_TILT;
                    currentLoadedModel.userData.tilt = DEFAULT_TILT;  // Store per-model
                    applyModelRotation(currentLoadedModel);
                    updateContactMarkerPositions();
                    tiltResetBtn.style.background = 'rgba(200,100,255,0.9)';
                    setTimeout(() => {
                        tiltResetBtn.style.background = 'rgba(255,255,255,0.9)';
                    }, 150);
                    saveModelState();  // Save after tilt reset
                }
            });

            // Add model button click event
            addModelBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                addModelBtn.style.background = 'rgba(200,200,200,0.9)';
                setTimeout(() => {
                    addModelBtn.style.background = 'rgba(255,255,255,0.9)';
                }, 150);
                addAnotherModelInstance();
            });

            // Remove model button click event
            removeModelBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                removeModelBtn.style.background = 'rgba(200,200,200,0.9)';
                setTimeout(() => {
                    removeModelBtn.style.background = 'rgba(255,255,255,0.9)';
                }, 150);
                removeCurrentModel();
            });

            // Thumbnail button click event - show original 2D image in modal
            thumbnailBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                thumbnailBtn.style.background = 'rgba(200,200,200,0.9)';
                setTimeout(() => {
                    thumbnailBtn.style.background = 'rgba(255,255,255,0.9)';
                }, 150);
                showThumbnailModal();
            });

            // Global mouse events
            document.addEventListener('mousemove', (e) => {
                if (isDraggingRotate && currentLoadedModel) {
                    const deltaX = e.clientX - lastMouseX;
                    rotateAroundFloor(currentLoadedModel, deltaX * 0.02);
                    updateControlPositions();
                    lastMouseX = e.clientX;
                }
                if (isDraggingScale && currentLoadedModel) {
                    const deltaY = e.clientY - lastMouseY;
                    const scaleFactor = 1 - deltaY * 0.005;
                    const newScale = currentLoadedModel.scale.x * scaleFactor;
                    if (newScale > 0.1 && newScale < 10) {
                        currentLoadedModel.scale.setScalar(newScale);
                    }
                    lastMouseY = e.clientY;
                }
                if (isDraggingBrightness && currentLoadedModel) {
                    const deltaX = e.clientX - lastMouseX;
                    modelBrightness = Math.max(0.2, Math.min(2.5, modelBrightness + deltaX * 0.01));
                    applyBrightnessToModel(modelBrightness);
                    lastMouseX = e.clientX;
                }
                if (isDraggingTilt && currentLoadedModel) {
                    const deltaY = e.clientY - lastMouseY;

                    // Update model tilt angle (drag down = tilt forward to see from above)
                    // Range: 0 (original level) to 0.5 (max tilt ~29 degrees)
                    modelTilt = Math.max(0, Math.min(0.5, modelTilt + deltaY * 0.005));
                    currentLoadedModel.userData.tilt = modelTilt;  // Store per-model

                    // Apply combined rotation (preserves Y rotation while adding tilt)
                    applyModelRotation(currentLoadedModel);

                    updateContactMarkerPositions();
                    updateControlPositions();
                    lastMouseY = e.clientY;
                }
            });

            document.addEventListener('mouseup', () => {
                let stateChanged = false;
                if (isDraggingRotate) {
                    isDraggingRotate = false;
                    rotateBtn.style.background = 'rgba(255,255,255,0.9)';
                    // Don't bake Y rotation - just let it accumulate
                    // Y rotation doesn't affect vertical alignment so no need to reset
                    stateChanged = true;
                }
                if (isDraggingScale) {
                    isDraggingScale = false;
                    scaleControl.style.background = 'rgba(255,255,255,0.9)';
                    // Update base scale and reference Z so moving doesn't reset the size
                    if (currentLoadedModel) {
                        modelBaseScale = currentLoadedModel.scale.x;
                        modelReferenceZ = currentLoadedModel.position.z;
                    }
                    stateChanged = true;
                }
                if (isDraggingBrightness) {
                    isDraggingBrightness = false;
                    brightnessControl.style.background = 'rgba(255,255,255,0.9)';
                    stateChanged = true;
                }
                if (isDraggingTilt) {
                    isDraggingTilt = false;
                    tiltControl.style.background = 'rgba(255,255,255,0.9)';
                    stateChanged = true;
                }
                if (stateChanged) saveModelState();
            });

            // Global touch events for mobile
            document.addEventListener('touchmove', (e) => {
                if (isDraggingRotate && currentLoadedModel) {
                    const deltaX = e.touches[0].clientX - lastMouseX;
                    rotateAroundFloor(currentLoadedModel, deltaX * 0.02);
                    updateControlPositions();
                    lastMouseX = e.touches[0].clientX;
                    e.preventDefault();
                }
                if (isDraggingScale && currentLoadedModel) {
                    const deltaY = e.touches[0].clientY - lastMouseY;
                    const scaleFactor = 1 - deltaY * 0.005;
                    const newScale = currentLoadedModel.scale.x * scaleFactor;
                    if (newScale > 0.1 && newScale < 10) {
                        currentLoadedModel.scale.setScalar(newScale);
                    }
                    lastMouseY = e.touches[0].clientY;
                    e.preventDefault();
                }
                if (isDraggingBrightness && currentLoadedModel) {
                    const deltaX = e.touches[0].clientX - lastMouseX;
                    modelBrightness = Math.max(0.2, Math.min(2.5, modelBrightness + deltaX * 0.01));
                    applyBrightnessToModel(modelBrightness);
                    lastMouseX = e.touches[0].clientX;
                    e.preventDefault();
                }
                if (isDraggingTilt && currentLoadedModel) {
                    const deltaY = e.touches[0].clientY - lastMouseY;

                    // Update model tilt angle (drag down = tilt forward to see from above)
                    // Range: 0 (original level) to 0.5 (max tilt ~29 degrees)
                    modelTilt = Math.max(0, Math.min(0.5, modelTilt + deltaY * 0.005));
                    currentLoadedModel.userData.tilt = modelTilt;  // Store per-model

                    // Apply combined rotation (preserves Y rotation while adding tilt)
                    applyModelRotation(currentLoadedModel);

                    updateContactMarkerPositions();
                    updateControlPositions();
                    lastMouseY = e.touches[0].clientY;
                    e.preventDefault();
                }
            }, { passive: false });

            document.addEventListener('touchend', () => {
                let stateChanged = false;
                if (isDraggingRotate) {
                    isDraggingRotate = false;
                    rotateBtn.style.background = 'rgba(255,255,255,0.9)';
                    stateChanged = true;
                }
                if (isDraggingScale) {
                    isDraggingScale = false;
                    scaleControl.style.background = 'rgba(255,255,255,0.9)';
                    // Update base scale and reference Z so moving doesn't reset the size
                    if (currentLoadedModel) {
                        modelBaseScale = currentLoadedModel.scale.x;
                        modelReferenceZ = currentLoadedModel.position.z;
                    }
                    stateChanged = true;
                }
                if (isDraggingBrightness) {
                    isDraggingBrightness = false;
                    brightnessControl.style.background = 'rgba(255,255,255,0.9)';
                    stateChanged = true;
                }
                if (isDraggingTilt) {
                    isDraggingTilt = false;
                    tiltControl.style.background = 'rgba(255,255,255,0.9)';
                    stateChanged = true;
                }
                if (stateChanged) saveModelState();
            });
        }

        function applyModelRotation(model) {
            // Apply combined rotation: leveling + Y rotation + X tilt
            // Order: first level, then Y rotate, then X tilt
            const savedX = model.position.x;
            const savedY = model.position.y;
            const savedZ = model.position.z;

            // Create Y rotation quaternion (horizontal rotation)
            const yRotQuat = new THREE.Quaternion().setFromAxisAngle(
                new THREE.Vector3(0, 1, 0), userYRotation
            );

            // Create X tilt quaternion (forward/backward tilt)
            const xTiltQuat = new THREE.Quaternion().setFromAxisAngle(
                new THREE.Vector3(1, 0, 0), modelTilt
            );

            // Combine: tilt * yRotation * leveling
            // This applies leveling first, then Y rotation, then tilt
            if (levelingQuaternion) {
                model.quaternion.copy(xTiltQuat).multiply(yRotQuat).multiply(levelingQuaternion);
            } else {
                model.quaternion.copy(xTiltQuat).multiply(yRotQuat);
            }
            model.updateMatrixWorld(true);

            // Restore exact position
            model.position.x = savedX;
            model.position.y = savedY;
            model.position.z = savedZ;
            model.updateMatrixWorld(true);
        }

        function rotateAroundFloor(model, angle) {
            // Update per-model Y rotation stored in userData
            if (model.userData.yRotation === undefined) {
                model.userData.yRotation = userYRotation;  // Initialize from global
            }
            model.userData.yRotation += angle;
            userYRotation = model.userData.yRotation;  // Sync global for current model
            applyModelRotation(model);
            updateContactMarkerPositions();
        }

        function levelModelToFloorWithoutAlign(model, contactPoints) {
            // Transform the model so all contact points lie on the horizontal plane (Y = 0)
            // This version does NOT call alignModelToFloorOrientation
            if (contactPoints.length < 3) return;

            // Convert contact points to world coordinates
            const worldPoints = contactPoints.map(p => model.localToWorld(p.clone()));

            // Calculate the plane normal from 3 points
            const p0 = worldPoints[0];
            const p1 = worldPoints[1];
            const p2 = worldPoints[2];

            const v1 = new THREE.Vector3().subVectors(p1, p0);
            const v2 = new THREE.Vector3().subVectors(p2, p0);
            const planeNormal = new THREE.Vector3().crossVectors(v1, v2).normalize();

            // Ensure normal points upward
            if (planeNormal.y < 0) planeNormal.negate();

            // Calculate rotation to make plane horizontal (normal = up vector)
            const upVector = new THREE.Vector3(0, 1, 0);
            const quaternion = new THREE.Quaternion().setFromUnitVectors(planeNormal, upVector);

            // Apply rotation to model
            model.quaternion.premultiply(quaternion);
            model.updateMatrixWorld(true);

            // Recalculate world positions after rotation
            const newWorldPoints = contactPoints.map(p => model.localToWorld(p.clone()));

            // Find the lowest Y after rotation
            const minY = Math.min(...newWorldPoints.map(p => p.y));

            // Move model so contact points are at world Y=0
            model.position.y -= minY;
            model.updateMatrixWorld(true);
        }

        function bakeRotation(model) {
            // Apply current rotation to geometry, preserving position
            // This keeps the visual orientation but resets rotation values

            // Save current position
            const savedPosition = model.position.clone();
            const savedScale = model.scale.clone();

            // Create rotation-only matrix
            const rotationMatrix = new THREE.Matrix4();
            rotationMatrix.makeRotationFromEuler(model.rotation);

            // Apply only rotation to geometry
            model.traverse((child) => {
                if (child.isMesh && child.geometry) {
                    child.geometry.applyMatrix4(rotationMatrix);
                }
            });

            // Reset only rotation, restore position and scale
            model.rotation.set(0, 0, 0);
            model.position.copy(savedPosition);
            model.scale.copy(savedScale);
            model.updateMatrix();
        }

        function startDefiningContactPoints(container, contactBtn, moveHint) {
            if (!currentLoadedModel) {
                alert('Load a 3D model first');
                return;
            }

            if (isDefiningContactPoints) {
                // Cancel contact point definition
                isDefiningContactPoints = false;
                contactBtn.innerHTML = '⊙ Legs';
                contactBtn.style.background = 'rgba(255,152,0,0.9)';
                moveHint.innerHTML = '✥ Drag object to move';
                moveHint.style.background = 'rgba(0,0,0,0.6)';
                return;
            }

            // Start contact point definition mode
            isDefiningContactPoints = true;
            objectContactPoints = [];
            clearContactMarkers();

            contactBtn.innerHTML = '✕ Cancel';
            contactBtn.style.background = 'rgba(244,67,54,0.9)';
            moveHint.innerHTML = 'Click 4 contact points on object (0/4)';
            moveHint.style.background = 'rgba(255,152,0,0.9)';

            // Add click handler to canvas for raycasting
            const canvas = container.querySelector('canvas');
            canvas.style.cursor = 'crosshair';

            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();

            const clickHandler = (e) => {
                if (!isDefiningContactPoints) return;

                e.preventDefault();
                e.stopPropagation();

                const rect = canvas.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                raycaster.setFromCamera(mouse, threeCamera);
                const intersects = raycaster.intersectObject(currentLoadedModel, true);

                if (intersects.length > 0) {
                    const point = intersects[0].point.clone();

                    // Store point in local coordinates relative to model
                    const localPoint = currentLoadedModel.worldToLocal(point.clone());
                    objectContactPoints.push(localPoint);

                    // Add visual marker at screen position
                    const screenX = e.clientX - rect.left;
                    const screenY = e.clientY - rect.top;
                    addContactMarker(container, screenX, screenY, objectContactPoints.length);

                    moveHint.innerHTML = `Click 4 contact points on object (${objectContactPoints.length}/4)`;
                    moveHint.style.background = 'rgba(255,152,0,0.9)';

                    if (objectContactPoints.length >= 4) {
                        // Done defining contact points
                        isDefiningContactPoints = false;
                        canvas.style.cursor = 'default';
                        canvas.removeEventListener('click', clickHandler);

                        contactBtn.innerHTML = '⊙ Legs ✓';
                        contactBtn.style.background = 'rgba(255,152,0,0.9)';
                        moveHint.innerHTML = '✥ Drag object to move';
                        moveHint.style.background = 'rgba(0,0,0,0.6)';

                        // Calculate average Y of contact points
                        const avgY = objectContactPoints.reduce((sum, p) => sum + p.y, 0) / 4;
                        console.log('Contact points defined:', objectContactPoints);
                        console.log('Contact points average Y:', avgY);
                    }
                } else {
                    // Missed the model - show warning
                    moveHint.innerHTML = '⚠ Click ON the 3D model, not background!';
                    moveHint.style.background = 'rgba(244,67,54,0.9)';
                    setTimeout(() => {
                        if (isDefiningContactPoints) {
                            moveHint.innerHTML = `Click 4 contact points on object (${objectContactPoints.length}/4)`;
                            moveHint.style.background = 'rgba(255,152,0,0.9)';
                        }
                    }, 1500);
                }
            };

            canvas.addEventListener('click', clickHandler);
        }

        function addContactMarker(container, x, y, index) {
            // Contact markers disabled - function kept for compatibility
            return;
        }

        function clearContactMarkers() {
            contactMarkers.forEach(m => m.remove());
            contactMarkers = [];
        }

        // Coordinate conversion functions
        function screenToWorld(screenX, screenY) {
            // Convert screen coordinates to world coordinates (X, Y at Z=0)
            if (!viewerContainer || !threeCamera) return null;
            const rect = viewerContainer.getBoundingClientRect();
            const ndcX = ((screenX - rect.left) / rect.width) * 2 - 1;
            const ndcY = -((screenY - rect.top) / rect.height) * 2 + 1;

            // For orthographic camera, convert NDC to world coords
            const worldX = (ndcX * (threeCamera.right - threeCamera.left) / 2);
            const worldY = (ndcY * (threeCamera.top - threeCamera.bottom) / 2);
            return { x: worldX, y: worldY };
        }

        function worldToScreen(worldX, worldY) {
            // Convert world coordinates to screen coordinates
            if (!viewerContainer || !threeCamera) return null;
            const rect = viewerContainer.getBoundingClientRect();
            const vec = new THREE.Vector3(worldX, worldY, 0);
            vec.project(threeCamera);
            return {
                x: (vec.x + 1) / 2 * rect.width,
                y: (-vec.y + 1) / 2 * rect.height
            };
        }

        function setDefaultPosition() {
            // Set default position to lower area of screen
            if (currentLoadedModel) {
                currentLoadedModel.position.y = -1.15;
                updateScaleForConstantSize();
                updateContactMarkerPositions();
                updateControlPositions();
            }
        }

        const DEFAULT_Y_POSITION = -1.15;  // Default bottom center position
        const MODEL_SPACING = 1.5;  // Horizontal spacing between models

        function addAnotherModelInstance() {
            if (!current3DModel?.model_url) {
                console.log('No model URL to duplicate');
                return;
            }

            const modelUrl = current3DModel.model_url;
            const loader = new THREE.GLTFLoader();

            loader.load(modelUrl, (gltf) => {
                const newModel = gltf.scene;

                // Copy scale from first model if exists
                if (currentLoadedModel) {
                    newModel.scale.copy(currentLoadedModel.scale);
                }

                // Determine placement position
                let newX = 0;
                const newY = DEFAULT_Y_POSITION;

                if (allLoadedModels.length === 0) {
                    // First model - place at center
                    newX = 0;
                } else {
                    // Check if default position (center) is occupied
                    const centerOccupied = allLoadedModels.some(m =>
                        Math.abs(m.position.x) < 0.5 && Math.abs(m.position.y - DEFAULT_Y_POSITION) < 0.5
                    );

                    if (!centerOccupied) {
                        // Place at default center position
                        newX = 0;
                    } else {
                        // Find rightmost model and place new one beside it
                        let maxX = -Infinity;
                        allLoadedModels.forEach(m => {
                            if (m.position.x > maxX) maxX = m.position.x;
                        });
                        newX = maxX + MODEL_SPACING;
                    }
                }

                newModel.position.set(newX, newY, 0);

                // Initialize per-model data in userData (start with defaults, not current model's rotation)
                newModel.userData.yRotation = 0;
                newModel.userData.tilt = DEFAULT_TILT;
                // Assign new instance_id as max existing + 1
                const maxInstanceId = allLoadedModels.reduce((max, m) =>
                    Math.max(max, m.userData.instanceId || 0), -1);
                newModel.userData.instanceId = maxInstanceId + 1;

                // Add to scene and tracking array
                threeScene.add(newModel);
                allLoadedModels.push(newModel);

                // Select the new model and set globals to its values
                currentLoadedModel = newModel;
                userYRotation = newModel.userData.yRotation;
                modelTilt = newModel.userData.tilt;

                // Apply rotation (tilt) using the same method as original model
                applyModelRotation(newModel);

                // Apply brightness using the same method as original model
                applyBrightnessToModel(modelBrightness);

                showControlButtons = true;
                updateControlVisibility();
                updateControlPositions();

                // Save the new model state
                saveAllModelStates();

                console.log('Added new model instance at x=' + newX);
            }, undefined, (error) => {
                console.error('Error loading model for duplication:', error);
            });
        }

        function removeCurrentModel() {
            if (!currentLoadedModel) return;

            // Find the index of the current model in allLoadedModels
            const modelIndex = allLoadedModels.indexOf(currentLoadedModel);
            if (modelIndex === -1) return;

            // Remove from scene
            threeScene.remove(currentLoadedModel);

            // Remove from array
            allLoadedModels.splice(modelIndex, 1);

            // Clear contact markers
            clearContactMarkers();
            objectContactPoints = [];

            // Hide buttons after deletion (don't auto-select another model)
            currentLoadedModel = null;
            showControlButtons = false;
            updateControlVisibility();

            // Save the updated state
            saveAllModelStates();

            console.log('Removed model. Remaining models:', allLoadedModels.length);
        }

        function updateThumbnailButtonIcon() {
            // Update the thumbnail button to show the current model's thumbnail
            if (!controlOverlay) return;
            const thumbnailCtrl = controlOverlay.querySelector('.thumbnail-control');
            if (!thumbnailCtrl) return;

            const thumbnailUrl = current3DModel?.input_thumbnail;
            if (thumbnailUrl) {
                thumbnailCtrl.style.backgroundImage = `url(${thumbnailUrl})`;
            } else {
                thumbnailCtrl.style.backgroundImage = 'none';
            }
        }

        function showThumbnailModal() {
            // Get the original image (or fall back to thumbnail for older entries)
            const originalUrl = current3DModel?.input_original || current3DModel?.input_thumbnail;
            if (!originalUrl) {
                console.warn('No input image available for this model');
                return;
            }

            // Create modal overlay
            const modalOverlay = document.createElement('div');
            modalOverlay.id = 'thumbnailModal';
            modalOverlay.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.8); display: flex; align-items: center;
                justify-content: center; z-index: 10000; cursor: pointer;
            `;

            // Create modal content container
            const modalContent = document.createElement('div');
            modalContent.style.cssText = `
                position: relative; width: 100%; max-height: 95vh;
                background: white; padding: 15px;
                box-shadow: 0 10px 50px rgba(0,0,0,0.5);
            `;

            // Create close button
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '&times;';
            closeBtn.style.cssText = `
                position: absolute; top: 5px; right: 15px;
                background: rgba(255,255,255,0.9); border: none; font-size: 36px;
                cursor: pointer; color: #333; line-height: 1;
                width: 44px; height: 44px; border-radius: 50%;
                z-index: 10001;
            `;
            closeBtn.onclick = (e) => {
                e.stopPropagation();
                modalOverlay.remove();
            };

            // Create image
            const img = document.createElement('img');
            img.src = originalUrl;
            img.alt = 'Original 2D Image';
            img.style.cssText = `
                width: 100%; max-height: 90vh; display: block;
                object-fit: contain;
            `;

            // Create label
            const label = document.createElement('div');
            label.textContent = 'Original 2D Input Image';
            label.style.cssText = `
                text-align: center; margin-top: 8px; font-size: 14px;
                color: #666;
            `;

            modalContent.appendChild(closeBtn);
            modalContent.appendChild(img);
            modalContent.appendChild(label);
            modalOverlay.appendChild(modalContent);

            // Close on overlay click (but not on content click)
            modalOverlay.onclick = (e) => {
                if (e.target === modalOverlay) {
                    modalOverlay.remove();
                }
            };

            // Close on Escape key
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    modalOverlay.remove();
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);

            document.body.appendChild(modalOverlay);
        }

        function updateControlVisibility() {
            if (!controlOverlay) return;
            const display = showControlButtons ? 'flex' : 'none';
            const rotateCtrl = controlOverlay.querySelector('.rotate-control');
            const scaleCtrl = controlOverlay.querySelector('.scale-control');
            const brightnessCtrl = controlOverlay.querySelector('.brightness-control');
            const tiltCtrl = controlOverlay.querySelector('.tilt-control');
            const tiltResetCtrl = controlOverlay.querySelector('.tilt-reset-control');
            const addModelCtrl = controlOverlay.querySelector('.add-model-control');
            const removeModelCtrl = controlOverlay.querySelector('.remove-model-control');
            const thumbnailCtrl = controlOverlay.querySelector('.thumbnail-control');
            if (rotateCtrl) rotateCtrl.style.display = display;
            if (scaleCtrl) scaleCtrl.style.display = display;
            if (brightnessCtrl) brightnessCtrl.style.display = display;
            if (tiltCtrl) tiltCtrl.style.display = display;
            if (tiltResetCtrl) tiltResetCtrl.style.display = display;
            if (addModelCtrl) addModelCtrl.style.display = display;
            if (removeModelCtrl) removeModelCtrl.style.display = display;
            if (thumbnailCtrl) thumbnailCtrl.style.display = display;
            // Update thumbnail button icon when showing controls
            if (showControlButtons) {
                updateThumbnailButtonIcon();
            }
        }

        function getLowestContactPointY() {
            // Get the lowest Y value among all contact points in world coords
            if (objectContactPoints.length === 0 || !currentLoadedModel) return null;

            let lowestY = Infinity;
            objectContactPoints.forEach(localPoint => {
                const worldPoint = currentLoadedModel.localToWorld(localPoint.clone());
                if (worldPoint.y < lowestY) {
                    lowestY = worldPoint.y;
                }
            });
            return lowestY;
        }

        function autoDetectContactPoints(model) {
            // Auto-detect the lowest points on the model (e.g., chair legs)
            // Uses spatial clustering to find 4 distinct leg positions
            objectContactPoints = [];
            clearContactMarkers();

            const allVertices = [];

            model.traverse((child) => {
                if (child.isMesh && child.geometry) {
                    const geometry = child.geometry;
                    const positionAttribute = geometry.getAttribute('position');

                    if (positionAttribute) {
                        for (let i = 0; i < positionAttribute.count; i++) {
                            const vertex = new THREE.Vector3();
                            vertex.fromBufferAttribute(positionAttribute, i);
                            // Transform to world coordinates
                            child.localToWorld(vertex);
                            // Then to model local coordinates
                            model.worldToLocal(vertex);
                            allVertices.push(vertex);
                        }
                    }
                }
            });

            if (allVertices.length === 0) {
                console.log('No vertices found for contact point detection');
                return;
            }

            // Find the minimum Y (lowest point) - use loop to avoid stack overflow with large arrays
            let minY = Infinity;
            for (const v of allVertices) {
                if (v.y < minY) minY = v.y;
            }

            // Find vertices within a small threshold of the minimum Y
            const threshold = 0.08;  // 8% of model size tolerance
            const box = new THREE.Box3().setFromObject(model);
            const modelHeight = box.max.y - box.min.y;
            const modelWidth = Math.max(box.max.x - box.min.x, box.max.z - box.min.z);
            const yThreshold = minY + modelHeight * threshold;

            const bottomVertices = allVertices.filter(v => v.y <= yThreshold);

            if (bottomVertices.length < 4) {
                // If not enough bottom vertices, just use the 4 lowest
                allVertices.sort((a, b) => a.y - b.y);
                objectContactPoints = allVertices.slice(0, 4).map(v => v.clone());
            } else {
                // Use farthest-point sampling to find 4 well-spread contact points
                // This guarantees we get 4 distinct, maximally-spread positions

                // Start with the lowest vertex
                bottomVertices.sort((a, b) => a.y - b.y);
                objectContactPoints.push(bottomVertices[0].clone());

                // Helper function to get min distance from a point to all selected points
                const minDistToSelected = (v) => {
                    let minDist = Infinity;
                    for (const selected of objectContactPoints) {
                        const dist = Math.sqrt(
                            Math.pow(v.x - selected.x, 2) +
                            Math.pow(v.z - selected.z, 2)
                        );  // Only X/Z distance (horizontal)
                        if (dist < minDist) {
                            minDist = dist;
                        }
                    }
                    return minDist;
                };

                // Find 3 more points, each time selecting the point farthest from all selected points
                while (objectContactPoints.length < 4) {
                    let farthestPoint = null;
                    let farthestMinDist = 0;

                    for (const v of bottomVertices) {
                        // Skip if already selected (or very close to selected)
                        const distToSelected = minDistToSelected(v);
                        if (distToSelected < 0.01) continue;  // Already selected

                        if (distToSelected > farthestMinDist) {
                            farthestMinDist = distToSelected;
                            farthestPoint = v;
                        }
                    }

                    if (farthestPoint) {
                        objectContactPoints.push(farthestPoint.clone());
                    } else {
                        break;  // No more distinct points found
                    }
                }

                // Refinement: snap each point to the lowest vertex within a small radius
                // This ensures points are at actual leg tips, not just spread-out bottom vertices
                const snapRadius = modelWidth * 0.12;  // Search within 12% of model width
                for (let i = 0; i < objectContactPoints.length; i++) {
                    const point = objectContactPoints[i];
                    let lowestInRadius = point;
                    let lowestY = point.y;

                    for (const v of allVertices) {
                        // Check if within snap radius (horizontal distance only)
                        const horizDist = Math.sqrt(
                            Math.pow(v.x - point.x, 2) +
                            Math.pow(v.z - point.z, 2)
                        );

                        if (horizDist < snapRadius && v.y < lowestY) {
                            lowestY = v.y;
                            lowestInRadius = v;
                        }
                    }

                    objectContactPoints[i] = lowestInRadius.clone();
                }

            }

            console.log('Auto-detected contact points:', objectContactPoints.length, objectContactPoints);

            // Level the model so all 4 contact points are at the same Y (world Y=0)
            if (objectContactPoints.length >= 3) {
                levelModelToFloor(model, objectContactPoints);
                // Note: No perspective tilt with orthographic camera
            }

            // Show visual markers for the detected contact points
            showContactPointMarkers();

            return objectContactPoints.length;
        }

        function levelModelToFloor(model, contactPoints) {
            // Rotate model so contact plane is horizontal, then position at world Y=0
            if (contactPoints.length < 3) return;

            // Convert contact points to world coordinates
            const worldPoints = contactPoints.map(p => model.localToWorld(p.clone()));

            // Calculate the plane normal from 3 points (best-fit plane)
            const p0 = worldPoints[0];
            const p1 = worldPoints[1];
            const p2 = worldPoints[2];

            const v1 = new THREE.Vector3().subVectors(p1, p0);
            const v2 = new THREE.Vector3().subVectors(p2, p0);
            const planeNormal = new THREE.Vector3().crossVectors(v1, v2).normalize();

            // Ensure normal points upward
            if (planeNormal.y < 0) planeNormal.negate();

            // Calculate rotation to make plane horizontal (normal = up vector)
            const upVector = new THREE.Vector3(0, 1, 0);
            const quaternion = new THREE.Quaternion().setFromUnitVectors(planeNormal, upVector);

            // Store leveling quaternion for combining with Y rotation later
            levelingQuaternion = quaternion.clone();

            // Apply rotation to model
            model.quaternion.copy(quaternion);
            model.updateMatrixWorld(true);

            // Recalculate world positions after rotation
            const newWorldPoints = contactPoints.map(p => model.localToWorld(p.clone()));

            // Find the average Y after rotation (should all be nearly the same now)
            const avgY = newWorldPoints.reduce((sum, p) => sum + p.y, 0) / newWorldPoints.length;

            // Move model so contact points are at world Y=0
            model.position.y -= avgY;
            model.updateMatrixWorld(true);

            console.log('Model leveled to world Y=0. Avg contact Y:', avgY);
        }

        function showContactPointMarkers() {
            // Clear existing markers
            clearContactMarkers();

            if (!currentLoadedModel || !viewerContainer || objectContactPoints.length === 0) return;

            const rect = viewerContainer.getBoundingClientRect();

            // Project each contact point to screen coordinates
            objectContactPoints.forEach((localPoint, index) => {
                // Convert local point to world coordinates
                const worldPoint = currentLoadedModel.localToWorld(localPoint.clone());

                // Project to screen coordinates
                const screenPoint = worldPoint.clone().project(threeCamera);
                const screenX = (screenPoint.x + 1) / 2 * rect.width;
                const screenY = (-screenPoint.y + 1) / 2 * rect.height;

                // Add marker
                addContactMarker(viewerContainer, screenX, screenY, index + 1);
            });
        }

        function updateContactMarkerPositions() {
            // Update contact marker positions when model moves
            if (!currentLoadedModel || !viewerContainer || objectContactPoints.length === 0) return;
            if (contactMarkers.length === 0) return;

            const rect = viewerContainer.getBoundingClientRect();

            objectContactPoints.forEach((localPoint, index) => {
                if (index >= contactMarkers.length) return;

                // Convert local point to world coordinates
                const worldPoint = currentLoadedModel.localToWorld(localPoint.clone());

                // Project to screen coordinates
                const screenPoint = worldPoint.clone().project(threeCamera);
                const screenX = (screenPoint.x + 1) / 2 * rect.width;
                const screenY = (-screenPoint.y + 1) / 2 * rect.height;

                // Update marker position
                const marker = contactMarkers[index];
                marker.style.left = screenX + 'px';
                marker.style.top = screenY + 'px';
            });
        }

        function applyBrightnessToModel(brightness) {
            if (!currentLoadedModel) return;

            currentLoadedModel.traverse((child) => {
                if (child.isMesh && child.material) {
                    const materials = Array.isArray(child.material) ? child.material : [child.material];
                    materials.forEach(mat => {
                        if (mat.color) {
                            // Store original color if not stored
                            if (!mat.userData.originalColor) {
                                mat.userData.originalColor = mat.color.clone();
                            }
                            // Apply brightness
                            mat.color.copy(mat.userData.originalColor).multiplyScalar(brightness);
                        }
                    });
                }
            });
        }

        let dragStartHitPoint = null;
        let dragStartModelPosition = null;
        let dragPlaneY = 0;
        let lastCursorHitPoint = null;  // Track cursor position for incremental movement

        // Update model scale to maintain constant apparent size when Z changes
        function updateScaleForConstantSize() {
            if (!currentLoadedModel || modelBaseScale === 0) return;

            // Calculate distance from camera at reference and current Z
            const referenceDistance = cameraZ - modelReferenceZ;
            const currentDistance = cameraZ - currentLoadedModel.position.z;

            // Scale proportionally with distance to maintain constant apparent size
            // When further away (larger distance), scale up to compensate for perspective shrinking
            if (currentDistance > 0 && referenceDistance > 0) {
                const newScale = modelBaseScale * (currentDistance / referenceDistance);
                currentLoadedModel.scale.setScalar(newScale);
            }
        }

        // Get target position for movement (no constraints - free movement)
        function getValidPosition(startX, startZ, deltaX, deltaZ) {
            return { x: startX + deltaX, z: startZ + deltaZ };
        }

        function getPlaneIntersection(clientX, clientY, canvas, planeY) {
            const rect = canvas.getBoundingClientRect();

            // For orthographic camera looking along -Z axis:
            // Screen X movement -> World X movement (left/right)
            // Screen Y movement -> World Z movement (forward/backward for depth)
            const ndcX = ((clientX - rect.left) / rect.width) * 2 - 1;
            const ndcY = -((clientY - rect.top) / rect.height) * 2 + 1;

            // Unproject to get world X position
            const worldPos = new THREE.Vector3(ndcX, ndcY, 0);
            worldPos.unproject(threeCamera);

            // For orthographic view from front:
            // - worldPos.x is the correct X position
            // - worldPos.y (screen Y) maps to world Z (depth) - invert for intuitive movement
            // Scale factor based on camera frustum size
            const frustumSize = 5;
            const worldZ = -ndcY * (frustumSize / 2);

            return new THREE.Vector3(worldPos.x, planeY, worldZ);
        }

        function setupModelDragEvents(container) {
            const canvas = container.querySelector('canvas');
            if (!canvas) return;

            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let clickStartPos = null;  // Track click start position to detect tap vs drag
            let modelWasClicked = false;  // Track if mousedown was on model

            // Function to toggle control buttons visibility (and leg points)
            function toggleControlButtons() {
                showControlButtons = !showControlButtons;
                const rotateCtrl = controlOverlay?.querySelector('.rotate-control');
                const scaleCtrl = controlOverlay?.querySelector('.scale-control');
                const brightnessCtrl = controlOverlay?.querySelector('.brightness-control');
                const tiltCtrl = controlOverlay?.querySelector('.tilt-control');
                const tiltResetCtrl = controlOverlay?.querySelector('.tilt-reset-control');
                const addModelCtrl = controlOverlay?.querySelector('.add-model-control');
                const removeModelCtrl = controlOverlay?.querySelector('.remove-model-control');
                const thumbnailCtrl = controlOverlay?.querySelector('.thumbnail-control');
                // Completely hide all buttons when toggled off
                const display = showControlButtons ? 'flex' : 'none';
                if (rotateCtrl) rotateCtrl.style.display = display;
                if (scaleCtrl) scaleCtrl.style.display = display;
                if (brightnessCtrl) brightnessCtrl.style.display = display;
                if (tiltCtrl) tiltCtrl.style.display = display;
                if (tiltResetCtrl) tiltResetCtrl.style.display = display;
                if (addModelCtrl) addModelCtrl.style.display = display;
                if (removeModelCtrl) removeModelCtrl.style.display = display;
                if (thumbnailCtrl) thumbnailCtrl.style.display = display;
                // Update thumbnail button icon when showing controls
                if (showControlButtons) {
                    updateThumbnailButtonIcon();
                }
                // Also toggle leg points visibility with controls
                contactMarkers.forEach(m => m.style.display = showControlButtons ? 'flex' : 'none');
            }

            canvas.addEventListener('mousedown', (e) => {
                if (isDraggingRotate || isDraggingScale || isDraggingBrightness || isDraggingTilt) return;

                clickStartPos = { x: e.clientX, y: e.clientY };
                modelWasClicked = false;

                const rect = canvas.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                raycaster.setFromCamera(mouse, threeCamera);

                // Check all models for intersection and select the clicked one
                let clickedModel = null;
                let closestIntersect = null;

                for (const model of allLoadedModels) {
                    const intersects = raycaster.intersectObject(model, true);
                    if (intersects.length > 0) {
                        if (!closestIntersect || intersects[0].distance < closestIntersect.distance) {
                            closestIntersect = intersects[0];
                            clickedModel = model;
                        }
                    }
                }

                if (clickedModel) {
                    // Switch to the clicked model
                    currentLoadedModel = clickedModel;
                    // Load per-model rotation from userData
                    userYRotation = clickedModel.userData.yRotation !== undefined ? clickedModel.userData.yRotation : 0;
                    modelTilt = clickedModel.userData.tilt !== undefined ? clickedModel.userData.tilt : DEFAULT_TILT;

                    isDraggingModel = true;
                    modelWasClicked = true;
                    canvas.style.cursor = 'move';

                    // Store the world position where user clicked (for click-point tracking)
                    const clickWorldPos = screenToWorld(e.clientX, e.clientY);
                    dragStartHitPoint = clickWorldPos;  // World position of click
                    dragStartModelPosition = currentLoadedModel.position.clone();
                }
            });

            canvas.addEventListener('mousemove', (e) => {
                if (isDraggingModel && currentLoadedModel && dragStartHitPoint && dragStartModelPosition) {
                    // Get current cursor world position
                    const currentWorldPos = screenToWorld(e.clientX, e.clientY);
                    if (!currentWorldPos) return;

                    // Calculate how much the cursor moved in world space
                    const worldDeltaX = currentWorldPos.x - dragStartHitPoint.x;
                    const worldDeltaY = currentWorldPos.y - dragStartHitPoint.y;

                    // Move the model so the clicked point follows the cursor
                    currentLoadedModel.position.x = dragStartModelPosition.x + worldDeltaX;
                    currentLoadedModel.position.y = dragStartModelPosition.y + worldDeltaY;

                    updateScaleForConstantSize();
                    updateContactMarkerPositions();
                }
            });

            canvas.addEventListener('mouseup', (e) => {
                // Check if this was a click (not a drag)
                if (clickStartPos) {
                    const dx = e.clientX - clickStartPos.x;
                    const dy = e.clientY - clickStartPos.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    // If movement is less than 5 pixels, treat as click
                    if (distance < 5) {
                        if (modelWasClicked) {
                            // Clicked on a model - show buttons (or keep showing if already visible)
                            if (!showControlButtons) {
                                toggleControlButtons();
                            }
                            // Update control positions for the newly selected model
                            updateControlPositions();
                        } else if (showControlButtons) {
                            // Clicked on background while buttons showing - hide them
                            toggleControlButtons();
                        }
                    }
                }
                // Save state if model was dragged
                if (isDraggingModel) {
                    saveModelState();
                }
                isDraggingModel = false;
                dragStartHitPoint = null;
                dragStartModelPosition = null;
                lastCursorHitPoint = null;
                clickStartPos = null;
                modelWasClicked = false;
                canvas.style.cursor = 'default';
            });

            canvas.addEventListener('mouseleave', () => {
                isDraggingModel = false;
                dragStartHitPoint = null;
                dragStartModelPosition = null;
                lastCursorHitPoint = null;
                canvas.style.cursor = 'default';
            });

            // Touch events for mobile
            let touchStartPos = null;  // Track touch start position
            let touchModelWasClicked = false;  // Track if touch was on model

            canvas.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    const touch = e.touches[0];
                    touchStartPos = { x: touch.clientX, y: touch.clientY };
                    touchModelWasClicked = false;

                    const rect = canvas.getBoundingClientRect();
                    mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;

                    raycaster.setFromCamera(mouse, threeCamera);

                    // Check all models for intersection and select the touched one
                    let touchedModel = null;
                    let closestIntersect = null;

                    for (const model of allLoadedModels) {
                        const intersects = raycaster.intersectObject(model, true);
                        if (intersects.length > 0) {
                            if (!closestIntersect || intersects[0].distance < closestIntersect.distance) {
                                closestIntersect = intersects[0];
                                touchedModel = model;
                            }
                        }
                    }

                    if (touchedModel) {
                        // Switch to the touched model
                        currentLoadedModel = touchedModel;
                        // Load per-model rotation from userData
                        userYRotation = touchedModel.userData.yRotation !== undefined ? touchedModel.userData.yRotation : 0;
                        modelTilt = touchedModel.userData.tilt !== undefined ? touchedModel.userData.tilt : DEFAULT_TILT;

                        isDraggingModel = true;
                        touchModelWasClicked = true;
                        // Store the world position where user touched (for touch-point tracking)
                        const touchWorldPos = screenToWorld(touch.clientX, touch.clientY);
                        dragStartHitPoint = touchWorldPos;  // World position of touch
                        dragStartModelPosition = currentLoadedModel.position.clone();
                        e.preventDefault();
                    }
                }
            }, { passive: false });

            canvas.addEventListener('touchmove', (e) => {
                if (isDraggingModel && currentLoadedModel && dragStartHitPoint && dragStartModelPosition && e.touches.length === 1) {
                    const touch = e.touches[0];

                    // Get current touch world position
                    const currentWorldPos = screenToWorld(touch.clientX, touch.clientY);
                    if (!currentWorldPos) return;

                    // Calculate how much the touch moved in world space
                    const worldDeltaX = currentWorldPos.x - dragStartHitPoint.x;
                    const worldDeltaY = currentWorldPos.y - dragStartHitPoint.y;

                    // Move the model so the touched point follows the finger
                    currentLoadedModel.position.x = dragStartModelPosition.x + worldDeltaX;
                    currentLoadedModel.position.y = dragStartModelPosition.y + worldDeltaY;

                    updateScaleForConstantSize();
                    updateContactMarkerPositions();

                    e.preventDefault();
                }
            }, { passive: false });

            canvas.addEventListener('touchend', (e) => {
                // Check if this was a tap (not a drag)
                if (touchStartPos && e.changedTouches.length > 0) {
                    const touch = e.changedTouches[0];
                    const dx = touch.clientX - touchStartPos.x;
                    const dy = touch.clientY - touchStartPos.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    // If movement is less than 10 pixels, treat as tap
                    if (distance < 10) {
                        if (touchModelWasClicked) {
                            // Tapped on a model - show buttons (or keep showing if already visible)
                            if (!showControlButtons) {
                                toggleControlButtons();
                            }
                            // Update control positions for the newly selected model
                            updateControlPositions();
                        } else if (showControlButtons) {
                            // Tapped on background while buttons showing - hide them
                            toggleControlButtons();
                        }
                    }
                }
                // Save state if model was dragged
                if (isDraggingModel) {
                    saveModelState();
                }
                isDraggingModel = false;
                dragStartHitPoint = null;
                dragStartModelPosition = null;
                lastCursorHitPoint = null;
                touchStartPos = null;
                touchModelWasClicked = false;
            });

        }

        function loadTextureAsPlane(textureUrl) {
            const loader = new THREE.TextureLoader();
            loader.load(textureUrl, (texture) => {
                // Remove existing model
                if (currentLoadedModel) {
                    threeScene.remove(currentLoadedModel);
                }

                // Calculate aspect ratio from texture
                const aspect = texture.image.width / texture.image.height;

                // Create plane geometry with correct aspect ratio
                const geometry = new THREE.PlaneGeometry(aspect * 1.5, 1.5);

                // Create material with texture and transparency
                const material = new THREE.MeshBasicMaterial({
                    map: texture,
                    transparent: true,
                    side: THREE.DoubleSide
                });

                const plane = new THREE.Mesh(geometry, material);
                plane.position.set(0, 0, 0);

                // Store reference for drag controls
                currentLoadedModel = plane;
                threeScene.add(plane);

            }, undefined, (error) => {
                console.error('Error loading texture:', error);
            });
        }

        function loadGLTFModel(url) {
            const loader = new THREE.GLTFLoader();
            loader.load(url, (gltf) => {
                // Remove all existing models
                allLoadedModels.forEach(m => threeScene.remove(m));
                allLoadedModels = [];
                if (currentLoadedModel) {
                    threeScene.remove(currentLoadedModel);
                }
                threeScene.children.forEach(child => {
                    if (child.type === 'Group' || child.type === 'Mesh') {
                        threeScene.remove(child);
                    }
                });

                const model = gltf.scene;

                // Model orientation - Y-up (standard GLB/Three.js)
                model.rotation.x = 0;
                model.rotation.y = 0;
                model.rotation.z = 0;

                // Center and scale model
                const box = new THREE.Box3().setFromObject(model);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 1.5 / maxDim;
                model.scale.setScalar(scale);
                model.position.set(0, 0, 0);

                // Store initial reference for constant size during movement
                modelReferenceZ = 0;
                modelBaseScale = scale;

                // Reset brightness, rotation and tilt for new model
                modelBrightness = 2.5; // Max brightness by default
                userYRotation = 0;
                modelTilt = DEFAULT_TILT;  // Reset to default tilt
                cameraTilt = 0;
                threeCamera.position.y = 0;
                threeCamera.lookAt(0, 0, 0);

                // Store reference for drag controls
                currentLoadedModel = model;
                model.visible = false;  // Hide until saved state is loaded
                threeScene.add(model);
                allLoadedModels.push(model);  // Track in models array

                // Initialize per-model data in userData (will be overwritten if saved state exists)
                model.userData.yRotation = 0;
                model.userData.tilt = DEFAULT_TILT;
                model.userData.instanceId = 0;

                // Apply max brightness by default
                applyBrightnessToModel(modelBrightness);

                // Auto-detect contact points and set up camera after model is loaded
                setTimeout(async () => {
                    // Auto-detect contact points (chair legs)
                    const numPoints = autoDetectContactPoints(model);
                    if (numPoints >= 4) {
                        console.log('Auto-detected ' + numPoints + ' contact points');
                    }

                    // Try to load all saved model instances
                    const modelUrl = current3DModel?.url || current3DModel?.model_url;
                    if (currentBackgroundImage) {
                        const allSavedModels = await loadAllSavedModels(currentBackgroundImage);
                        // Filter to only include models matching the current model_url
                        const savedModels = allSavedModels ? allSavedModels.filter(m => m.model_url === modelUrl) : [];
                        if (savedModels && savedModels.length > 0) {
                            console.log('Restoring ' + savedModels.length + ' saved instances of ' + modelUrl);

                            // Apply first saved state to the initial model
                            const firstState = savedModels[0];
                            model.position.set(
                                firstState.position_x || 0,
                                firstState.position_y || 0,
                                firstState.position_z || 0
                            );
                            if (firstState.scale) {
                                model.scale.setScalar(firstState.scale);
                                modelBaseScale = firstState.scale;
                            }
                            userYRotation = firstState.rotation_y || 0;
                            modelTilt = firstState.tilt !== undefined ? firstState.tilt : DEFAULT_TILT;
                            // Store per-model data in userData
                            model.userData.yRotation = userYRotation;
                            model.userData.tilt = modelTilt;
                            model.userData.instanceId = firstState.instance_id || 0;
                            modelBrightness = firstState.brightness !== undefined ? firstState.brightness : 2.5;
                            applyModelRotation(model);
                            applyBrightnessToModel(modelBrightness);

                            // Load additional model instances if any
                            if (savedModels.length > 1 && modelUrl) {
                                const loader = new THREE.GLTFLoader();
                                for (let i = 1; i < savedModels.length; i++) {
                                    const savedState = savedModels[i];
                                    // Load another copy of the model
                                    loader.load(modelUrl, (gltf) => {
                                        const additionalModel = gltf.scene;

                                        // Apply saved state
                                        additionalModel.position.set(
                                            savedState.position_x || 0,
                                            savedState.position_y || 0,
                                            savedState.position_z || 0
                                        );
                                        if (savedState.scale) {
                                            additionalModel.scale.setScalar(savedState.scale);
                                        }

                                        // Store per-model data in userData
                                        const savedYRot = savedState.rotation_y || 0;
                                        const savedTilt = savedState.tilt !== undefined ? savedState.tilt : DEFAULT_TILT;
                                        const savedInstanceId = savedState.instance_id || 0;
                                        additionalModel.userData.yRotation = savedYRot;
                                        additionalModel.userData.tilt = savedTilt;
                                        additionalModel.userData.instanceId = savedInstanceId;

                                        // Add to scene
                                        threeScene.add(additionalModel);

                                        // Insert in correct position based on instance_id to maintain order
                                        let insertIndex = allLoadedModels.length;
                                        for (let j = 0; j < allLoadedModels.length; j++) {
                                            const existingId = allLoadedModels[j].userData.instanceId || 0;
                                            if (savedInstanceId < existingId) {
                                                insertIndex = j;
                                                break;
                                            }
                                        }
                                        allLoadedModels.splice(insertIndex, 0, additionalModel);

                                        // Apply this model's saved rotation
                                        // Temporarily set globals for applyModelRotation
                                        const prevModel = currentLoadedModel;
                                        const prevYRot = userYRotation;
                                        const prevTilt = modelTilt;
                                        currentLoadedModel = additionalModel;
                                        userYRotation = savedYRot;
                                        modelTilt = savedTilt;
                                        applyModelRotation(additionalModel);
                                        applyBrightnessToModel(modelBrightness);
                                        // Restore globals
                                        currentLoadedModel = prevModel;
                                        userYRotation = prevYRot;
                                        modelTilt = prevTilt;

                                        console.log('Loaded additional model instance ' + i + ' with rotation:', savedYRot, savedTilt);
                                    });
                                }
                            }
                        } else {
                            // No saved state, apply default tilt
                            applyModelRotation(model);
                            // Set default position
                            setDefaultPosition();
                        }
                    } else {
                        // No background image, apply default tilt
                        applyModelRotation(model);
                        // Set default position
                        setDefaultPosition();
                    }

                    // Set camera at Y=0 looking straight ahead
                    threeCamera.position.y = 0;
                    threeCamera.lookAt(0, 0, 0);
                    threeCamera.updateProjectionMatrix();

                    // Show model now that position is set
                    model.visible = true;

                    updateContactMarkerPositions();
                    updateControlPositions();
                }, 100);
            }, undefined, (error) => {
                console.error('Error loading 3D model:', error);
                document.getElementById('threejsViewer').innerHTML =
                    '<p style="color: #f5576c; padding: 2rem; text-align: center;">Error loading 3D model</p>';
            });
        }

        function base64ToBlob(base64, mimeType) {
            const byteCharacters = atob(base64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            return new Blob([byteArray], { type: mimeType });
        }

        async function load3DHistory() {
            try {
                const response = await fetch('/api/model3d-history');
                const data = await response.json();

                if (data.history && data.history.length > 0) {
                    const historyGrid = document.getElementById('model3dHistoryGrid');
                    historyGrid.innerHTML = '';

                    // Display in reverse order (newest first)
                    const reversedHistory = [...data.history].reverse();
                    reversedHistory.forEach((item, index) => {
                        const historyItem = document.createElement('div');
                        historyItem.className = 'history-item';
                        historyItem.style.cursor = 'pointer';
                        historyItem.style.position = 'relative';

                        const timestamp = new Date(item.timestamp).toLocaleString();
                        const originalIndex = data.history.length - 1 - index;  // Index in original array

                        historyItem.innerHTML = `
                            <div style="text-align: center;">
                                <img src="${item.input_thumbnail}" alt="Input" style="max-height: 120px; border-radius: 8px;">
                                <div class="label" style="margin-top: 0.5rem;">3D Model</div>
                                <div style="font-size: 0.8rem; color: #666;">${item.method} | ${item.processing_time?.toFixed(1) || '?'}s</div>
                                <div class="timestamp">${timestamp}</div>
                                <button class="delete-model-btn" data-index="${originalIndex}"
                                    style="position: absolute; top: 5px; right: 5px; background: #ff4444; color: white;
                                           border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer;
                                           font-size: 14px; line-height: 1; display: flex; align-items: center; justify-content: center;
                                           opacity: 0; transition: opacity 0.2s;"
                                    title="Delete this model">×</button>
                            </div>
                        `;

                        // Show delete button on hover
                        historyItem.onmouseenter = () => {
                            historyItem.querySelector('.delete-model-btn').style.opacity = '1';
                        };
                        historyItem.onmouseleave = () => {
                            historyItem.querySelector('.delete-model-btn').style.opacity = '0';
                        };

                        // Handle delete button click
                        historyItem.querySelector('.delete-model-btn').onclick = (e) => {
                            e.stopPropagation();
                            delete3DModel(originalIndex, item.model_url);
                        };

                        historyItem.onclick = () => load3DModelFromHistory(item);
                        historyGrid.appendChild(historyItem);
                    });

                    document.getElementById('model3dHistorySection').classList.remove('hidden');

                    // Auto-load the most recent 3D model
                    if (reversedHistory.length > 0) {
                        load3DModelFromHistory(reversedHistory[0]);
                    }
                } else {
                    document.getElementById('model3dHistorySection').classList.add('hidden');
                }
            } catch (error) {
                console.error('Failed to load 3D history:', error);
            }
        }

        function load3DModelFromHistory(item) {
            // Update current3DModel reference
            current3DModel = {
                model_url: item.model_url,
                format: item.format,
                processing_time: item.processing_time,
                input_thumbnail: item.input_thumbnail,
                input_original: item.input_original
            };

            document.getElementById('3dModelInfo').textContent =
                `Method: ${item.method} | Time: ${item.processing_time?.toFixed(2) || '?'}s | Format: ${item.format || 'glb'}`;

            document.getElementById('convert3DResults').classList.remove('hidden');

            // If scene already exists with models, add as new instance instead of reinitializing
            if (threeScene && allLoadedModels.length > 0) {
                addModelFromUrlToScene(item.model_url);
            } else {
                init3DViewer(item.model_url, item.format);
            }

            // Scroll to viewer
            document.getElementById('convert3DResults').scrollIntoView({ behavior: 'smooth' });
        }

        function addModelFromUrlToScene(modelUrl) {
            // Add a model from a URL to the existing scene
            const loader = new THREE.GLTFLoader();

            loader.load(modelUrl, (gltf) => {
                const newModel = gltf.scene;

                // Copy scale from first model if exists
                if (currentLoadedModel) {
                    newModel.scale.copy(currentLoadedModel.scale);
                }

                // Determine placement position
                let newX = 0;
                const newY = DEFAULT_Y_POSITION;

                if (allLoadedModels.length === 0) {
                    // First model - place at center
                    newX = 0;
                } else {
                    // Check if default position (center) is occupied
                    const centerOccupied = allLoadedModels.some(m =>
                        Math.abs(m.position.x) < 0.5 && Math.abs(m.position.y - DEFAULT_Y_POSITION) < 0.5
                    );

                    if (!centerOccupied) {
                        // Place at default center position
                        newX = 0;
                    } else {
                        // Find rightmost model and place new one beside it
                        let maxX = -Infinity;
                        allLoadedModels.forEach(m => {
                            if (m.position.x > maxX) maxX = m.position.x;
                        });
                        newX = maxX + MODEL_SPACING;
                    }
                }

                newModel.position.set(newX, newY, 0);

                // Initialize per-model data in userData
                newModel.userData.yRotation = 0;
                newModel.userData.tilt = DEFAULT_TILT;
                // Assign new instance_id
                const maxInstanceId = allLoadedModels.reduce((max, m) =>
                    Math.max(max, m.userData.instanceId || 0), -1);
                newModel.userData.instanceId = maxInstanceId + 1;

                // Add to scene and tracking array
                threeScene.add(newModel);
                allLoadedModels.push(newModel);

                // Select the new model
                currentLoadedModel = newModel;
                userYRotation = newModel.userData.yRotation;
                modelTilt = newModel.userData.tilt;

                // Apply rotation (tilt)
                applyModelRotation(newModel);

                // Apply brightness
                applyBrightnessToModel(modelBrightness);

                showControlButtons = true;
                updateControlVisibility();
                updateControlPositions();

                // Save state
                saveAllModelStates();

                console.log('Added model from history at x=' + newX);
            }, undefined, (error) => {
                console.error('Error loading model from history:', error);
            });
        }

        async function delete3DModel(index, modelUrl) {
            if (!confirm('Delete this 3D model? This cannot be undone.')) {
                return;
            }

            try {
                const response = await fetch('/api/delete-model3d', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ index, model_url: modelUrl })
                });

                const data = await response.json();
                if (data.success) {
                    // Reload the history to reflect the deletion
                    load3DHistory();
                    // Hide the viewer if the deleted model was being displayed
                    if (current3DModel && current3DModel.model_url === modelUrl) {
                        document.getElementById('convert3DResults').classList.add('hidden');
                        document.getElementById('roomPlacementSection').classList.add('hidden');
                        current3DModel = null;
                    }
                } else {
                    showError('Failed to delete model: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                showError('Delete error: ' + error.message);
            }
        }

        function populateRoomSelector() {
            const select = document.getElementById('roomImageSelect');
            select.innerHTML = '<option value="">Select a room image...</option>';

            // Get after images from history
            currentImages.filter(img => img.caption.startsWith('After')).forEach((img, index) => {
                const option = document.createElement('option');
                option.value = img.src;
                option.textContent = img.caption;
                select.appendChild(option);
            });

            select.onchange = () => {
                document.getElementById('placeBtn').disabled = !select.value;
            };
        }

        function placeFurnitureInRoom() {
            const roomImage = document.getElementById('roomImageSelect').value;
            if (!roomImage || !current3DModel) {
                showError('Please select a room and ensure 3D model is ready');
                return;
            }

            const viewer = document.getElementById('roomCompositeViewer');
            viewer.style.display = 'block';
            viewer.innerHTML = '<p style="color: #fff; padding: 2rem; text-align: center;">Room placement feature coming soon!</p>';

            document.getElementById('exportBtn').style.display = 'inline-block';
        }

        function exportComposite() {
            alert('Export feature coming soon!');
        }
    """)

    return (
        Title("Inpainting Methods Test"),
        styles,
        scripts,
        Div(
            H1("🏠 Decor8.ai Furniture Removal Test"),
            P("AI-powered furniture removal for interior design", cls="subtitle"),

            # Upload section
            Div(
                H3("📸 Upload or Drop an Image"),
                P("Drag and drop an image or click to browse", style="color: #666; margin: 1rem 0;"),
                Input(type="file", id="imageInput", accept="image/*", onchange="handleFileSelect(event)"),
                Button("Choose Image", onclick="triggerUpload()", cls="upload-btn"),
                cls="upload-section"
            ),

            # Preview section
            Div(
                H3("Original Image"),
                Img(id="previewImage", src="", alt="Preview"),
                P("Click the button below to remove furniture:",
                  style="color: #666; margin-top: 1rem;"),
                Div(
                    Button("Remove Furniture with Decor8.ai", onclick="vacateImage(5)",
                           cls="vacate-btn method-5", disabled=True),
                    cls="btn-group"
                ),
                id="previewSection",
                cls="preview-section hidden"
            ),

            # Loading section
            Div(
                Div(cls="spinner"),
                P("Processing...", id="loadingText",
                  style="color: #666; font-size: 1.1rem;"),
                id="loadingSection",
                cls="loading hidden"
            ),

            # Results section
            Div(
                H2("Result", style="text-align: center; margin-bottom: 2rem; color: #333;"),
                Div(
                    # Method 5: Decor8.ai
                    Div(
                        H3("Decor8.ai Result"),
                        P("", id="result5Desc", cls="method-description"),
                        Img(id="result5Image", src="", alt="Decor8.ai Result"),
                        Div(
                            Div(
                                Div("Processing Time", cls="stat-label"),
                                Div("0.00s", id="result5Time", cls="stat-value time"),
                                cls="stat-item"
                            ),
                            Div(
                                Div("Estimated Cost", cls="stat-label"),
                                Div("$0.00", id="result5Cost", cls="stat-value cost"),
                                cls="stat-item"
                            ),
                            Div(
                                Div("Quality Rating", cls="stat-label"),
                                Div("0/10", id="result5Quality", cls="stat-value quality"),
                                cls="stat-item"
                            ),
                            cls="stats"
                        ),
                        id="result5Card",
                        cls="result-card"
                    ),

                    cls="results-grid"
                ),
                id="resultsSection",
                cls="hidden"
            ),

            # History section
            Div(
                H2("📚 Before & After Gallery"),
                P("All processed images from newest to oldest",
                  style="text-align: center; color: #666; margin-bottom: 1.5rem;"),
                Div(id="historyGrid", cls="history-grid"),
                id="historySection",
                cls="history-section hidden"
            ),

            # Furniture to 3D section
            Div(
                H2("🪑 Furniture Image Processing"),
                P("Upload furniture image → Choose: Remove Background OR Convert to 3D (or both)",
                  style="text-align: center; color: #666; margin-bottom: 1.5rem;"),

                # Upload furniture image
                Div(
                    H3("📷 Upload Furniture Image"),
                    P("Drag and drop a furniture image or click to browse", style="color: #666; margin: 1rem 0;"),
                    Input(type="file", id="furnitureInput", accept="image/*", onchange="handleFurnitureSelect(event)"),
                    Button("Choose Furniture Image", onclick="triggerFurnitureUpload()", cls="upload-btn"),
                    cls="upload-section",
                    id="furnitureUploadSection"
                ),

                # Furniture preview
                Div(
                    H3("Uploaded Furniture"),
                    Img(id="furniturePreview", src="", alt="Furniture Preview", style="max-height: 300px;"),
                    id="furniturePreviewSection",
                    cls="preview-section hidden"
                ),

                # Background Removal Section
                Div(
                    Div(
                        H4("🎨 Background Removal", style="margin-bottom: 0.5rem;"),
                        Div(
                            Label(
                                Input(type="radio", name="bgMethod", value="rembg", checked=True),
                                " Rembg (Free, Local)",
                                style="margin-right: 1rem; cursor: pointer;"
                            ),
                            Label(
                                Input(type="radio", name="bgMethod", value="removebg"),
                                " Remove.bg (API)",
                                style="margin-right: 1rem; cursor: pointer;"
                            ),
                            Label(
                                Input(type="radio", name="bgMethod", value="photoroom"),
                                " Photoroom (API)",
                                style="cursor: pointer;"
                            ),
                            style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;"
                        ),
                        Button("Remove Background", onclick="removeBackground()", cls="vacate-btn method-1",
                               id="removeBgBtn", disabled=True, style="margin-top: 1rem;"),
                        style="margin-bottom: 1.5rem;"
                    ),
                    id="bgRemovalSection",
                    cls="hidden",
                    style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; text-align: center;"
                ),

                # Background removed result
                Div(
                    H4("Background Removed"),
                    Img(id="bgRemovedPreview", src="", alt="Background Removed",
                        style="max-height: 300px; background: repeating-conic-gradient(#ccc 0% 25%, white 0% 50%) 50%/20px 20px;"),
                    P("", id="bgRemovalPreviewInfo", style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;"),
                    id="bgRemovedPreviewSection",
                    cls="preview-section hidden"
                ),

                # 3D Conversion Section
                Div(
                    Div(
                        H4("🧊 2D to 3D Conversion", style="margin-bottom: 0.5rem;"),
                        P("Converts image to real 3D mesh using Tripo3D API (v2.5)", style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;"),

                        # Tripo3D Parameters
                        Div(
                            P("⚙️ Parameters:", style="font-weight: bold; margin-bottom: 0.5rem; color: #333;"),
                            Div(
                                Label(
                                    Input(type="checkbox", id="tripo3dPbr", checked=True),
                                    " PBR Materials",
                                    style="cursor: pointer; margin-right: 1rem;"
                                ),
                                Label(
                                    Input(type="checkbox", id="tripo3dAutofix", checked=True),
                                    " Image Autofix",
                                    style="cursor: pointer; margin-right: 1rem;"
                                ),
                                Label(
                                    Input(type="checkbox", id="tripo3dOrientation", checked=True),
                                    " Align Orientation",
                                    style="cursor: pointer;"
                                ),
                                style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-bottom: 0.75rem;"
                            ),
                            style="background: #f5f5f5; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;"
                        ),

                        # Prompt field
                        Div(
                            P("📝 Prompt:", style="font-weight: bold; margin-bottom: 0.5rem; color: #333;"),
                            Input(type="text", id="tripo3dPrompt",
                                  value="Front facing, legs touching floor level.",
                                  style="width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 6px; font-size: 0.9rem;"),
                            style="text-align: left; margin-bottom: 1rem;"
                        ),

                        P("⏱️ Processing takes 60-90 seconds", style="color: #888; font-size: 0.8rem; margin-top: 0.5rem;"),
                        Div(
                            Label(
                                Input(type="checkbox", id="useBgRemoved", checked=False),
                                " Use background-removed image (if available)",
                                style="cursor: pointer; font-size: 0.9rem; color: #666;"
                            ),
                            style="margin-top: 0.75rem;"
                        ),
                        Button("Convert to 3D", onclick="convertTo3D()", cls="vacate-btn method-2",
                               id="convertBtn", disabled=True, style="margin-top: 1rem;"),
                    ),
                    id="convert3DSection",
                    cls="hidden",
                    style="background: #e8f5e9; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; text-align: center;"
                ),

                # Processing status
                Div(
                    Div(cls="spinner"),
                    P("", id="convert3DStatus", style="color: #666; font-size: 1.1rem;"),
                    id="convert3DLoading",
                    cls="loading hidden"
                ),

                # 3D Model Results
                Div(
                    H4("3D Model Generated"),
                    Div(id="threejsViewer", style="background: #1a1a2e;"),
                    P("", id="3dModelInfo", style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;"),
                    id="convert3DResults",
                    cls="result-card hidden",
                    style="text-align: center; margin-top: 1.5rem;"
                ),

                # Room placement section
                Div(
                    H3("🏠 Place in Room"),
                    P("Select an 'After' image from the gallery above, then position the 3D furniture",
                      style="color: #666; margin-bottom: 1rem;"),
                    Div(
                        Select(
                            Option("Select a room image...", value=""),
                            id="roomImageSelect",
                            style="padding: 0.5rem; border-radius: 6px; margin-right: 1rem;"
                        ),
                        Button("Place Furniture", onclick="placeFurnitureInRoom()", cls="vacate-btn method-4",
                               id="placeBtn", disabled=True),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(id="roomCompositeViewer",
                        style="height: 500px; background: #1a1a2e; display: none;"),
                    Div(
                        Button("📷 Export as Image", onclick="exportComposite()", cls="vacate-btn method-5",
                               id="exportBtn", style="display: none;"),
                        style="margin-top: 1rem; text-align: center;"
                    ),
                    id="roomPlacementSection",
                    cls="hidden",
                    style="margin-top: 2rem; padding-top: 2rem; border-top: 2px solid #e0e0e0;"
                ),

                # 3D Model History Section
                Div(
                    H3("🧊 3D Model History"),
                    P("Click on a model to view it in the 3D viewer above",
                      style="color: #666; margin-bottom: 1rem;"),
                    Div(id="model3dHistoryGrid", cls="history-grid"),
                    id="model3dHistorySection",
                    cls="hidden",
                    style="margin-top: 2rem; padding-top: 2rem; border-top: 2px solid #e0e0e0;"
                ),

                id="furniture3DSection",
                cls="history-section"
            ),

            cls="container"
        ),

        # Image Modal
        Div(
            Span("×", cls="modal-close", onclick="closeModal()"),
            Span("‹", cls="modal-nav prev", onclick="navigateModal(-1)"),
            Span("›", cls="modal-nav next", onclick="navigateModal(1)"),
            Img(id="modalImage", cls="modal-content", src="", alt="Full size image"),
            Div("", id="modalCaption", cls="modal-caption"),
            id="imageModal",
            cls="modal",
            onclick="event.target.id === 'imageModal' && closeModal()"
        )
    )
