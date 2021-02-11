#importar bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

url_confirmados = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_mortes = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recuperados = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
url_iso = 'https://raw.githubusercontent.com/AnthonyEbert/COVID-19_ISO-3166/master/JohnsHopkins-to-A3.csv'


@st.cache
def load_dados(url):
    """
    Carrega os dados do covid-19.

    :return: DataFrame com colunas selecionadas.
    """
    columns = {
        'Lat': 'latitude',
        'Long': 'longitude'
    }

    dados = pd.read_csv(url)
    dados = dados.rename(columns=columns)
    dados = dados.dropna(subset=['latitude', 'longitude'])

    iso = pd.read_csv(url_iso)
    dict_iso = dict(zip(iso['Country/Region'], iso['alpha3']))
    dados['alpha3'] = dados['Country/Region'].map(dict_iso)

    return dados


def america_do_sul(df):
    """
    Carrega os dados do covid-19 para os países da América do Sul.

    :return: DataFrame com colunas selecionadas.
    """
    paises_1 = ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname',
                'Uruguay', 'Venezuela', 'French Guiana', 'Falkland Islands']
    paises_2 = ['Falkland Islands', 'French Guiana']

    america_sul_1 = df[df['Country/Region'].str.contains('|'.join(paises_1), na=False)]
    america_sul_2 = df[df['Province/State'].str.contains('|'.join(paises_2), na=False)]

    df = pd.concat([america_sul_1, america_sul_2], axis=0)
    df['Country/Region'] = df['Country/Region'].replace({
        'France': 'French Guiana',
        'United Kingdom': 'Falkland Islands (Malvinas)'
    })

    df = df.drop('Province/State', axis=1)

    return df


# DADOS
# carregar os dados
df_conf = load_dados(url_confirmados)
df_mortes = load_dados(url_mortes)
df_recup = load_dados(url_recuperados)

df_sul_conf = america_do_sul(df_conf)
df_sul_mortes = america_do_sul(df_mortes)
df_sul_recup = america_do_sul(df_recup)

# separar casos por país
mundo_conf = df_conf.groupby('Country/Region').sum().iloc[:, 2:]
mundo_mortes = df_mortes.groupby('Country/Region').sum().iloc[:, 2:]
mundo_recup = df_recup.groupby('Country/Region').sum().iloc[:, 2:]

am_sul_conf = df_sul_conf.groupby('Country/Region').sum().iloc[:, 2:]
am_sul_mortes = df_sul_mortes.groupby('Country/Region').sum().iloc[:, 2:]
am_sul_recup = df_sul_recup.groupby('Country/Region').sum().iloc[:, 2:]

# informacoes gerais
informacoes_mundo = [mundo_conf.iloc[:,-1], mundo_mortes.iloc[:,-1], mundo_recup.iloc[:,-1]]
atual_mundo = pd.concat(informacoes_mundo, axis=1)
atual_mundo.columns = ['confirmados', 'mortes', 'recuperados']
atual_mundo['fatalidade'] = round(atual_mundo['mortes'] / atual_mundo['confirmados'], 2)

informacoes_am_sul = [am_sul_conf.iloc[:,-1], am_sul_mortes.iloc[:,-1], am_sul_recup.iloc[:,-1]]
atual_am_sul = pd.concat(informacoes_am_sul, axis=1)
atual_am_sul.columns = ['confirmados', 'mortes', 'recuperados']
atual_am_sul['fatalidade'] = round(atual_am_sul['mortes'] / atual_am_sul['confirmados'], 2)

# SIDEBAR
# selecionar parâmetros
st.sidebar.header('Selação de parâmetros')
info_sidebar = st.sidebar.empty()

# selecionar mundo ou america do sul
tipo_mapa = ['Mundo', 'América do Sul']
filtro_mapa = st.sidebar.selectbox('Selação de mapa', tipo_mapa)

# contato e creditos
st.sidebar.subheader('Contato:')
st.sidebar.markdown('[Linkedin](https://www.linkedin.com/in/leonardo-vilani-selan/)')
st.sidebar.markdown('[Github/Portfolio](https://github.com/leovilani/portfolio)')

st.sidebar.subheader('Creditos:')
st.sidebar.markdown('"COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at'
                    ' Johns Hopkins University." [LINK](https://github.com/CSSEGISandData/COVID-19)')
st.sidebar.markdown('"Johns Hopkins Country/Region column to ISO-3166 alpha-3 country code." '
                    '[LINK](https://github.com/AnthonyEbert/COVID-19_ISO-3166)')

# MAIN
# head
st.title('Dashboard Covid-19 no Mundo')
st.markdown("Em 31 de Dezembro de 2019, a [Organização Mundial da Saúde (OMS)]"
            "(https://www.who.int/emergencies/diseases/novel-coronavirus-2019)"
            " alertou sobre diversos casos de pneumonia em Wuhan, província de Hubei na "
            "China. O vírus não era relacionado com nenhum outro conhecido. Não sabíamos como esse novo vírus afetaria "
            "a vida das pessoas ao redor do mundo.")
st.markdown('O objetivo desse Dashboard é uma análise com gráficos dos casos de Covid após mais de um ano de '
            'contaminação. Ele irá atualizar os dados automaticamente de acordo com o Dataset da [Johns Hopkins]'
            '(https://github.com/CSSEGISandData/COVID-19).')

