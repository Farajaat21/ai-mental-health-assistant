let isVoiceActive = false;
let isIntroPlaying = false;
let activeUtterance = null;
let mediaRecorder;
let audioChunks = [];
const chatContainer = document.getElementById("chat-container");
const micButton = document.getElementById("microphone");

// Add this function to select the best female voice
async function getBestFemaleVoice() {
    return new Promise((resolve) => {
        // Wait for voices to be loaded
        window.speechSynthesis.onvoiceschanged = () => {
            const voices = window.speechSynthesis.getVoices();
            // Look for high-quality female voices in preferred order
            const preferredVoices = [
                "Microsoft Zira",    // Windows English female
                "Google UK English Female",
                "Samantha",         // MacOS female voice
                "Victoria",         // MacOS female voice
                "Karen",            // Australian female
                "Moira",            // Irish female
                "Samantha"          // Generic female
            ];
            
            // Try to find a preferred voice
            let selectedVoice = null;
            for (let preferred of preferredVoices) {
                selectedVoice = voices.find(voice => voice.name.includes(preferred));
                if (selectedVoice) break;
            }
            
            // If no preferred voice found, try to find any female voice
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => voice.name.includes('female') || voice.name.includes('woman'));
            }
            
            // Fallback to first available voice if no female voice found
            resolve(selectedVoice || voices[0]);
        };
    });
}

// Add new visualization elements
function createVoiceUI() {
    const voiceUI = document.createElement('div');
    voiceUI.id = 'voice-ui';
    voiceUI.classList.add('voice-ui');
    voiceUI.innerHTML = `
        <div class="voice-visualizer">
            <div class="voice-status">
                <span class="status-text">Voice Mode Active</span>
                <div class="voice-instructions">
                    <p>I'm listening to you now. Please speak clearly after the beep.</p>
                    <p>To end voice mode, click the red "Stop Voice Mode" button below.</p>
                </div>
                <button class="stop-voice" onclick="deactivateVoiceMode()">
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                    Stop Voice Mode
                </button>
            </div>
            <div class="voice-waves">
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
            </div>
        </div>
    `;
    // Append voice UI to the document
    document.body.appendChild(voiceUI);
    return voiceUI;
}

// More clear welcome message
const welcomeMessage = "Voice mode activated. I'm here to listen and support you. Please speak after the beep sound. When you're ready to end voice mode, just press the red 'Stop Voice Mode' button that appears below.";

// Add voice state tracking
let isCurrentlySpeaking = false;

// Add silence detection
let silenceTimeout;
const SILENCE_DURATION = 1500; // 1.5 seconds of silence before stopping

// Update toggleVoice function
function toggleVoice() {
    if (isVoiceActive) {
        deactivateVoiceMode();
        return;
    }

    // Prevent activation if speech is ongoing
    if (isCurrentlySpeaking || isIntroPlaying) {
        return;
    }

    // Only activate if completely inactive
    navigator.permissions.query({ name: 'microphone' })
        .then((permissionStatus) => {
            if (permissionStatus.state === 'granted') {
                activateVoiceMode();
            } else if (permissionStatus.state === 'prompt') {
                displayDebugText("Requesting microphone access...");
                activateVoiceMode();
            } else {
                throw new Error("Microphone access blocked");
            }
        })
        .catch(error => {
            console.error("Permission error:", error);
            displayDebugText(`Error: ${error.message}`);
            deactivateVoiceMode(); // Ensure cleanup if error
        });
}

async function speakText(text) {
    try {
        if (!isVoiceActive) return;

        // Cancel any ongoing speech first
        if (activeUtterance) {
            window.speechSynthesis.cancel();
            activeUtterance = null;
        }

        // Don't allow multiple intro messages
        if (text === welcomeMessage && isIntroPlaying) {
            return;
        }

        if (text === welcomeMessage) {
            isIntroPlaying = true;
        }

        isCurrentlySpeaking = true;
        const statusText = document.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = 'AI Speaking...';
        }

        // First try: ElevenLabs
        displayDebugText("Generating voice response...");
        const response = await fetch("/speak", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text: text })
        });

        // Check if we're still in voice mode
        if (!isVoiceActive) {
            isCurrentlySpeaking = false;
            return;
        }

        if (response.ok) {
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            return new Promise((resolve) => {
                audio.onplay = () => {
                    micButton.style.backgroundColor = "#4CAF50";
                };

                audio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                    isCurrentlySpeaking = false;
                    isIntroPlaying = false;
                    if (isVoiceActive) {
                        micButton.style.backgroundColor = "#ff4d4d";
                        if (statusText) {
                            statusText.textContent = 'Listening...';
                        }
                        startContinuousRecording();
                    } else {
                        micButton.style.backgroundColor = "";
                    }
                    resolve();
                };

                audio.play();
            });
        }

        // Second try: Google Cloud TTS (if implemented)
        // You could add another API call here to a different TTS service

        // Last resort: Browser's built-in speech synthesis with best available voice
        displayDebugText("Using system voice...");
        const utterance = new SpeechSynthesisUtterance(text);
        const voice = await getBestFemaleVoice();
        
        utterance.voice = voice;
        utterance.pitch = 1.0;
        utterance.rate = 0.9;
        utterance.volume = 1.0;
        
        // Add natural pauses
        text = text.replace(/\./g, '... ');
        text = text.replace(/,/g, '.. ');
        utterance.text = text;

        utterance.onend = () => {
            isCurrentlySpeaking = false;
            isIntroPlaying = false;
            activeUtterance = null;
            if (isVoiceActive) {
                startContinuousRecording();
            }
        };

        activeUtterance = utterance;
        window.speechSynthesis.speak(utterance);

    } catch (error) {
        isCurrentlySpeaking = false;
        isIntroPlaying = false;
        console.error("Voice generation error:", error);
        displayDebugText("Voice generation failed");
    }
}

