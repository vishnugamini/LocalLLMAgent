document.addEventListener("DOMContentLoaded", () => {
  const socket = io("http://localhost:5000");
  window.socket = socket;

  socket.on("connect", () => {
    console.log("Socket connected (from script.js)");
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
      displayWorkflowReceived(data.workflowText || "Workflow details here.");
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

  // --- Utility: Scroll Chat to Bottom ---
  function scrollChatToBottom() {
    const chatWindow = document.getElementById("chat-window");
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  // --- Helper Functions for Displaying Messages ---
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