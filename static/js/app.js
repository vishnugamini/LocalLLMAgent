function escapeHtml(text) {
    if (!text) {
        return "";
    }
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
const promptTextarea = document.getElementById("prompt");

promptTextarea.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
});

$(document).ready(function () {
    var socket = io();
    $("#refresh-btn").click(function () {
        refresh();
    });

    $("#clear-btn").click(function () {
        clear();
    });

    $("#send-btn").click(function () {
        sendPrompt();
    });

    $("#end-btn").click(function () {
        endProcessing();
    });

    $("#prompt").keypress(function (e) {
        if (e.which == 13) {
            sendPrompt();
            return false;
        }
    });

    socket.on("connect", function () {
        console.log("Connected to server");
    });

    socket.on("agent_response", function (data) {
        if (data.type === "thinking_message") {
            displayThinkingMessage(data.content, data.msg_id);
        }
        if (data.type === "loading_message") {
            displayLoadingMessage(data.content, data.msg_id);
        } else if (data.type === "search_results") {
            updateSearchResults(data.content, data.results, data.msg_id);
        } else if (data.type === "compiler_message") {
            displayCodeExecutionMessage(data.content, data.code, data.msg_id);
            console.log(data.code);
        } else if (data.type === "success_message") {
            updateLoadingMessage(data.msg_id, data.content);
        } else if (data.type === "error_message") {
            updateLoadingMessageWithError(data.msg_id, data.content);
        } else if (data.type === "error") {
            displayErrorMessage(data.content);
        } else if (data.type === "thinking_message") {
            displayThinkingMessage(data.content, data.msg_id);
        } else {
            displayAgentMessage(data.content);
        }
        scrollChatToBottom();
    });
    socket.on("agent_status", function (data) {
        const statusElement = $("#agent-status");
        if (data.status === "true") {
            statusElement.text("STATUS: Active");
            statusElement.removeClass("inactive").addClass("active");
            toggleButtons(true);
        } else {
            statusElement.text("STATUS: Inactive");
            statusElement.removeClass("active").addClass("inactive");
            toggleButtons(false);
        }
    });
    function displayThinkingMessage(message, msg_id) {
        let regex = /(\d+\)\s+)/g;
        let parts = message.split(regex);
        let items = [];
        for (let i = 1; i < parts.length; i += 2) {
            let number = parts[i];
            let content = parts[i + 1] ? parts[i + 1].trim() : "";
            items.push({ number: number.trim(), content: content });
        }

        let html = `
      <h3 class="think-header" id="think-title-${msg_id}">
        THINKING PHASE
      </h3>
      <div class="thinking-container">
    `;

        items.forEach(function (item) {
            html += `
        <div class="thinking-card">
          <div class="card-header">
            <span class="step-number">Step ${item.number}</span>
          </div>
          <div class="card-body">
            <p>${escapeHtml(item.content)}</p>
          </div>
        </div>
      `;
        });

        html += "</div>";

        $("#think-window").html(html);
        $("#think-window").addClass("highlight");

        setTimeout(function () {
            $("#think-window").removeClass("highlight");
        }, 4000);
    }

    function toggleButtons(isActive) {
        if (isActive) {
            $("#send-btn").prop("disabled", true).hide();
            $("#end-btn").show();
        } else {
            $("#send-btn").prop("disabled", false).show();
            $("#end-btn").hide();
        }
    }
    function endProcessing() {
        socket.emit("end_processing");
        toggleButtons(false);
    }
    function updateSearchResults(message, results, msg_id) {
        let html = `
            <span>${escapeHtml(message)}</span>
            <i class="bi bi-check-circle-fill" style="margin-left: 10px;"></i>
            <pre class="hidden-results" id="results-block-${msg_id}" style="display: none; margin-top: 10px;"><code>${escapeHtml(
            results
        )}</code></pre>
        `;

        $(`#msg-${msg_id}`).html(html);
        $(`#msg-${msg_id}`)
            .removeClass("loading-message")
            .addClass("search-results-message");

        $(`#show-results-${msg_id}`).click(function () {
            toggleResultsVisibility(msg_id);
        });
    }

    function toggleResultsVisibility(msg_id) {
        let resultsBlock = $(`#results-block-${msg_id}`);
        let showResultsBtn = $(`#show-results-${msg_id}`);

        if (resultsBlock.is(":visible")) {
            resultsBlock.hide();
            showResultsBtn.text("Show Results");
        } else {
            resultsBlock.show();
            showResultsBtn.text("Hide Results");
        }
    }
    function displayCodeExecutionMessage(message, code, msg_id) {
        code = code || "No code available";

        let html = `
            <div class="message code-execution-message" id="msg-${msg_id}">
                <span>${escapeHtml(message)}</span>
                <button class="show-code-btn" id="show-code-${msg_id}" data-msg-id="${msg_id}">Show Code</button>
                <pre class="hidden-code" id="code-block-${msg_id}" style="display: none;"><code>${escapeHtml(
            code
        )}</code></pre>
            </div>
        `;
        $("#chat-window").append(html);

        $(`#show-code-${msg_id}`).click(function () {
            toggleCodeVisibility(msg_id);
        });
    }

    function displayLoadingMessage(message, msg_id) {
        let html = `
            <div class="message loading-message" id="msg-${msg_id}">
                <span>${escapeHtml(message)}</span>
                <div class="spinner-border spinner-border-sm text-primary" role="status" style="margin-left: 10px;">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        $("#chat-window").append(html);
    }

    function toggleCodeVisibility(msg_id) {
        let codeBlock = $(`#code-block-${msg_id}`);
        let showCodeBtn = $(`#show-code-${msg_id}`);

        if (codeBlock.is(":visible")) {
            codeBlock.hide();
            showCodeBtn.text("Show Code");
        } else {
            codeBlock.show();
            showCodeBtn.text("Hide Code");
        }
    }

    function updateLoadingMessage(msg_id, message) {
        let messageElement = $(`#msg-${msg_id}`);
        if (messageElement.length) {
            messageElement.removeClass("loading-message").addClass("success-message");
            messageElement.html(`
                <span>${message}</span>
                <i class="bi bi-check-circle-fill tick-icon"></i>
            `);
        }
    }

    function updateLoadingMessageWithError(msg_id, message) {
        let messageElement = $(`#msg-${msg_id}`);
        if (messageElement.length) {
            messageElement.removeClass("loading-message").addClass("error-message");
            messageElement.html(`
                <span>${message}</span>
                <i class="bi bi-exclamation-triangle-fill"></i>
            `);
        }
    }

    function displayErrorMessage(message) {
        let html = `
            <div class="message error-message">
                <i class="bi bi-exclamation-triangle-fill"></i> ${message}
            </div>
        `;
        $("#chat-window").append(html);
    }

    function displayAgentMessage(message) {
        let html = `
            <div class="message agent-message">
                ${marked.parse(message)}
            </div>
        `;
        $("#chat-window").append(html);
    }
    function clear() {
        const outerDiv = document.getElementById("think-window");
        outerDiv.querySelector(".thinking-container").innerHTML = "";
        // document.getElementsByClassName("thinking-container").innerHTML = "";
        document.getElementById("chat-window").innerHTML = "";
    }

    function refresh() {
        socket.emit("refresh");
    }

    function sendPrompt() {
        let prompt = $("#prompt").val().trim();
        if (prompt === "") {
            return;
        }

        let html = `
            <div class="message user-message">
                <span>${prompt}</span>
            </div>
        `;
        $("#chat-window").append(html);
        scrollChatToBottom();
        $("#prompt").val("");

        socket.emit("user_prompt", { prompt: prompt });
    }

    function scrollChatToBottom() {
        $("#chat-window").scrollTop($("#chat-window")[0].scrollHeight);
    }
});

const apiBtn = document.getElementById("api-btn");
const apiModal = document.getElementById("api-modal");
const closeBtn = document.querySelector(".close-btn");

apiBtn.addEventListener("click", () => {
    apiModal.style.display = "block";
});

closeBtn.addEventListener("click", () => {
    apiModal.style.display = "none";
});

window.addEventListener("click", (event) => {
    if (event.target === apiModal) {
        apiModal.style.display = "none";
    }
});
