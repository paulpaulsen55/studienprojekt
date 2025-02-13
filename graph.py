import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from urllib.parse import urlparse

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

def statistische_analyse_und_diagramm(ausfuehrungszeiten, url_fuer_titel):
    """
    Führt statistische Analyse der Ausführungszeiten durch und erstellt Histogramm und Boxplot.
    Der Diagrammtitel wird basierend auf dem Port, dem ersten und dem letzten Pfad-Parameter generiert.
    Portzuordnung:
      8000: dev
      8010: apache
      8020: nginx
      8030: iis

    Beispiel:
      URL: localhost:8000/t1/parallel  =>  Diagrammtitel: "dev test1 parallel"

    Args:
        ausfuehrungszeiten (list): Liste der Ausführungszeiten.
        url_fuer_titel (str): Die URL, um den Diagrammtitel zu generieren.
    """
    if not ausfuehrungszeiten:
        print("Keine gültigen Ausführungszeiten für die Analyse vorhanden.")
        return

    df = pd.DataFrame({'Ausführungszeit (ms)': ausfuehrungszeiten})

    print("\nStatistische Kennzahlen:")
    print(df.describe())

    # Diagrammtitel neu generieren
    parsed_url = urlparse(url_fuer_titel)
    # Portbasiertes Mapping
    port = parsed_url.port
    server_mapping = {
        8000: "dev",
        8010: "apache",
        8020: "nginx",
        8030: "iis"
    }
    server_title = server_mapping.get(port, "unknown")
    
    pfad_teile = parsed_url.path.strip('/').split('/')
    if pfad_teile:
        first_param = pfad_teile[0]
        # Falls first_param im Format t<number> vorliegt, umwandeln in test<number>
        if first_param.startswith("t") and first_param[1:].isdigit():
            first_param = "test" + first_param[1:]
        last_param = pfad_teile[-1]  # Letzter Parameter
        diagramm_titel = f"{server_title} {first_param} {last_param}"
    else:
        diagramm_titel = "Ausführungszeiten"

    # Histogramm erstellen
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Ausführungszeit (ms)'], bins=30, kde=True)
    plt.title(f'Verteilung der Ausführungszeiten - {diagramm_titel}')
    plt.xlabel('Ausführungszeit (Millisekunden)')
    plt.ylabel('Häufigkeit')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f'histogram_ausfuehrungszeit_website_{diagramm_titel.replace(" ", "_")}.png')

    # Boxplot erstellen
    plt.figure(figsize=(8, 6))
    sns.boxplot(y=df['Ausführungszeit (ms)'])
    plt.title(f'Boxplot der Ausführungszeiten - {diagramm_titel}')
    plt.ylabel('Ausführungszeit (Millisekunden)')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f'boxplot_ausfuehrungszeit_website_{diagramm_titel.replace(" ", "_")}.png')

    plt.show()

if __name__ == "__main__":
    webseiten_url = "http://localhost:8010/t1/parallel" # Beispiel URL - HIER ANPASSEN
    wiederholungsanzahl = 1000 # Anzahl der Messungen

    gemessene_zeiten = erfasse_ausfuehrungszeiten(webseiten_url, wiederholungsanzahl)
    if gemessene_zeiten:
        statistische_analyse_und_diagramm(gemessene_zeiten, webseiten_url) # URL für Titel übergeben
        print(f"\nDiagramme als 'histogram_ausfuehrungszeit_website_{urlparse(webseiten_url).path.strip('/').replace('/', '_').upper()}.png' und 'boxplot_ausfuehrungszeit_website_{urlparse(webseiten_url).path.strip('/').replace('/', '_').upper()}.png' gespeichert.")
    else:
        print("Keine Ausführungszeiten erfasst. Bitte überprüfen Sie die URL und die Webseite.")