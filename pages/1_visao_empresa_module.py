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
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', layout='wide' )
# -------------------------------------------------------------
# Funções
# -------------------------------------------------------------

def clean_code( df1 ): #o df do parametro deve ser o mesmo df q tá no código
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
    df1.shape
    
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

def order_metric( df1 ): #poderia passar as colunas de parametro tb
    # vi q tanto na fç qto no uso dela, o param é df1
    cols = ['ID', 'Order_Date']
    
    # seleçao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    # desenhar o gráfico de linhas
    fig = px.bar( df_aux, x='Order_Date', y='ID' )

    return fig

def traffic_order_share( df1 ):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density').count().reset_index()
    
    # lembrando q quero o percentual
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    
    fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

def traffic_order_city( df1 ):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    # df_aux ao printar, noto os NaN. aí, devo remover os NaN. meigarom disse q melhor seria remover la na limpeza dos dados
    df_aux = df_aux.loc[df_aux['City'] != 'NaN'] #removi pq ja fiz isso na limpeza (ok entao)
    ddf_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN']
    
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City' ) #o size é o tamanho da bolha
    
    return fig

def order_by_week( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' ) # Mascara %U considera q primeiro dia da semana é domingo
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
            
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig #AQUI MEIGAROM ESCREVEU Q ERA RETURN DF1... SOA  ERRADO MAS TEJE REGISTRADO

def order_share_by_week( df1 ):
    # Quantidade de pedidos por semana / Numero unico de entregadores por semana
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    
   
    df_aux = pd.merge( df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    fig = px.line( df_aux, x='week_of_year', y='order_by_deliver')
            
    return fig

def country_maps( df1 ):
    df_aux = ( df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                  .groupby(['City','Road_traffic_density'])
                  .median()
                  .reset_index() )
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
        #df_aux = df_aux.head() deu certo sem o head mas qdo ha mtsss linhas as vzs o pc trava

        # PRA DESENHAR MAPA, USO BIBLIO FOLIUM
    map = folium.Map() # Aqui, eu desenhei o mapa e guardei na variavel chamada map

    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )  # Maker coloca um ponto no mapa
# o popup eu uso pra mostrar informações qdo eu clicar em cima do pino
        folium_static( map, width=1024, height=600 )
        return None #ja vai desenhar o mapa. nao precisa de return

# ------------------ Início da Estrutura lógica do código -----------------------------
# -------------
#Import dataset
# -------------
df = pd.read_csv( 'dataset/train.csv' ) #no colabs se usa o cl.files.upload. aqui nao precisa. nao tenho pq mandar pra nuvem

# ---------------------
# Limpando os dados
# ---------------------
df1= df.copy()

df1 = clean_code( df ) # DEU TROCENTOS ERROS... O PROBLEMA NO FIM ERA  Q ESSA LINHA TAVA ACIMA DA DF1= DF.COPY.. EU TAVA USANDO DF1
#SEM O DITO DF1 EXISTIR

# ==================================================================
# Barra Lateral no Streamlit >> apos criar grafs, vimos qo fitlro nao se conecta aos grafs. meigarom so agora vai resolver isso 
# ==================================================================
st.header( 'Marketplace- Visão Cliente' )
#st.header('This is a header') # meigarom copiou esse comando da documentação do streamlit
#após copiar, ele foi no terminal e, ao inves de python visao_empresa.py, passou streamlit run visao_empresa.py

image_path = 'logo.png' #pra ter certeza q o caminho do arq ta certo, poso abrir outro terminal (outro! 1 ta ocupado com o streamlit)
# ls - l e ai vejo q a imagem ta na pasta q to trabalhando. comando pwd no terminal da todo caminho do arq (repos blabla)
# ai dnetro das aspas posso colocar toooodo caminho. algo tipo 'documents/repos/ftc..'
#image_path= 'Users\Administrator\Documents\repos\repos_2023\ftc_programacao_python' .. testei e nao deu certo ee
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
tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', 'Visão Tática', 'Visão Geográfica' ] )
#palavra reservada with: assim, consigo 'dizer' em q tab cada info estará
with tab1:
    with st.container():
        # Order Metric
        fig = order_metric( df1 )
        st.markdown( '# Order by Day')
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        col1, col2 = st.columns( 2 ) #passo o numero de colunas q quero. pelo esboço de dashborad, q fizemos, no 'meio' tem 2 col
#pra fazer as coisas dentro de cada col, tb preciso usar o with
        with col1:
            fig = traffic_order_share( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_width=True )
            
        with col2:
            st.header( 'Traffic Order City' )
            fig = traffic_order_city( df1 )
            st.plotly_chart( fig, use_container_width=True )

with tab2:
    with st.container():
        st.markdown( '# Order by Week' )
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True)
        
    with st.container():
        st.markdown( '# Order Share by Week' )
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True)
        
# a reta se influencia por variaçao do num e do denom.. pra saber exatamente o q influenciou, deveria plotar s´o num e só o denom
with tab3:
    st.markdown( '# Country Maps' )
    country_maps( df1 )
