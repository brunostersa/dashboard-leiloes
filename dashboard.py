import streamlit as st
import pandas as pd
pd.set_option("styler.render.max_elements", 600000)
import plotly.express as px
import os
import firebase_admin
from firebase_admin import credentials, db
from filtros_sidebar import renderizar_filtros
from firebase_auth import exibir_login_cadastro
from session_utils import limpar_sessao, carregar_usuario
import plotly.express as px

# Função que exibe o conteúdo principal do dashboard
def mostrar_dashboard():
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # === Session
    user_email = st.session_state.get("user_email") or carregar_usuario()
    if not user_email:
        st.switch_page("login.py")  # ou outro nome da sua tela de login



    # Inicializa Firebase se necessário
    if not firebase_admin._apps:
        try:
            if "firebase" in st.secrets:
                # Estamos no Streamlit Cloud: pegar dados do secrets
                firebase_info = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_info)
            else:
                # Rodando localmente
                cred = credentials.Certificate("leiloesdevproject-firebase-adminsdk-fbsvc-fb8c7e8d47.json")

            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://leiloesdevproject-default-rtdb.firebaseio.com/'
            }, name="leiloes_app")
        except Exception as e:
            st.error(f"Erro ao inicializar o Firebase: {e}")
  

    # === Funções utilitárias ===
    @st.cache_data(ttl=600)
    def carregar_dados(caminho):
        if not os.path.exists(caminho):
            st.error("Arquivo de dados não encontrado.")
            st.stop()
        df = pd.read_excel(caminho, sheet_name="Imóveis Caixa")
        df["Desconto"] = pd.to_numeric(df["Desconto"], errors="coerce")
        df["Preço Venda"] = pd.to_numeric(df["Preço Venda"], errors="coerce")
        df["Preço Avaliação"] = pd.to_numeric(df["Preço Avaliação"], errors="coerce")
        df["Lucro Potencial"] = df["Preço Avaliação"] - df["Preço Venda"]
        df["Modalidade"] = df["Modo Venda"].fillna("Outros")
        for col in df.columns:
            if "data" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    df.rename(columns={col: "Data Cadastro"}, inplace=True)
                    break
                except:
                    pass
        return df

    def calcular_score(df):
        agrupado = df.groupby(["Cidade", "Tipo"])["Preço Venda"].mean().reset_index()
        agrupado.rename(columns={"Preço Venda": "Preço Médio"}, inplace=True)
        df = df.merge(agrupado, on=["Cidade", "Tipo"], how="left")

        # Normalização para garantir valores de 0 a 100
        score_bruto = (
            ((df["Desconto"] / 100).fillna(0)) * 0.4 +
            ((df["Lucro Potencial"] / df["Preço Médio"]).fillna(0)) * 0.3 +
            ((1 - (df["Preço Venda"] / df["Preço Médio"])).fillna(0)) * 0.3
        )

        score_bruto = score_bruto.clip(lower=0)
        score_min, score_max = score_bruto.min(), score_bruto.max()
        df["Score"] = ((score_bruto - score_min) / (score_max - score_min) * 100).clip(0, 100).round(2)

        return df

    # === Carregamento de dados ===
    arquivo = "smart_leiloes_imoveis_caixa.xlsx"
    df = carregar_dados(arquivo)
    df = calcular_score(df)

    # === Filtros ===
    modalidades, estados, cidades, tipos, desconto_range, financiamento, lucro, score_minimo = renderizar_filtros(df)

    # === Aplicação dos filtros ===
    if modalidades:
        df = df[df["Modalidade"].isin(modalidades)]
    if estados:
        df = df[df["Estado"].isin(estados)]
    if cidades:
        df = df[df["Cidade"].isin(cidades)]
    if tipos:
        df = df[df["Tipo"].isin(tipos)]
    df = df[(df["Desconto"] >= desconto_range[0]) & (df["Desconto"] <= desconto_range[1])]
    if financiamento:
        df = df[df["Aceita Financiamento"].str.upper() == "SIM"]
    if lucro:
        df = df[df["Lucro Potencial"] > 0]
    df = df[df["Score"] >= score_minimo]
    
    st.markdown("---")

    # === KPIs ===
    st.subheader("📊 Indicadores")
    col1, col2, col3 = st.columns(3)
    col1.metric("🏠 Total de Imóveis", len(df))
    col2.metric("💲 Desconto Médio", f'{df["Desconto"].mean():.2f}%')
    financiaveis = df[df["Aceita Financiamento"].str.upper() == "SIM"]
    lucro_medio = financiaveis["Lucro Potencial"].sum() / len(financiaveis) if len(financiaveis) > 0 else 0
    col3.metric("💼 Lucro Médio (Financiáveis)", f'R$ {lucro_medio:,.2f}')

    st.markdown("---")

    # === Tabela Completa com Melhorias ===
    st.subheader("📋 Tabela Completa")

    # Ordenar do melhor Score para o pior
    df_fmt = df[["Cidade", "Tipo", "Modalidade", "Aceita Financiamento", "Desconto", "Preço Avaliação", "Preço Venda", "Lucro Potencial", "Score", "Site"]].copy()
    df_fmt = df_fmt.sort_values(by="Score", ascending=False)

    # Formatar valores numéricos
    for col in ["Desconto", "Preço Avaliação", "Preço Venda", "Lucro Potencial"]:
        if "Desconto" in col:
            df_fmt[col] = df_fmt[col].map("{:.2f}%".format)
        else:
            df_fmt[col] = df_fmt[col].map("R$ {:,.2f}".format)



    
    # Paginação com botões e exibição por 200 registros
    registros_por_pagina = 200
    total_paginas = (len(df_fmt) - 1) // registros_por_pagina + 1

    # Inicializa estado da página
    if "pagina_tabela" not in st.session_state:
        st.session_state.pagina_tabela = 1

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    with col_pag1:
        if st.button("⬅️ Anterior") and st.session_state.pagina_tabela > 1:
            st.session_state.pagina_tabela -= 1
    with col_pag2:
        st.markdown(f"<p style='text-align:center;'>Página {st.session_state.pagina_tabela} de {total_paginas}</p>", unsafe_allow_html=True)
    with col_pag3:
        if st.button("Próxima ➡️") and st.session_state.pagina_tabela < total_paginas:
            st.session_state.pagina_tabela += 1

    inicio = (st.session_state.pagina_tabela - 1) * registros_por_pagina
    fim = inicio + registros_por_pagina
    df_paginado = df_fmt.iloc[inicio:fim]
    
    # Tabela Completa e estilo
    styled_df_paginado = df_paginado.style.format({"Score": "{:.2f}"}).background_gradient(
        subset=["Score"], cmap="RdYlGn", vmin=0, vmax=100
    )

    st.dataframe(
        styled_df_paginado,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Site": st.column_config.LinkColumn("🔗 Link")
        }
    )

    # === Gráfico: Top 10 cidades com mais imóveis ===
    st.subheader("🏙️ Top 10 Cidades com Mais Imóveis")

    top_cidades = df["Cidade"].value_counts().nlargest(10).reset_index()
    top_cidades.columns = ["Cidade", "Quantidade"]

    fig = px.bar(
        top_cidades,
        x="Quantidade",
        y="Cidade",
        orientation="h",
        title="Top 10 Cidades com Mais Imóveis",
        text="Quantidade"
    )
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

    # Exportar CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Exportar Resultados", csv, file_name="imoveis_filtrados.csv", mime="text/csv")


