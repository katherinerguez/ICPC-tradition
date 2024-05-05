import json
import pandas as pd
import plotly.express as px
import streamlit as st

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