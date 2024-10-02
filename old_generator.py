import sys
from multiprocessing.dummy import Pool
from pprint import pprint
import threading

# Rekursionslimit erhöhen
sys.setrecursionlimit(5000)

# Punktesystem für deutsche Buchstaben (ähnlich wie Scrabble)
LETTER_SCORES = {
    'A': 1, 'B': 3, 'C': 4, 'D': 1, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 6, 'L': 3, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 6, 'W': 3, 'X': 8,
    'Y': 10, 'Z': 3, 'Ä': 6, 'Ö': 8, 'Ü': 6, 'ß': 3
}

# Initialisiere ein Thread-sicheres Set und einen Lock
word_candidates = set()
lock = threading.Lock()

def calculate_word_score(word, letter_scores):
    """Berechnet die Punktzahl eines Wortes basierend auf den Buchstabenpunkten."""
    return sum(letter_scores.get(char, 0) for char in word.upper())

def next_character(visited, current_row, current_column, dictionary, board):
    counter = 0
    if len(visited) > 7:
        return counter
    # Füge die aktuelle Position zum Pfad hinzu und bilde das Wort
    new_visited = visited + [(current_row, current_column)]
    word = "".join([board[row][col] for row, col in new_visited])
    # Überprüfen, ob das Wort gültig ist
    if word.upper() in dictionary and len(word) > 5:
        with lock:
            if word not in word_candidates:
                word_candidates.add(word)
                print(word)  # Live-Feed der einzigartigen Wörter
    # Definition der möglichen Bewegungsrichtungen (N, NE, E, SE, S, SW, W, NW)
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                  (1, 0), (1, -1), (0, -1), (-1, -1)]
    
    for dr, dc in directions:
        new_row = current_row + dr
        new_col = current_column + dc
        # Überprüfen, ob die neue Position innerhalb des Rasters liegt und nicht bereits besucht wurde
        if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]) and (new_row, new_col) not in new_visited:
            # Rekursiver Aufruf mit der neuen Position
            counter += next_character(new_visited, new_row, new_col, dictionary, board)
    return counter

def create_board(input_str):
    arr = [
        [input_str[0], input_str[1], input_str[2], input_str[3]],
        [input_str[4], input_str[5], input_str[6], input_str[7]],
        [input_str[8], input_str[9], input_str[10], input_str[11]],
        [input_str[12], input_str[13], input_str[14], input_str[15]]
    ]
    print("Board:")
    for row in arr:
        print(" ".join(row))
    return arr

def main():
    global word_candidates
    # Importieren und Konvertieren der Wortliste in Großbuchstaben
    try:
        with open('wordlist-de.txt', 'r', encoding='utf-8') as f:
            dictionary = set(word.strip().upper() for word in f)
    except FileNotFoundError:
        print("Die Datei 'wordlist-de.txt' wurde nicht gefunden.")
        sys.exit(1)
    
    # Eingabe des Boards vom Benutzer
    user_input = input("Die Wörter? (max. 16): ").strip().upper()
    if len(user_input) != 16:
        print("Bitte genau 16 Zeichen eingeben.")
        sys.exit(1)
    board = create_board(user_input)
    
    iterator = []
    
    # Initialisieren der Iterationen für jedes Feld des Boards
    for row in range(4):
        for column in range(4):
            iterator.append(([], row, column, dictionary, board))
    
    results = []
    
    # Verwenden von Multiprocessing für die Verarbeitung
    with Pool(4) as pool:
        results = pool.starmap(next_character, iterator)
    
    # Berechnung der Punktzahlen für die gefundenen Wörter
    word_scores = {word: calculate_word_score(word, LETTER_SCORES) for word in word_candidates}
    
    # Sortieren und Ausgeben der gefundenen Wörter
    # Primär nach Punktzahl (absteigend), sekundär nach Länge (absteigend), tertiär alphabetisch (aufsteigend)
    sorted_words = sorted(word_scores.items(), key=lambda x: (-x[1], -len(x[0]), x[0]))
    
    print(f"\nAnzahl gefundener Wörter: {len(sorted_words)}\n")
    
    # Ausgabe der Wörter mit ihren Punktzahlen
    for word, score in sorted_words:
        print(f"{word}: {score} Punkte")
    
    # Optional: Falls du eine kompakte Ausgabe möchtest, kannst du auch eine Zeile verwenden
    # print(', '.join([f"{word}: {score} Punkte" for word, score in sorted_words]))

if __name__ == "__main__":
    main()
