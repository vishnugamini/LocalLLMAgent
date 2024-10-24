let calculationHistory = [];

function appendToDisplay(value) {
    document.getElementById('display').value += value;
}

function calculateResult() {
    const display = document.getElementById('display');
    try {
        const result = eval(display.value);
        display.value = result;
        updateHistory(display.value);
    } catch (error) {
        display.value = 'Error';
    }
}

function clearDisplay() {
    document.getElementById('display').value = '';
}

function updateHistory(calculation) {
    calculationHistory.push(calculation);
    const historyList = document.getElementById('historyList');
    historyList.innerHTML += `<li>${calculation}</li>`;
}