function displayMessage(message, sender) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    messageDiv.textContent = message;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

const emotionEmojis = {
    "Neutral": "😊",
    "Sadness": "😔",
    "Depression": "😞",
    "Anxiety": "😰",
    "Stress": "😫",
    "Frustration": "😤",
    "Anger": "😠",
    "Fear": "😨",
    "Worry": "😟",
    "Loneliness": "🥺",
    "Hopelessness": "💔",
    "Pain": "😣",
    "Grief": "😢",
    "Overwhelmed": "😩",
    "Trauma": "😰"
};

function updateMoodEmoji(emotion) {
    const emojiElement = document.getElementById('mood-emoji');
    console.log("Updating emoji for emotion:", emotion); // Debug log
    
    if (!emotion || emotion === "Neutral") {
        emojiElement.textContent = "😊";
        return;
    }
    
    const newEmoji = emotionEmojis[emotion] || "😊";
    console.log("Selected emoji:", newEmoji); // Debug log
    
    gsap.to(emojiElement, {
        opacity: 0,
        y: -20,
        duration: 0.3,
        onComplete: () => {
            emojiElement.textContent = newEmoji;
            gsap.to(emojiElement, {
                opacity: 1,
                y: 0,
                duration: 0.3,
                ease: "back.out"
            });
        }
    });
}

function adjustInputHeight() {
    const input = document.getElementById("user-input");
    input.style.height = "auto";
    input.style.height = (input.scrollHeight) + "px";
}

document.getElementById("user-input").addEventListener("input", adjustInputHeight);

async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    displayMessage(userInput, 'user');
    
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: userInput }),
            credentials: 'same-origin'
        });

        const data = await response.json();
        console.log("Response data:", data); // Debug log

        if (data.error || !response.ok) {
            throw new Error(data.reply || 'Network error');
        }

        // For emotional content, show quote first then response
        if (data.emotion !== "Neutral" && data.quote) {
            console.log("Displaying quote for emotion:", data.emotion);
            
            // Show quote first
            setTimeout(() => {
                const quoteDiv = document.createElement('div');
                quoteDiv.classList.add('message', 'bot-message', 'quote-message');
                quoteDiv.innerHTML = `<blockquote>${data.quote}</blockquote>`;
                document.getElementById('chat-container').appendChild(quoteDiv);

                const chatContainer = document.getElementById('chat-container');
                chatContainer.scrollTop = chatContainer.scrollHeight;
                

                
                chatContainer.scrollTo({
                    top: chatContainer.scrollHeight,
                    behavior: 'smooth'
                });
                // Then show response with a slight delay
                setTimeout(() => {
                    displayMessage(data.reply, 'bot');
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                }, 500);
            }, 800);
        } else {
            // For casual messages, just show response
            displayMessage(data.reply, 'bot');
        }

        // Update mood emoji if valid emotion
        if (data.emotion && emotionEmojis[data.emotion]) {
            console.log("Updating emoji for emotion:", data.emotion);
            updateMoodEmoji(data.emotion);
        }
        
        // Update rotating quote
        if (data.default_quote) {
            document.getElementById('quote').innerHTML = `<p class="quote-text">${data.default_quote}</p>`;
        }

    } catch (error) {
        console.error("Error:", error);
        displayMessage("I'm here to help. Could you please share more about what you're feeling? Service unavalible", 'bot');
    }

    document.getElementById("user-input").value = "";
    adjustInputHeight();
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent default form submission
        sendMessage();
    }
});

function toggleMic() {
    const micOff = document.querySelector('.mic-off');
    const micOn = document.querySelector('.mic-on');
    micOff.classList.toggle('hidden');
    micOn.classList.toggle('hidden');
}

function toggleVideo() {
    const videoOff = document.querySelector('.video-off');
    const videoOn = document.querySelector('.video-on');
    videoOff.classList.toggle('hidden');
    videoOn.classList.toggle('hidden');
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('Microphone access granted');
        
        alert("Microphone activated! (Recording functionality coming soon)");
    } catch (err) {
        console.error('Error accessing microphone:', err);
        alert("Could not access microphone. Please check your permissions.");
    }
}

async function openCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        console.log('Camera access granted');
        alert("Camera activated! (Video functionality coming soon)");
    } catch (err) {
        console.error('Error accessing camera:', err);
        alert("Could not access camera. Please check your permissions or stite still not securied.");
    }
}

