document.addEventListener("DOMContentLoaded", () => {
    const socket = io("http://localhost:5000");
    window.socket = socket;
  
    socket.on("connect", () => {
      console.log("Socket connected (from script.js)");
    });
    
    socket.on("workflow_response", function(data) {
        console.log("Received workflow_response:", data);
        if (data.redirect && data.query) {
          localStorage.setItem("pendingQuery", data.query);
          window.location.href = data.redirect;
        }
    });
    
    let workflowCount = 0;
  
    document.getElementById("addFunction").addEventListener("click", () => {
      const functionType = document.getElementById("functionType").value;
      addFunctionBlock(functionType);
    });
  
    document.getElementById("saveWorkflow").addEventListener("click", () => {
      // Prompt for workflow name
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
  
      // Save to localStorage with custom name
      const savedWorkflows = JSON.parse(localStorage.getItem("workflows") || "{}");
      
      // Check if name already exists
      if (savedWorkflows[workflowName] && !confirm(`A workflow named "${workflowName}" already exists. Do you want to overwrite it?`)) {
        return;
      }
      
      savedWorkflows[workflowName] = {
        name: workflowName,
        steps: workflow
      };
      
      localStorage.setItem("workflows", JSON.stringify(savedWorkflows));
      workflowCount++;
  
      // Add to sidebar
      addWorkflowToSidebar(workflowName, workflow);
  
      // Clear the container
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
  
    // Load saved workflows from localStorage when the window loads
    window.onload = function () {
      const savedWorkflows = JSON.parse(localStorage.getItem("workflows") || "{}");
      for (let name in savedWorkflows) {
        const workflow = savedWorkflows[name];
        addWorkflowToSidebar(name, workflow.steps || workflow); // Handle both new and old format
        workflowCount = Object.keys(savedWorkflows).length;
      }
    };
});