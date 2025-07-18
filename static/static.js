function displayMessage(message, sender) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    if (sender === 'bot') {
        // Find quote between quotation marks with author - improved regex to be more accurate
        const quoteRegex = /"([^"]+)"\s*-\s*([^"\n.]+)/;
        const match = message.match(quoteRegex);
        
        if (match) {
            const [fullQuote, quoteText, author] = match;
            const remainingText = message.replace(fullQuote, '').trim();
            
            // Create quote element with proper styling
            const quoteElement = document.createElement('blockquote');
            quoteElement.innerHTML = `"${quoteText}"<br><span class="quote-author">- ${author}</span>`;
            messageDiv.appendChild(quoteElement);
            
            // Format remaining text with paragraphs
            if (remainingText) {
                const paragraphs = remainingText.split('\n\n');
                paragraphs.forEach(paragraph => {
                    if (paragraph.trim()) {
                        const textElement = document.createElement('p');
                        textElement.textContent = paragraph.trim();
                        messageDiv.appendChild(textElement);
                    }
                });
            }
        } else {
            // Fall back to simple text display if no quote is found
            const paragraphs = message.split('\n\n');
            paragraphs.forEach(paragraph => {
                if (paragraph.trim()) {
                    const textElement = document.createElement('p');
                    textElement.textContent = paragraph.trim();
                    messageDiv.appendChild(textElement);
                }
            });
        }
    } else {
        messageDiv.textContent = message;
    }
    
    // Add animation
    gsap.from(messageDiv, {
        opacity: 0,
        y: 20,
        duration: 0.3,
        ease: "back.out"
    });
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

const emotionEmojis = {
    // Standard emotions
    "neutral": "😊",
    "Neutral": "😊",
    "casual": "👋",
    "Casual": "👋",
    
    // Sadness related
    "general sadness": "😔",
    "General sadness": "😔",
    "deep sadness": "😞",
    "Deep sadness": "😞",
    "sadness": "😔",
    "Sadness": "😔",
    
    // Anxiety related
    "anxiety": "😰",
    "Anxiety": "😰",
    "social anxiety": "😨",
    "Social anxiety": "😨",
    
    // Stress related
    "stress": "😫",
    "Stress": "😫",
    "academic stress": "📚",
    "Academic stress": "📚",
    
    // Negative emotions
    "frustration": "😤",
    "Frustration": "😤",
    "anger": "😠",
    "Anger": "😠",
    "fear": "😨",
    "Fear": "😨",
    "worry": "😟",
    "Worry": "😟",
    
    // Emotional states
    "loneliness": "🥺",
    "Loneliness": "🥺",
    "helplessness": "💔",
    "Helplessness": "💔",
    "pain": "😣",
    "Pain": "😣",
    
    // Loss related
    "grief": "😢",
    "Grief": "😢",
    "loss": "💔",
    "Loss": "💔",
    "pet loss": "🐾",
    "Pet loss": "🐾",
    
    // Other emotional states
    "overwhelmed": "😩",
    "Overwhelmed": "😩",
    "trauma": "😰",
    "Trauma": "😰",
    "depression": "😞",
    "Depression": "😞",
    
    // Concerns
    "family concern": "👨‍👩‍👧‍👦",
    "Family concern": "👨‍👩‍👧‍👦",
    "identity concern": "🤔",
    "Identity concern": "🤔",
    "mental health concern": "🧠",
    "Mental Health concern": "🧠",
    
    // Positive emotions
    "growth": "🌱",
    "Growth": "🌱",
    
    // Self-perception
    "inadequacy": "📉",
    "Inadequacy": "📉",
    
    // Complex emotions
    "mixed emotions": "😕",
    "Mixed emotions": "😕"
};

// Helper function to display emotion info in the console
function debugEmotion(emotion) {
    console.group("Emotion Debug Info");
    console.log("Raw emotion value:", emotion);
    console.log("Type:", typeof emotion);
    console.log("In emotionEmojis?", emotion in emotionEmojis);
    console.log("Lowercase in emotionEmojis?", emotion.toLowerCase() in emotionEmojis);
    console.log("Available emotions:", Object.keys(emotionEmojis).join(", "));
    console.groupEnd();
}