# data e dados
data_att = datetime.strptime(mundo_conf.columns[-1], "%m/%d/%y")
st.subheader(f'Atualizado em: {data_att.strftime("%d-%m-%Y")}')
st.markdown(f'**Confirmados**: {atual_mundo.confirmados.sum()}')
st.markdown(f'**Mortes**: {atual_mundo.mortes.sum()}')
st.markdown(f'**Recuperados**: {atual_mundo.recuperados.sum()}')

# grafico
with st.spinner('Carragando dados...'):
    if filtro_mapa == 'Mundo':

        line_conf = mundo_conf.sum()
        line_mortes = mundo_mortes.sum()
        line_recup = mundo_recup.sum()

        # grafico de contagem
        tipo_contagem = ['Confirmados', 'Mortes', 'Recuperados']
        filtro_contagem = st.selectbox('Gráfico de contagem', tipo_contagem)

        if filtro_contagem == 'Confirmados':
            fig = px.bar(x=line_conf.index, y=line_conf.values,
                         title='Contagem de casos confirmados de Covid-19 no Mundo',
                         labels={
                             'x': 'Tempo (dia)',
                             'y': 'Casos confirmados'
                         })
            st.plotly_chart(fig)
        if filtro_contagem == 'Mortes':
            fig = px.bar(x=line_mortes.index, y=line_mortes.values,
                         title='Contagem de mortes por Covid-19 no Mundo',
                         labels={
                             'x': 'Tempo (dia)',
                             'y': 'Mortes'
                         })
            st.plotly_chart(fig)
        if filtro_contagem == 'Recuperados':
            fig = px.bar(x=line_recup.index, y=line_recup.values,
                         title='Contagem de recuperados de Covid-19 no Mundo',
                         labels={
                             'x': 'Tempo (dia)',
                             'y': 'Recuperados'
                         })
            st.plotly_chart(fig)

        # grafico de linha
        labels = list(atual_mundo.index)
        default = list(atual_mundo.sort_values('confirmados', ascending=False).index)
        df_t = mundo_conf.T

        filtro_line = st.multiselect(
            label="Escolha de países para gráfico de linha",
            options=labels,
            default=default[:5]
        )
        line_filtrado = df_t[filtro_line]
        fig = px.line(line_filtrado, x=line_filtrado.index, y=line_filtrado.columns,
                      title='Número de casos por país')
        fig.update_layout(xaxis_title='Tempo', yaxis_title='Casos confirmados', legend_title='País')
        st.plotly_chart(fig)

        # mapa
        mapa = df_conf[['Country/Region', 'alpha3']]
        mapa['total'] = df_conf.iloc[:, -2]

        fig = px.choropleth(mapa, locations="alpha3",
                            color="total",
                            hover_name="Country/Region",
                            color_continuous_scale=px.colors.sequential.OrRd,
                            labels={
                                'total': 'Casos Confirmados'
                            },
                            title='Mapa de casos de Covid-19 no Mundo')
        st.plotly_chart(fig)

        # tabela
        st.dataframe(atual_mundo.sort_values('confirmados', ascending=False))

with st.spinner('Carragando dados...'):
    if filtro_mapa == 'América do Sul':

        line_conf = am_sul_conf.sum()
        line_mortes = am_sul_mortes.sum()
        line_recup = am_sul_recup.sum()

        # grafico de contagem
        tipo_contagem = ['Confirmados', 'Mortes', 'Recuperados']
        filtro_contagem = st.selectbox('Gráfico de contagem', tipo_contagem)

        if filtro_contagem == 'Confirmados':
            fig = px.bar(x=line_conf.index, y=line_conf.values,
                         title='Contagem de casos confirmados de Covid-19 na América do Sul',
                         labels={
                             'x': 'Tempo (dia)',
                             'y': 'Casos confirmados'
                         })
            st.plotly_chart(fig)
        if filtro_contagem == 'Mortes':
            fig = px.bar(x=line_mortes.index, y=line_mortes.values,
                         title='Contagem de mortes por Covid-19 na América do Sul',
                         labels={
                             'x': 'Tempo (dia)',
                             'y': 'Mortes'
                         })
            st.plotly_chart(fig)
        if filtro_contagem == 'Recuperados':
            fig = px.bar(x=line_recup.index, y=line_recup.values,
                         title='Contagem de recuperados de Covid-19 na América do Sul',
                         labels={
                             'x': 'Tempo (dia)',
                             'y': 'Recuperados'
                         })
            st.plotly_chart(fig)

        # grafico de linha
        labels = list(atual_am_sul.index)
        default = list(atual_am_sul.sort_values('confirmados', ascending=False).index)
        df_t = am_sul_conf.T

        filtro_line = st.multiselect(
            label="Escolha de países para gráfico de linha",
            options=labels,
            default=default[:3]
        )
        line_filtrado = df_t[filtro_line]
        fig = px.line(line_filtrado, x=line_filtrado.index, y=line_filtrado.columns,
                      title='Número de casos por país')
        fig.update_layout(xaxis_title='Tempo', yaxis_title='Casos confirmados', legend_title='País')
        st.plotly_chart(fig)

        mapa = df_sul_conf[['Country/Region', 'latitude', 'longitude']]
        mapa['total'] = df_sul_conf.iloc[:, -2]

        fig = px.scatter_geo(mapa, lat='latitude', lon='longitude', hover_name='Country/Region',
                             size='total', scope='south america',
                             size_max=50, labels={'total': 'Casos'},
                             title='Número de casos na América do Sul')
        st.plotly_chart(fig)

        # tabela
        st.dataframe(atual_am_sul.sort_values('confirmados', ascending=False))
