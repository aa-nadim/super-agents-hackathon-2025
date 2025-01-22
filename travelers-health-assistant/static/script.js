document.addEventListener('DOMContentLoaded', function () {
    const botButton = document.getElementById('botButton');
    const modal = document.getElementById('botModal');
    const sendButton = document.getElementById('sendButton');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const chatMessages = document.getElementById('chatMessages');
    const locationInput = document.getElementById('location');

    // Toggle modal
    botButton.addEventListener('click', () => {
        modal.classList.toggle('active');
    });

    // Handle form submission
    sendButton.addEventListener('click', async () => {
        const location = locationInput.value.trim();
        if (!location) return;

        // Disable input and button while processing
        locationInput.disabled = true;
        sendButton.disabled = true;

        // Clear previous messages
        chatMessages.innerHTML = '';

        // Display user message
        appendMessage('You', location, 'user-message');

        // Show progress bar
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';

        try {
            // Start EventSource connection
            const eventSource = new EventSource(`/get_travel_advisory?location=${encodeURIComponent(location)}`);
            let completedTasks = 0;
            const totalTasks = 6; // Updated to include supervisor task

            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.error) {
                    appendMessage('Error', data.error, 'error-message');
                    eventSource.close();
                    return;
                }

                // Update progress bar
                completedTasks++;
                const progress = (completedTasks / totalTasks) * 100;
                progressBar.style.width = `${progress}%`;

                // Display agent message
                if (data.agent >= 'Travel Advisory Supervisor') {
                    appendMessage(data.agent, data.result, 'supervisor-message');
                } else {
                    appendMessage(data.agent, data.result, 'bot-message');
                }

                // Close connection when all tasks are complete
                if (completedTasks >= totalTasks) {
                    eventSource.close();
                    progressContainer.style.display = 'none';
                    
                    // Re-enable input and button
                    locationInput.disabled = false;
                    sendButton.disabled = false;
                }
            };

            eventSource.onerror = function(error) {
                console.error('EventSource failed:', error);
                appendMessage('Error', 'Connection lost. Please try again.', 'error-message');
                eventSource.close();
                progressContainer.style.display = 'none';
                
                // Re-enable input and button
                locationInput.disabled = false;
                sendButton.disabled = false;
            };
        } catch (error) {
            console.error('Failed to start EventSource:', error);
            appendMessage('Error', 'Failed to start processing. Please try again.', 'error-message');
            progressContainer.style.display = 'none';
            
            // Re-enable input and button
            locationInput.disabled = false;
            sendButton.disabled = false;
        }
    });

    // Helper function to append messages
    function appendMessage(sender, text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        
        const senderDiv = document.createElement('div');
        senderDiv.className = 'agent-name';
        senderDiv.textContent = sender;
        
        const textDiv = document.createElement('div');
        textDiv.textContent = text;
        
        messageDiv.appendChild(senderDiv);
        messageDiv.appendChild(textDiv);
        chatMessages.appendChild(messageDiv);
        
        // Auto-scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Allow pressing Enter to send
    locationInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendButton.click();
        }
    });
});