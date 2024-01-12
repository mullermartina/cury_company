# Libraries
import pandas as pd # "caso dê erro por nao ter o pandas fazer pip install pandas no terminal"
from haversine import haversine
import datetime
import streamlit as st

#blbiotecas necessarias
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import folium
import numpy as np
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

def distance( df1, fig ):
    if fig == False: #num retorna o valor da media e noutro retorna figura
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance(km)'] = df1.loc[:, cols].apply( lambda x:
                                        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),        (x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis = 1)
        avg_distance = np.round( df1['distance(km)'].mean(), 1 )
        
        return avg_distance
        
    else:
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        df1['distance'] = ( df1.loc[:, cols].apply( lambda x:
                                        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                   (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )
        avg_distance = df1.loc[:, ['City','distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.05, 0])])
        
        return fig

def avg_std_time_delivery( df1, festival, op):
    """
        Esta funçao calcula o tempo medio e o desvio padrao do tempo de entrega.
        Paramentros:
            Input:
                - df: Dataframe com os dados necessarios para o calculo
                - op: Tipo de operaçao que precisa ser calculado
                    'avg_time': Calcula o tempo medio
                    'std_time': Calcula o desvio padrao do tempo
            Output:
                - df: Dataframe com 2 colunas e 1 linha
    """
    df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']].groupby( 'Festival' ).agg( {'Time_taken(min)': ['mean', 'std']} ) )
    df_aux.columns = [ 'avg_time', 'std_time' ]
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, op], 2 )

    return df_aux

def avg_std_time_graph (df1 ):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
            
    fig = go.Figure()
    fig.add_trace(go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'],error_y=dict( type='data', array=df_aux['std_time'])) ) 
    fig.update_layout(barmode='group')

    return fig

def avg_std_time_on_traffic( df1 ):
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    return fig
    
# ------------------ Início da Estrutura lógica do código -----------------------------
# -------------
#Import dataset
# -------------
df = pd.read_csv( 'dataset/train.csv' ) 

# -----------------
# Limpando os dados
# -----------------
df1 = clean_code( df ) #vi que o meigarom nem faz copia... a propria limpeza uma cópia limpa

# ==================================================================
# Barra Lateral no Streamlit 
# ==================================================================
st.header( 'Marketplace- Visão Entregadores' )

#meigarom foi ate o powered by comunidade ds e decidiu por uma imagem. comandos dessa açao abaixo
image_path = 'logo2.png' #pra ter certeza q o caminho do arq ta certo, poso abrir outro terminal (outro! 1 ta ocupado com o streamlit)
# ls - l e ai vejo q a imagem ta na pasta q to trabalhando. comando pwd no terminal da todo caminho do arq (repos blabla)
# ai dnetro das aspas posso colocar toooodo caminho. algo tipo 'documents/repos/ftc..'
#image_path= 'Users\Administrator\Documents\repos\repos_2023\ftc_programacao_python' .. testei e nao deu certo ee
#antes de por tudo na mesma pag, tava somente 'logo.png'.. qdo foi pra dentro de pages q tive q mudar
image = Image.open( image_path ) #Image é a biblio
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' ) #sidebar q faz ir pra barra do lado. fosse so o markdown ia ser titulo na tela ppal
# ser ### ou ## ou # difere no tamanho da letra, como se fosse titulo, subtitulo e tal
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" ) #ssim eu crio uma linha

st.sidebar.markdown( '## Selecione uma data limite' )
#descobrindo o valor de data minimo: csg ver pq, qdo clico no titulo ta col, ele ordena
#st.dataframe( df1 )
date_slider = st.sidebar.slider( #esse slider é pra ter uma barrinha q corre entre essas datas
    'Até qual valor?',
    value=datetime.datetime( 2022, 4, 13), #value é o valor default q o sist vai assumir se
    # o usuario  nao escolher nenhum
    min_value=datetime.datetime( 2022, 2, 11),
    max_value=datetime.datetime( 2022, 4, 6),
    format='DD-MM-YYYY')

#st.header( date_slider ) era só teste pra visualizar data e hora
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

# filtro de transito >> pedaço isin é pra ver se ta dentro duma lista. lista essa q o usuario ta escolhendo dentre as opçoes
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ==================================================================
# Layout no Streamlit
# ==================================================================
tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', '_', '_' ] )

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            #st.markdown( '###### Coluna 1' )
            delivery_unique = len(df1['Delivery_person_ID'].unique())
            col1.metric( 'Entregadores unicos', delivery_unique )
            
        with col2:
            avg_distance = distance( df1, fig=False )
            col2.metric( 'Distancia média', avg_distance )
            
        with col3:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'avg_time' )            
            col3.metric( 'Tempo médio', df_aux )

        with col4:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'std_time' )
            col4.metric( 'STD entrega', df_aux )
            
        with col5:
            df_aux = avg_std_time_delivery( df1, 'No', 'avg_time' )
            col5.metric( 'Tempo médio', df_aux )
            
        with col6:
            df_aux = avg_std_time_delivery( df1, 'No', 'std_time' )
            col6.metric( 'STD entrega', df_aux )
            

    with st.container():
        st.markdown( """---""" )
        col1, col2 = st.columns( 2 )

        with col1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

    with st.container():
        st.markdown( """---""" )
        st.title( 'Distribuiçao do Tempo' )

        col1, col2 = st.columns( 2 )
        with col1:
            fig = distance( df1, fig=True )
            st.plotly_chart( fig, use_container_width=True ) #meigarom usou só o fig mas acho q precisa do outro param.. usei outro cod
            
        with col2:
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig )
            