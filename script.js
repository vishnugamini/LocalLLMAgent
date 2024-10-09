
const cells = document.querySelectorAll('.cell');
const messageDisplay = document.getElementById('message');
const restartButton = document.getElementById('restart');

let board = ['', '', '', '', '', '', '', '', ''];
let currentPlayer = 'X';
let gameActive = true;

const winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
];

function handleCellClick(clickedCell, clickedCellIndex) {
    if (board[clickedCellIndex] !== '' || !gameActive) {
        return;
    }
    board[clickedCellIndex] = currentPlayer;
    clickedCell.textContent = currentPlayer;
    checkForWinner();
    currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    if (currentPlayer === 'O') {
        aiMove();
    }
}

function checkForWinner() {
    let roundWon = false;
    for (let i = 0; i < winningConditions.length; i++) {
        const [a, b, c] = winningConditions[i];
        if (board[a] === '' || board[b] === '' || board[c] === '') {
            continue;
        }
        if (board[a] === board[b] && board[a] === board[c]) {
            roundWon = true;
            break;
        }
    }
    if (roundWon) {
        messageDisplay.textContent = `Player ${currentPlayer} has won!`;
        gameActive = false;
        return;
    }
    if (!board.includes('')) {
        messageDisplay.textContent = 'Game ended in a draw!';
        gameActive = false;
        return;
    }
}

function aiMove() {
    let availableCells = board.map((cell, index) => cell === '' ? index : null).filter(index => index !== null);
    let randomIndex = Math.floor(Math.random() * availableCells.length);
    let aiCell = availableCells[randomIndex];
    board[aiCell] = currentPlayer;
    cells[aiCell].textContent = currentPlayer;
    checkForWinner();
    currentPlayer = 'X';
}

function handleCellClickWrapper(event) {
    handleCellClick(event.target, event.target.id);
}

function restartGame() {
    currentPlayer = 'X';
    gameActive = true;
    board = ['', '', '', '', '', '', '', '', ''];
    messageDisplay.textContent = '';
    cells.forEach(cell => cell.textContent = '');
}

cells.forEach((cell) => cell.addEventListener('click', handleCellClickWrapper));
restartButton.addEventListener('click', restartGame);
