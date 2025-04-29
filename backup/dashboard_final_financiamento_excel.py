
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Imóveis Caixa", layout="wide")
st.title("📊 Painel de Oportunidades - Imóveis Caixa")

caminho_arquivo = "Smart Leilões - Imóveis Caixa.xlsx"
arquivo = caminho_arquivo

@st.cache_data
def carregar_dados(arquivo):
    df = pd.read_excel(arquivo, sheet_name="Imóveis Caixa")
    df["Desconto"] = pd.to_numeric(df["Desconto"], errors="coerce")
    df["Preço Venda"] = pd.to_numeric(df["Preço Venda"], errors="coerce")
    df["Preço Avaliação"] = pd.to_numeric(df["Preço Avaliação"], errors="coerce")
    df["Lucro Potencial"] = df["Preço Avaliação"] - df["Preço Venda"]
    df["Modalidade"] = df["Modo Venda"].fillna("Outros")
    return df

def calcular_score(df):
    agrupado = df.groupby(["Cidade", "Tipo"])["Preço Venda"].mean().reset_index()
    agrupado.rename(columns={"Preço Venda": "Preço Médio"}, inplace=True)
    df = df.merge(agrupado, on=["Cidade", "Tipo"], how="left")
    df["Score"] = (
        (df["Desconto"] / 100) * 40 +
        (df["Lucro Potencial"] / df["Preço Médio"]) * 30 +
        (1 - (df["Preço Venda"] / df["Preço Médio"])) * 30
    ).clip(lower=0, upper=100)
    def classificar(score):
        if score > 75:
            return "🟢 Excelente"
        elif score > 50:
            return "🟡 Médio"
        else:
            return "🔴 Ruim"
    df["Classificação"] = df["Score"].apply(classificar)
    return df

if arquivo:
    df = carregar_dados(arquivo)
    df = calcular_score(df)

    with st.sidebar:
        st.header("🔍 Filtros")

        modalidades = st.multiselect("Modalidade de Venda", sorted(df["Modalidade"].unique()), default=sorted(df["Modalidade"].unique()))
        df = df[df["Modalidade"].isin(modalidades)]

        min_d, max_d = st.slider("Intervalo de Desconto (%)",
                                 float(df["Desconto"].min()),
                                 float(df["Desconto"].max()),
                                 (float(df["Desconto"].min()), float(df["Desconto"].max())))
        df = df[(df["Desconto"] >= min_d) & (df["Desconto"] <= max_d)]

        estados = st.multiselect("Estado", sorted(df["Estado"].dropna().unique()), default=sorted(df["Estado"].dropna().unique()))
        df = df[df["Estado"].isin(estados)]

        cidades = st.multiselect("Cidade", sorted(df["Cidade"].dropna().unique()), default=sorted(df["Cidade"].dropna().unique()))
        df = df[df["Cidade"].isin(cidades)]

        tipos = st.multiselect("Tipo de Imóvel", sorted(df["Tipo"].dropna().unique()), default=sorted(df["Tipo"].dropna().unique()))
        df = df[df["Tipo"].isin(tipos)]

        st.markdown("---")
        st.markdown("### 🧾 Condições da Oferta")

        oferta_financiamento = st.checkbox("Apenas imóveis que aceitam financiamento")

        if oferta_financiamento:
            df = df[df["Aceita Financiamento"].str.upper() == "SIM"]

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("🏠 Imóveis", len(df))
    col2.metric("💲 Desconto Médio", f'{df["Desconto"].mean():.2f}%')
    col3.metric("📊 Lucro Total", f'R$ {df["Lucro Potencial"].sum():,.2f}')

    # Cidade x Modalidade
    st.subheader("📍 Visão por Cidade e Modalidade")
    piv = df.groupby(["Cidade", "Modalidade"]).size().unstack(fill_value=0)
    piv["Total"] = piv.sum(axis=1)
    st.dataframe(piv.sort_values("Total", ascending=False), use_container_width=True)

    # Desconto por cidade
    st.subheader("🔥 Média de Desconto por Cidade")
    fig = px.bar(df.groupby("Cidade")["Desconto"].mean().sort_values(ascending=False).reset_index(),
                 x="Cidade", y="Desconto", color="Desconto", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)

    # Top 10
    st.subheader("🚀 Top 10 Descontos")
    top10 = df.sort_values("Desconto", ascending=False).head(10)
    top10["Ver Imóvel"] = top10["Site"].apply(lambda url: f"{url}" if pd.notna(url) else "")
    st.dataframe(top10[["Cidade", "Tipo", "Aceita Financiamento", "Desconto", "Lucro Potencial", "Classificação", "Ver Imóvel"]], use_container_width=True)

    # Tabela final
    st.subheader("📋 Tabela Completa")
    st.dataframe(df[["Cidade", "Tipo", "Modalidade", "Aceita Financiamento", "Desconto", "Preço Avaliação", "Preço Venda", "Lucro Potencial", "Classificação", "Site"]], use_container_width=True)

else:
    st.info("📂 Coloque o arquivo 'Smart Leilões - Imóveis Caixa.xlsx' na mesma pasta do script para iniciar.")
