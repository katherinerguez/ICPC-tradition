import json
import pandas as pd
import plotly.express as px
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

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
st.header("Ranking",divider="gray")
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

#prize
new_df['Prize'] = new_df['Prize'].astype(int)
df_university =new_df.groupby(['University',"Country"])['Prize'].sum().reset_index()

df_university=df_university.sort_values('Prize',ascending=False)
df_university=df_university.head(10)
new_df1=new_df[new_df["University"].isin(df_university["University"]) ]
grouped_df = df.groupby(['University', 'Anno'])['Prize'].sum().reset_index()

st.header("Cantidad de dinero obtenido por las universidades", divider= "gray")
selected_university = st.multiselect('Selecciona las universidades que quieres visualizar:',options=new_df1["University"].unique(), default="Peking University")  
df_filtered = new_df1[new_df1["University"].isin(selected_university) | (selected_university == [])]  
fig = px.line(df_filtered, x="Anno", y="Prize", color="University", title='Ganancias en ICPC por universidades', markers=True)
st.plotly_chart(fig)
st.write(df_university)

#transmision de conocimiento
df=new_df
grafos = {}

for universidad in df["University"].unique():
    grafo = nx.Graph()
    for index, row in df[df["University"] == universidad].iterrows():
        participantes = row["Participants"]
        for participante in participantes:
            grafo.add_node(row["Anno"], participants=participante)

    for i in range(1, len(grafo.nodes)):
        anno1 = list(grafo.nodes)[i - 1]
        anno2 = list(grafo.nodes)[i]
        participantes_anno1 = set(grafo.nodes[anno1]['participants'])
        participantes_anno2 = set(grafo.nodes[anno2]['participants'])
        if participantes_anno1.intersection(participantes_anno2):
            grafo.add_edge(anno1, anno2)
    grafos[universidad] = grafo

universidad_seleccionada = st.selectbox("Selecciona una universidad:", grafos.keys())
grafo_seleccionado = grafos[universidad_seleccionada]
fig = go.Figure()

pos = nx.spring_layout(grafo_seleccionado)
for nodo in grafo_seleccionado.nodes:
    fig.add_trace(go.Scatter(x=[pos[nodo][0]], y=[pos[nodo][1]], mode='markers+text', text=str(nodo)))
for arista in grafo_seleccionado.edges:
    x0, y0 = pos[arista[0]]
    x1, y1 = pos[arista[1]]
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines'))

fig.update_layout(title=f"Grafo de {universidad_seleccionada}",
                  xaxis=dict(visible=False),
                  yaxis=dict(visible=False))

st.plotly_chart(fig)