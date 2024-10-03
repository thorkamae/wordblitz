import sys
import random
from multiprocessing import Pool, cpu_count
from collections import Counter
import string

# Rekursionslimit erhöhen (optional, je nach Bedarf)
sys.setrecursionlimit(5000)

# Punktesystem für deutsche Buchstaben (ähnlich wie Scrabble)
LETTER_SCORES = {
    'A': 1, 'B': 3, 'C': 2, 'D': 3, 'E': 1, 'F': 3, 'G': 2, 'H': 2,
    'I': 1, 'J': 6, 'K': 3, 'L': 2, 'M': 3, 'N': 1, 'O': 2, 'P': 4,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 2, 'V': 6, 'W': 4, 'X': 8,
    'Y': 6, 'Z': 4
}

# Längenbonus für Wörter basierend auf ihrer Länge
LENGTH_BONUS = {
    1: 1, 2: 3, 3: 4, 4: 6,
    5: 9, 6: 11, 7: 14, 8: 17,
    9: 19, 10: 22
}

# Buchstabenhäufigkeit basierend auf deutscher Sprache (optional angepasst)
LETTER_FREQUENCY = {
    'A': 6.5, 'B': 1.9, 'C': 3.0, 'D': 5.1, 'E': 17.4, 'F': 1.7,
    'G': 3.0, 'H': 4.8, 'I': 7.3, 'J': 0.3, 'K': 1.6, 'L': 3.4,
    'M': 2.5, 'N': 9.8, 'O': 2.5, 'P': 0.8, 'Q': 0.2, 'R': 7.0,
    'S': 7.3, 'T': 6.2, 'U': 4.2, 'V': 0.7, 'W': 1.9, 'X': 0.1,
    'Y': 0.04, 'Z': 1.1
}

# Erstelle eine Liste von Buchstaben entsprechend ihrer Häufigkeit
def create_letter_pool():
    pool = []
    for letter, freq in LETTER_FREQUENCY.items():
        pool.extend([letter] * int(freq * 10))  # Multiplizieren für bessere Granularität
    return pool

LETTER_POOL = create_letter_pool()

def calculate_word_score(word, letter_scores, length_bonus):
    """Berechnet die Gesamtpunktzahl eines Wortes basierend auf den Buchstabenpunkten und dem Längenbonus."""
    letter_score = sum(letter_scores.get(char, 0) for char in word.upper())
    bonus = length_bonus.get(len(word), 0)  # Standardbonus 0, falls die Wortlänge nicht im Dictionary ist
    total_score = letter_score + bonus
    return total_score

def create_board(input_str):
    """Erstellt ein 4x4-Board aus einem 16-Zeichen-String."""
    return [
        [input_str[0], input_str[1], input_str[2], input_str[3]],
        [input_str[4], input_str[5], input_str[6], input_str[7]],
        [input_str[8], input_str[9], input_str[10], input_str[11]],
        [input_str[12], input_str[13], input_str[14], input_str[15]]
    ]

def next_character(args):
    """Rekursive Funktion zur Suche nach Wörtern auf dem Board."""
    visited, current_row, current_column, dictionary, board, min_len, max_len = args
    if len(visited) > max_len:  # Maximale Wortlänge
        return set()
    
    # Füge die aktuelle Position zum Pfad hinzu und bilde das Wort
    new_visited = visited + [(current_row, current_column)]
    word = ''.join([board[row][col] for row, col in new_visited])
    
    local_found = set()
    
    # Überprüfen, ob das Wort gültig ist
    if word.upper() in dictionary and min_len <= len(word) <= max_len:
        local_found.add(word)
    
    # Definition der möglichen Bewegungsrichtungen (N, NE, E, SE, S, SW, W, NW)
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                  (1, 0), (1, -1), (0, -1), (-1, -1)]
    
    for dr, dc in directions:
        new_row = current_row + dr
        new_col = current_column + dc
        # Überprüfen, ob die neue Position innerhalb des Rasters liegt und nicht bereits besucht wurde
        if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]) and (new_row, new_col) not in new_visited:
            # Rekursiver Aufruf mit der neuen Position
            local_found.update(next_character((new_visited, new_row, new_col, dictionary, board, min_len, max_len)))
    
    return local_found

