
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Carrega o CSV estratégico real
df = pd.read_csv("imoveis_goias_estrategico.csv", sep=";", encoding="utf-8")

# Conversões
df["Valor avaliação"] = pd.to_numeric(df["Valor avaliação"], errors="coerce")
df["Valor venda"] = pd.to_numeric(df["Valor venda"], errors="coerce")
df["Desconto (%)"] = pd.to_numeric(df["Desconto (%)"], errors="coerce")
df["Potencial"] = df["Desconto (%)"].apply(lambda x: "🔥 ALTO" if x >= 50 else ("👍 MÉDIO" if x >= 25 else "🧊 BAIXO"))

# Layout
st.set_page_config(page_title="Imóveis Caixa GO (Estratégico)", layout="wide")
st.title("🏠 Dashboard Estratégico - Imóveis Caixa Goiás")

# Filtros básicos
with st.expander("🔍 Filtros rápidos"):
    col1, col2 = st.columns(2)
    with col1:
        preco_min, preco_max = df["Valor venda"].min(), df["Valor venda"].max()
        preco_range = st.slider("Faixa de Preço (R$)", float(preco_min), float(preco_max), (float(preco_min), float(preco_max)))
    with col2:
        desc_min, desc_max = df["Desconto (%)"].min(), df["Desconto (%)"].max()
        desc_range = st.slider("Faixa de Desconto (%)", float(desc_min), float(desc_max), (float(desc_min), float(desc_max)))

with st.expander("🏦 Formas de Pagamento"):
    col3, col4 = st.columns(2)
    financiamento_opcoes = df["Permite financiamento"].dropna().unique().tolist()
    fgts_opcoes = df["Permite FGTS"].dropna().unique().tolist()
    with col3:
        financiamento = st.multiselect("Permite financiamento?", financiamento_opcoes)
    with col4:
        fgts = st.multiselect("Permite uso do FGTS?", fgts_opcoes)

# Aplicar filtros
df_filtrado = df.copy()
df_filtrado = df_filtrado[df_filtrado["Valor venda"].between(*preco_range)]
df_filtrado = df_filtrado[df_filtrado["Desconto (%)"].between(*desc_range)]
if financiamento: df_filtrado = df_filtrado[df_filtrado["Permite financiamento"].isin(financiamento)]
if fgts: df_filtrado = df_filtrado[df_filtrado["Permite FGTS"].isin(fgts)]

# Link como botão
df_filtrado["Link"] = df_filtrado["Link"].apply(lambda x: f"[🔗 Acessar]({x})" if pd.notna(x) else "")

# Exibição
st.markdown(f"🔎 **{len(df_filtrado)} imóveis encontrados.**")
if not df_filtrado.empty:
    st.dataframe(df_filtrado[[
        "Título", "Descrição", "Valor avaliação", "Valor venda",
        "Desconto (%)", "Potencial", "Permite FGTS", "Permite financiamento", "Link"
    ]])
else:
    st.warning("Nenhum imóvel corresponde aos filtros selecionados.")

# Gráficos
st.markdown("## 📊 Análises Visuais")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("### Top 10 palavras mais comuns no título")
    if not df_filtrado.empty:
        palavras = pd.Series(" ".join(df_filtrado["Título"].dropna()).lower().split())
        top_palavras = palavras.value_counts().head(10)
        fig1, ax1 = plt.subplots()
        top_palavras.plot(kind="barh", ax=ax1)
        ax1.set_xlabel("Frequência")
        ax1.set_ylabel("Palavra")
        ax1.invert_yaxis()
        st.pyplot(fig1)

with col_g2:
    st.markdown("### Top 10 maiores descontos (%)")
    if not df_filtrado.empty:
        top_desc = df_filtrado.sort_values(by="Desconto (%)", ascending=False).head(10)
        fig2, ax2 = plt.subplots()
        ax2.barh(top_desc["Título"], top_desc["Desconto (%)"])
        ax2.set_xlabel("Desconto (%)")
        ax2.set_ylabel("Imóvel")
        ax2.invert_yaxis()
        st.pyplot(fig2)
