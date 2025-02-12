import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

def erfasse_ausfuehrungszeiten(url, wiederholungen):
    """
    Erfasst die Ausführungszeiten von einer Webseite, indem der Wert
    des Elements mit der ID 'executionTime' abgerufen wird.

    Args:
        url (str): Die URL der Webseite, die die Ausführungszeit enthält.
        wiederholungen (int): Die Anzahl der Wiederholungen der Messung.

    Returns:
        list: Eine Liste der erfassten Ausführungszeiten.
    """
    ausfuehrungszeiten = []
    for _ in range(wiederholungen):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Fehlerhafte Statuscodes werfen eine Ausnahme
            soup = BeautifulSoup(response.content, 'html.parser')
            execution_time_element = soup.find(id='executionTime')
            if execution_time_element:
                execution_zeit_text = execution_time_element.text.replace(' ms', '').strip() # " ms" entfernen und Leerzeichen
                try:
                    execution_zeit = float(execution_zeit_text)
                    ausfuehrungszeiten.append(execution_zeit)
                except ValueError:
                    print(f"Warnung: Ungültige Ausführungszeit gefunden: '{execution_zeit_text}'. Überspringe diesen Wert.")
            else:
                print(f"Warnung: Element mit ID 'executionTime' nicht gefunden auf {url}")
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen von {url}: {e}")
            continue # Bei Fehler Webseite abrufen, nächste Wiederholung versuchen
        time.sleep(0.1) # Kurze Pause, um Server nicht zu überlasten (optional)
    return ausfuehrungszeiten

def statistische_analyse_und_diagramm(ausfuehrungszeiten):
    """
    Führt statistische Analyse der Ausführungszeiten durch und erstellt Histogramm und Boxplot.

    Args:
        ausfuehrungszeiten (list): Liste der Ausführungszeiten.
    """
    if not ausfuehrungszeiten:
        print("Keine gültigen Ausführungszeiten für die Analyse vorhanden.")
        return

    df = pd.DataFrame({'Ausführungszeit (ms)': ausfuehrungszeiten})

    print("\nStatistische Kennzahlen:")
    print(df.describe())

    # Histogramm erstellen
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Ausführungszeit (ms)'], bins=30, kde=True)
    plt.title('Verteilung der Ausführungszeiten')
    plt.xlabel('Ausführungszeit (Millisekunden)')
    plt.ylabel('Häufigkeit')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig('histogram_ausfuehrungszeit_website.png')

    # Boxplot erstellen
    plt.figure(figsize=(8, 6))
    sns.boxplot(y=df['Ausführungszeit (ms)'])
    plt.title('Boxplot der Ausführungszeiten')
    plt.ylabel('Ausführungszeit (Millisekunden)')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig('boxplot_ausfuehrungszeit_website.png')

    plt.show()

if __name__ == "__main__":
    webseiten_url = "http://localhost:8010/t1/parallel" # Ersetzen Sie dies mit der tatsächlichen URL Ihrer Webseite
    wiederholungsanzahl = 100 # Anzahl der Messungen

    gemessene_zeiten = erfasse_ausfuehrungszeiten(webseiten_url, wiederholungsanzahl)
    if gemessene_zeiten:
        statistische_analyse_und_diagramm(gemessene_zeiten)
        print(f"\nDiagramme als 'histogram_ausfuehrungszeit_website.png' und 'boxplot_ausfuehrungszeit_website.png' gespeichert.")
    else:
        print("Keine Ausführungszeiten erfasst. Bitte überprüfen Sie die URL und die Webseite.")