
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Imóveis Caixa", layout="wide")
st.title("📊 Painel de Oportunidades - Imóveis Caixa")

# === Funções ===
@st.cache_data
def carregar_dados(caminho):
    df = pd.read_excel(caminho, sheet_name="Imóveis Caixa")
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

# === Dados ===
arquivo = "Smart Leilões - Imóveis Caixa.xlsx"
df = carregar_dados(arquivo)
df = calcular_score(df)

# === Carregar filtros salvos (se existir) ===
filtros_carregados = {}
if os.path.exists("filtros_salvos.json"):
    with open("filtros_salvos.json", "r") as f:
        filtros_carregados = json.load(f)

# === Filtros ===
with st.sidebar:
    st.header("🔍 Filtros")

    todas_modalidades = sorted(df["Modalidade"].dropna().unique())
    modalidades = st.multiselect("Modalidade de Venda", todas_modalidades, default=filtros_carregados.get("modalidades", todas_modalidades))
    df = df[df["Modalidade"].isin(modalidades)]

    desconto_min = float(df["Desconto"].min())
    desconto_max = float(df["Desconto"].max())
    min_d, max_d = st.slider("Intervalo de Desconto (%)",
                             desconto_min, desconto_max,
                             (filtros_carregados.get("desconto_min", desconto_min), filtros_carregados.get("desconto_max", desconto_max)))
    df = df[(df["Desconto"] >= min_d) & (df["Desconto"] <= max_d)]

    todos_estados = sorted(df["Estado"].dropna().unique())
    estados = st.multiselect("Estado", todos_estados, default=filtros_carregados.get("estados", todos_estados))
    df = df[df["Estado"].isin(estados)]

    todas_cidades = sorted(df["Cidade"].dropna().unique())
    cidades = st.multiselect("Cidade", todas_cidades, default=filtros_carregados.get("cidades", todas_cidades))
    df = df[df["Cidade"].isin(cidades)]

    todos_tipos = sorted(df["Tipo"].dropna().unique())
    tipos = st.multiselect("Tipo de Imóvel", todos_tipos, default=filtros_carregados.get("tipos", todos_tipos))
    df = df[df["Tipo"].isin(tipos)]

    st.markdown("---")
    st.markdown("### 🧾 Condições da Oferta")

    financiamento = st.checkbox("Apenas imóveis que aceitam financiamento", value=filtros_carregados.get("financiamento", False))
    fgts = st.checkbox("Apenas imóveis que aceitam FGTS", value=filtros_carregados.get("fgts", False))
    disputa = st.checkbox("Apenas imóveis em disputa", value=filtros_carregados.get("disputa", False))
    lucro = st.checkbox("Apenas imóveis com decréscimo no preço", value=filtros_carregados.get("lucro", False))

    if financiamento:
        df = df[df["Aceita Financiamento"].str.upper() == "SIM"]
    if fgts:
        df = df[df["Modalidade"].str.contains("FGTS", case=False, na=False)]
    if disputa:
        df = df[df["Modalidade"].str.contains("Leilão", case=False, na=False)]
    if lucro:
        df = df[df["Lucro Potencial"] > 0]

    st.markdown("---")
    if st.button("💾 Salvar Filtros"):
        filtros = {
            "modalidades": modalidades,
            "desconto_min": min_d,
            "desconto_max": max_d,
            "estados": estados,
            "cidades": cidades,
            "tipos": tipos,
            "financiamento": financiamento,
            "fgts": fgts,
            "disputa": disputa,
            "lucro": lucro
        }
        with open("filtros_salvos.json", "w") as f:
            json.dump(filtros, f)
        st.success("✅ Filtros salvos com sucesso!")

# === KPIs e Tabelas ===
col1, col2, col3 = st.columns(3)
col1.metric("🏠 Imóveis", len(df))
col2.metric("💲 Desconto Médio", f'{df["Desconto"].mean():.2f}%')
col3.metric("📊 Lucro Total", f'R$ {df["Lucro Potencial"].sum():,.2f}')

st.subheader("📍 Visão por Cidade e Modalidade")
piv = df.groupby(["Cidade", "Modalidade"]).size().unstack(fill_value=0)
piv["Total"] = piv.sum(axis=1)
st.dataframe(piv.sort_values("Total", ascending=False), use_container_width=True)

st.subheader("🔥 Média de Desconto por Cidade")
fig = px.bar(df.groupby("Cidade")["Desconto"].mean().sort_values(ascending=False).reset_index(),
             x="Cidade", y="Desconto", color="Desconto", color_continuous_scale="RdYlGn")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🚀 Top 10 Descontos")
top10 = df.sort_values("Desconto", ascending=False).head(10)
top10["Ver Imóvel"] = top10["Site"].apply(lambda url: f"{url}" if pd.notna(url) else "")
st.dataframe(top10[["Cidade", "Tipo", "Aceita Financiamento", "Desconto", "Lucro Potencial", "Classificação", "Ver Imóvel"]], use_container_width=True)

st.subheader("📋 Tabela Completa")
st.dataframe(df[["Cidade", "Tipo", "Modalidade", "Aceita Financiamento", "Desconto", "Preço Avaliação", "Preço Venda", "Lucro Potencial", "Classificação", "Site"]], use_container_width=True)
