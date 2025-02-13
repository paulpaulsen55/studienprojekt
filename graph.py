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
    print(f"Starte Messung für {url}...")
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
            print(f"Fehler beim Abrufen von {url}: {e}\nAntworttext: {response.text}")
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
    # Liste der URLs der Webserver (mit IIS korrekt getrennt)
    webseiten_urls = [
        "http://localhost:8000/t1/parallel",  # dev
        "http://localhost:8010/t1/parallel",  # apache
        "http://localhost:8020/t1/parallel",  # nginx
        "http://localhost:8030/t1/parallel"   # iis
    ]
    wiederholungsanzahl = 100  # Anzahl der Messungen pro Server

    all_data = []  # Liste zum Sammeln aller DataFrames
    server_mapping = {
        8000: "dev",
        8010: "apache",
        8020: "nginx",
        8030: "iis"
    }

    for url in webseiten_urls:
        gemessene_zeiten = erfasse_ausfuehrungszeiten(url, wiederholungsanzahl)
        if gemessene_zeiten:
            parsed_url = urlparse(url)
            port = parsed_url.port
            server_title = server_mapping.get(port, "unknown")
            df_temp = pd.DataFrame({'Ausführungszeit (ms)': gemessene_zeiten})
            df_temp['Server'] = server_title
            all_data.append(df_temp)
        else:
            print(f"Keine Ausführungszeiten erfasst für {url}")

    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)
        print("\nStatistische Kennzahlen pro Server:")
        print(df_all.groupby('Server')['Ausführungszeit (ms)'].describe())

        # Diagramm 1: Liniendiagramm (Kernel Density Estimate) für jeden Server
        plt.figure(figsize=(10, 6))
        sns.kdeplot(
            data=df_all,
            x='Ausführungszeit (ms)',
            hue='Server',
            common_norm=False,
            fill=False,
            palette="bright"
        )
        plt.title('KDE-Liniendiagramm der Ausführungszeiten - Mehrere Server')
        plt.xlabel('Ausführungszeit (Millisekunden)')
        plt.ylabel('Dichte')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig('kde_liniendiagramm_ausfuehrungszeit_mehrere_server.png')

        # Diagramm 2: Histogramm (Säulen) für jeden Server, Balken nebeneinander
        plt.figure(figsize=(10, 6))
        sns.histplot(
            data=df_all,
            x='Ausführungszeit (ms)',
            hue='Server',
            bins=30,
            kde=True,
            multiple="dodge",  # Balken nebeneinander statt übereinander
            alpha=0.8,
            palette="bright"
        )
        plt.title('Histogramm der Ausführungszeiten - Mehrere Server')
        plt.xlabel('Ausführungszeit (Millisekunden)')
        plt.ylabel('Häufigkeit')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig('histogram_ausfuehrungszeit_mehrere_server.png')
    else:
        print("Keine Ausführungszeiten erfasst für alle Server.")