document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const conversationList = document.getElementById('conversation-list');
    let activeChatId = null;
    let lastMessageTimestamp = null; // Keep track of the latest message timestamp
    let socket;

    conversationList.addEventListener('click', function(event) {
        const target = event.target.closest('.conversation');
        if (target) {
            document.querySelectorAll('.conversation').forEach(conversation => {
                conversation.classList.remove('active');
            });
            target.classList.add('active');
            
            activeChatId = target.getAttribute('data-chat-id');
            lastMessageTimestamp = null; // Reset the timestamp when switching chats
            loadChat(activeChatId);
        }
    });

    searchInput.addEventListener('input', function() {
        const filter = searchInput.value.toLowerCase();
        const conversations = conversationList.getElementsByClassName('conversation');
        
        Array.from(conversations).forEach(function(conversation) {
            const username = conversation.querySelector('.username').innerText.toLowerCase();
            if (username.includes(filter)) {
                conversation.style.display = '';
            } else {
                conversation.style.display = 'none';
            }
        });
    });

    function loadChat(chatId) {
        fetch(`/chat/${chatId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const chatHistory = document.getElementById('chat-history');
            const profilePic = document.getElementById('profile-pic');
            const chatUsername = document.getElementById('chat-username');

            // Update chat header
            profilePic.src = data.profile.avatar_url;
            chatUsername.textContent = data.profile.username;

            // Update chat history
            chatHistory.innerHTML = '';
            data.messages.forEach(message => {
                addMessageToChatHistory(chatHistory, message, data.current_user);
            });

            // Update last message timestamp
            if (data.messages.length > 0) {
                lastMessageTimestamp = data.messages[data.messages.length - 1].timestamp;
            }

            setupWebSocket(chatId);
        })
        .catch(error => {
            console.error('Error loading chat:', error);
        });
    }

    function addMessageToChatHistory(chatHistory, message, currentUser) {
        // Check if message already exists
        const existingMessage = chatHistory.querySelector(`[data-timestamp="${message.timestamp}"]`);
        if (existingMessage) return;
    
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', message.sender === currentUser ? 'my-message' : 'other-message');
        messageElement.setAttribute('data-timestamp', message.timestamp);
    
        let fileContent = '';
	if (message.file && message.file.length > 0) {
            message.file.forEach(file => {
                const fileType = file.is_image ? 'image' : 'file';
                if (fileType === 'image') {
                    fileContent = `<img src="${file.url}" alt="Image preview" style="max-width: 200px; max-height: 200px; display: block; margin-top: 10px;">`;
                } else {
                    fileContent = `<a href="${file.url}" download>Download</a>`;
                }
            });
        }
    
        messageElement.innerHTML = `
            <div class="message-data ${message.sender === currentUser ? 'text-right' : ''}">
                <span class="message-data-time">${message.timestamp}</span>
            </div>
            <div class="message-text">
                ${message.text}
                ${fileContent}
            </div>
        `;
        chatHistory.appendChild(messageElement);
    }

    function checkForNewMessages() {
        if (activeChatId && lastMessageTimestamp) {
            fetch(`/chat/${activeChatId}/new_messages/?since=${lastMessageTimestamp}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.messages.length > 0) {
                    const chatHistory = document.getElementById('chat-history');
                    data.messages.forEach(message => {
                        addMessageToChatHistory(chatHistory, message, data.current_user);
                    });

                    // Update last message timestamp
                    lastMessageTimestamp = data.messages[data.messages.length - 1].timestamp;

                    // Scroll to the bottom of the chat history
                    // chatHistory.scrollTop = chatHistory.scrollHeight;
                }
            })
            .catch(error => {
                console.error('Error checking for new messages:', error);
            });
        }
    }

    // Poll for new messages every 5 seconds
    setInterval(checkForNewMessages, 1000);

    // Handle form submission
    const chatForm = document.getElementById('chat-form');
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const activeConversation = document.querySelector('.conversation.active');
        if (!activeConversation) {
            console.error('No active conversation found.');
            return;
        }
        const chatId = activeConversation.getAttribute('data-chat-id');
        const textInput = document.getElementById('message-input');

        if (!textInput) {
            console.error('Input element not found.');
            return;
        }

        const textValue = textInput.value.trim();

        if (!textValue) {
            alert('Message cannot be empty.');
            return;
        }

        const formData = new FormData(chatForm);
        formData.set('text', textValue); // Ensure the trimmed value is set

        fetch(`/chat/${chatId}/send_message/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                loadChat(chatId);
                chatForm.reset();
            } else {
                alert('Error sending message');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
        });
    });

    

    function setupWebSocket(chatId) {
        if (socket) {
            socket.close();
      }
    
        const websocketUrl = `wss://${window.location.host}/ws/chat/${chatId}/`;
        console.log(`Attempting to connect to WebSocket at ${websocketUrl}`);
    
        socket = new WebSocket(websocketUrl);
    
        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
    
            if (data.type === 'user_status') {
               updateUserStatus(data.user_id, data.status, data.timestamp);
            }
        };
    
        socket.onopen = function(e) {
            console.log('WebSocket connection opened');
        };
    
        socket.onclose = function(e) {
            console.log('WebSocket connection closed');
        };
    
        socket.onerror = function(e) {
            console.error('WebSocket error observed:', e);
        };
    }
    
    function updateUserStatus(userId, status, timestamp) {
        console.log(`Updating status for user ID: ${userId}, status: ${status}, timestamp: ${timestamp}`);
        const onlineStatusElement = document.querySelector(`.status.online-status[data-user-id="${userId}"]`);
        const offlineStatusElement = document.querySelector(`.status.offline-status[data-user-id="${userId}"]`);
    
        if (!onlineStatusElement || !offlineStatusElement) {
            console.error(`Status elements for user ID ${userId} not found.`);
            return;
        }
    
        if (status === 'online') {
            onlineStatusElement.style.display = 'block';
            offlineStatusElement.style.display = 'none';
        } else if (status === 'offline') {
            onlineStatusElement.style.display = 'none';
            offlineStatusElement.style.display = 'block';
            offlineStatusElement.innerText = `Last seen at ${timestamp}`;
        } else if (status === 'typing') {
            onlineStatusElement.innerText = 'Typing...';
        } else if (status === 'stop_typing') {
            onlineStatusElement.innerText = 'Online';
        }
        const messageInput = document.getElementById('message-input');
    messageInput.addEventListener('keydown', () => {
        if (socket) {
            socket.send(JSON.stringify({ 'type': 'typing' }));
        }
    });

    messageInput.addEventListener('keyup', () => {
        if (socket) {
            socket.send(JSON.stringify({ 'type': 'stop_typing' }));
        }
    });
    }
})