function updateMoodEmoji(emotion) {
    const emojiElement = document.getElementById('mood-emoji');
    console.log("Updating emoji for emotion:", emotion); // Debug log
    
    if (!emotion || emotion === "Neutral" || emotion === "null" || emotion === null) {
        console.log("Using default emoji for neutral/null emotion");
        emojiElement.textContent = "😊";
        return;
    }
    
    // Debug emotion information
    debugEmotion(emotion);
    
    // Try to find the emoji in the map (case insensitive)
    let newEmoji = "😊"; // Default
    for (const [key, value] of Object.entries(emotionEmojis)) {
        if (key.toLowerCase() === emotion.toLowerCase()) {
            newEmoji = value;
            console.log(`Found emoji match: ${key} -> ${value}`);
            break;
        }
    }
    
    console.log("Selected emoji:", newEmoji, "for emotion:", emotion);
    
    // Add a data attribute to track the current emotion for styling
    emojiElement.dataset.emotion = emotion;
    
    // FASTER ANIMATION - reduced from 0.3s to 0.15s
    gsap.to(emojiElement, {
        opacity: 0,
        y: -10, // Reduced movement for faster perception
        duration: 0.15, // Half the previous duration
        onComplete: () => {
            emojiElement.textContent = newEmoji;
            gsap.to(emojiElement, {
                opacity: 1,
                y: 0,
                duration: 0.15, // Half the previous duration
                ease: "power1.out" // Faster ease
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
    const userInput = document.getElementById("user-input");
    const message = userInput.value.trim();
    
    if (message === "") return;
    
    // Display user message
    displayMessage(message, 'user');
    userInput.value = "";
    adjustInputHeight();
    
    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('bot-message', 'typing-indicator');
    typingDiv.textContent = "...";
    document.getElementById('chat-container').appendChild(typingDiv);
    
    // PRE-EMPTIVE EMOTION DETECTION
    // Try to predict emotion before server responds for faster UI update
    const predictedEmotion = predictEmotion(message);
    if (predictedEmotion) {
        console.log("Pre-emptively updating emoji based on message content:", predictedEmotion);
        updateMoodEmoji(predictedEmotion);
    }
    
    let retries = 2;
    while (retries > 0) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout
            
            console.log("Sending chat request to server...");
            const response = await fetch("/chat", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-Retry-Count": `${3 - retries}`
                },
                body: JSON.stringify({ message: message }),
                credentials: 'same-origin',
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            typingDiv.remove();

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Raw server response:", data);
            
            if (data.error) {
                throw new Error(data.reply || 'Unknown error');
            }

            // Display the message
            displayMessage(data.reply, 'bot');
            
            // Handle emotion update
            if (data.emotion) {
                console.log("Server detected emotion:", data.emotion);
                
                // Update with no delay
                updateMoodEmoji(data.emotion);
                
                // Store the emotion for future reference
                window.lastDetectedEmotion = data.emotion;
            } else {
                console.log("No emotion data in response");
            }
            
            return;
            
        } catch (error) {
            console.error(`Attempt ${3 - retries} failed:`, error);
            retries--;
            
            if (retries === 0) {
                typingDiv.remove();
                displayMessage("I'm having trouble responding right now. Please try again in a moment.", 'bot');
            }
            
            // Wait before retry
            if (retries > 0) {
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }
    }
}

// Simple client-side emotion prediction for faster UI updates
function predictEmotion(message) {
    message = message.toLowerCase();
    
    // Common emotion patterns
    const patterns = [
        { regex: /(sad|depressed|unhappy|crying|tear|down|blue)/i, emotion: "General sadness" },
        { regex: /(anxiety|anxious|nervous|worried|panic|stress)/i, emotion: "Anxiety" },
        { regex: /(school|class|exam|test|grade|study|college|homework|assignment)/i, emotion: "Academic stress" },
        { regex: /(angry|mad|frustrated|annoyed|irritated|upset)/i, emotion: "Anger" },
        { regex: /(scared|afraid|terrified|fear|frightened)/i, emotion: "Fear" },
        { regex: /(lonely|alone|isolated|no friends|no one)/i, emotion: "Loneliness" },
        { regex: /(grief|death|died|passed away|loss|lost)/i, emotion: "Grief" },
        { regex: /(dog|cat|pet|animal) (died|passed|gone)/i, emotion: "Pet loss" },
        { regex: /(family|parent|mother|father|mom|dad|sister|brother)/i, emotion: "Family concern" },
        { regex: /(overwhelmed|too much|can't handle|drowning)/i, emotion: "Overwhelmed" },
        { regex: /(happy|glad|joy|excited|pleased|delighted)/i, emotion: "Growth" }
    ];
    
    for (const pattern of patterns) {
        if (pattern.regex.test(message)) {
            return pattern.emotion;
        }
    }
    
    return null;
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent default form submission
        sendMessage();
    }
});

// Removed voice recognition functions (toggleMic, startRecording, openCamera)
// Voice functionality now resides in voiceRecognition.js
