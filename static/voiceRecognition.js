let isVoiceActive = false;
let mediaRecorder;
let audioChunks = [];
const chatContainer = document.getElementById("chat-container");
const micButton = document.getElementById("microphone");

// Replace the existing speakText function with this new version
async function speakText(text) {
    try {
        const response = await fetch("/speak", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.onplay = () => {
            console.log("AI speaking...");
            micButton.style.backgroundColor = "#4CAF50";
        };

        audio.onended = () => {
            console.log("AI finished speaking");
            URL.revokeObjectURL(audioUrl);
            if (isVoiceActive) {
                micButton.style.backgroundColor = "#ff4d4d";
                startContinuousRecording();
            } else {
                micButton.style.backgroundColor = "";
            }
        };

        await audio.play();

    } catch (error) {
        console.error("Error playing audio:", error);
        // Fallback to browser's speech synthesis if ElevenLabs fails
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
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
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstart = () => {
            // Pulse the microphone button to show active listening
            micButton.style.animation = "pulse 1.5s infinite";
        };

        mediaRecorder.onstop = async () => {
            micButton.style.animation = "none";
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            const transcript = await sendAudioForTranscription(audioBlob);
            if (transcript) {
                displayDebugText(`Recognized: ${transcript}`);
                try {
                    const response = await fetch("/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ message: transcript }),
                    });
                    const data = await response.json();
                    if (data.reply) {
                        speakText(data.reply);
                        // Wait for AI to finish speaking before listening again
                        waitForSpeechToFinish(() => {
                            if (isVoiceActive) {
                                startContinuousRecording();
                            }
                        });
                    }
                } catch (err) {
                    console.error("Chat error:", err);
                    displayDebugText("Error processing chat response");
                }
            } else {
                // If no transcript, restart recording immediately
                if (isVoiceActive) {
                    startContinuousRecording();
                }
            }
        };

        mediaRecorder.start();
        // Stop recording after 5 seconds
        setTimeout(() => {
            if (mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
            }
        }, 5000);
    } catch (error) {
        console.error("Error in startContinuousRecording:", error);
        displayDebugText("Error accessing microphone");
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

// Update toggleVoice to be more responsive
function toggleVoice() {
    const micIcon = micButton.querySelector('svg path');
    
    if (isVoiceActive) {
        isVoiceActive = false;
        micButton.style.backgroundColor = "";
        micIcon.setAttribute('fill', '#000000');
        displayDebugText("Voice recognition turned off");
        window.speechSynthesis.cancel();
    } else {
        isVoiceActive = true;
        micButton.style.backgroundColor = "#ff4d4d";
        micIcon.setAttribute('fill', '#ff4d4d');
        
        // Test speech synthesis immediately
        speakText("Hello! I'm your AI companion. When I finish speaking, you can start talking.");
        displayDebugText("Starting voice interaction...");
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