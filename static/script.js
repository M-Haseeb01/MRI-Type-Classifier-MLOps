// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const imagePreview = document.getElementById('imagePreview');
const previewContainer = document.getElementById('previewContainer');
const removeBtn = document.getElementById('removeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const resultClass = document.getElementById('resultClass');
const resultIcon = document.getElementById('resultIcon');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceFill = document.getElementById('confidenceFill');
const predictionsGrid = document.getElementById('predictionsGrid');

let selectedFile = null;

// Click to browse
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop handlers
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Handle file selection
function handleFile(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        previewContainer.style.display = 'block';
        dropZone.style.display = 'none';
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// Remove image
removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetUpload();
});

// Reset upload state
function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    previewContainer.style.display = 'none';
    dropZone.style.display = 'block';
    analyzeBtn.disabled = true;
}

// Analyze button click
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // Show loading state
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-flex';
    analyzeBtn.disabled = true;

    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Send request
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during prediction. Please try again.');
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        analyzeBtn.disabled = false;
    }
});

// Display results
function displayResults(data) {
    // Set result class
    resultClass.textContent = data.predicted_class;

    // Set icon based on result
    if (data.predicted_class === 'No Tumor') {
        resultIcon.textContent = '✅';
    } else {
        resultIcon.textContent = '⚠️';
    }

    // Set confidence
    const confidencePercent = (data.confidence * 100).toFixed(2);
    confidenceValue.textContent = confidencePercent + '%';
    confidenceFill.style.width = confidencePercent + '%';

    // Display all predictions
    predictionsGrid.innerHTML = '';

    // Sort predictions by probability
    const sortedPredictions = Object.entries(data.all_predictions)
        .sort((a, b) => b[1] - a[1]);

    sortedPredictions.forEach(([className, probability]) => {
        const percent = (probability * 100).toFixed(2);

        const predictionItem = document.createElement('div');
        predictionItem.className = 'prediction-item';
        predictionItem.innerHTML = `
            <div class="prediction-name">${className}</div>
            <div class="prediction-bar-container">
                <div class="prediction-bar-fill" style="width: ${percent}%"></div>
            </div>
            <div class="prediction-percentage">${percent}%</div>
        `;

        predictionsGrid.appendChild(predictionItem);
    });

    // Show results section, hide upload section
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// New analysis button
newAnalysisBtn.addEventListener('click', () => {
    // Hide results, show upload
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';

    // Reset upload state
    resetUpload();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Theme Toggle Functionality
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Update toggle state
    themeToggle.checked = savedTheme === 'light';

    // Add event listener
    themeToggle.addEventListener('change', () => {
        const newTheme = themeToggle.checked ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// Initialize theme on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
} else {
    initTheme();
}
