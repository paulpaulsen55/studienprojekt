from io import BytesIO
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from urllib.parse import urlparse
import os

def erfasse_ausfuehrungszeiten(url, wiederholungen):
    print(f"Starte Messung für {url}...")
    ausfuehrungszeiten = []
    for _ in range(wiederholungen):
        try:            
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            execution_time_element = soup.find(id='executionTime')
            if execution_time_element:
                execution_zeit_text = execution_time_element.text.replace(' ms', '').strip()
                try:
                    execution_zeit = float(execution_zeit_text)
                    ausfuehrungszeiten.append(execution_zeit)
                except ValueError:
                    print(f"Warnung: Ungültige Ausführungszeit gefunden: '{execution_zeit_text}'. Überspringe diesen Wert.")
            else:
                print(f"Warnung: Element mit ID 'executionTime' nicht gefunden auf {url}")
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen von {url}: {e}\nAntworttext: {response.text}")
            continue
        time.sleep(0.1) # Kurze Pause
    return ausfuehrungszeiten

def erfasse_ausfuehrungszeiten_post(url, wiederholungen, image_paths, library_value="parallel"):
    print(f"Starte POST-Messung für {url} (library = {library_value}) mit Bildern: {image_paths}...")
    ausfuehrungszeiten = []
    post_data = {"library": library_value}
    
    # Check that image_paths is a list and every image exists
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    
    image_files = []
    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"Fehler: Bilddatei nicht gefunden unter Pfad: {image_path}. Breche Upload ab.")
            return []
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            image_files.append( (os.path.basename(image_path), image_data, 'image/png') )
        except Exception as e:
            print(f"Fehler beim Öffnen der Bilddatei '{image_path}': {e}. Breche Upload ab.")
            return []
    
    for _ in range(wiederholungen):
        try:
            files = [("images[]", (filename, BytesIO(data), 'image/png')) for (filename, data, _) in image_files]
            response = requests.post(url, data=post_data, files=files)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            execution_time_element = soup.find(id='executionTime')
            if execution_time_element:
                ausfuehrungszeit_text = execution_time_element.text.replace(' ms', '').strip()
                try:
                    ausfuehrungszeit = float(ausfuehrungszeit_text)
                    ausfuehrungszeiten.append(ausfuehrungszeit)
                except ValueError:
                    print(f"Warnung: Ungültiger Ausführungszeitwert: '{ausfuehrungszeit_text}'. Überspringe diesen Wert.")
            else:
                print(f"Warnung: Element mit ID 'executionTime' nicht gefunden auf {url}")
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Senden des POST-Requests an {url}: {e}\nAntworttext: {response.text}")
            continue
        time.sleep(0.1)
    return ausfuehrungszeiten

if __name__ == "__main__":
    webseiten_urls = [
        "http://localhost:8000/t3/upload",  # dev
        "http://localhost:8010/t3/upload",  # apache
        "http://localhost:8020/t3/upload",  # nginx
        "http://localhost:8030/t3/upload"   # iis
    ]
    wiederholungsanzahl = 100  # Anzahl der Messungen pro Server
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
        if server not in url_mapping:
            url_mapping[server] = url

    all_data = []
    for url in webseiten_urls:
        gemessene_zeiten = erfasse_ausfuehrungszeiten_post(
            url,
            wiederholungsanzahl,
            image_paths=["./diagramms/test_images/1.png", "./diagramms/test_images/2.jpeg", "./diagramms/test_images/3.png"],
            library_value="fibers" # "parallel" oder "fibers"
        )
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