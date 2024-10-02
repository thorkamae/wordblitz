import copy
import sys
from multiprocessing.dummy import Pool
from functools import partial
from itertools import repeat
from pprint import pprint
import threading

# Rekursionslimit erhöhen
sys.setrecursionlimit(5000)

# Initialisiere ein Thread-sicheres Set und einen Lock
word_candidates = set()
lock = threading.Lock()

def next_character(visited, current_row, current_column, dictionary):
    counter = 0
    if len(visited) > 7:
        return counter
    word = ""
    visited.append((current_row, current_column))
    for letter in visited:
        word += board[letter[0]][letter[1]]
    if word.upper() in dictionary and len(word) > 3:
        with lock:
            if word not in word_candidates:
                word_candidates.add(word)
                print(word)
    # Berechnung der nächsten Positionen
    prev_row = current_row - 1
    next_row = current_row + 1
    prev_column = current_column - 1
    next_column = current_column + 1
    # Überprüfen und rekursives Aufrufen für alle Richtungen
    if next_row < len(board) and ((next_row, current_column) not in visited):
        counter += next_character(copy.deepcopy(visited), next_row, current_column, dictionary)
    if next_row < len(board) and next_column < len(board[next_row]) and ((next_row, next_column) not in visited):
        counter += next_character(copy.deepcopy(visited), next_row, next_column, dictionary)
    if next_column < len(board[current_row]) and ((current_row, next_column) not in visited):
        counter += next_character(copy.deepcopy(visited), current_row, next_column, dictionary)
    if next_column < len(board[current_row]) and prev_row >= 0 and ((prev_row, next_column) not in visited):
        counter += next_character(copy.deepcopy(visited), prev_row, next_column, dictionary)
    if prev_row >= 0 and ((prev_row, current_column) not in visited):
        counter += next_character(copy.deepcopy(visited), prev_row, current_column, dictionary)
    if prev_row >= 0 and prev_column >= 0 and ((prev_row, prev_column) not in visited):
        counter += next_character(copy.deepcopy(visited), prev_row, prev_column, dictionary)
    if prev_column >= 0 and ((current_row, prev_column) not in visited):
        counter += next_character(copy.deepcopy(visited), current_row, prev_column, dictionary)
    if prev_column >= 0 and next_row < len(board) and ((next_row, prev_column) not in visited):
        counter += next_character(copy.deepcopy(visited), next_row, prev_column, dictionary)
    return counter

def create_board(input_str):
    arr = [
        [input_str[0], input_str[1], input_str[2], input_str[3]],
        [input_str[4], input_str[5], input_str[6], input_str[7]],
        [input_str[8], input_str[9], input_str[10], input_str[11]],
        [input_str[12], input_str[13], input_str[14], input_str[15]]
    ]
    print(input_str[0], input_str[1], input_str[2], input_str[3])
    print(input_str[4], input_str[5], input_str[6], input_str[7])
    print(input_str[8], input_str[9], input_str[10], input_str[11])
    print(input_str[12], input_str[13], input_str[14], input_str[15])
    return arr

# Importieren und Konvertieren der Wortliste in Großbuchstaben
try:
    with open('wordlist-de.txt', 'r', encoding='utf-8') as f:
        dictionary = set(word.strip().upper() for word in f)
except FileNotFoundError:
    print("Die Datei 'wordlist-de.txt' wurde nicht gefunden.")
    sys.exit(1)

# Eingabe des Boards vom Benutzer
user_input = input("Die Wörter? (max. 16): ").strip()
if len(user_input) != 16:
    print("Bitte genau 16 Zeichen eingeben.")
    sys.exit(1)
board = create_board(user_input)
word_candidates = set()
iterator = []

# Initialisieren der Iterationen für jedes Feld des Boards
for row in range(4):
    for column in range(4):
        iterator.append(([], row, column, dictionary))

results = []

# Verwenden von Multiprocessing für die Verarbeitung
with Pool(4) as pool:
    results = pool.starmap(next_character, iterator)

# Sortieren und Ausgeben der gefundenen Wörter
# Primär nach Länge (absteigend), sekundär alphabetisch (aufsteigend)
sorted_words = sorted(word_candidates, key=lambda x: (len(x), x))
print(f"Anzahl gefundener Wörter: {len(sorted_words)}")
pprint(sorted_words)
