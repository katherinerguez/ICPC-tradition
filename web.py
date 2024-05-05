import json 
import pandas as pd 

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

        