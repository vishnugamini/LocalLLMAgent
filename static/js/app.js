$(document).ready(function(){
    var socket = io();

    // Send button click event
    $('#send-btn').click(function(){
        sendPrompt();
    });

    // Press Enter to send the prompt
    $('#prompt').keypress(function(e){
        if(e.which == 13){
            sendPrompt();
            return false; 
        }
    });

    // Socket connection success
    socket.on('connect', function(){
        console.log('Connected to server');
    });

    // Handling agent response
    socket.on('agent_response', function(data){
        if(data.type === "loading_message"){
            displayLoadingMessage(data.content, data.msg_id);
        }
        else if(data.type === "success_message"){
            updateLoadingMessage(data.msg_id, data.content);
        }
        else if(data.type === "error_message"){
            updateLoadingMessageWithError(data.msg_id, data.content);
        }
        else if(data.type === "error"){
            displayErrorMessage(data.content);
        }
        else {
            // Process all other messages through the marked parser
            displayAgentMessage(data.content);
        }
        scrollChatToBottom();
    });

    // Function to display a loading message with a unique ID
    function displayLoadingMessage(message, msg_id){
        let html = `
            <div class="message loading-message" id="msg-${msg_id}">
                <span>${message}</span>
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        $('#chat-window').append(html);
    }
    
    // Function to update the loading message with a success tick
    function updateLoadingMessage(msg_id, message){
        let messageElement = $(`#msg-${msg_id}`);
        if(messageElement.length){
            messageElement.removeClass('loading-message').addClass('success-message');
            messageElement.html(`
                <span>${message}</span>
                <i class="bi bi-check-circle-fill tick-icon"></i>
            `);
        }
    }

    // Function to update the loading message with an error indicator
    function updateLoadingMessageWithError(msg_id, message){
        let messageElement = $(`#msg-${msg_id}`);
        if(messageElement.length){
            messageElement.removeClass('loading-message').addClass('error-message');
            messageElement.html(`
                <span>${message}</span>
                <i class="bi bi-exclamation-triangle-fill"></i>
            `);
        }
    }

    // Function to display error message for general errors
    function displayErrorMessage(message){
        let html = `
            <div class="message error-message">
                <i class="bi bi-exclamation-triangle-fill"></i> ${message}
            </div>
        `;
        $('#chat-window').append(html);
    }

    // Function to display agent message (all messages processed as Markdown)
    function displayAgentMessage(message){
        // Parse the message using marked to convert it to HTML
        let html = `
            <div class="message agent-message">
                ${marked.parse(message)}
            </div>
        `;
        $('#chat-window').append(html);
    }

    // Send prompt to the server
    function sendPrompt(){
        let prompt = $('#prompt').val().trim();
        if(prompt === ""){
            return;
        }

        let html = `
            <div class="message user-message">
                <span>${prompt}</span>
            </div>
        `;
        $('#chat-window').append(html);
        scrollChatToBottom();
        $('#prompt').val('');
        
        // Send the prompt to the server
        socket.emit('user_prompt', {'prompt': prompt});
    }

    // Scroll chat to bottom
    function scrollChatToBottom(){
        $('#chat-window').scrollTop($('#chat-window')[0].scrollHeight);
    }
});
