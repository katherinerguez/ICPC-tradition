import json
import pandas as pd
import plotly.express as px
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from datetime import datetime as dt

st.title("Título pendiente")
st.markdown("Toda persona aficionada al mundo de la programación ha escuchado hablar alguna vez sobre la Competencia Internacional Universitaria de Programación, conocida por sus siglas en inglés ICPC (International Collegiate Programming Contest). Esta importante competición desafía a los estudiantes a resolver problemas complejos de programación en un tiempo limitado, poniendo a prueba sus habilidades, creatividad y trabajo en equipo; convirtiéndose en una plataforma perfecta para identificar y promover el talento en informática y ciencias de la computación.")
st.markdown("En los últimos años, muchas universidades a nivel global han sido representadas con el talento de muchos de sus estudiantes, incluidas las universidades de nuestro país. Por eso hemos analizado cómo se comportan las universidades con mejores resultados en esta competición en los últimos 15 años.")
st.header("Análisis", divider="gray")
with open('datos.json','r') as a:
    archivos=json.load(a)

#Convertir el json en un Dataframe
data=pd.DataFrame.from_dict(archivos, orient='index')
data.reset_index(inplace=True)
dfs_combinados=[]
for i in data[0]:
    i_dict = json.loads(i)
    combinado=pd.DataFrame.from_dict(i_dict, orient='index')
    dfs_combinados.append(combinado)
df = pd.concat(dfs_combinados, ignore_index=True)

#ranking inverso
point=[]
c=100
c1=1
while True:
    point.append(c)
    c-=1
    if c==0:
        c=100
    if c1==len(df['Rank']):
        break
    c1+=1
df_aux=pd.DataFrame({'University':df['University'],'Point':point})
df_aux = df_aux.groupby('University')['Point'].sum().reset_index()
df_aux = df_aux.sort_values(by='Point', ascending=False)
top_50 = df_aux.head(50)

#filtrar para 50 universidades
new_df=df

new_df=new_df[new_df['University'].isin(top_50['University'])]
new_df = new_df.reset_index(drop=True)
#ranking
ranking = pd.merge(top_50, new_df, on="University", how="inner")
u_ranking = ranking[['University', 'Point', "Country", "Prize"]]
u_ranking = ranking.drop(columns=['Point', "Prize"])
u_ranking = u_ranking.reindex(columns=['University', 'Country'])
u_ranking = u_ranking.drop_duplicates(subset=["University"])
u_ranking = u_ranking.reset_index(drop=True)
u_ranking.index += 1
st.markdown("Hoy en día Rusia encabeza el ranking con las 3 universidades con mejores resultados en la competición, seguida por el Instituto de Tecnología de Massachusetts (MIT) en Estados Unidos y la Universidad Nacional de Taiwán.")
st.dataframe(u_ranking,width=2000)

#Distribucion de universidades por paises 
st.header("Distribución de las universidades por países", divider= "gray")
selected_year = st.selectbox('Observa cuáles son los países con más universidades compitiendo en este evento en un anno en específico:', sorted(new_df['Anno'].unique()), key='selectbox_year1')
filtered_data = new_df[new_df['Anno'] == selected_year]
grouped_data = filtered_data.groupby('Country')['University'].count().reset_index()
grouped_data = grouped_data.sort_values(by='University', ascending=False)

fig = px.bar(grouped_data, x='Country', y='University', title=f'Cantidad de universidades por país en el año {selected_year}')
st.plotly_chart(fig)

#Promedio de scores por anno
st.header("Scores en la competición", divider="gray")
new_df['Score'] = pd.to_numeric(new_df['Score'], errors='coerce')
new_df['Score'] = new_df['Score'].fillna(0).astype(int)
avg_scores_by_year = new_df.groupby('Anno')['Score'].mean().reset_index()

fig = px.bar(avg_scores_by_year, x='Anno', y='Score', title='Promedio de scores por año')
st.plotly_chart(fig)

#prize total
new_df['Prize'] = new_df['Prize'].astype(int)
df_university =new_df.groupby(['University',"Country"])['Prize'].sum().reset_index()

df_university=df_university.sort_values('Prize',ascending=False)
df_total=df_university
df_total.reset_index(drop=True, inplace=True)
df_total.index+=1
df_university=df_university.head(10)
new_df1=new_df[new_df["University"].isin(df_university["University"]) ]
grouped_df = df.groupby(['University', 'Anno'])['Prize'].sum().reset_index()