// Make debug text more visible and persist longer
function displayDebugText(text) {
    const debugDiv = document.createElement("div");
    debugDiv.classList.add("debug-message");
    debugDiv.innerHTML = `🎤 <strong>Voice Input:</strong> ${text}`;
    debugDiv.style.cssText = `
        background-color: rgba(0, 0, 0, 0.1);
        color: #333;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        font-style: italic;
        border-left: 3px solid #ff4d4d;
    `;
    chatContainer.appendChild(debugDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Remove after 5 seconds instead of 3
    setTimeout(() => {
        debugDiv.remove();
    }, 5000);
}

// Add this function to detect when AI finishes speaking
function waitForSpeechToFinish(callback) {
    const checkSpeaking = setInterval(() => {
        if (!window.speechSynthesis.speaking) {
            clearInterval(checkSpeaking);
            callback();
        }
    }, 100);
}

// Update the recording function to show active transcription
async function startContinuousRecording() {
    try {
        if (!isVoiceActive) return;

        // Check if we're on HTTPS
        if (window.location.protocol !== 'https:') {
            throw new Error("Microphone access requires HTTPS. Please use a secure connection.");
        }

        // Check if browser supports getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("Your browser doesn't support audio recording. Please try a modern browser like Chrome or Firefox.");
        }

        // Request permission explicitly
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            },
            video: false
        });

        // Create audio context for silence detection
        const audioContext = new AudioContext();
        const audioSource = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        audioSource.connect(analyser);

        // Reduced silence threshold and duration for better responsiveness
        const SILENCE_THRESHOLD = 5; // More sensitive
        const SILENCE_DURATION = 1000; // 1 second silence

        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstart = () => {
            updateVoiceUI(true);
            displayDebugText("Started listening...");
        };

        mediaRecorder.onstop = async () => {
            updateVoiceUI(false);
            
            if (audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                displayDebugText("Processing speech...");
                const transcript = await sendAudioForTranscription(audioBlob);
                
                if (transcript && transcript.trim()) {
                    displayDebugText("Transcribed: " + transcript);
                    await handleVoiceChat(transcript);
                } else {
                    displayDebugText("No speech detected, listening again...");
                    if (isVoiceActive && !isCurrentlySpeaking) {
                        startContinuousRecording();
                    }
                }
            }
            
            audioChunks = [];
        };

        // Start recording in shorter chunks
        if (isVoiceActive) {
            mediaRecorder.start();
            // Stop after 4 seconds to process
            setTimeout(() => {
                if (mediaRecorder && mediaRecorder.state === "recording") {
                    mediaRecorder.stop();
                }
            }, 4000);
        }

    } catch (error) {
        console.error("Microphone access error:", error);
        displayDebugText(`Error: ${error.message}`);
        deactivateVoiceMode();
    }
}

// Send audio blob to the backend /whisper endpoint for transcription.
async function sendAudioForTranscription(audioBlob) {
    try {
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.webm");

        const response = await fetch("/whisper", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        if (data.transcript) {
            return data.transcript;
        } else {
            console.error("Transcription error:", data.error);
            return "";
        }
    } catch (error) {
        console.error("Error sending audio:", error);
        return "";
    }
}

// Update activateVoiceMode function
async function activateVoiceMode() {
    try {
        // Make sure we're not already in voice mode
        if (isVoiceActive) return;
        
        isVoiceActive = true;
        
        // Create and display voice UI
        const voiceUI = createVoiceUI();
        document.body.appendChild(voiceUI);
        
        // Update microphone button to show it's active
        const micButton = document.getElementById('microphone');
        if (micButton) {
            micButton.classList.add('active');
            micButton.style.backgroundColor = "#4CAF50";
        }
        
        // Hide chat container content but keep it in the DOM
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            // Keep chat container visible but clear previous messages
            const previousMessages = Array.from(chatContainer.querySelectorAll('.message'));
            previousMessages.forEach(msg => {
                gsap.to(msg, {
                    opacity: 0,
                    y: -20,
                    duration: 0.3,
                    onComplete: () => msg.remove()
                });
            });
        }
        
        // Play welcome message
        await speakText(welcomeMessage);
        
        // Initialize audio recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                if (!isVoiceActive) return; // Don't process if we've deactivated
                
                // Create audio blob from chunks
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = []; // Reset for next recording
                
                // Update UI to show processing
                updateVoiceUI(false);
                
                // Send for transcription
                const transcript = await sendAudioForTranscription(audioBlob);
                
                if (transcript && transcript.trim()) {
                    // Display user message
                    displayMessage(transcript, 'user');
                    
                    // Process with chat endpoint
                    await handleVoiceChat(transcript);
                } else {
                    // If no speech detected, restart recording
                    if (isVoiceActive) {
                        startContinuousRecording();
                    }
                }
            };
            
            // Start recording
            startContinuousRecording();
            
        } catch (error) {
            console.error('Microphone access error:', error);
            displayMessage("I couldn't access your microphone. Please check your permissions and try again.", 'bot');
            deactivateVoiceMode();
        }
        
    } catch (error) {
        console.error('Voice activation error:', error);
        displayMessage("I'm having trouble with the voice mode. Please try again later.", 'bot');
        deactivateVoiceMode();
    }
}

