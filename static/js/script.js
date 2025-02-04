let workflowCount = 0;

document.getElementById('addFunction').addEventListener('click', () => {
    const functionType = document.getElementById('functionType').value;
    addFunctionBlock(functionType);
});

document.getElementById('saveWorkflow').addEventListener('click', saveWorkflow);

function addFunctionBlock(type) {
    const container = document.getElementById('workflowContainer');
    const functionBlock = document.createElement('div');
    functionBlock.className = 'function-block';
    
    const functionLabel = document.createElement('div');
    functionLabel.className = 'function-label';
    functionLabel.textContent = type.charAt(0).toUpperCase() + type.slice(1);
    
    const labelInput = document.createElement('input');
    labelInput.type = 'text';
    labelInput.className = 'label-input';
    labelInput.placeholder = 'Enter label';
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.textContent = 'Delete';
    deleteBtn.onclick = () => functionBlock.remove();
    
    functionBlock.appendChild(functionLabel);
    functionBlock.appendChild(labelInput);
    functionBlock.appendChild(deleteBtn);
    
    container.appendChild(functionBlock);
}

function saveWorkflow() {
    const container = document.getElementById('workflowContainer');
    const blocks = container.getElementsByClassName('function-block');
    
    if (blocks.length === 0) {
        alert('Please add at least one function to save the workflow');
        return;
    }

    const workflow = [];
    for (let block of blocks) {
        const type = block.querySelector('.function-label').textContent;
        const label = block.querySelector('.label-input').value;
        workflow.push({ type, label });
    }

    workflowCount++;
    const workflowName = `Workflow ${workflowCount}`;
    
    // Save to localStorage
    const savedWorkflows = JSON.parse(localStorage.getItem('workflows') || '{}');
    savedWorkflows[workflowName] = workflow;
    localStorage.setItem('workflows', JSON.stringify(savedWorkflows));
    
    // Add to sidebar
    addWorkflowToSidebar(workflowName, workflow);
    
    // Clear the container
    container.innerHTML = '';
}

function deleteWorkflow(name, element) {
    // Remove from localStorage
    const savedWorkflows = JSON.parse(localStorage.getItem('workflows') || '{}');
    delete savedWorkflows[name];
    localStorage.setItem('workflows', JSON.stringify(savedWorkflows));
    
    // Remove from sidebar
    element.remove();
}

// Previous JavaScript remains the same until addWorkflowToSidebar function

function addWorkflowToSidebar(name, workflow) {
    const savedList = document.getElementById('savedWorkflowsList');
    const workflowElement = document.createElement('div');
    workflowElement.className = 'saved-workflow';
    
    const workflowName = document.createElement('div');
    workflowName.className = 'saved-workflow-name';
    workflowName.textContent = name;
    workflowName.onclick = () => loadWorkflow(workflow);
    
    const kickoffBtn = document.createElement('button');
    kickoffBtn.className = 'kickoff-workflow-btn';
    kickoffBtn.textContent = 'Kick Off Workflow';
    kickoffBtn.onclick = (e) => {
        e.stopPropagation();
        kickoffWorkflow(workflow);
    };
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-workflow-btn';
    deleteBtn.textContent = 'Delete';
    deleteBtn.onclick = (e) => {
        e.stopPropagation();
        if (confirm(`Are you sure you want to delete ${name}?`)) {
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
        alert('No workflow steps to execute');
        return;
    }

    console.log('Workflow to be kicked off:', workflow);
    
    // Emit the workflow data to the backend via Socket.IO
    if (window.socket && window.socket.emit) {
        window.socket.emit('kickoff_workflow', { workflow: workflow });
    } else {
        console.error('Socket connection not available');
    }
    
    // Optionally, update the UI to show that the workflow has been sent
    alert('Workflow has been sent to the backend for processing.');
}
// Rest of the previous JavaScript remains the same
function loadWorkflow(workflow) {
    const container = document.getElementById('workflowContainer');
    container.innerHTML = '';
    
    workflow.forEach(function(item) {
        const functionBlock = document.createElement('div');
        functionBlock.className = 'function-block';
        
        const functionLabel = document.createElement('div');
        functionLabel.className = 'function-label';
        functionLabel.textContent = item.type;
        
        const labelInput = document.createElement('input');
        labelInput.type = 'text';
        labelInput.className = 'label-input';
        labelInput.value = item.label;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = 'Delete';
        deleteBtn.onclick = () => functionBlock.remove();
        
        functionBlock.appendChild(functionLabel);
        functionBlock.appendChild(labelInput);
        functionBlock.appendChild(deleteBtn);
        
        container.appendChild(functionBlock);
    });
}

// Load saved workflows from localStorage on page load
window.onload = function() {
    const savedWorkflows = JSON.parse(localStorage.getItem('workflows') || '{}');
    for (let name in savedWorkflows) {
        addWorkflowToSidebar(name, savedWorkflows[name]);
        workflowCount = Math.max(workflowCount, 
            parseInt(name.split(' ')[1] || '0'));
    }
};