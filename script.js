// Buchstaben-Punktwerte und Längenbonus
const LETTER_SCORES = {
    'A': 1, 'B': 3, 'C': 2, 'D': 3, 'E': 1, 'F': 3, 'G': 2, 'H': 2,
    'I': 1, 'J': 6, 'K': 3, 'L': 2, 'M': 3, 'N': 1, 'O': 2, 'P': 4,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 2, 'V': 6, 'W': 4, 'X': 8,
    'Y': 6, 'Z': 4
};

const LENGTH_BONUS = {
    1: 1, 2: 3, 3: 4, 4: 6,
    5: 9, 6: 11, 7: 14, 8: 17,
    9: 19, 10: 22
};

let dictionary = new Set();
let dictionaryLoaded = false; // Flag hinzufügen
let board = [];

function loadDictionary() {
    fetch('wordlist-de.json')
        .then(response => response.json())
        .then(data => {
            dictionary = new Set(data);
            dictionaryLoaded = true; // Flag setzen
            console.log('Wörterliste geladen:', dictionary.size, 'Wörter');
            // Start-Button aktivieren
            const startButton = document.getElementById('startButton');
            if (startButton) {
                startButton.disabled = false;
            }
        })
        .catch(error => {
            console.error('Fehler beim Laden der Wörterliste:', error);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    loadDictionary();
    // Cursor in das Eingabefeld setzen
    document.getElementById('inputLetters').focus();
});

function startGame() {
    if (!dictionaryLoaded) {
        alert('Die Wörterliste wird noch geladen. Bitte warten Sie einen Moment und versuchen Sie es erneut.');
        return;
    }
    const inputField = document.getElementById('inputLetters');
    const input = inputField.value.toUpperCase().replace(/[^A-ZÄÖÜẞ]/g, '');
    if (input.length !== 16) {
        alert('Bitte genau 16 Buchstaben eingeben.');
        return;
    }
    createBoard(input);
    const allFoundWords = findAllWords();
    displayResults(allFoundWords);
    // Start-Button deaktivieren
    document.getElementById('startButton').disabled = true;
}

function resetGame() {
    // Eingabefeld leeren
    const inputField = document.getElementById('inputLetters');
    inputField.value = '';
    inputField.focus();
    // Brett und Ergebnisse zurücksetzen
    document.getElementById('board').innerHTML = '';
    document.getElementById('results').innerHTML = '';
    // Start-Button deaktivieren
    document.getElementById('startButton').disabled = false;
}

document.getElementById('inputLetters').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        if (!dictionaryLoaded) {
            alert('Die Wörterliste wird noch geladen. Bitte warten Sie einen Moment und versuchen Sie es erneut.');
            return;
        }
        startGame();
    }
});

function createBoard(input) {
    board = [
        [input[0], input[1], input[2], input[3]],
        [input[4], input[5], input[6], input[7]],
        [input[8], input[9], input[10], input[11]],
        [input[12], input[13], input[14], input[15]]
    ];
    const boardDiv = document.getElementById('board');
    boardDiv.innerHTML = '<h2>Board:</h2>';
    board.forEach(row => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'row';
        row.forEach(cell => {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'cell';
            cellDiv.textContent = cell;
            rowDiv.appendChild(cellDiv);
        });
        boardDiv.appendChild(rowDiv);
    });
}

function calculateWordScore(word) {
    const letterScore = word.split('').reduce((sum, char) => sum + (LETTER_SCORES[char] || 0), 0);
    const bonus = LENGTH_BONUS[word.length] || 0;
    return letterScore + bonus;
}

function findAllWords() {
    const allFoundWords = new Set();
    for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
            nextCharacter([], row, col, allFoundWords);
        }
    }
    const wordScores = {};
    allFoundWords.forEach(word => {
        if (word.length > 4 && dictionary.has(word)) {
            wordScores[word] = calculateWordScore(word);
        }
    });
    return wordScores;
}

