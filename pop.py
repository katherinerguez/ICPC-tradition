import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

def sracp(url,c):
# Realizar la solicitud GET a la URL
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

# Encontrar todas las tablas con la clase específica
    tables = soup.find_all('table', class_='table table-bordered table-striped table-hover w-auto')

    data = []
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            cols = [col.get_text(strip=True) for col in cols]
            data.append(cols)

# Crear un DataFrame
    df = pd.DataFrame(data, columns=['Rank', 'Country', 'Team', 'Score', 'Penalty', 'Prize'])
    df= df[['Rank','Country', 'Team','Score','Prize']]
    df= df.head(100)

    df[['University','Teams', 'Participants']] = df['Team'].str.extract(r'(.+)\((.+)\)\:(.+)')
# Eliminar los caracteres ':' y ',' de la lista de participantes


# Eliminar la columna original 'Team'
    df.drop('Team', axis=1, inplace=True)

    def convert_to_list(value):
        if isinstance(value, list):
            return value
        else:
            return [value]
    df["Anno"]=c
    df['Participants'] = df['Participants'].apply(convert_to_list)
    df.set_index('Teams', inplace=True)
    df['Prize'] = df['Prize'].fillna(0)
    for b in df['Prize']:
            a=b.split("$")
            try:
                int(a[-1])
                resultado = a[-1]
            except ValueError:
                resultado = "0"              
            df['Prize'] = df['Prize'].replace(b, resultado)

    json2019 = df.T.to_json()
    return json2019
json_data={}

for item in range(0,15):
    c=2023-item
    url=f'https://cphof.org/standings/icpc/{c}'
    print(url)
    data=sracp(url,c)
    if data is not None:
        json_data[c] = data
nombre_archivo = "datos.json"
with open(nombre_archivo, "w",encoding='utf-8') as archivo_json:
    json.dump(json_data, archivo_json,ensure_ascii=False, indent=4)