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

            const method3D = document.querySelector('input[name="3dMethod"]:checked').value;
            const useBgRemovedCheckbox = document.getElementById('useBgRemoved');

            // Determine which image to use
            let imageToConvert = furnitureImage;
            if (useBgRemovedCheckbox.checked && bgRemovedImage) {
                imageToConvert = 'data:image/png;base64,' + bgRemovedImage;
            }

            // Show loading
            document.getElementById('convert3DLoading').classList.remove('hidden');
            document.getElementById('convert3DStatus').textContent = 'Converting to 3D with TripoSR... (this may take 30-60 seconds)';
            document.getElementById('convertBtn').disabled = true;

            // Start a timer to show progress
            let elapsed = 0;
            const timer = setInterval(() => {
                elapsed++;
                document.getElementById('convert3DStatus').textContent =
                    `Converting to 3D with TripoSR... ${elapsed}s elapsed`;
            }, 1000);

            try {
                // Use AbortController for timeout (3 minutes max)
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 180000);

                const response3D = await fetch('/api/convert-to-3d', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageToConvert,
                        method: method3D
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
                    `Method: TripoSR | Time: ${data3D.processing_time?.toFixed(2) || '?'}s | Format: ${data3D.format || 'glb'} | Source: ${usedImage}`;

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

        let currentLoadedModel = null;
        let isDraggingModel = false;
        let isDraggingRotate = false;
        let isDraggingScale = false;
        let isDraggingBrightness = false;
        let lastMouseX = 0;
        let lastMouseY = 0;
        let modelBrightness = 2.5; // Max brightness by default
        let viewerContainer = null;
        let controlOverlay = null;

        // Floor plane definition
        let floorPoints = [];  // 4 screen coordinates defining the floor (absolute pixels)
        let floorPointsNormalized = [];  // 4 normalized coordinates (0-1 range relative to canvas)
        let floorWorldPoints = [];  // 4 world coordinates of the floor corners
        let floorCenter = null;  // Center of the floor rectangle in world coords
        let isDefiningFloor = false;
        let floorMarkers = [];  // DOM elements showing floor points
        let floorPlaneY = 0;  // Y level of the floor in world coords

        // Object contact points (e.g., chair legs)
        let objectContactPoints = [];  // 4 world coordinates on the object that touch floor
        let isDefiningContactPoints = false;
        let contactMarkers = [];  // DOM elements showing contact points
        let userYRotation = 0;  // Track user's Y rotation separately from leveling

        // For maintaining constant apparent size when moving in Z
        let modelReferenceZ = 0;  // Z position where baseScale applies
        let modelBaseScale = 1;   // Scale at reference Z position
        const cameraZ = 10;       // Camera Z position (must match camera setup)

        function setupThreeScene(container, modelData, format) {
            viewerContainer = container;
            const width = window.innerWidth;
            const height = width * (3 / 4); // 4:3 aspect ratio
            container.style.height = height + 'px';

            // Scene
            threeScene = new THREE.Scene();

            // Use 2nd after photo as background if available (index 3 = 2nd after)
            if (currentImages.length > 3 && currentImages[3].src) {
                const textureLoader = new THREE.TextureLoader();
                textureLoader.load(currentImages[3].src, (bgTexture) => {
                    threeScene.background = bgTexture;
                }, undefined, (error) => {
                    console.error('Error loading background:', error);
                    threeScene.background = new THREE.Color(0x1a1a2e);
                });
            } else {
                threeScene.background = new THREE.Color(0x1a1a2e);
            }

            // Camera - low FOV for minimal perspective distortion (objects stay similar size at different depths)
            threeCamera = new THREE.PerspectiveCamera(25, width / height, 0.1, 1000);
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

            // Load saved floor data from localStorage (if any)
            loadFloorFromStorage(container);

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
                threeCamera.aspect = newWidth / newHeight;
                threeCamera.updateProjectionMatrix();
                threeRenderer.setSize(newWidth, newHeight);

                // Update floor markers to follow the resized background
                updateFloorMarkersOnResize(container);
            });

            // Setup mouse/touch events for model dragging
            setupModelDragEvents(container);
        }

        function getModelScreenPosition() {
            if (!currentLoadedModel || !threeCamera || !viewerContainer) return null;

            // Get model bounding box
            const box = new THREE.Box3().setFromObject(currentLoadedModel);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());

            // Project center and corners to screen
            const centerScreen = center.clone().project(threeCamera);
            const bottomCenter = new THREE.Vector3(center.x, box.min.y, center.z).project(threeCamera);
            const topCenter = new THREE.Vector3(center.x, box.max.y, center.z).project(threeCamera);
            const rightCenter = new THREE.Vector3(box.max.x, center.y, center.z).project(threeCamera);
            const leftCenter = new THREE.Vector3(box.min.x, center.y, center.z).project(threeCamera);

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

            if (rotateCtrl) {
                rotateCtrl.style.left = pos.centerX + 'px';
                rotateCtrl.style.top = Math.min(pos.bottomY + 15, viewerContainer.clientHeight - 50) + 'px';
            }
            if (scaleCtrl) {
                scaleCtrl.style.left = Math.min(pos.rightX + 15, viewerContainer.clientWidth - 50) + 'px';
                scaleCtrl.style.top = pos.centerY + 'px';
            }
            if (brightnessCtrl) {
                brightnessCtrl.style.left = Math.max(pos.leftX - 55, 10) + 'px';
                brightnessCtrl.style.top = pos.centerY + 'px';
            }
        }

        function addControlOverlay(container) {
            // Remove existing overlay if any
            const existingOverlay = container.querySelector('.viewer-controls');
            if (existingOverlay) existingOverlay.remove();

            const overlay = document.createElement('div');
            overlay.className = 'viewer-controls';
            overlay.style.cssText = 'position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none;';
            controlOverlay = overlay;

            // Rotate control (left-right arrows) - positioned under object (Y rotation)
            const rotateBtn = document.createElement('div');
            rotateBtn.className = 'rotate-control';
            rotateBtn.innerHTML = '↔';
            rotateBtn.style.cssText = `
                position: absolute; bottom: 20px; left: 50%; transform: translate(-50%, 0);
                width: 50px; height: 36px; background: rgba(255,255,255,0.9); border-radius: 18px;
                display: flex; align-items: center; justify-content: center; font-size: 24px;
                cursor: ew-resize; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #333; font-weight: bold;
            `;
            rotateBtn.title = 'Drag left/right to rotate (Y axis)';


            // Scale control (up-down arrows) - positioned to right of object
            const scaleControl = document.createElement('div');
            scaleControl.className = 'scale-control';
            scaleControl.innerHTML = '↕';
            scaleControl.style.cssText = `
                position: absolute; right: 20px; top: 50%; transform: translate(0, -50%);
                width: 36px; height: 50px; background: rgba(255,255,255,0.9); border-radius: 18px;
                display: flex; align-items: center; justify-content: center; font-size: 24px;
                cursor: ns-resize; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #333; font-weight: bold;
            `;
            scaleControl.title = 'Drag up/down to resize';

            // Brightness control (sun icon) - positioned to left of object
            const brightnessControl = document.createElement('div');
            brightnessControl.className = 'brightness-control';
            brightnessControl.innerHTML = '☀';
            brightnessControl.style.cssText = `
                position: absolute; left: 20px; top: 50%; transform: translate(0, -50%);
                width: 36px; height: 50px; background: rgba(255,255,255,0.9); border-radius: 18px;
                display: flex; align-items: center; justify-content: center; font-size: 20px;
                cursor: ns-resize; pointer-events: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                user-select: none; color: #f5a623; font-weight: bold;
            `;
            brightnessControl.title = 'Drag up/down to adjust brightness';

            // Move hint in center
            const moveHint = document.createElement('div');
            moveHint.className = 'move-hint';
            moveHint.innerHTML = '✥ Drag object to move';
            moveHint.style.cssText = `
                position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
                padding: 8px 16px; background: rgba(0,0,0,0.6); border-radius: 20px;
                color: white; font-size: 12px; pointer-events: none;
            `;

            // Define Floor button (top right)
            const floorBtn = document.createElement('div');
            floorBtn.className = 'floor-btn';
            floorBtn.innerHTML = '⬚ Floor';
            floorBtn.style.cssText = `
                position: absolute; top: 10px; right: 10px;
                padding: 8px 16px; background: rgba(76,175,80,0.9); border-radius: 20px;
                color: white; font-size: 12px; cursor: pointer; pointer-events: auto;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3); user-select: none;
            `;
            floorBtn.title = 'Click to define 4 floor corner points';
            floorBtn.onclick = () => startDefiningFloor(container, floorBtn, moveHint);

            overlay.appendChild(rotateBtn);
            overlay.appendChild(scaleControl);
            overlay.appendChild(brightnessControl);
            overlay.appendChild(moveHint);
            overlay.appendChild(floorBtn);
            container.style.position = 'relative';
            container.appendChild(overlay);

            // Rotate control events (Y axis - bottom)
            rotateBtn.addEventListener('mousedown', (e) => {
                e.preventDefault();
                isDraggingRotate = true;
                lastMouseX = e.clientX;
                rotateBtn.style.background = 'rgba(100,200,255,0.9)';
            });

            // Scale control events
            scaleControl.addEventListener('mousedown', (e) => {
                e.preventDefault();
                isDraggingScale = true;
                lastMouseY = e.clientY;
                scaleControl.style.background = 'rgba(100,255,100,0.9)';
            });

            // Brightness control events
            brightnessControl.addEventListener('mousedown', (e) => {
                e.preventDefault();
                isDraggingBrightness = true;
                lastMouseY = e.clientY;
                brightnessControl.style.background = 'rgba(255,200,100,0.9)';
            });

            // Global mouse events
            document.addEventListener('mousemove', (e) => {
                if (isDraggingRotate && currentLoadedModel) {
                    const deltaX = e.clientX - lastMouseX;
                    const angle = deltaX * 0.02;
                    // Use floor pivot rotation to keep legs on floor
                    rotateAroundFloor(currentLoadedModel, angle);
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
                    const deltaY = e.clientY - lastMouseY;
                    modelBrightness = Math.max(0.2, Math.min(2.5, modelBrightness - deltaY * 0.01));
                    applyBrightnessToModel(modelBrightness);
                    lastMouseY = e.clientY;
                }
            });

            document.addEventListener('mouseup', () => {
                if (isDraggingRotate) {
                    isDraggingRotate = false;
                    rotateBtn.style.background = 'rgba(255,255,255,0.9)';
                    // Don't bake Y rotation - just let it accumulate
                    // Y rotation doesn't affect vertical alignment so no need to reset
                }
                if (isDraggingScale) {
                    isDraggingScale = false;
                    scaleControl.style.background = 'rgba(255,255,255,0.9)';
                }
                if (isDraggingBrightness) {
                    isDraggingBrightness = false;
                    brightnessControl.style.background = 'rgba(255,255,255,0.9)';
                }
            });
        }

        function rotateAroundFloor(model, angle) {
            // Update tracked Y rotation
            userYRotation += angle;

            // Reset model rotation to just the user's Y rotation (no leveling tilt yet)
            model.quaternion.identity();
            model.rotation.set(0, userYRotation, 0);
            model.updateMatrixWorld(true);

            // Apply leveling on top of the Y rotation
            if (objectContactPoints.length >= 3) {
                // Level model to floor (makes contact plane horizontal)
                levelModelToFloorWithoutAlign(model, objectContactPoints);

                // Re-apply perspective tilt (but keep user's Y rotation)
                applyPerspectiveTilt(model, objectContactPoints);

                updateContactMarkerPositions();
            }
        }

        function levelModelToFloorWithoutAlign(model, contactPoints) {
            // Transform the model so all contact points lie on the floor plane (Y = floorPlaneY)
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

            // Determine target floor Y
            const targetY = (floorPoints.length >= 4) ? floorPlaneY : 0;

            // Move model so contact points are at floor level
            model.position.y -= (minY - targetY);
            model.updateMatrixWorld(true);
        }

        function applyPerspectiveTilt(model, contactPoints) {
            // Apply perspective tilt without changing Y rotation
            if (floorWorldPoints.length < 4) return;

            const floorBackLeft = floorWorldPoints[0];
            const floorBackRight = floorWorldPoints[3];
            const floorFrontLeft = floorWorldPoints[1];
            const floorFrontRight = floorWorldPoints[2];

            // Calculate perspective tilt from floor trapezoid ratio
            const rect = viewerContainer.getBoundingClientRect();
            const projectToScreen = (p) => {
                const sp = p.clone().project(threeCamera);
                return { x: (sp.x + 1) / 2 * rect.width, y: (-sp.y + 1) / 2 * rect.height };
            };

            const screenBackLeft = projectToScreen(floorBackLeft);
            const screenBackRight = projectToScreen(floorBackRight);
            const screenFrontLeft = projectToScreen(floorFrontLeft);
            const screenFrontRight = projectToScreen(floorFrontRight);

            const backLength = Math.sqrt(
                Math.pow(screenBackRight.x - screenBackLeft.x, 2) +
                Math.pow(screenBackRight.y - screenBackLeft.y, 2)
            );
            const frontLength = Math.sqrt(
                Math.pow(screenFrontRight.x - screenFrontLeft.x, 2) +
                Math.pow(screenFrontRight.y - screenFrontLeft.y, 2)
            );

            const perspectiveRatio = backLength / frontLength;

            let perspectiveTilt = 0;
            if (perspectiveRatio < 1) {
                perspectiveTilt = Math.asin(Math.min(1 - perspectiveRatio, 1));
            }

            if (perspectiveTilt > 0.001) {
                // Apply X rotation for perspective tilt
                const euler = new THREE.Euler().setFromQuaternion(model.quaternion, 'XYZ');
                euler.x = euler.x + perspectiveTilt;
                model.setRotationFromEuler(euler);
                model.updateMatrixWorld(true);

                // Re-level model after tilt
                const worldPoints = contactPoints.map(p => model.localToWorld(p.clone()));
                const minY = Math.min(...worldPoints.map(p => p.y));
                const targetY = (floorPoints.length >= 4) ? floorPlaneY : 0;
                model.position.y -= (minY - targetY);
                model.updateMatrixWorld(true);
            }
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

        function startDefiningFloor(container, floorBtn, moveHint) {
            if (isDefiningFloor) {
                // Cancel floor definition
                isDefiningFloor = false;
                floorBtn.innerHTML = '⬚ Floor';
                floorBtn.style.background = 'rgba(76,175,80,0.9)';
                moveHint.innerHTML = '✥ Drag object to move';
                moveHint.style.pointerEvents = 'none';
                return;
            }

            // Start floor definition mode
            isDefiningFloor = true;
            floorPoints = [];
            floorPointsNormalized = [];
            floorWorldPoints = [];
            floorCenter = null;
            clearFloorMarkers();

            floorBtn.innerHTML = '✕ Cancel';
            floorBtn.style.background = 'rgba(244,67,54,0.9)';
            moveHint.innerHTML = 'Click 4 corners of the floor (0/4)';
            moveHint.style.background = 'rgba(76,175,80,0.9)';

            // Add click handler to canvas
            const canvas = container.querySelector('canvas');
            canvas.style.cursor = 'crosshair';

            const clickHandler = (e) => {
                if (!isDefiningFloor) return;

                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                // Add floor point (both absolute and normalized)
                floorPoints.push({ x, y });
                floorPointsNormalized.push({ x: x / rect.width, y: y / rect.height });
                addFloorMarker(container, x, y, floorPoints.length);

                moveHint.innerHTML = `Click 4 corners of the floor (${floorPoints.length}/4)`;

                if (floorPoints.length >= 4) {
                    // Done defining floor
                    isDefiningFloor = false;
                    canvas.style.cursor = 'default';
                    canvas.removeEventListener('click', clickHandler);

                    floorBtn.innerHTML = '⬚ Floor ✓';
                    floorBtn.style.background = 'rgba(76,175,80,0.9)';
                    moveHint.innerHTML = '✥ Drag object to move (floor locked)';
                    moveHint.style.background = 'rgba(0,0,0,0.6)';

                    // Calculate floor plane Y by converting screen coordinates to world coordinates
                    // Use raycasting from screen position to find world Y
                    const avgScreenY = floorPoints.reduce((sum, p) => sum + p.y, 0) / 4;
                    const avgScreenX = floorPoints.reduce((sum, p) => sum + p.x, 0) / 4;
                    const rect = canvas.getBoundingClientRect();

                    // Convert screen position to normalized device coordinates
                    const ndcX = (avgScreenX / rect.width) * 2 - 1;
                    const ndcY = -(avgScreenY / rect.height) * 2 + 1;

                    // First, calculate floor Y level from screen coordinates
                    // Lower on screen (higher Y) = lower in world (lower Y)
                    const maxScreenY = Math.max(...floorPoints.map(p => p.y));
                    const bottomNdcY = -(maxScreenY / rect.height) * 2 + 1;
                    floorPlaneY = bottomNdcY * 2;  // Scale factor based on camera setup

                    // Convert all 4 floor screen points to world X/Z coordinates
                    // Use raycasting with a horizontal plane at the calculated floor Y
                    const raycaster = new THREE.Raycaster();
                    const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -floorPlaneY);

                    floorWorldPoints = [];
                    for (const screenPt of floorPoints) {
                        const ptNdcX = (screenPt.x / rect.width) * 2 - 1;
                        const ptNdcY = -(screenPt.y / rect.height) * 2 + 1;
                        raycaster.setFromCamera(new THREE.Vector2(ptNdcX, ptNdcY), threeCamera);

                        const intersection = new THREE.Vector3();
                        raycaster.ray.intersectPlane(floorPlane, intersection);
                        if (intersection) {
                            floorWorldPoints.push(intersection.clone());
                        }
                    }

                    // Calculate floor center (average of 4 points)
                    if (floorWorldPoints.length === 4) {
                        floorCenter = new THREE.Vector3(0, 0, 0);
                        for (const wp of floorWorldPoints) {
                            floorCenter.add(wp);
                        }
                        floorCenter.divideScalar(4);
                    } else {
                        floorCenter = null;
                    }

                    console.log('Floor defined:', floorPoints, 'World points:', floorWorldPoints, 'Center:', floorCenter, 'Floor Y:', floorPlaneY);
                    drawFloorOutline(container);

                    // Save floor data to localStorage for persistence across page reloads
                    saveFloorToStorage();

                    // Auto-relocate object to floor and bake position
                    if (currentLoadedModel) {
                        // Get the lowest point of the model (either contact points or bounding box)
                        let modelBottomY;
                        if (objectContactPoints.length >= 4) {
                            modelBottomY = getLowestContactPointY();
                        } else {
                            const box = new THREE.Box3().setFromObject(currentLoadedModel);
                            modelBottomY = box.min.y;
                        }

                        // Move model so its bottom is at floor level
                        const offset = modelBottomY - floorPlaneY;
                        currentLoadedModel.position.y -= offset;
                        console.log('Model auto-placed on floor, offset:', offset);

                        // Center geometry on Y axis so rotation keeps all legs on floor
                        // Get the center of the model's footprint
                        const boxForCenter = new THREE.Box3().setFromObject(currentLoadedModel);
                        const center = boxForCenter.getCenter(new THREE.Vector3());

                        // Translate geometry so center X/Z is at origin
                        // This makes the Y axis pass through the footprint center
                        const offsetX = center.x - currentLoadedModel.position.x;
                        const offsetZ = center.z - currentLoadedModel.position.z;

                        currentLoadedModel.traverse((child) => {
                            if (child.isMesh && child.geometry) {
                                child.geometry.translate(-offsetX, 0, -offsetZ);
                            }
                        });

                        // Adjust position to compensate (keep visual position same)
                        currentLoadedModel.position.x += offsetX;
                        currentLoadedModel.position.z += offsetZ;

                        console.log('Geometry centered for Y rotation, offset X:', offsetX, 'Z:', offsetZ);

                        // Re-detect contact points after geometry modification
                        autoDetectContactPoints(currentLoadedModel);
                    }
                }
            };

            canvas.addEventListener('click', clickHandler);
        }

        function addFloorMarker(container, x, y, index) {
            const marker = document.createElement('div');
            marker.className = 'floor-marker';
            marker.innerHTML = index;
            marker.style.cssText = `
                position: absolute; left: ${x}px; top: ${y}px;
                width: 24px; height: 24px; margin-left: -12px; margin-top: -12px;
                background: rgba(76,175,80,0.9); border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                color: white; font-size: 12px; font-weight: bold;
                pointer-events: none; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            `;
            container.appendChild(marker);
            floorMarkers.push(marker);
        }

        function clearFloorMarkers() {
            floorMarkers.forEach(m => m.remove());
            floorMarkers = [];
            // Remove floor outline if exists
            const outline = document.querySelector('.floor-outline');
            if (outline) outline.remove();
        }

        function drawFloorOutline(container) {
            if (floorWorldPoints.length < 4) return;

            // Remove existing outline first
            const existingOutline = container.querySelector('.floor-outline');
            if (existingOutline) existingOutline.remove();

            const rect = container.getBoundingClientRect();

            // Project floor world points to screen coordinates using current camera
            // This ensures the outline aligns with leg marker projections
            const screenPoints = floorWorldPoints.map(wp => {
                const screenPt = wp.clone().project(threeCamera);
                return {
                    x: (screenPt.x + 1) / 2 * rect.width,
                    y: (-screenPt.y + 1) / 2 * rect.height
                };
            });

            // Create SVG overlay for floor outline
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.classList.add('floor-outline');
            svg.style.cssText = `
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                pointer-events: none;
            `;

            const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            const points = screenPoints.map(p => `${p.x},${p.y}`).join(' ');
            polygon.setAttribute('points', points);
            polygon.setAttribute('fill', 'rgba(76,175,80,0.1)');
            polygon.setAttribute('stroke', 'rgba(76,175,80,0.8)');
            polygon.setAttribute('stroke-width', '2');
            polygon.setAttribute('stroke-dasharray', '5,5');

            svg.appendChild(polygon);
            container.appendChild(svg);
        }

        function updateFloorMarkersOnResize(container) {
            // Update floor markers and outline based on projected world coordinates
            if (floorWorldPoints.length < 4 || !viewerContainer || !threeCamera) return;

            const rect = viewerContainer.getBoundingClientRect();

            // Project floor world points to screen using current camera
            const screenPoints = floorWorldPoints.map(wp => {
                const screenPt = wp.clone().project(threeCamera);
                return {
                    x: (screenPt.x + 1) / 2 * rect.width,
                    y: (-screenPt.y + 1) / 2 * rect.height
                };
            });

            // Clear and redraw markers at projected positions
            clearFloorMarkers();
            screenPoints.forEach((p, i) => {
                addFloorMarker(container, p.x, p.y, i + 1);
            });
            drawFloorOutline(container);
        }

        function saveFloorToStorage() {
            // Save floor data to localStorage (use normalized coordinates for portability)
            const floorData = {
                floorPoints: floorPoints,
                floorPointsNormalized: floorPointsNormalized,
                floorPlaneY: floorPlaneY,
                floorWorldPoints: floorWorldPoints.map(p => ({ x: p.x, y: p.y, z: p.z })),
                floorCenter: floorCenter ? { x: floorCenter.x, y: floorCenter.y, z: floorCenter.z } : null
            };
            localStorage.setItem('floor3DData', JSON.stringify(floorData));
            console.log('Floor data saved to localStorage');
        }

        function loadFloorFromStorage(container) {
            // Load floor data from localStorage
            const savedData = localStorage.getItem('floor3DData');
            if (!savedData) return false;

            try {
                const floorData = JSON.parse(savedData);

                if (floorData.floorPoints && floorData.floorPoints.length >= 4) {
                    floorPlaneY = floorData.floorPlaneY || 0;

                    // Load normalized coordinates (or calculate from absolute if not available)
                    if (floorData.floorPointsNormalized && floorData.floorPointsNormalized.length >= 4) {
                        floorPointsNormalized = floorData.floorPointsNormalized;
                    } else {
                        // Backward compatibility: calculate normalized from absolute
                        // Assume original canvas was same aspect ratio
                        const rect = container.getBoundingClientRect();
                        floorPointsNormalized = floorData.floorPoints.map(p => ({
                            x: p.x / rect.width,
                            y: p.y / rect.height
                        }));
                    }

                    // Calculate absolute positions from normalized for current canvas size
                    const rect = container.getBoundingClientRect();
                    floorPoints = floorPointsNormalized.map(p => ({
                        x: p.x * rect.width,
                        y: p.y * rect.height
                    }));

                    // Reconstruct THREE.Vector3 objects for world points
                    if (floorData.floorWorldPoints) {
                        floorWorldPoints = floorData.floorWorldPoints.map(p =>
                            new THREE.Vector3(p.x, p.y, p.z)
                        );
                    }

                    if (floorData.floorCenter) {
                        floorCenter = new THREE.Vector3(
                            floorData.floorCenter.x,
                            floorData.floorCenter.y,
                            floorData.floorCenter.z
                        );
                    }

                    console.log('Floor data loaded from localStorage:', floorPoints, 'Normalized:', floorPointsNormalized, 'Floor Y:', floorPlaneY);

                    // Draw floor markers and outline using projected world coordinates
                    // This ensures alignment with leg marker projections
                    floorWorldPoints.forEach((wp, i) => {
                        const screenPt = wp.clone().project(threeCamera);
                        const screenX = (screenPt.x + 1) / 2 * rect.width;
                        const screenY = (-screenPt.y + 1) / 2 * rect.height;
                        addFloorMarker(container, screenX, screenY, i + 1);
                    });
                    drawFloorOutline(container);

                    // Update UI to show floor is defined
                    const floorBtn = container.querySelector('.floor-btn');
                    const moveHint = container.querySelector('.move-hint');
                    if (floorBtn) {
                        floorBtn.innerHTML = '⬚ Floor ✓';
                    }
                    if (moveHint) {
                        moveHint.innerHTML = '✥ Drag object to move (floor locked)';
                    }

                    return true;
                }
            } catch (e) {
                console.error('Error loading floor data:', e);
            }

            return false;
        }

        function getFloorYAtScreenPos(screenX, screenY) {
            // Calculate Y position on floor plane based on screen position
            // Using perspective interpolation from the 4 floor points
            if (floorPoints.length < 4) return null;

            const rect = viewerContainer.getBoundingClientRect();
            const relX = screenX / rect.width;
            const relY = screenY / rect.height;

            // Simple linear interpolation (approximate)
            // For more accuracy, use perspective-correct interpolation
            return floorPlaneY;
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
                        moveHint.innerHTML = '✥ Drag object to move (legs on floor)';
                        moveHint.style.background = 'rgba(0,0,0,0.6)';

                        // Calculate average Y of contact points as floor level
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
            const marker = document.createElement('div');
            marker.className = 'contact-marker';
            marker.innerHTML = index;
            marker.style.cssText = `
                position: absolute; left: ${x}px; top: ${y}px;
                width: 24px; height: 24px; margin-left: -12px; margin-top: -12px;
                background: rgba(255,152,0,0.9); border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                color: white; font-size: 12px; font-weight: bold;
                pointer-events: none; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                border: 2px solid white;
            `;
            container.appendChild(marker);
            contactMarkers.push(marker);
        }

        function clearContactMarkers() {
            contactMarkers.forEach(m => m.remove());
            contactMarkers = [];
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

        function adjustModelToFloor() {
            // Adjust model position so contact points touch the floor
            if (objectContactPoints.length === 0 || floorPoints.length < 4 || !currentLoadedModel) return;

            const lowestY = getLowestContactPointY();
            if (lowestY !== null) {
                const offset = lowestY - floorPlaneY;
                currentLoadedModel.position.y -= offset;
            }
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

            // Find the minimum Y (lowest point)
            const minY = Math.min(...allVertices.map(v => v.y));

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

            // Level the model so all 4 contact points are at the same Y (floor level)
            if (objectContactPoints.length >= 3) {
                levelModelToFloor(model, objectContactPoints);
            }

            // Show visual markers for the detected contact points
            showContactPointMarkers();

            return objectContactPoints.length;
        }

        function levelModelToFloor(model, contactPoints) {
            // Transform the model so all contact points lie on the floor plane (Y = floorPlaneY)
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

            // Determine target floor Y
            const targetY = (floorPoints.length >= 4) ? floorPlaneY : 0;

            // Move model so contact points are at floor level
            model.position.y -= (minY - targetY);
            model.updateMatrixWorld(true);  // Update after position change

            console.log('Model leveled to floor. Min contact Y:', minY, '-> Target Y:', targetY);

            // Note: We don't modify objectContactPoints - they stay in local coordinates.
            // The model transformation (rotation + position) handles the world positioning.
            // When markers are rendered, localToWorld() will give correct screen positions.
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

        // Check if a point (x, z) is inside the floor polygon (using X-Z coordinates)
        function isPointInFloorPolygon(x, z) {
            if (floorWorldPoints.length < 4) return true; // No floor defined, allow all movement

            // Ray casting algorithm for point-in-polygon test
            let inside = false;
            const points = floorWorldPoints;
            for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
                const xi = points[i].x, zi = points[i].z;
                const xj = points[j].x, zj = points[j].z;

                if (((zi > z) !== (zj > z)) && (x < (xj - xi) * (z - zi) / (zj - zi) + xi)) {
                    inside = !inside;
                }
            }
            return inside;
        }

        // Check if all contact points would be inside floor after moving model
        function wouldContactPointsBeInFloor(newPosX, newPosZ) {
            if (floorWorldPoints.length < 4) return true; // No floor defined
            if (objectContactPoints.length === 0) return true; // No contact points

            // Temporarily move model to new position
            const oldX = currentLoadedModel.position.x;
            const oldZ = currentLoadedModel.position.z;
            currentLoadedModel.position.x = newPosX;
            currentLoadedModel.position.z = newPosZ;

            // Check all contact points
            let allInside = true;
            for (const localPoint of objectContactPoints) {
                const worldPoint = currentLoadedModel.localToWorld(localPoint.clone());
                if (!isPointInFloorPolygon(worldPoint.x, worldPoint.z)) {
                    allInside = false;
                    break;
                }
            }

            // Restore original position
            currentLoadedModel.position.x = oldX;
            currentLoadedModel.position.z = oldZ;

            return allInside;
        }

        // Count how many contact points would be inside floor at given position
        function countContactPointsInFloor(posX, posZ) {
            if (floorWorldPoints.length < 4 || objectContactPoints.length === 0) return objectContactPoints.length;

            const oldX = currentLoadedModel.position.x;
            const oldZ = currentLoadedModel.position.z;
            currentLoadedModel.position.x = posX;
            currentLoadedModel.position.z = posZ;
            currentLoadedModel.updateMatrixWorld(true);

            let count = 0;
            for (const localPoint of objectContactPoints) {
                const worldPoint = currentLoadedModel.localToWorld(localPoint.clone());
                if (isPointInFloorPolygon(worldPoint.x, worldPoint.z)) {
                    count++;
                }
            }

            currentLoadedModel.position.x = oldX;
            currentLoadedModel.position.z = oldZ;
            currentLoadedModel.updateMatrixWorld(true);
            return count;
        }

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

        // Check if movement is allowed - allow if it doesn't make things worse
        function getValidPosition(startX, startZ, deltaX, deltaZ) {
            if (floorWorldPoints.length < 4 || objectContactPoints.length === 0) {
                return { x: startX + deltaX, z: startZ + deltaZ };
            }

            const targetX = startX + deltaX;
            const targetZ = startZ + deltaZ;

            // Count current points inside
            const currentInside = countContactPointsInFloor(startX, startZ);

            // Try full movement - allow if at least as many points inside
            const fullMoveInside = countContactPointsInFloor(targetX, targetZ);
            if (fullMoveInside >= currentInside) {
                return { x: targetX, z: targetZ };
            }

            // Full movement blocked - try X only (slide along Z edge)
            if (Math.abs(deltaX) > 0.001) {
                const xOnlyInside = countContactPointsInFloor(targetX, startZ);
                if (xOnlyInside >= currentInside) {
                    return { x: targetX, z: startZ };
                }
            }

            // Try Z only (slide along X edge)
            if (Math.abs(deltaZ) > 0.001) {
                const zOnlyInside = countContactPointsInFloor(startX, targetZ);
                if (zOnlyInside >= currentInside) {
                    return { x: startX, z: targetZ };
                }
            }

            // No valid movement - stay in place
            return { x: startX, z: startZ };
        }

        function getPlaneIntersection(clientX, clientY, canvas, planeY) {
            const rect = canvas.getBoundingClientRect();
            const mouse = new THREE.Vector2();
            mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, threeCamera);

            // Create horizontal plane at the specified Y height
            const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -planeY);
            const intersection = new THREE.Vector3();

            if (raycaster.ray.intersectPlane(plane, intersection)) {
                return intersection;
            }
            return null;
        }

        function setupModelDragEvents(container) {
            const canvas = container.querySelector('canvas');
            if (!canvas) return;

            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();

            canvas.addEventListener('mousedown', (e) => {
                if (isDraggingRotate || isDraggingScale || isDraggingBrightness) return;

                const rect = canvas.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                raycaster.setFromCamera(mouse, threeCamera);

                if (currentLoadedModel) {
                    const intersects = raycaster.intersectObject(currentLoadedModel, true);
                    if (intersects.length > 0) {
                        isDraggingModel = true;
                        canvas.style.cursor = 'move';

                        // Store the exact 3D point where user clicked on the model
                        dragStartHitPoint = intersects[0].point.clone();
                        dragPlaneY = dragStartHitPoint.y;
                        dragStartModelPosition = currentLoadedModel.position.clone();
                        lastCursorHitPoint = dragStartHitPoint.clone();  // Initialize for incremental tracking
                    }
                }
            });

            canvas.addEventListener('mousemove', (e) => {
                if (isDraggingModel && currentLoadedModel && lastCursorHitPoint) {
                    // Get intersection with plane at the same Y height as the original click
                    const currentPoint = getPlaneIntersection(e.clientX, e.clientY, canvas, dragPlaneY);

                    if (currentPoint) {
                        // Calculate incremental movement from last cursor position
                        const deltaX = currentPoint.x - lastCursorHitPoint.x;
                        const deltaZ = currentPoint.z - lastCursorHitPoint.z;

                        // Get valid position from current model position (incremental movement)
                        const validPos = getValidPosition(
                            currentLoadedModel.position.x,
                            currentLoadedModel.position.z,
                            deltaX,
                            deltaZ
                        );

                        // Move the model
                        currentLoadedModel.position.x = validPos.x;
                        currentLoadedModel.position.z = validPos.z;
                        updateScaleForConstantSize();
                        updateContactMarkerPositions();

                        // Always update cursor tracking for next frame
                        lastCursorHitPoint = currentPoint.clone();
                    }
                }
            });

            canvas.addEventListener('mouseup', () => {
                isDraggingModel = false;
                dragStartHitPoint = null;
                dragStartModelPosition = null;
                lastCursorHitPoint = null;
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
            canvas.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    const touch = e.touches[0];
                    const rect = canvas.getBoundingClientRect();
                    mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;

                    raycaster.setFromCamera(mouse, threeCamera);

                    if (currentLoadedModel) {
                        const intersects = raycaster.intersectObject(currentLoadedModel, true);
                        if (intersects.length > 0) {
                            isDraggingModel = true;
                            dragStartHitPoint = intersects[0].point.clone();
                            dragPlaneY = dragStartHitPoint.y;
                            dragStartModelPosition = currentLoadedModel.position.clone();
                            lastCursorHitPoint = dragStartHitPoint.clone();
                            e.preventDefault();
                        }
                    }
                }
            }, { passive: false });

            canvas.addEventListener('touchmove', (e) => {
                if (isDraggingModel && currentLoadedModel && lastCursorHitPoint && e.touches.length === 1) {
                    const touch = e.touches[0];
                    const currentPoint = getPlaneIntersection(touch.clientX, touch.clientY, canvas, dragPlaneY);

                    if (currentPoint) {
                        // Calculate incremental movement from last cursor position
                        const deltaX = currentPoint.x - lastCursorHitPoint.x;
                        const deltaZ = currentPoint.z - lastCursorHitPoint.z;

                        // Get valid position from current model position (incremental movement)
                        const validPos = getValidPosition(
                            currentLoadedModel.position.x,
                            currentLoadedModel.position.z,
                            deltaX,
                            deltaZ
                        );

                        // Move the model
                        currentLoadedModel.position.x = validPos.x;
                        currentLoadedModel.position.z = validPos.z;
                        updateScaleForConstantSize();
                        updateContactMarkerPositions();

                        // Always update cursor tracking for next frame
                        lastCursorHitPoint = currentPoint.clone();
                    }
                    e.preventDefault();
                }
            }, { passive: false });

            canvas.addEventListener('touchend', () => {
                isDraggingModel = false;
                dragStartHitPoint = null;
                dragStartModelPosition = null;
                lastCursorHitPoint = null;
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
                // Remove existing model
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

                // Reset brightness and rotation for new model
                modelBrightness = 2.5; // Max brightness by default
                userYRotation = 0;

                // Store reference for drag controls
                currentLoadedModel = model;
                threeScene.add(model);

                // Apply max brightness by default
                applyBrightnessToModel(modelBrightness);

                // Apply floor and detect contact points after model is loaded
                setTimeout(() => {
                    // If floor is already defined (from background), apply it FIRST
                    // This modifies the geometry, so contact detection must come AFTER
                    if (floorPoints.length >= 4) {
                        applyFloorToModel(model);
                    }

                    // THEN auto-detect contact points (chair legs)
                    // This must happen after geometry modifications are done
                    const numPoints = autoDetectContactPoints(model);
                    if (numPoints >= 4) {
                        console.log('Auto-detected ' + numPoints + ' contact points');
                    }
                }, 100);
            }, undefined, (error) => {
                console.error('Error loading 3D model:', error);
                document.getElementById('threejsViewer').innerHTML =
                    '<p style="color: #f5576c; padding: 2rem; text-align: center;">Error loading 3D model</p>';
            });
        }

        function applyFloorToModel(model) {
            // Apply existing floor settings to a newly loaded model
            if (!model || floorPoints.length < 4) return;

            // Get the lowest point of the model (either contact points or bounding box)
            let modelBottomY;
            if (objectContactPoints.length >= 4) {
                modelBottomY = getLowestContactPointY();
            } else {
                const box = new THREE.Box3().setFromObject(model);
                modelBottomY = box.min.y;
            }

            // Move model so its bottom is at floor level
            const offset = modelBottomY - floorPlaneY;
            model.position.y -= offset;
            console.log('Model placed on existing floor, offset:', offset);

            // Center geometry on Y axis so rotation keeps all legs on floor
            const boxForCenter = new THREE.Box3().setFromObject(model);
            const center = boxForCenter.getCenter(new THREE.Vector3());

            // Translate geometry so center X/Z is at origin
            const offsetX = center.x - model.position.x;
            const offsetZ = center.z - model.position.z;

            model.traverse((child) => {
                if (child.isMesh && child.geometry) {
                    child.geometry.translate(-offsetX, 0, -offsetZ);
                }
            });

            // Adjust position to compensate (keep visual position same)
            model.position.x += offsetX;
            model.position.z += offsetZ;

            console.log('Geometry centered for Y rotation, offset X:', offsetX, 'Z:', offsetZ);

            // Store reference Z and scale for constant apparent size during movement
            modelReferenceZ = model.position.z;
            modelBaseScale = model.scale.x;
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

        function download3DModel(format) {
            if (!current3DModel) {
                showError('No 3D model available');
                return;
            }
            // Download the GLB file
            if (current3DModel.model_url) {
                const a = document.createElement('a');
                a.href = current3DModel.model_url;
                a.download = 'model.' + (format || 'glb');
                a.click();
            } else {
                alert('Download not available for this model');
            }
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

                        const timestamp = new Date(item.timestamp).toLocaleString();

                        historyItem.innerHTML = `
                            <div style="text-align: center;">
                                <img src="${item.input_thumbnail}" alt="Input" style="max-height: 120px; border-radius: 8px;">
                                <div class="label" style="margin-top: 0.5rem;">3D Model</div>
                                <div style="font-size: 0.8rem; color: #666;">${item.method} | ${item.processing_time?.toFixed(1) || '?'}s</div>
                                <div class="timestamp">${timestamp}</div>
                            </div>
                        `;

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
            current3DModel = {
                model_url: item.model_url,
                format: item.format,
                processing_time: item.processing_time
            };

            document.getElementById('3dModelInfo').textContent =
                `Method: ${item.method} | Time: ${item.processing_time?.toFixed(2) || '?'}s | Format: ${item.format || 'glb'}`;

            document.getElementById('convert3DResults').classList.remove('hidden');
            init3DViewer(item.model_url, item.format);

            // Scroll to viewer
            document.getElementById('convert3DResults').scrollIntoView({ behavior: 'smooth' });
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
                        P("Converts image to real 3D mesh using TripoSR (Stability AI)", style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;"),
                        Div(
                            Label(
                                Input(type="radio", name="3dMethod", value="triposr", checked=True),
                                " TripoSR (Free, HuggingFace)",
                                style="cursor: pointer;"
                            ),
                            style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;"
                        ),
                        P("⏱️ Processing takes 30-60 seconds", style="color: #888; font-size: 0.8rem; margin-top: 0.5rem;"),
                        Div(
                            Label(
                                Input(type="checkbox", id="useBgRemoved", checked=True),
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
                    Div(
                        Button("Download .glb", onclick="download3DModel('glb')", cls="vacate-btn method-1",
                               style="font-size: 0.9rem; padding: 0.5rem 1rem;"),
                        Button("Download .obj", onclick="download3DModel('obj')", cls="vacate-btn method-3",
                               style="font-size: 0.9rem; padding: 0.5rem 1rem;"),
                        style="margin-top: 1rem;"
                    ),
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
