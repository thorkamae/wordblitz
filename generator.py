import sys
from multiprocessing.dummy import Pool
import threading
import Levenshtein  # Importiere die Levenshtein-Bibliothek

# Rekursionslimit erhöhen
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

# Initialisiere ein Thread-sicheres Set und einen Lock
word_candidates = set()
lock = threading.Lock()

def calculate_word_score(word, letter_scores, length_bonus):
    """Berechnet die Gesamtpunktzahl eines Wortes basierend auf den Buchstabenpunkten und dem Längenbonus."""
    letter_score = sum(letter_scores.get(char, 0) for char in word.upper())
    bonus = length_bonus.get(len(word), 0)  # Standardbonus 0, falls die Wortlänge nicht im Dictionary ist
    total_score = letter_score + bonus
    return total_score

def next_character(visited, current_row, current_column, dictionary, board):
    if len(visited) > 9:  # Maximale Wortlänge 9
        return set()
    
    # Füge die aktuelle Position zum Pfad hinzu und bilde das Wort
    new_visited = visited + [(current_row, current_column)]
    word = ''.join([board[row][col] for row, col in new_visited])
    
    local_found = set()
    
    # Überprüfen, ob das Wort gültig ist
    if word.upper() in dictionary and len(word) > 5:
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
            local_found.update(next_character(new_visited, new_row, new_col, dictionary, board))
    
    return local_found

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

def group_words_by_similarity(sorted_words, max_distance=2):
    """
    Gruppiert Wörter basierend auf dem Levenshtein-Abstand.
    
    :param sorted_words: Liste von Tupeln (Wort, Score), sortiert alphabetisch.
    :param max_distance: Maximale Levenshtein-Distanz für die Gruppierung.
    :return: Liste von Gruppen, jede Gruppe ist eine Liste von Tupeln (Wort, Score).
    """
    groups = []
    
    for word, score in sorted_words:
        placed = False
        for group in groups:
            # Vergleiche mit dem ersten Wort der Gruppe
            if Levenshtein.distance(word, group[0][0]) <= max_distance:
                group.append((word, score))
                placed = True
                break
        if not placed:
            groups.append([(word, score)])
    
    return groups

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
    
    # Verwenden von Multiprocessing für die Verarbeitung
    with Pool(8) as pool:
        results = pool.starmap(next_character, iterator)
    
    # Vereinigung aller gefundenen Wörter
    all_found_words = set()
    for result in results:
        all_found_words.update(result)
    
    # Entfernen von Duplikaten und Filtern nach Länge und Dictionary
    word_candidates = {word for word in all_found_words if word.upper() in dictionary and len(word) > 4}
    
    # Berechnung der Punktzahlen für die gefundenen Wörter
    word_scores = {}
    for word in word_candidates:
        total_score = calculate_word_score(word, LETTER_SCORES, LENGTH_BONUS)
        word_scores[word] = total_score
    
    # Sortieren der Wörter alphabetisch für konsistente Gruppierung
    sorted_words_alpha = sorted(word_scores.items(), key=lambda x: x[0])
    
    # Gruppieren der Wörter basierend auf dem Levenshtein-Abstand
    max_distance = 3  # Du kannst diesen Wert anpassen
    grouped_words = group_words_by_similarity(sorted_words_alpha, max_distance)
    
    # Sortieren der Gruppen basierend auf der Summe der Punktzahlen (aufsteigend)
    grouped_words_sorted = sorted(
        grouped_words,
        key=lambda group: sum(score for word, score in group)
    )
    
    # Sortieren innerhalb jeder Gruppe nach Punktzahl absteigend und dann alphabetisch
    for group in grouped_words_sorted:
        group.sort(key=lambda x: (-x[1], x[0]))
    
    # Ausgabe der gruppierten Wörter
    total_words = len(sorted_words_alpha)
    print(f"\nAnzahl gefundener Wörter: {total_words}\n")
    
    for idx, group in enumerate(grouped_words_sorted, 1):
        # Berechne die Gesamtsumme der Punkte für die Gruppe
        group_total_score = sum(score for word, score in group)
        
        # Optional: Bestimme einen Gruppennamen, z.B. das erste Wort oder ein repräsentatives Wort
        group_words = [word for word, score in group]
        group_name = group_words[0]  # Du könntest eine intelligentere Methode wählen
        
        print(f"Gruppe {idx} (Gesamtpunkte: {group_total_score}):")
        for word, score in group:
            print(f"  {word}: {score} Punkte")
        print()  # Leerzeile zwischen den Gruppen

if __name__ == "__main__":
    main()
