# Definiere die Pfade zur Eingabe- und Ausgabedatei
input_datei = 'wordlist-de.txt'          # Ersetze dies mit dem Pfad zu deiner Eingabedatei
output_datei = 'wordlist-de_neu.txt'    # Ersetze dies mit dem gewünschten Pfad für die Ausgabedatei

# Funktion zur Umwandlung der Umlaute und Großschreibung
def umlaut_umwandeln(word):
    ersetzungen = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'Ä': 'AE',
        'Ö': 'OE',
        'Ü': 'UE',
        # Optional: Wenn du auch 'ß' ersetzen möchtest, kannst du folgende Zeile hinzufügen
        # 'ß': 'SS'
    }
    for umlaut, ersatz in ersetzungen.items():
        word = word.replace(umlaut, ersatz)
    return word.upper()

# Lies die Eingabedatei, verarbeite die Wörter und schreibe in die Ausgabedatei
def verarbeite_wortliste(input_pfad, output_pfad):
    try:
        with open(input_pfad, 'r', encoding='utf-8') as infile, \
             open(output_pfad, 'w', encoding='utf-8') as outfile:
            for zeile in infile:
                wort = zeile.strip()
                if wort:  # Stelle sicher, dass die Zeile nicht leer ist
                    if len(wort) <= 10:  # Überprüfe, ob das Wort 10 Zeichen oder weniger hat
                        neues_wort = umlaut_umwandeln(wort)
                        outfile.write(neues_wort + '\n')
                    else:
                        # Optional: Du kannst hier eine Nachricht ausgeben oder das Wort anderweitig verarbeiten
                        pass  # In diesem Fall werden Wörter mit mehr als 10 Zeichen einfach übersprungen
        print(f"Die umgewandelte Wortliste wurde erfolgreich in '{output_pfad}' gespeichert.")
    except FileNotFoundError:
        print(f"Die Datei '{input_pfad}' wurde nicht gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

# Führe die Verarbeitung durch
if __name__ == "__main__":
    verarbeite_wortliste(input_datei, output_datei)