// Add fallback for voice synthesis
async function playWelcomeMessage() {
    try {
        const welcomeText = "Hello! I'm your voice assistant. I'm ready to listen to you. Please speak now.";
        await speakText(welcomeText);
    } catch (error) {
        console.error('Welcome message error:', error);
        // Fallback to text display if speech fails
        displayMessage("Hello! I'm your voice assistant. I'm ready to listen to you. Please speak now.", 'bot');
    }
}

// Update deactivateVoiceMode function
function deactivateVoiceMode() {
    // Cancel any ongoing speech first
    if (activeUtterance) {
        window.speechSynthesis.cancel();
        activeUtterance = null;
    }
    isCurrentlySpeaking = false;
    isIntroPlaying = false;
    
    // Stop recording if active
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }

    // Stop all media tracks
    if (mediaRecorder && mediaRecorder.stream) {
        mediaRecorder.stream.getTracks().forEach(track => {
            track.stop();
            track.enabled = false;
        });
    }

    // Clear any pending timeouts
    if (silenceTimeout) {
        clearTimeout(silenceTimeout);
        silenceTimeout = null;
    }

    // Reset all states
    isVoiceActive = false;
    audioChunks = [];

    // Clean up UI
    const voiceUI = document.getElementById('voice-ui');
    if (voiceUI) {
        voiceUI.remove();
    }

    // Reset microphone button
    const micButton = document.getElementById('microphone');
    if (micButton) {
        micButton.style.backgroundColor = "";
        micButton.classList.remove('speaking', 'listening', 'active');
        const micIcon = micButton.querySelector('svg path');
        if (micIcon) {
            micIcon.setAttribute('fill', '#000000');
        }
    }

    // Restore chat container
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.style.display = 'flex';
        chatContainer.innerHTML = '';
        displayMessage("Voice mode deactivated", 'bot');
    }

    // Cancel any pending audio
    document.querySelectorAll('audio').forEach(audio => {
        audio.pause();
        audio.remove();
    });
}

// Update voice UI
function updateVoiceUI(isListening) {
    const statusText = document.querySelector('.status-text');
    const waveContainer = document.querySelector('.voice-waves');
    
    if (statusText) {
        statusText.textContent = isListening ? 'Listening...' : 'Processing...';
    }
    
    if (waveContainer) {
        waveContainer.classList.toggle('active', isListening);
    }
}

// Add CSS animation for the microphone pulse
const style = document.createElement('style');
style.textContent = `
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}`;
document.head.appendChild(style);

micButton.addEventListener("click", toggleVoice);

// Update handleVoiceChat to be more supportive
async function handleVoiceChat(transcript) {
    try {
        if (!isVoiceActive) return;

        // Display user's message first
        displayMessage(transcript, 'user');

        const response = await fetch("/voice-chat", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ message: transcript })
        });

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.reply);
        }

        // Display bot's response with proper formatting
        displayMessage(data.reply, 'bot');
        
        if (isVoiceActive) {
            await speakText(data.reply);
            if (isVoiceActive) {
                startContinuousRecording();
            }
        }
    } catch (error) {
        console.error("Voice chat error:", error);
        displayDebugText("Error: " + error.message);
    }
}

function displayMessage(message, type) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    
    // Add appropriate class based on message type
    if (type === 'user') {
        messageDiv.classList.add('user-message');
    } else if (type === 'bot') {
        messageDiv.classList.add('bot-message');
        
        // Check if message contains a quote
        if (message.includes('"')) {
            const parts = message.split('\n\n');
            if (parts.length > 1) {
                // Format quote differently
                const quoteDiv = document.createElement('blockquote');
                quoteDiv.textContent = parts[0];
                messageDiv.appendChild(quoteDiv);
                
                // Add remaining text
                const textDiv = document.createElement('p');
                textDiv.textContent = parts.slice(1).join('\n\n');
                messageDiv.appendChild(textDiv);
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return;
            }
        }
    }
    
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}