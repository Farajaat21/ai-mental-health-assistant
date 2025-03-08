document.addEventListener('DOMContentLoaded', function () {
    const quoteContainer = document.getElementById('quote');
    const nextQuoteButton = document.getElementById('next-quote-button');

    const quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "The best way to predict the future is to invent it. - Alan Kay",
        "Life is 10% what happens to us and 90% how we react to it. - Charles R. Swindoll",
        "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
        "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt"
    ];

    let currentQuoteIndex = 0;

    function displayNextQuote() {
        currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length;
        quoteContainer.textContent = quotes[currentQuoteIndex];
    }

    nextQuoteButton.addEventListener('click', displayNextQuote);

    displayNextQuote();
});