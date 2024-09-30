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

$(document).ready(function () {
  var socket = io();

  $("#send-btn").click(function () {
    sendPrompt();
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
    } else {
      displayAgentMessage(data.content);
    }
    scrollChatToBottom();
  });
  function updateSearchResults(message, results, msg_id) {
    let html = `
            <span>${escapeHtml(message)}</span>
            <i class="bi bi-check-circle-fill" style="margin-left: 10px;"></i>
            <button class="show-results-btn" id="show-results-${msg_id}" data-msg-id="${msg_id}" style="margin-left: 10px;">Show Results</button>
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

  function displaySearchResults(message, results, msg_id) {
    let html = `
            <div class="message search-results-message" id="msg-${msg_id}">
                <span>${escapeHtml(message)}</span>
                <i class="bi bi-check-circle-fill" style="margin-left: 10px;"></i>
                <button class="show-results-btn" id="show-results-${msg_id}" data-msg-id="${msg_id}" style="margin-left: 10px;">Show Results</button>
                <pre class="hidden-results" id="results-block-${msg_id}" style="display: none; margin-top: 10px;"><code>${escapeHtml(
      results
    )}</code></pre>
            </div>
        `;
    $("#chat-window").append(html);

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

  function displayLoadingMessage(message, msg_id) {
    let html = `
            <div class="message loading-message" id="msg-${msg_id}">
                <span>${message}</span>
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    $("#chat-window").append(html);
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
