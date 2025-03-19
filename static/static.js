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
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput }),
            credentials: 'same-origin'
        });

        const data = await response.json();
        
        if (data.error || !response.ok) {
            throw new Error(data.reply || 'Network error');
        }

        let quotePart = null;
        let responsePart = data.reply;

        if (data.reply.includes("QUOTE:") && data.reply.includes("RESPONSE:")) {
            const parts = data.reply.split("RESPONSE:");
            quotePart = parts[0].replace("QUOTE:", "").trim();
            responsePart = parts[1].trim();
            // Create a single div with the quote and response separated by extra space
            const quoteDiv = document.createElement('div');
            quoteDiv.classList.add('message', 'bot-message', 'quote-message');
            quoteDiv.innerHTML = `<blockquote>${quotePart}</blockquote><p>&nbsp;&nbsp;${responsePart}</p>`;
            document.getElementById('chat-container').appendChild(quoteDiv);
        } else {
            displayMessage(responsePart, 'bot');
        }

        if (data.emotion && emotionEmojis[data.emotion]) {
            updateMoodEmoji(data.emotion);
        }

    } catch (error) {
        console.error("Error:", error);
        displayMessage("I apologize, but I'm having trouble responding right now. Could you please try again?", 'bot');
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

// Removed voice recognition functions (toggleMic, startRecording, openCamera)
// Voice functionality now resides in voiceRecognition.js

