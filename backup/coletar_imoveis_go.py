
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import re

# Carregar CSV
df = pd.read_csv("go.csv", sep=";", encoding="latin1", skiprows=5, header=None)
df.columns = [
    "NUMERO_IMOVEL", "UF", "Cidade", "Bairro", "Endereco",
    "Valor avaliacao", "Valor venda", "Codigo", "Descricao",
    "Modo Venda", "Link"
]

# Conversão
df["Valor venda"] = df["Valor venda"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
df["Valor avaliacao"] = df["Valor avaliacao"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
df["Desconto (%)"] = round(100 * (1 - df["Valor venda"] / df["Valor avaliacao"]), 2)
df["Permite financiamento"] = df["Modo Venda"].apply(lambda x: "Sim" if "SFI" in x.upper() else "Não")
df["Tipo"] = df["Descricao"].str.extract(r'^(.*?)\,')
df["Permite FGTS"] = "Sim"
df["Potencial"] = df["Desconto (%)"].apply(lambda x: "🔥 ALTO" if x >= 50 else ("👍 MÉDIO" if x >= 25 else "🧊 BAIXO"))

# Layout
st.set_page_config(page_title="Imóveis Caixa GO", layout="wide")
st.title("🏠 Dashboard Estratégico - Imóveis Caixa Goiás")

# Filtros
with st.expander("📍 Localização"):
    col1, col2 = st.columns(2)
    with col1:
        cidades = st.multiselect("Cidade", sorted(df["Cidade"].dropna().unique()))
    with col2:
        bairros = st.multiselect("Bairro", sorted(df["Bairro"].dropna().unique()))

with st.expander("🏘️ Características do Imóvel"):
    col3, col4 = st.columns(2)
    with col3:
        tipos = st.multiselect("Tipo de Imóvel", sorted(df["Tipo"].dropna().unique()))
    with col4:
        modos_venda = st.multiselect("Modo de Venda", sorted(df["Modo Venda"].dropna().unique()))

with st.expander("💰 Condições Financeiras"):
    col5, col6 = st.columns(2)
    with col5:
        preco_min, preco_max = float(df["Valor venda"].min()), float(df["Valor venda"].max())
        preco_range = st.slider("Faixa de Preço (R$)", preco_min, preco_max, (preco_min, preco_max))
    with col6:
        desc_min, desc_max = float(df["Desconto (%)"].min()), float(df["Desconto (%)"].max())
        desc_range = st.slider("Faixa de Desconto (%)", desc_min, desc_max, (desc_min, desc_max))

with st.expander("🏦 Formas de Pagamento"):
    col7, col8 = st.columns(2)
    financiamento_opcoes = df["Permite financiamento"].dropna().unique().tolist()
    fgts_opcoes = df["Permite FGTS"].dropna().unique().tolist()
    with col7:
        financiamento = st.multiselect("Permite financiamento?", financiamento_opcoes)
    with col8:
        fgts = st.multiselect("Permite uso do FGTS?", fgts_opcoes)

# Aplicar filtros
df_filtrado = df.copy()
if cidades: df_filtrado = df_filtrado[df_filtrado["Cidade"].isin(cidades)]
if bairros: df_filtrado = df_filtrado[df_filtrado["Bairro"].isin(bairros)]
if tipos: df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipos)]
if modos_venda: df_filtrado = df_filtrado[df_filtrado["Modo Venda"].isin(modos_venda)]
df_filtrado = df_filtrado[df_filtrado["Valor venda"].between(*preco_range)]
df_filtrado = df_filtrado[df_filtrado["Desconto (%)"].between(*desc_range)]
if financiamento: df_filtrado = df_filtrado[df_filtrado["Permite financiamento"].isin(financiamento)]
if fgts: df_filtrado = df_filtrado[df_filtrado["Permite FGTS"].isin(fgts)]

# Link
df_filtrado["Link"] = df_filtrado["Link"].apply(lambda x: f"[🔗 Acessar]({x})")

# Exportar Excel com limpeza
def gerar_excel(df_export):
    def limpar(val):
        if isinstance(val, str):
            return re.sub(r"[\x00-\x1F\x7F]", "", val)
        return val
    df_limpo = df_export.applymap(limpar)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_limpo.to_excel(writer, index=False)
    return buffer.getvalue()

# Exibição
st.markdown(f"🔍 **{len(df_filtrado)} imóveis encontrados.**")
if not df_filtrado.empty:
    st.dataframe(df_filtrado[[
        "Cidade", "Bairro", "Tipo", "Modo Venda", "Desconto (%)", "Potencial",
        "Valor avaliacao", "Valor venda", "Permite FGTS", "Permite financiamento",
        "Endereco", "Link"
    ]])
else:
    st.warning("Nenhum imóvel corresponde aos filtros selecionados.")

# Botão de download
st.download_button(
    "📥 Baixar imóveis filtrados (.xlsx)",
    data=gerar_excel(df_filtrado),
    file_name="imoveis_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
