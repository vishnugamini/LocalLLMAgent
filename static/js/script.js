document.addEventListener("DOMContentLoaded", () => {
  const socket = io("http://localhost:5000");
  window.socket = socket;

  socket.on("connect", () => {
    console.log("Socket connected (from script.js)");
  });
  const toggleChatBtn = document.getElementById("toggleChatBtn");
  let isFullscreen = false;
  let originalRect = null; 

  toggleChatBtn.addEventListener("click", () => {
    const chatContainer = document.querySelector(".chat-container");
    const mainContainer = document.querySelector(".main-container");
    const savedWorkflows = document.querySelector(".saved-workflows");

    if (!isFullscreen) {
      originalRect = chatContainer.getBoundingClientRect();

      chatContainer.style.position = "fixed";
      chatContainer.style.top = originalRect.top + "px";
      chatContainer.style.left = originalRect.left + "px";
      chatContainer.style.width = originalRect.width + "px";
      chatContainer.style.height = originalRect.height + "px";
      chatContainer.style.zIndex = "9999";

      chatContainer.style.transition = "top 0.3s ease, left 0.3s ease, width 0.3s ease, height 0.3s ease";
      mainContainer.style.transition = "opacity 0.3s ease";
      savedWorkflows.style.transition = "opacity 0.3s ease";

      chatContainer.getBoundingClientRect();

      chatContainer.style.top = "0";
      chatContainer.style.left = "0";
      chatContainer.style.width = "100vw";
      chatContainer.style.height = "100vh";

      mainContainer.style.opacity = "0";
      savedWorkflows.style.opacity = "0";

      isFullscreen = true;
    } else {
      chatContainer.style.top = originalRect.top + "px";
      chatContainer.style.left = originalRect.left + "px";
      chatContainer.style.width = originalRect.width + "px";
      chatContainer.style.height = originalRect.height + "px";

      mainContainer.style.opacity = "1";
      savedWorkflows.style.opacity = "1";

      chatContainer.addEventListener("transitionend", function handler(e) {
        if (e.propertyName === "height") {
          chatContainer.style.position = "";
          chatContainer.style.top = "";
          chatContainer.style.left = "";
          chatContainer.style.width = "";
          chatContainer.style.height = "";
          chatContainer.style.zIndex = "";
          chatContainer.style.transition = "";
          chatContainer.removeEventListener("transitionend", handler);
        }
      });

      isFullscreen = false;
    }
  });


  socket.on("workflow_response", function (data) {
    console.log("Received workflow_response:", data);
  
    if (data.status && data.status === "received") {
      displayWorkflowReceived(data.workflowText || "Workflow details here.");
    }
  
    if (data.status && data.status === "completed") {
      displayWorkflowCompleted();
    }
  
    if (window.location.pathname.includes("create_agent")) {
      if (data.query) {
        const messageHtml = `
          <div class="message agent-message">
            <span>${data.query}</span>
          </div>`;
        document.getElementById("chat-window").insertAdjacentHTML("beforeend", messageHtml);
        scrollChatToBottom();
      }
    } else {
      if (data.redirect && data.query) {
        localStorage.setItem("pendingQuery", data.query);
        window.location.href = data.redirect;
      }
    }
  });
  socket.on("agent_response", function (data) {
    console.log("agent_response received:", data);

    if (
      data.type === "info" &&
      data.content === "Workflow completed." &&
      !window.location.pathname.includes("create_agent")
    ) {
      console.log("Skipping 'Workflow completed.' message because we're not on create_agent");
      return;
    }

    if (data.type === "workflow_received") {
      displayWorkflowReceived(data.workflowText || "");
    } else if (data.type === "workflow_completed") {
      displayWorkflowCompleted();
    } else if (data.type === "thinking_message") {
    } else if (data.type === "loading_message") {
      displayLoadingMessage(data.content, data.msg_id);
    } else if (data.type === "search_results") {
      updateSearchResults(data.content, data.results, data.msg_id);
    } else if (data.type === "compiler_message") {
      displayCodeExecutionMessage(data.content, data.code, data.msg_id);
    } else if (data.type === "success_message") {
      updateLoadingMessage(data.msg_id, data.content);
    } else if (data.type === "error_message") {
      updateLoadingMessageWithError(data.msg_id, data.content, data.code);
    } else if (data.type === "error") {
      displayErrorMessage(data.content);
    } else if (data.type === "search_agent_message") {
      SearchAgentMessage(data.content);
    } else if (data.type === "info") {
      displayAgentMessage(data.content);
    } else {
      displayAgentMessage(data.content);
    }
    scrollChatToBottom();
  });

  function sendPrompt() {
    const promptEl = document.getElementById("prompt");
    let promptText = promptEl.value.trim();

    if (!promptText) return;

    console.log("Sending prompt:", promptText);

    const chatWindow = document.getElementById("chat-window");
    const userMessage = document.createElement("div");
    userMessage.className = "message user-message";
    userMessage.innerHTML = `<span>${promptText}</span>`;
    chatWindow.appendChild(userMessage);
    scrollChatToBottom();

    promptEl.value = "";
    promptEl.style.height = "";

    socket.emit("user_prompt", { prompt: promptText, mode: "agent" });

    if (window.autoWorkflowMessage) {
      window.autoWorkflowMessage = false;
    }
  }

  document.getElementById("send-btn").addEventListener("click", sendPrompt);
  document.getElementById("prompt").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendPrompt();
    }
  });

  function scrollChatToBottom() {
    const chatWindow = document.getElementById("chat-window");
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function displayAgentMessage(message) {
    const msg_id = Date.now();
    const html = `
      <div class="message agent-message" id="msg-${msg_id}">
        <span>${message}</span>
      </div>`;
    document.getElementById("chat-window").insertAdjacentHTML("beforeend", html);
  }

  function displayLoadingMessage(message, msg_id) {
    const html = `
      <div class="message loading-message" id="msg-${msg_id}">
        <span>${message}</span>
        <span class="spinner" style="margin-left: 10px;">⏳</span>
      </div>`;
    document.getElementById("chat-window").insertAdjacentHTML("beforeend", html);
  }

  function updateSearchResults(message, results, msg_id) {
    const resultHtml = `<pre>${results}</pre>`;
    document.getElementById(`msg-${msg_id}`).insertAdjacentHTML("beforeend", resultHtml);
  }

  function updateLoadingMessage(msg_id, message) {
    document.getElementById(`msg-${msg_id}`).innerHTML = `<span>${message}</span>`;
  }

  function displayCodeExecutionMessage(content, code, msg_id) {
    const html = `
      <div class="message code-execution-message" id="msg-${msg_id}">
        <pre>${code}</pre>
        <span>${content}</span>
      </div>`;
    document.getElementById("chat-window").insertAdjacentHTML("beforeend", html);
  }

  function updateLoadingMessageWithError(msg_id, message, code) {
    const html = `
      <div class="message error-message" id="msg-${msg_id}">
        <span>${message}</span>
        <pre>${code}</pre>
      </div>`;
    document.getElementById("chat-window").insertAdjacentHTML("beforeend", html);
  }

  function displayErrorMessage(message) {
    const msg_id = Date.now();
    const html = `
      <div class="message error-message" id="msg-${msg_id}">
        <span>${message}</span>
      </div>`;
    document.getElementById("chat-window").insertAdjacentHTML("beforeend", html);
  }

  function SearchAgentMessage(content) {
    const msg_id = Date.now();
    const html = `
      <div class="message search-message" id="msg-${msg_id}">
        <span>${content}</span>
      </div>`;
    document.getElementById("chat-window").insertAdjacentHTML("beforeend", html);
  }

  function displayWorkflowReceived(workflowText) {
    let msg_id = Date.now();
    const html = `
      <div class="workflow-message success" id="workflow-msg-${msg_id}">
        <div class="workflow-header">Workflow Received</div>
        <div class="workflow-content">
          <pre>${workflowText}</pre>
        </div>
      </div>
    `;
    $("#chat-window").append(html);
    scrollChatToBottom();
  }

  function displayWorkflowCompleted() {
    let msg_id = Date.now();
    const html = `
      <div class="workflow-message success completed" id="workflow-completed-${msg_id}">
        <div class="workflow-header">Workflow Completed</div>
      </div>
    `;
    $("#chat-window").append(html);
    scrollChatToBottom();
  
    setTimeout(() => {
      const $workflowMessages = $("#chat-window .workflow-message");
      if ($workflowMessages.length > 0) {
        const $startMessage = $workflowMessages.first();
        const $endMessage = $workflowMessages.last();
  
        $startMessage.addClass("green-pulse");
        $endMessage.addClass("green-pulse");
  
        setTimeout(() => {
          $startMessage.removeClass("green-pulse");
          $endMessage.removeClass("green-pulse");
        }, 1500); 
      }
    }, 100);
  }

  let workflowCount = 0;
  document.getElementById("addFunction").addEventListener("click", () => {
    const functionType = document.getElementById("functionType").value;
    addFunctionBlock(functionType);
  });

  document.getElementById("saveWorkflow").addEventListener("click", () => {
    const workflowName = prompt("Enter a name for your workflow:", `Workflow ${workflowCount + 1}`);
    if (workflowName) {
      saveWorkflow(workflowName);
    }
  });

  function addFunctionBlock(type) {
    const container = document.getElementById("workflowContainer");
    const functionBlock = document.createElement("div");
    functionBlock.className = "function-block";

    const functionLabel = document.createElement("div");
    functionLabel.className = "function-label";
    functionLabel.textContent = type.charAt(0).toUpperCase() + type.slice(1);

    const labelInput = document.createElement("input");
    labelInput.type = "text";
    labelInput.className = "label-input";
    labelInput.placeholder = "Enter label";

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "Delete";
    deleteBtn.onclick = () => functionBlock.remove();

    functionBlock.appendChild(functionLabel);
    functionBlock.appendChild(labelInput);
    functionBlock.appendChild(deleteBtn);
    container.appendChild(functionBlock);
  }

  function saveWorkflow(workflowName) {
    const container = document.getElementById("workflowContainer");
    const blocks = container.getElementsByClassName("function-block");

    if (blocks.length === 0) {
      alert("Please add at least one function to save the workflow");
      return;
    }

    const workflow = [];
    for (let block of blocks) {
      const type = block.querySelector(".function-label").textContent;
      const label = block.querySelector(".label-input").value;
      workflow.push({ type, label });
    }

    const savedWorkflows = JSON.parse(localStorage.getItem("workflows") || "{}");
    if (savedWorkflows[workflowName] && !confirm(`A workflow named "${workflowName}" already exists. Do you want to overwrite it?`)) {
      return;
    }

    savedWorkflows[workflowName] = {
      name: workflowName,
      steps: workflow
    };

    localStorage.setItem("workflows", JSON.stringify(savedWorkflows));
    workflowCount++;

    addWorkflowToSidebar(workflowName, workflow);
    container.innerHTML = "";
  }

  function deleteWorkflow(name, element) {
    const savedWorkflows = JSON.parse(localStorage.getItem("workflows") || "{}");
    delete savedWorkflows[name];
    localStorage.setItem("workflows", JSON.stringify(savedWorkflows));
    element.remove();
  }

  function addWorkflowToSidebar(name, workflow) {
    const savedList = document.getElementById("savedWorkflowsList");
    const workflowElement = document.createElement("div");
    workflowElement.className = "saved-workflow";

    const workflowName = document.createElement("div");
    workflowName.className = "saved-workflow-name";
    workflowName.textContent = name;
    workflowName.onclick = () => loadWorkflow(workflow);

    const kickoffBtn = document.createElement("button");
    kickoffBtn.className = "kickoff-workflow-btn";
    kickoffBtn.textContent = "Kick Off";
    kickoffBtn.onclick = (e) => {
      e.stopPropagation();
      kickoffWorkflow(workflow);
    };

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-workflow-btn";
    deleteBtn.textContent = "Delete";
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      if (confirm(`Are you sure you want to delete "${name}"?`)) {
        deleteWorkflow(name, workflowElement);
      }
    };

    workflowElement.appendChild(workflowName);
    workflowElement.appendChild(kickoffBtn);
    workflowElement.appendChild(deleteBtn);
    savedList.appendChild(workflowElement);
  }

  function kickoffWorkflow(workflow) {
    if (!workflow || workflow.length === 0) {
      alert("No workflow steps to execute");
      return;
    }
    console.log("Workflow to be kicked off:", workflow);
    if (window.socket && window.socket.emit) {
      window.socket.emit("kickoff_workflow", { workflow: workflow });
    } else {
      console.error("Socket connection not available");
    }
  }

  function loadWorkflow(workflow) {
    const container = document.getElementById("workflowContainer");
    container.innerHTML = "";
    workflow.forEach(function (item) {
      const functionBlock = document.createElement("div");
      functionBlock.className = "function-block";

      const functionLabel = document.createElement("div");
      functionLabel.className = "function-label";
      functionLabel.textContent = item.type;

      const labelInput = document.createElement("input");
      labelInput.type = "text";
      labelInput.className = "label-input";
      labelInput.value = item.label;

      const deleteBtn = document.createElement("button");
      deleteBtn.className = "delete-btn";
      deleteBtn.textContent = "Delete";
      deleteBtn.onclick = () => functionBlock.remove();

      functionBlock.appendChild(functionLabel);
      functionBlock.appendChild(labelInput);
      functionBlock.appendChild(deleteBtn);
      container.appendChild(functionBlock);
    });
  }

  window.onload = function () {
    const savedWorkflows = JSON.parse(localStorage.getItem("workflows") || "{}");
    for (let name in savedWorkflows) {
      const workflow = savedWorkflows[name];
      addWorkflowToSidebar(name, workflow.steps || workflow);
      workflowCount = Object.keys(savedWorkflows).length;
    }
  };
});

