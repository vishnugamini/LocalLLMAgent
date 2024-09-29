

$(document).ready(function(){
    var socket = io();

    
    $('#send-btn').click(function(){
        sendPrompt();
    });

    
    $('#prompt').keypress(function(e){
        if(e.which == 13){
            sendPrompt();
            return false; 
        }
    });

    
    socket.on('connect', function(){
        console.log('Connected to server');
    });

-    
    socket.on('agent_response', function(data){
        removeLoadingSpinner(); 

        if(data.type === "loading_message"){
            displayLoadingMessage(data.content);
        }
        else if(data.type === "error"){
            displayErrorMessage(data.content);
        }
        else {
            displayAgentMessage(data.content, data.type);
        }
        scrollChatToBottom();
    });


    /**
     * Displays a loading message with a spinner.
     * @param {string} message - The loading message content.
     */
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
    

    /**
     * Displays an error message.
     * @param {string} message - The error message content.
     */
    function displayErrorMessage(message){
        let html = `
            <div class="message error-message">
                <i class="bi bi-exclamation-triangle-fill"></i> ${message}
            </div>
        `;
        $('#chat-window').append(html);
    }

    /**
     * Displays agent messages.
     * @param {string} message - The agent message content.
     * @param {string} type - The type of agent message.
     */
    function displayAgentMessage(message, type){
        let messageTypeClass = '';

        switch(type){
            case "user_message":
                messageTypeClass = 'user-message';
                break;
            case "compiler_message":
            case "search_message":
            case "picture_message":
            case "child_agent_message":
            case "refresh":
                messageTypeClass = 'agent-message';
                break;
            default:
                messageTypeClass = 'agent-message';
        }

        
        let isReadme = type === 'readme_message';  
        let htmlMessage = isReadme ? marked.parse(message) : `<span>${message}</span>`;

        let html = `
            <div class="message ${messageTypeClass}">
                ${htmlMessage}
            </div>
        `;
        $('#chat-window').append(html);
    }

    /**
     * Function to Send Prompt
     */
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
        
        
        socket.emit('user_prompt', {'prompt': prompt});
    }

    /**
     * Function to Scroll Chat to Bottom
     */
    function scrollChatToBottom(){
        $('#chat-window').scrollTop($('#chat-window')[0].scrollHeight);
    }
    /**
     * Removes the loading message.
     */
    function removeLoadingMessage(){
        $('.loading-message').remove();
    }
    /**
     * Removes the spinner from the loading message.
     */
    function removeLoadingSpinner(){
        $('.loading-message .spinner-border').remove(); 
    }


});