function nextCharacter(visited, row, col, foundWords) {
    if (visited.length > 9) return;
    const newVisited = visited.concat([[row, col]]);
    const word = newVisited.map(([r, c]) => board[r][c]).join('');
    if (dictionary.has(word)) {
        foundWords.add(word);
    }
    const directions = [
        [-1, 0], [-1, 1], [0, 1], [1, 1],
        [1, 0], [1, -1], [0, -1], [-1, -1]
    ];
    directions.forEach(([dr, dc]) => {
        const newRow = row + dr;
        const newCol = col + dc;
        if (newRow >= 0 && newRow < 4 && newCol >= 0 && newCol < 4) {
            if (!newVisited.some(([r, c]) => r === newRow && c === newCol)) {
                nextCharacter(newVisited, newRow, newCol, foundWords);
            }
        }
    });
}

// Levenshtein-Distanz-Funktion
function levenshteinDistance(a, b) {
    const an = a.length;
    const bn = b.length;
    if (an === 0) return bn;
    if (bn === 0) return an;

    const matrix = [];

    // Initialisierung der ersten Zeile und Spalte
    for (let i = 0; i <= bn; i++) {
        matrix[i] = [i];
    }
    for (let j = 0; j <= an; j++) {
        matrix[0][j] = j;
    }

    // Fülle die Matrix
    for (let i = 1; i <= bn; i++) {
        for (let j = 1; j <= an; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1, // Ersetzen
                    matrix[i][j - 1] + 1,     // Einfügen
                    matrix[i - 1][j] + 1      // Löschen
                );
            }
        }
    }

    return matrix[bn][an];
}

// Funktion zum Gruppieren der Wörter basierend auf Levenshtein-Distanz
function groupWordsByLevenshtein(sortedWords, maxDistance = 2) {
    const groups = [];

    sortedWords.forEach(([word, score]) => {
        let placed = false;
        for (let group of groups) {
            // Vergleiche mit dem ersten Wort der Gruppe
            if (levenshteinDistance(word, group[0][0]) <= maxDistance) {
                group.push([word, score]);
                placed = true;
                break;
            }
        }
        if (!placed) {
            groups.push([[word, score]]);
        }
    });

    return groups;
}

function displayResults(wordScores) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<h2>Ergebnisse:</h2>';

    // Wandelt das Wort-Score-Objekt in ein Array um und sortiert es alphabetisch
    const sortedWords = Object.entries(wordScores).sort((a, b) => a[0].localeCompare(b[0]));

    // Ausgabe der Ergebnisse
    if (sortedWords.length === 0) {
        resultsDiv.innerHTML += '<p>Keine Wörter gefunden.</p>';
        return;
    }

    // Gruppiere die Wörter basierend auf Levenshtein-Distanz
    const maxDistance = 3; // Du kannst diesen Wert anpassen
    const groupedWords = groupWordsByLevenshtein(sortedWords, maxDistance);

    // Sortiere die Gruppen basierend auf der Summe der Punkte (absteigend)
    groupedWords.sort((a, b) => {
        const sumA = a.reduce((sum, [word, score]) => sum + score, 0);
        const sumB = b.reduce((sum, [word, score]) => sum + score, 0);
        return sumB - sumA;
    });

    // Erstelle einen Container für die Gruppen
    const groupContainer = document.createElement('div');
    groupContainer.id = 'groupContainer';

    groupedWords.forEach((group, idx) => {
        const groupTotalScore = group.reduce((sum, [word, score]) => sum + score, 0);
        const groupDiv = document.createElement('div');
        groupDiv.className = 'group';

        groupDiv.innerHTML = `<h3>Gruppe ${idx + 1} (Gesamtpunkte: ${groupTotalScore}):</h3>`;
        const ul = document.createElement('ul');

        // Sortiere die Wörter innerhalb der Gruppe nach Punktzahl absteigend und dann alphabetisch
        group.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

        group.forEach(([word, score]) => {
            const li = document.createElement('li');
            li.textContent = `${word}: ${score} Punkte`;
            ul.appendChild(li);
        });

        groupDiv.appendChild(ul);
        groupContainer.appendChild(groupDiv);
    });

    resultsDiv.appendChild(groupContainer);
}
