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
        removeLoadingSpinner(); 

        if(data.type === "loading_message"){
            displayLoadingMessage(data.content);
        }
        else if(data.type === "error"){
            displayErrorMessage(data.content);
        }
        else {
            // Process all messages through the marked parser
            displayAgentMessage(data.content);
        }
        scrollChatToBottom();
    });

    // Function to display a loading message
    function displayLoadingMessage(message){
        removeLoadingMessage(); 
        let html = `
            <div class="message loading-message">
                <span>${message}</span>
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        $('#chat-window').append(html);
    }
    
    // Function to display error message
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

    // Remove loading message
    function removeLoadingMessage(){
        $('.loading-message').remove();
    }

    // Remove spinner from loading message
    function removeLoadingSpinner(){
        $('.loading-message .spinner-border').remove(); 
    }
});
