import streamlit as st
import pandas as pd
pd.set_option("styler.render.max_elements", 600000)
import os
import firebase_admin
from firebase_admin import credentials, db
from filtros_sidebar import renderizar_filtros
from firebase_auth import exibir_login_cadastro
from session_utils import limpar_sessao, carregar_usuario
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap



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
    modalidades, estados, cidades, tipos, desconto_range, financiamento, lucro, score_minimo, preco_venda_range = renderizar_filtros(df)



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
    df = df[(df["Preço Venda"] >= preco_venda_range[0]) & (df["Preço Venda"] <= preco_venda_range[1])]
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
    # === Tabela Completa com Melhorias ===
    st.subheader("📋 Tabela Completa")
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
    
    # Exportar CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Exportar Resultados", csv, file_name="imoveis_filtrados.csv", mime="text/csv")

    # === Gráfico: Top 10 cidades com mais imóveis ===
    

    top_cidades = df["Cidade"].value_counts().nlargest(10).reset_index()
    top_cidades.columns = ["Cidade", "Quantidade"]

    fig = px.bar(
        top_cidades,
        x="Quantidade",
        y="Cidade",
        orientation="h",
        title="Top 10 Cidades ",
        text="Quantidade"
    )
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)
    
    
    # === Gráfico 2
    top_cidades = df.groupby("Cidade")["Desconto"].mean().sort_values(ascending=False).head(5).reset_index()

    fig = px.bar(
        top_cidades,
        x="Desconto",
        y="Cidade",
        orientation="h",
        title="🏙️ Maiores Descontos Médios por Cidade",
        text="Desconto",
        labels={"Desconto": "Desconto (%)", "Cidade": "Cidade"}
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(showlegend=False)  # barra simples não precisa de legenda de cor
    st.plotly_chart(fig, use_container_width=True)
    
     # === Gráfico 3
    lucro_tipo = df.groupby("Tipo")["Lucro Potencial"].mean().reset_index()

    fig = px.bar(
        lucro_tipo,
        x="Tipo",
        y="Lucro Potencial",
        title="💰 Lucro Médio por Tipo de Imóvel",
        text="Lucro Potencial",
        labels={"Tipo": "Tipo de Imóvel", "Lucro Potencial": "Lucro (R$)"}
    )
    fig.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Nova visao de pbi, tabela por modalidade v2
    st.subheader("📊 Tabela de Modalidades por Cidade (com Cores e Totais)")

    # Pivot
    tabela = pd.pivot_table(
        df,
        index="Cidade",
        columns="Modalidade",
        values="Tipo",
        aggfunc="count",
        fill_value=0
    )

    # Total
    tabela["Total"] = tabela.sum(axis=1)

    # Ordenar
    tabela = tabela.sort_values(by="Total", ascending=False)

    # Emojis Top 3
    top_cidades = tabela.index[:3]
    emojis = ["🥇", "🥈", "🥉"]
    renomear = {cidade: f"{emoji} {cidade}" for cidade, emoji in zip(top_cidades, emojis)}
    tabela = tabela.rename(index=renomear)

    # Reordena colunas
    colunas_ordenadas = [col for col in tabela.columns if col != "Total"] + ["Total"]
    tabela = tabela[colunas_ordenadas]

    # Gradiente branco → azul
    white_to_blue = LinearSegmentedColormap.from_list("white_to_blue", ["#ffffff", "#1f77b4"])

    # Estilo: cores + ocultar zeros
    styled_tabela = (
        tabela.style
        .background_gradient(cmap=white_to_blue)
        .format(lambda x: "–" if x == 0 else f"{int(x)}")
    )

    # Exibição
    st.dataframe(
        styled_tabela,
        use_container_width=True
    )


    df_modalidade = df["Modalidade"].value_counts().reset_index()
    df_modalidade.columns = ["Modalidade", "Quantidade"]

    fig_modalidade = px.bar(
        df_modalidade,
        x="Modalidade", y="Quantidade",
        title="📦 Quantidade de Imóveis por Modalidade",
        color="Modalidade"
    )
    st.plotly_chart(fig_modalidade, use_container_width=True)


    # === 3. Boxplot – Preço por Tipo de Imóvel
    fig_box = px.box(
        df, x="Tipo", y="Preço Venda",
        title="💸 Distribuição de Preço de Venda por Tipo de Imóvel",
        points="outliers"
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # === 4. Scatterplot – Score vs Lucro Potencial
    fig_scatter = px.scatter(
        df, x="Lucro Potencial", y="Score",
        color="Tipo", hover_data=["Cidade", "Modalidade"],
        title="🎯 Score vs Lucro Potencial"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # === 6. Histograma – Distribuição dos Descontos
    fig_hist = px.histogram(
        df, x="Desconto", nbins=20,
        title="📉 Distribuição dos Descontos (%)"
    )
    st.plotly_chart(fig_hist, use_container_width=True)





