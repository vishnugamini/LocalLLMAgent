// static/js/app.js

$(document).ready(function(){
    var socket = io();

    // Handle Send Button Click
    $('#send-btn').click(function(){
        sendPrompt();
    });

    // Handle Enter Key Press in Input
    $('#prompt').keypress(function(e){
        if(e.which == 13){
            sendPrompt();
            return false; // Prevent default form submission
        }
    });

    // On Connection
    socket.on('connect', function(){
        console.log('Connected to server');
    });

    // Handle Agent Responses
    socket.on('agent_response', function(data){
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
                messageTypeClass = 'agent-message';
                break;
            case "search_message":
                messageTypeClass = 'agent-message';
                break;
            case "picture_message":
                messageTypeClass = 'agent-message';
                break;
            case "child_agent_message":
                messageTypeClass = 'agent-message';
                break;
            case "refresh":
                messageTypeClass = 'agent-message';
                message = `<i class="bi bi-arrow-clockwise"></i> ${message}`;
                break;
            default:
                messageTypeClass = 'agent-message';
        }

        let html = `
            <div class="message ${messageTypeClass}">
                <span>${message}</span>
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

        // Display user message
        let html = `
            <div class="message user-message">
                <span>${prompt}</span>
            </div>
        `;
        $('#chat-window').append(html);
        scrollChatToBottom();
        $('#prompt').val('');
        
        // Emit prompt to server
        socket.emit('user_prompt', {'prompt': prompt});
    }

    /**
     * Function to Scroll Chat to Bottom
     */
    function scrollChatToBottom(){
        $('#chat-window').scrollTop($('#chat-window')[0].scrollHeight);
    }
});
