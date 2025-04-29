import streamlit as st
import pandas as pd

def mostrar_dashboard():
    st.title("📊 Painel de Oportunidades")

    df = carregar_dados("smart_leiloes_imoveis_caixa.xlsx")
    # filtros, indicadores, tabela...
    st.dataframe(df)

def carregar_dados(caminho):
    df = pd.read_excel(caminho)
    # trata colunas e cálculo de score
    return df