$(document).ready(function () {
  $("#preview-btn").click(function () {
      showPreviewModal();
  });
});

function showPreviewModal() {
  let modalHtml = `
  <div class="modal" id="preview-modal">
    <div class="modal-contents">
      <span class="close-preview-modal">&times;</span>
      <div class="modal-body">
        <div class="web-app-preview">
          <iframe id="preview-iframe" src="about:blank" frameborder="0" scrolling="yes"></iframe>
        </div>
      </div>
    </div>
  </div>
`;
  $("body").append(modalHtml);

  $("#preview-modal").css({
      position: "fixed",
      top: "0",
      left: "0",
      right: "0",
      bottom: "0",
      width: "100vw",
      height: "100vh",
      "background-color": "rgba(0, 0, 0, 0.9)",
      "z-index": "9999",
      display: "flex",
      "align-items": "center",
      "justify-content": "center",
  });

  $("#preview-modal .modal-contents").css({
      position: "relative",
      width: "100vw",
      height: "100vh",
      "background-color": "#fff",
      display: "flex",
      "flex-direction": "column",
      overflow: "hidden",
      margin: "0",
      padding: "0",
  });

  $("#preview-modal .modal-body").css({
      flex: "1",
      overflow: "hidden",
      padding: "0",
      margin: "0",
      width: "100%",
      height: "100%",
  });

  $("#preview-modal .web-app-preview").css({
      width: "100%",
      height: "100%",
      "background-color": "#fff",
      overflow: "hidden",
      display: "flex",
  });

  $("#preview-modal .web-app-preview iframe").css({
      border: "solid 12px",
      width: "100%",
      height: "100%",
      border: "none",
      margin: "0",
      padding: "0",
      overflow: "auto",
      flex: "1",
  });

  $("#preview-modal .close-preview-modal").css({
      position: "fixed",
      top: "-5px",
      right: "20px",
      "font-size": "40px",
      cursor: "pointer",
      color: "#050505",
      "z-index": "10000",
      "text-shadow": "0 0 10px white",
  });

  $("#preview-modal .close-preview-modal").click(function () {
      $("#preview-modal").remove();
  });

  $(document).on("keydown", function (e) {
      if (e.key === "Escape") {
          $("#preview-modal").remove();
      }
  });

  $("#preview-modal").on("click", function (e) {
      if ($(e.target).is("#preview-modal")) {
          $("#preview-modal").remove();
      }
  });

  renderWebApp();
}

function renderWebApp() {
  const iframe = document.getElementById("preview-iframe");
  iframe.onload = function () {
      try {
          const iframeDoc =
              iframe.contentDocument || iframe.contentWindow.document;
          const style = document.createElement("style");
          style.textContent = `
      ::-webkit-scrollbar {
          width: 15px;
      }
      ::-webkit-scrollbar-thumb {
          background: #ada7a7b6;
          border-radius: 10px;
          border: 5px white solid;
      }
      `;
          iframeDoc.head.appendChild(style);

          if (!iframeDoc.querySelector('meta[name="viewport"]')) {
              const meta = iframeDoc.createElement("meta");
              meta.name = "viewport";
              meta.content =
                  "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no";
              iframeDoc.head.appendChild(meta);
          }
      } catch (e) {
          console.log(
              "Cannot access iframe content - likely due to same-origin policy"
          );
      }
  };

  iframe.src = "render/index.html";
}