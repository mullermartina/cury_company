import streamlit as st
from PIL import Image

#pra por emoji, seria page_icon= dentro dos () abaixo. Edit> Emoji> escolher
st.set_page_config(
    page_title='Home' 
)

#image_path = 'pages'
#image = Image.open( image_path + '\logo.png' )
image = Image.open( 'logo2.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write( '# Cury Company Growth Dashboard' )

st.markdown(
    """
        Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
        ### Como utilizar esse Growth Dashboard?
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tática: Indicadores semanais de crescimento.
            - Visão Geográfica: Insights de geolocalização.
        - Visão Entregador:
            - Acompanhamento dos indocadores semanais de crescimento
        - Visão Restaurante:
            - Indicadores semanais de crescimento dos restaurantes
        ### Ask for Help
        - Time de Data Science no Discord
            = @meigarom
""" )

#Pra ficarem distribuidos os graficos em todo o espaço, meigarom pos st.set_page_config( page_title='Visão Empresa', layout='wide' )
# acima das funçoes em visao empresa, vis entrega e vis rest