def process_random_board(args):
    """Generiert ein zufälliges Board, sucht nach Wörtern und gibt die gefundenen Wörter zurück."""
    dictionary, letter_pool, min_len, max_len = args
    # Generiere ein zufälliges 16-Buchstaben-Board
    board_letters = ''.join(random.choices(letter_pool, k=16))
    board = create_board(board_letters)
    
    # Optional: Debugging - Ausgabe des generierten Boards
    # print("Generated Board:")
    # for row in board:
    #     print(" ".join(row))
    
    # Initialisieren der Iterationen für jedes Feld des Boards
    iterator = [([], row, column, dictionary, board, min_len, max_len) for row in range(4) for column in range(4)]
    
    # Verarbeitung der Iterationen sequenziell, um verschachtelte Pools zu vermeiden
    all_found_words = set()
    for args in iterator:
        all_found_words.update(next_character(args))
    
    # Filtern der Wörter nach Dictionary und Mindest-/Maximallänge
    word_candidates = {word for word in all_found_words if word.upper() in dictionary and min_len <= len(word) <= max_len}
    
    return word_candidates

def main():
    # Anzahl der zufälligen Boards, die durchgespielt werden sollen
    NUM_BOARDS = 100  # Beispiel: 100.000 Boards

    # Wortlängenbereich
    MIN_WORD_LENGTH = 4
    MAX_WORD_LENGTH = 5

    # Importieren und Konvertieren der Wortliste in Großbuchstaben
    try:
        with open('wordlist-de.txt', 'r', encoding='utf-8') as f:
            dictionary = set(word.strip().upper() for word in f if word.strip())
    except FileNotFoundError:
        print("Die Datei 'wordlist-de.txt' wurde nicht gefunden.")
        sys.exit(1)
    
    # Überprüfen, ob die Wortliste Wörter im gewünschten Längenbereich enthält
    sample_words = [word for word in dictionary if MIN_WORD_LENGTH <= len(word) <= MAX_WORD_LENGTH]
    if not sample_words:
        print(f"Keine Wörter mit der Länge zwischen {MIN_WORD_LENGTH} und {MAX_WORD_LENGTH} gefunden.")
        sys.exit(1)
    else:
        print(f"Anzahl der Wörter im Wörterbuch mit Länge zwischen {MIN_WORD_LENGTH} und {MAX_WORD_LENGTH}: {len(sample_words)}")

    # Initialisiere einen Counter für Wortfrequenzen
    word_counter = Counter()

    # Definiere Batch-Größe für Fortschrittsanzeige
    BATCH_SIZE = 1000
    boards_processed = 0

    # Argumente für die Pool-Verarbeitung vorbereiten
    pool_args = [(dictionary, LETTER_POOL, MIN_WORD_LENGTH, MAX_WORD_LENGTH) for _ in range(NUM_BOARDS)]
    
    # Verwenden von Pool für parallele Generierung und Verarbeitung
    with Pool(cpu_count()) as pool:
        # Verwenden von imap für eine effizientere Verarbeitung mit chunksize
        results = pool.imap(process_random_board, pool_args, chunksize=100)
        
        for i, words in enumerate(results, 1):
            word_counter.update(words)
            if i % BATCH_SIZE == 0 or i == NUM_BOARDS:
                print(f"Verarbeitet: {i}/{NUM_BOARDS} Boards")
    
    print("Alle Boards verarbeitet.")
    
    # Identifizieren der häufigsten Wörter
    most_common_words = word_counter.most_common(100)  # Top 100 Wörter
    
    if not most_common_words:
        print("Keine Wörter gefunden. Überprüfen Sie die Wortliste und die Wortlängenbeschränkungen.")
        sys.exit(1)
    
    # Berechnung der Punktzahlen für die häufigsten Wörter
    word_scores = {word: calculate_word_score(word, LETTER_SCORES, LENGTH_BONUS) for word, _ in most_common_words}
    
    # Sortieren der häufigsten Wörter nach Häufigkeit und Punktzahl
    sorted_words = sorted(most_common_words, key=lambda x: (-x[1], -word_scores[x[0]], x[0]))
    
    print(f"\nTop {len(sorted_words)} häufigste Wörter:\n")
    
    # Ausgabe der Wörter mit ihren Häufigkeiten und Punktzahlen
    for word, count in sorted_words:
        score = word_scores[word]
        print(f"{word}: {count} Vorkommen, {score} Punkte")
    
    # Optional: Speichern der Ergebnisse in einer Datei
    with open('word_frequencies.txt', 'w', encoding='utf-8') as f:
        for word, count in sorted_words:
            score = word_scores[word]
            f.write(f"{word}: {count} Vorkommen, {score} Punkte\n")
    
    print("\nErgebnisse wurden in 'word_frequencies.txt' gespeichert.")

if __name__ == "__main__":
    main()
