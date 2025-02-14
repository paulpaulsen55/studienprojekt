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
        time.sleep(0.1) # Kurze Pause
    return ausfuehrungszeiten

def statistische_analyse_und_diagramm(ausfuehrungszeiten, url_fuer_titel):
    """
    Führt statistische Analyse der Ausführungszeiten durch und erstellt Histogramm und Boxplot.
    Der Diagrammtitel wird basierend auf dem Port, dem Testfall, dem letzten Pfad-Parameter
    und der verwendeten Bibliothek generiert.
    Portzuordnung:
      8000: dev
      8010: apache
      8020: nginx
      8030: iis

    Beispiel:
      URL: http://localhost:8030/t1/parallel  
      =>  Diagrammtitel: "iis/Testfall 1/parallel/Seaborn"

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
        testcase = pfad_teile[0]
        if testcase.startswith("t") and testcase[1:].isdigit():
            testcase = f"Testfall {testcase[1:]}"
        last_param = pfad_teile[-1]  # Letzter Parameter
        library_name = "Seaborn"  # Bibliothek, die verwendet wurde
        diagramm_titel = f"{server_title}/{testcase}/{last_param}/{library_name}"
    else:
        diagramm_titel = "Ausführungszeiten"

    # Histogramm erstellen
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Ausführungszeit (ms)'], bins=30, kde=True)
    plt.title(f'Verteilung der Ausführungszeiten - {diagramm_titel}')
    plt.xlabel('Ausführungszeit (Millisekunden)')
    plt.ylabel('Häufigkeit')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f'histogram_ausfuehrungszeit_website_{diagramm_titel.replace("/", "_")}.png')

    # Boxplot erstellen
    plt.figure(figsize=(8, 6))
    sns.boxplot(y=df['Ausführungszeit (ms)'])
    plt.title(f'Boxplot der Ausführungszeiten - {diagramm_titel}')
    plt.ylabel('Ausführungszeit (Millisekunden)')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f'boxplot_ausfuehrungszeit_website_{diagramm_titel.replace("/", "_")}.png')

    plt.show()

if __name__ == "__main__":
    # Liste der URLs der Webserver (mit IIS korrekt getrennt)
    webseiten_urls = [
        "http://localhost:8000/t2/parallel",  # dev
        "http://localhost:8010/t2/parallel",  # apache
        "http://localhost:8020/t2/parallel",  # nginx
        "http://localhost:8030/t2/parallel"   # iis
    ]
    wiederholungsanzahl = 10  # Anzahl der Messungen pro Server

    # Helper mapping to extract the URL for a given server for diagram naming
    server_mapping = {
        8000: "dev",
        8010: "apache",
        8020: "nginx",
        8030: "iis"
    }
    url_mapping = {}
    for url in webseiten_urls:
        from urllib.parse import urlparse
        p = urlparse(url)
        port = p.port
        server = server_mapping.get(port, "unknown")
        # Bei mehrfachen URLs für den gleichen Server wird der erste verwendet
        if server not in url_mapping:
            url_mapping[server] = url

    all_data = []  # Liste zum Sammeln aller DataFrames

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

        # Für aggregierte Diagramme: Verwende die Testfall-Information aus der ersten URL
        first_url = webseiten_urls[0]
        parsed_first = urlparse(first_url)
        pfad_teile = parsed_first.path.strip('/').split('/')
        if pfad_teile:
            testcase = pfad_teile[0]
            if testcase.startswith("t") and testcase[1:].isdigit():
                testcase = f"Testfall {testcase[1:]}"
            last_param = pfad_teile[-1]
        else:
            testcase = "Unbekannter Testfall"
            last_param = "unbekannt"
        # Diagramm 1: KDE-Liniendiagramm für alle Server (Seaborn)
        diagramm_titel_agg = f"Mehrere Server - {testcase}/{last_param}"
        plt.figure(figsize=(10, 6))
        sns.kdeplot(
            data=df_all,
            x='Ausführungszeit (ms)',
            hue='Server',
            common_norm=False,
            fill=False,
            palette="bright"
        )
        plt.title(f'KDE-Liniendiagramm der Ausführungszeiten - {diagramm_titel_agg}')
        plt.xlabel('Ausführungszeit (Millisekunden)')
        plt.ylabel('Dichte')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(f'kde_liniendiagramm_ausfuehrungszeit_mehrere_server_{testcase.replace(" ", "")}_{last_param}.png')

        # Diagramm 2: KDE-Liniendiagramm für dev, apache, nginx (Seaborn)
        df_subset = df_all[df_all['Server'].isin(['dev', 'apache', 'nginx'])]
        diagramm_titel_subset = f"dev_apache_nginx - {testcase}/{last_param}"
        plt.figure(figsize=(10, 6))
        sns.kdeplot(
            data=df_subset,
            x='Ausführungszeit (ms)',
            hue='Server',
            common_norm=False,
            fill=False,
            palette="bright"
        )
        plt.title(f'KDE-Liniendiagramm der Ausführungszeiten - {diagramm_titel_subset}')
        plt.xlabel('Ausführungszeit (Millisekunden)')
        plt.ylabel('Dichte')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(f'kde_liniendiagramm_ausfuehrungszeit_dev_apache_nginx_{testcase.replace(" ", "")}_{last_param}.png')

        # Diagramm 3: Balkendiagramm für jeden Server (Matplotlib)
        for server in df_all['Server'].unique():
            df_server = df_all[df_all['Server'] == server]
            # Hole die URL, die für diesen Server gemappt wurde, um den Testfall und den letzten Parameter zu extrahieren
            server_url = url_mapping.get(server)
            if server_url:
                parsed = urlparse(server_url)
                pfad = parsed.path.strip('/').split('/')
                if pfad:
                    tc = pfad[0]
                    if tc.startswith("t") and tc[1:].isdigit():
                        tc = f"Testfall {tc[1:]}"
                    lp = pfad[-1]
                else:
                    tc, lp = "Unbekannt", "unbekannt"
            else:
                tc, lp = "Unbekannt", "unbekannt"

            diagramm_titel_bar = f"{server}/{tc}/{lp}"
            plt.figure(figsize=(10, 6))
            plt.hist(df_server['Ausführungszeit (ms)'], bins=30, color='skyblue', edgecolor='black')
            plt.xlabel('Ausführungszeit (ms)')
            plt.ylabel('Anzahl Messungen')
            plt.title(f'Histogramm der Ausführungszeiten - {diagramm_titel_bar}')
            plt.grid(axis='y', alpha=0.75)
            plt.savefig(f'histogram_ausfuehrungszeit_{server}_{tc.replace(" ", "")}_{lp}.png')
    else:
        print("Keine Ausführungszeiten erfasst für alle Server.")