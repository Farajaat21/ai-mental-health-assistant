function displayMessage(message, sender) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function fetchQuote(userMessage) {
    console.log('Fetching quote for message:', userMessage);
    fetch('/quote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Received quote response:', data);
        const quoteContainer = document.getElementById('quote');
        quoteContainer.innerHTML = `<p class="quote-text">${data.quote}</p>`;
    })
    .catch(error => console.error('Error fetching quote:', error));
}

function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    // Signal that chat has started
    if (window.startedChat) {
        window.startedChat();
    }

    console.log('Sending message:', userInput);
    displayMessage(userInput, 'user');

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userInput }),
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then((data) => {
        console.log('Received chat response:', data);
        if (data.error) {
            displayMessage("Sorry, I encountered an error. Please try again.", 'bot');
        } else {
            displayMessage(data.reply, 'bot');
            fetchQuote(userInput); 
        }
    })
    .catch((error) => {
        console.error("Error sending message:", error);
        displayMessage("Sorry, I encountered an error. Please try again.", 'bot');
    });

    document.getElementById("user-input").value = "";
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});