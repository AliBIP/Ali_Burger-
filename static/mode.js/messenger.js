document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const userSearch = document.getElementById('user-search');
    const searchBtn = document.getElementById('search-btn');
    const conversationsEl = document.getElementById('conversations');
    const messagesEl = document.getElementById('messages');
    const messageText = document.getElementById('message-text');
    const sendBtn = document.getElementById('send-btn');
    const giftBtn = document.getElementById('gift-btn');
    const giftModal = document.getElementById('gift-modal');
    const closeModal = document.querySelector('.close-modal');
    const giftOptions = document.querySelectorAll('.gift-option');
    
    let currentConversationId = null;
    
    // Load conversations
    function loadConversations() {
        fetch('/api/conversations')
            .then(response => response.json())
            .then(conversations => {
                conversationsEl.innerHTML = '';
                conversations.forEach(conv => {
                    const convEl = document.createElement('div');
                    convEl.className = 'conversation';
                    convEl.dataset.conversationId = conv.id;
                    convEl.innerHTML = `
                        <img src="${conv.other_user.avatar_url || '/static/images/default-avatar.png'}" 
                             class="conversation-avatar" alt="${conv.other_user.username}">
                        <div>
                            <h4>${conv.other_user.username}</h4>
                            <p>${conv.last_message ? conv.last_message.content.substring(0, 30) : 'No messages yet'}</p>
                        </div>
                        ${conv.unread_count > 0 ? `<span class="unread-count">${conv.unread_count}</span>` : ''}
                    `;
                    convEl.addEventListener('click', () => loadMessages(conv.id, conv.other_user));
                    conversationsEl.appendChild(convEl);
                });
            });
    }
    
    // Load messages for a conversation
    function loadMessages(conversationId, otherUser = null) {
        currentConversationId = conversationId;
        
        fetch(`/api/messages/${conversationId}`)
            .then(response => response.json())
            .then(messages => {
                messagesEl.innerHTML = '';
                
                if (otherUser) {
                    document.getElementById('current-chat').textContent = `Chat with ${otherUser.username}`;
                }
                
                messages.forEach(msg => {
                    const messageEl = document.createElement('div');
                    messageEl.className = `message ${msg.sender_id === current_user.id ? 'sent' : 'received'}`;
                    
                    if (msg.is_gift) {
                        messageEl.innerHTML = `
                            <p>Sent a gift</p>
                            <img src="/static/images/${msg.gift_id}.jpg" alt="Gift" class="gift-image">
                        `;
                    } else {
                        messageEl.textContent = msg.content;
                    }
                    
                    messagesEl.appendChild(messageEl);
                });
                
                // Scroll to bottom
                messagesEl.scrollTop = messagesEl.scrollHeight;
            });
    }
    
    // Send message
    function sendMessage() {
        const content = messageText.value.trim();
        if (!content || !currentConversationId) return;
        
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                content: content
            })
        })
        .then(response => response.json())
        .then(() => {
            messageText.value = '';
            loadMessages(currentConversationId);
        });
    }
    
    // Search users
    function searchUsers() {
        const query = userSearch.value.trim();
        if (!query) return;
        
        fetch(`/api/search_users?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(users => {
                conversationsEl.innerHTML = '';
                users.forEach(user => {
                    const userEl = document.createElement('div');
                    userEl.className = 'conversation';
                    userEl.innerHTML = `
                        <img src="${user.avatar_url || '/static/images/default-avatar.png'}" 
                             class="conversation-avatar" alt="${user.username}">
                        <h4>${user.username}</h4>
                    `;
                    userEl.addEventListener('click', () => startConversation(user.id, user.username));
                    conversationsEl.appendChild(userEl);
                });
            });
    }
    
    // Start new conversation
    function startConversation(userId, username) {
        fetch(`/api/start_conversation/${userId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            loadMessages(data.conversation_id, {id: userId, username: username});
            loadConversations();
        });
    }
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    messageText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    searchBtn.addEventListener('click', searchUsers);
    userSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchUsers();
    });
    
    giftBtn.addEventListener('click', () => {
        giftModal.style.display = 'block';
    });
    
    closeModal.addEventListener('click', () => {
        giftModal.style.display = 'none';
    });
    
    giftOptions.forEach(option => {
        option.addEventListener('click', () => {
            const giftId = option.dataset.giftId;
            fetch('/api/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: currentConversationId,
                    content: 'Sent a gift',
                    is_gift: true,
                    gift_id: giftId
                })
            })
            .then(response => response.json())
            .then(() => {
                giftModal.style.display = 'none';
                loadMessages(currentConversationId);
            });
        });
    });
    
    // Initial load
    loadConversations();
    
    // Poll for new messages every 5 seconds
    setInterval(() => {
        if (currentConversationId) {
            loadMessages(currentConversationId);
        }
    }, 5000);
});