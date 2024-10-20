const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  const voiceInputBtn = document.getElementById("voice-input-btn");
  const promptTextarea = document.getElementById("prompt");
  const sendButton = document.getElementById("send-btn");

  voiceInputBtn.addEventListener("click", () => {
    recognition.start();
    voiceInputBtn.classList.add("listening");
  });

  recognition.addEventListener("result", (event) => {
    const transcript = event.results[0][0].transcript;

    promptTextarea.value = transcript;
  });

  recognition.addEventListener("speechend", () => {
    recognition.stop();
    voiceInputBtn.classList.remove("listening");

    sendButton.click();
  });

  recognition.addEventListener("error", (event) => {
    console.error("Speech recognition error:", event.error);
    voiceInputBtn.classList.remove("listening");

    alert("Error with speech recognition: " + event.error);
  });
} else {
  console.warn("SpeechRecognition API is not supported in this browser.");
  document.getElementById("voice-input-btn").style.display = "none";
}

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
      statusElement.text("Thinking");
      statusElement.removeClass("inactive").addClass("active");
      toggleButtons(true);
    } else {
      statusElement.text("Inactive");
      statusElement.removeClass("active").addClass("inactive");
      toggleButtons(false);
    }
  });
  function scrollChatToBottom() {
    $("#chat-window").scrollTop($("#chat-window")[0].scrollHeight);
  }

  function scrollThinkingWindowToBottom() {
    $("#think-window").scrollTop($("#think-window")[0].scrollHeight);
  }

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
        <div class="thinking-container" id="thinking-container-${msg_id}">
        </div>
        `;
    $("#think-window").html(html);

    typeThinkingSteps(items, msg_id);
  }

  function typeThinkingSteps(steps, msg_id) {
    let container = $(`#thinking-container-${msg_id}`);
    let stepIndex = 0;

    function typeNextStep() {
      if (stepIndex < steps.length) {
        let step = steps[stepIndex];

        let stepHtml = `
                    <div class="thinking-card" id="thinking-card-${msg_id}-${stepIndex}">
                    <div class="card-header">
                        <span class="step-number">Step ${step.number}</span>
                    </div>
                    <div class="card-body">
                        <p id="step-content-${msg_id}-${stepIndex}"></p>
                    </div>
                    </div>
                `;
        container.append(stepHtml);
        scrollThinkingWindowToBottom();

        typeStepContent(step.content, msg_id, stepIndex, function () {
          stepIndex++;
          typeNextStep();
        });
      } else {
        $("#think-window").removeClass("highlight");
      }
    }

    $("#think-window").addClass("highlight");
    typeNextStep();
  }

  function typeStepContent(content, msg_id, stepIndex, callback) {
    let contentElement = $(`#step-content-${msg_id}-${stepIndex}`);
    let index = 0;
    let speed = 20;
    let tempContent = "";

    function typeChar() {
      if (index < content.length) {
        let currentChar = content.charAt(index);
        tempContent += currentChar;
        contentElement.html(escapeHtml(tempContent));
        index++;
        scrollThinkingWindowToBottom();
        setTimeout(typeChar, speed);
      } else {
        let parsedContent = marked.parse(tempContent);
        contentElement.html(parsedContent);
        scrollThinkingWindowToBottom();
        if (callback) callback();
      }
    }

    typeChar();
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
    let msg_id = Date.now();
    let html = `
            <div class="message agent-message" id="msg-${msg_id}">
                <span></span>
            </div>
        `;
    $("#chat-window").append(html);
    typeMessageCharacterByCharacter(message, msg_id);
  }
  function typeMessageCharacterByCharacter(message, msg_id) {
    let messageElement = $(`#msg-${msg_id}`).find("span");
    let index = 0;
    let speed = 5;
    let tempMessage = "";

    function typeChar() {
      if (index < message.length) {
        let currentChar = message.charAt(index);
        tempMessage += currentChar;
        messageElement.html(escapeHtml(tempMessage));
        index++;
        scrollChatToBottom();
        setTimeout(typeChar, speed);
      } else {
        let parsedMessage = marked.parse(tempMessage);
        messageElement.html(parsedMessage);
        scrollChatToBottom();
      }
    }
    typeChar();
  }

  function clear() {
    const outerDiv = document.getElementById("think-window");
    outerDiv.querySelector(".thinking-container").innerHTML = "";
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