st.header("Cantidad de dinero obtenido por las universidades", divider= "gray")
st.markdown('Los equipos que terminen en las cuatro primeras posiciones recibirán medallas de oro. Los equipos que finalicen del quinto al octavo lugar recibirán medallas de plata. Aquellos equipos que finalicen del noveno al duodécimo lugar recibirán medallas de bronce. Se podrán otorgar medallas de bronce adicionales.'

'El equipo con mayor puntuación es el Campeón del Mundo y recibirá la Copa de Campeón del Mundo y placas. Los otros doce mejores equipos, los campeones de América del Norte, los campeones de América Latina, los campeones de Europa, los campeones del Pacífico Sur, los campeones de Asia y los campeones de África y Medio Oriente también recibirán placas.'

'El equipo campeón del mundo recibirá 15.000 dólares. Cada uno de los otros tres equipos con medalla de oro recibirá 7.500 dólares. Cada equipo que obtenga la medalla de plata recibirá 6.000 dólares. Cada equipo que obtenga la medalla de bronce recibirá 3.000 dólares.'

'Cortesía de la Sociedad de Honor de Ciencias de la Computación de la UPE, el premio a la primera solución será de 1500 dólares y el primero en resolver el problema "X" será de 1200 dólares (para todos los problemas resueltos excepto el primero).(https://icpc.global/worldfinals/acmicpc)')

st.header("Ranking por prize", divider="gray")
st.dataframe(df_total,width=1000)

selected_university = st.multiselect('Selecciona las universidades que quieres visualizar:',options=new_df1["University"].unique(), default="Peking University")  
df_filtered = new_df1[new_df1["University"].isin(selected_university) | (selected_university == [])]  
fig = px.line(df_filtered, x="Anno", y="Prize", color="University", title='Ganancias en ICPC por universidades', markers=True)
st.plotly_chart(fig)

#prize por paises
st.subheader("Cantidad de dinero obtenido por las universidades distribuido por países", divider= "gray")

new_df['Anno'] = new_df['Anno'].astype(int)
if 'fecha_minima' not in st.session_state:
    st.session_state.fecha_minima = dt(new_df['Anno'].min(), 1, 1).date()
if 'fecha_maxima' not in st.session_state:
    st.session_state.fecha_maxima = dt(new_df['Anno'].max(), 12, 31).date()

fecha_inicio = st.selectbox("Selecciona el año de inicio", options=range(new_df['Anno'].min(), new_df['Anno'].max() + 1))

fecha_fin = st.selectbox("Selecciona el año de finalización", options=range(new_df['Anno'].min(), new_df['Anno'].max() + 1))

filter = new_df[(new_df['Anno'] >= fecha_inicio) & (new_df['Anno'] <= fecha_fin)]

#grafico de barras por grupos para representar los prizes de paises por annos
fig_prize = go.Figure()

for i in filter['Country'].unique():
    fig_prize.add_trace(go.Bar(
        x=filter[filter['Country'] == i]['Anno'],
        y=filter[filter['Country'] == i]['Prize'],
        name=i,
        marker_color=None 
    ))

fig_prize.update_layout(
    title='Cantidad de dinero recibido de las universidades por país',
    xaxis_title='Año de las competencias',
    yaxis_title='Cantidad de dinero',
    barmode='group'
)

st.plotly_chart(fig_prize)

#transmision de conocimiento
df=new_df

grafos = {}

for universidad in df["University"].unique():
    grafo = nx.Graph()
    for index, row in df[df["University"] == universidad].iterrows():
        grafo.add_node(row["Anno"], participants=row["Participants"])
    
    for nodo1, data1 in grafo.nodes(data=True):
        for nodo2, data2 in grafo.nodes(data=True):
            if nodo1 != nodo2 and set(data1['participants']).intersection(set(data2['participants'])):
                grafo.add_edge(nodo1, nodo2)
    
    grafos[universidad] = grafo

universidad_seleccionada = st.selectbox("Selecciona una universidad:", list(grafos.keys()))
grafo_seleccionado = grafos[universidad_seleccionada]
fig = go.Figure()

pos = nx.spring_layout(grafo_seleccionado, k=20)
for nodo in grafo_seleccionado.nodes:
    fig.add_trace(go.Scatter(x=[pos[nodo][0]], y=[pos[nodo][1]], mode='markers+text', text=str(nodo), marker=dict(size=25),hoverinfo='text', hovertext='<br>'.join(grafo_seleccionado.nodes[nodo]['participants'])))
for arista in grafo_seleccionado.edges:
    x0, y0 = pos[arista[0]]
    x1, y1 = pos[arista[1]]
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines'))

fig.update_layout(title=f"Grafo de {universidad_seleccionada}",
                 xaxis=dict(visible=False),
                 yaxis=dict(visible=False))

st.plotly_chart(fig)