// static/js/main.js
const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const recommendationsSummary = document.getElementById('recommendations-summary');
const cardList = document.getElementById('card-list');

let sessionId = localStorage.getItem('creditCardAdvisorSessionId');
if (!sessionId) {
    sessionId = 'user_' + Date.now();
    localStorage.setItem('creditCardAdvisorSessionId', sessionId);
}

function appendMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.textContent = message;
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll to bottom
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (message === '') return;

    appendMessage('user', message);
    userInput.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message, session_id: sessionId }),
        });
        const data = await response.json();
        appendMessage('assistant', data.response);

        if (data.recommendations && data.recommendations.length > 0) {
            displayRecommendations(data.recommendations);
        } else {
            recommendationsSummary.style.display = 'none'; // Hide if no recommendations
        }

    } catch (error) {
        console.error('Error sending message:', error);
        appendMessage('assistant', 'Sorry, I am having trouble connecting. Please try again.');
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function displayRecommendations(cards) {
    chatWindow.style.display = 'none'; // Hide chat 
    document.querySelector('.input-area').style.display = 'none'; // Hide input area 
    recommendationsSummary.style.display = 'block'; // Show summary 
    cardList.innerHTML = ''; // Clear previous recommendations

    cards.forEach(card => {
        const cardItem = document.createElement('div');
        cardItem.classList.add('card-item');
        cardItem.innerHTML = `
            <img src="${card.image_url}" alt="${card.card_name}">
            <h3>${card.card_name}</h3>
            <p class="reasons">${card.key_reasons}</p>
            <p class="reward-sim">${card.reward_simulation}</p>
            <a href="${card.affiliate_link}" target="_blank">Apply Now</a>
        `;
        cardList.appendChild(cardItem);
    });
}

function restartFlow() {
    localStorage.removeItem('creditCardAdvisorSessionId'); // Clear session
    window.location.reload(); // Reload the page to restart the conversation 
}