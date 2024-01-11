# Libraries
import pandas as pd
from haversine import haversine
import datetime
import streamlit as st

#blbiotecas necessarias
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', layout='wide' )
# -------------------------------------------------------------
# Funções
# -------------------------------------------------------------
def clean_code( df1 ): # prof copiou da visao_empresa_module... ja tava pronto e funcionando.. pq nao?
    """ Esta funçao tem a responsabilidade de limpar o dataframe

    Tipos de limpeza:
    1. remoção dos dados NaN
    2. mudança do tipo da coluna de dados
    3. remoçao dos espaços das variaveis de texto
    4. formataçao daata
    5. limpeza da coluna de tempo (remoçao do texto da variavel numerica)

    Input: Dataframe
    Output: Dataframe
    """#qdo ler no futuro, eu bato o olho e sei do que se trata
    
    # 1. convertendo a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    # 2. convertendo a coluna Ratings de texto para numero decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    # 3. convertendoa coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')
    #df1.dtypes
    
    # 4. convertendo multiple_deliveries de texto para numero inteiro ( int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ') & (df1['multiple_deliveries'].notna())
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    # 6. removendo os espaços dentro de strings/texto/object SEM O FOR >> Devo fazer isso só eo colunas que tem o espaço e nao pro df #inteiro
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    
    # 7. limpando a coluna de time taken
    #apply é um comando q permite q eu aplique outro comando linha a linha.. esse x seria tipo o x de f(x) = ax + b.
    #lambda x no caso é f(x). na pratica dai, x tem o valor de cada linha, col time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1

def top_delivers( df1, top_asc ):
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby(['City', 'Delivery_person_ID'])
               .mean()
               .sort_values(['City', 'Time_taken(min)'], ascending=top_asc) #com o top_asc, posso usar a fç 2x, pros +rap e +lento
               .reset_index() )

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True)

    return df3

# ------------------ Início da Estrutura lógica do código -----------------------------
# -------------
#Import dataset
# -------------
df = pd.read_csv( 'dataset/train.csv' )

df1= df.copy()

# ---------------------
# Limpando os dados
# ---------------------
df1 = clean_code( df )

# ==================================================================
# Barra Lateral no Streamlit 
# ==================================================================
st.header( 'Marketplace- Visão Entregadores' )


image_path = 'logo.png'
image = Image.open( image_path ) #Image é a biblio
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' ) #sidebar q faz ir pra barra do lado. fosse so o markdown ia ser titulo na tela ppal
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" ) #ssim eu crio uma linha
st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( #esse slider é pra ter uma barrinha q corre entre essas datas
    'Até qual valor?',
    value=datetime.datetime( 2022, 4, 13), #value é o valor default q o sist vai assumir se
    # o usuario  nao escolher nenhum
    min_value=datetime.datetime( 2022, 2, 11),
    max_value=datetime.datetime( 2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condiçoes do transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# ajeitando o filtro
# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ==================================================================
# Layout no Streamlit
# ==================================================================
tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', '_', '_' ] )
with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4,  gap='large' )
        # PRA ESSES 4 NUM ABAIXO DARIA PRA FAZER UMA FUNÇAO SÓ, PQ O Q MUDA É A COL E SE É MIN OU MAX:
        #def calculate_big_number( col, operation ):
            #if operation == 'max':
                #results = df1.loc[:, col].max()
            #elif operation =='min':
                #results = df1.loc[:, col].min()
                
            #return results

        # Aí, chamaria essa função assim:
        # number = calculate_big_number( 'Delivery_person_Age', operation='max' )
        # col1.metric ( 'Maior idade', number )
    
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max() #aqui nao precisa ter funçao pq ja é uma linha só
            col1.metric ( 'Maior idade', maior_idade )

        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric ( 'Menor idade', menor_idade )
            
        with col3:
            melhor_condicao =  df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condiçao', melhor_condicao )
            
        with col4:
            pior_condicao =  df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', pior_condicao )
            
    with st.container(): 
        st.markdown( """---""" )
        st.title( 'Avaliações' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliação média por entregador' ) #aqui tb daria pra fazer mas é uma linha só
            df_average_ratings_per_deliver = ( df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']]
                                                  .groupby('Delivery_person_ID')
                                                  .mean()
                                                  .reset_index() )
            st.dataframe( df_average_ratings_per_deliver )

        with col2:
            st.markdown( '##### Avaliaçao media por transito' ) #aqui e o debaixo tb daria pra fazer uma funçao só
            df_avg_std_ratings_per_traffic = (df1.loc[ :, [ 'Delivery_person_Ratings', 'Road_traffic_density' ] ]
                                                  .groupby( 'Road_traffic_density' )
                                                  .agg( {'Delivery_person_Ratings': ['mean', 'std']} ))
            df_avg_std_ratings_per_traffic.columns = [ 'delivery_mean', 'delivery_std' ]
            df_avg_std_ratings_per_traffic.reset_index()
            st.dataframe( df_avg_std_ratings_per_traffic )
            
            st.markdown( '##### Avaliaçao media por clima' )
            df_avg_std_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                      .groupby('Weatherconditions')
                                      .agg({'Delivery_person_Ratings': ['mean', 'std']}) )
            df_avg_std_weather.columns = ['delivery mean', 'delivery std']
            df_avg_std_weather.reset_index()
            st.dataframe( df_avg_std_weather )

    with st.container():
        st.markdown( """---""" )
        st.title( 'Velocidade de Entrega' )

        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown( '##### Top Entregadores mais rapidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )

        with col2:
            st.markdown( '##### Top entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )