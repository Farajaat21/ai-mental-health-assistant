let isCameraActive = false;
let videoStream = null;

function createCameraUI() {
    const cameraPreviewWindow = document.createElement('div');
    cameraPreviewWindow.id = 'camera-preview-window';
    cameraPreviewWindow.classList.add('camera-preview-window');
    cameraPreviewWindow.style.display = 'none'; // Hidden by default
    cameraPreviewWindow.innerHTML = `
        <div class="camera-preview">
            <video id="video-preview" autoplay playsinline></video>
            <div class="emotion-overlay">
                <span class="emotion-text">Analyzing...</span>
            </div>
            <div class="camera-controls">
                <button id="toggle-preview" class="preview-btn">
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                    </svg>
                </button>
                <button id="close-camera" class="close-camera-btn">
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(cameraPreviewWindow);
    return cameraPreviewWindow;
}

// Add new preview functionality
function togglePreview() {
    if (!isCameraActive || !videoStream) return;
    
    let previewWindow = document.getElementById('camera-preview-window');
    if (!previewWindow) {
        previewWindow = createCameraUI();
    }
    
    const isVisible = previewWindow.style.display !== 'none';
    previewWindow.style.display = isVisible ? 'none' : 'block';
    
    const video = document.getElementById('video-preview');
    if (!isVisible && video) {
        video.srcObject = videoStream;
        video.play();
    }
    
    const previewButton = document.getElementById('previewButton');
    if (previewButton) {
        previewButton.classList.toggle('preview-active');
    }
}

async function openCamera() {
    if (isVoiceActive) {
        alert("Please turn off voice mode before using camera");
        return;
    }
    
    if (isCameraActive) {
        closeCamera();
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: "user",
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        });
        
        videoStream = stream;
        isCameraActive = true;

        // Create preview window but keep it hidden initially
        createCameraUI();
        
        // Enable preview button
        const previewButton = document.getElementById('previewButton');
        if (previewButton) {
            previewButton.disabled = false;
            previewButton.classList.add('active');
            previewButton.onclick = togglePreview;
        }

        // Update camera button
        const cameraButton = document.getElementById('camera');
        cameraButton.classList.add('active');
        
        startEmotionDetection();

    } catch (error) {
        console.error('Error accessing camera:', error);
        displayDebugText('Error accessing camera: ' + error.message);
    }
}

function closeCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    
    isCameraActive = false;
    
    // Update UI
    const cameraButton = document.getElementById('camera');
    const previewButton = document.getElementById('previewButton');
    const previewWindow = document.getElementById('camera-preview-window');
    
    if (cameraButton) {
        cameraButton.classList.remove('active');
    }
    
    if (previewButton) {
        previewButton.disabled = true;
        previewButton.classList.remove('active', 'preview-active');
    }
    
    if (previewWindow) {
        previewWindow.style.display = 'none';
    }
    
    // Reset emotion text
    const emotionText = document.querySelector('.emotion-text');
    if (emotionText) {
        emotionText.textContent = 'Camera closed';
    }
}

async function startEmotionDetection() {
    if (!isCameraActive || !videoStream) return;
    
    const video = document.getElementById('video-preview');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const emotionText = document.querySelector('.emotion-text');
    
    let lastEmotion = null;
    let emotionConfidence = 0;
    let emotionCounter = {};
    const CONFIDENCE_THRESHOLD = 0.5; // Lowered threshold to detect more emotions
    
    async function detectEmotion() {
        if (!isCameraActive) return;
        
        try {
            // Capture frame
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert to base64
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            // Send to backend for emotion detection
            const response = await fetch('/detect-emotion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            });
            
            if (!response.ok) {
                throw new Error('Emotion detection failed');
            }
            
            const data = await response.json();
            
            // Update emotion display with confidence threshold and smoothing
            if (data.emotion && data.confidence >= CONFIDENCE_THRESHOLD) {
                // Count emotion occurrences for stability
                emotionCounter[data.emotion] = (emotionCounter[data.emotion] || 0) + 1;
                
                // Only update UI if we have a consistent emotion or a strong confidence
                if (emotionCounter[data.emotion] >= 2 || data.confidence > 0.7) {
                    if (data.emotion !== lastEmotion || data.confidence > emotionConfidence + 0.1) {
                        lastEmotion = data.emotion;
                        emotionConfidence = data.confidence;
                        
                        // Show emoji with emotion name
                        const emoji = getEmoji(data.emotion);
                        const displayEmotion = getEmotionDisplay(data.emotion);
                        
                        // Update UI with animation
                        gsap.to(emotionText, {
                            opacity: 0,
                            y: -10,
                            duration: 0.2,
                            onComplete: () => {
                                emotionText.innerHTML = `${emoji} ${displayEmotion} <span style="font-size: 0.8em">(${Math.round(data.confidence * 100)}%)</span>`;
                                gsap.to(emotionText, {
                                    opacity: 1,
                                    y: 0,
                                    duration: 0.2
                                });
                            }
                        });
                        
                        // Update mood emoji if confidence is high
                        if (data.confidence >= 0.7) {
                            updateMoodEmoji(data.emotion);
                            // Store for potential use in next message
                            window.lastDetectedEmotion = data.emotion;
                        }
                        
                        // Reset counter after updating
                        emotionCounter = {};
                        emotionCounter[data.emotion] = 1;
                    }
                }
            }
            
        } catch (error) {
            console.error('Emotion detection error:', error);
            if (emotionText) {
                emotionText.textContent = 'Analyzing...';
            }
        }
        
        // Schedule next detection
        if (isCameraActive) {
            setTimeout(detectEmotion, 800); // Check more frequently
        }
    }
    
    // Start detection
    detectEmotion();
}

function getEmoji(emotion) {
    const emojiMap = {
        'happy': '😊',
        'masking_pain': '🙂',
        'sad': '😔',
        'anxious': '😰',
        'stressed': '😫',
        'overwhelmed': '😩',
        'angry': '😠',
        'expressive': '😲',
        'focused': '🧐',
        'alert': '👀',
        'tired': '😴',
        'hopeful': '🙂',
        'neutral': '😐',
        'no_face': '❓'
    };
    return emojiMap[emotion] || '🤔';
}

function getEmotionDisplay(emotion) {
    const displayMap = {
        'happy': 'Happy',
        'masking_pain': 'Masking Pain',
        'sad': 'Sad',
        'anxious': 'Anxious',
        'stressed': 'Stressed',
        'overwhelmed': 'Overwhelmed',
        'angry': 'Angry',
        'expressive': 'Expressive',
        'focused': 'Focused',
        'alert': 'Alert',
        'tired': 'Tired',
        'hopeful': 'Hopeful',
        'neutral': 'Neutral',
        'no_face': 'No Face Detected'
    };
    return displayMap[emotion] || emotion;
}

async function handleEmotionDetected(emotion, confidence) {
    try {
        const response = await fetch('/emotion-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                emotion: emotion,
                confidence: confidence
            })
        });
        
        const data = await response.json();
        if (!data.error) {
            displayMessage(data.reply, 'bot');
        }
    } catch (error) {
        console.error('Error handling emotion:', error);
    }
}

// Modify sendMessage function to include detected emotion
const originalSendMessage = window.sendMessage;
window.sendMessage = async function() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (message) {
        // Show user message immediately
        displayMessage(message, 'user');
        userInput.value = '';
        
        const payload = {
            message: message
        };
        
        if (window.lastDetectedEmotion) {
            payload.detected_emotion = window.lastDetectedEmotion;
            window.lastDetectedEmotion = null;
        }
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            if (!data.error) {
                displayMessage(data.reply, 'bot');
            }
        } catch (error) {
            console.error('Chat error:', error);
            displayMessage("Sorry, there was an error sending your message.", 'bot');
        }
    }
};
