import streamlit as st

def renderizar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros")

        colf1, colf2 = st.columns(2)
        with colf1:
            if st.button("🧹 Limpar Filtros"):
                st.session_state.modalidades = []
                st.session_state.estados = ["GO"]
                st.session_state.cidades = []
                st.session_state.tipos = []
                st.session_state.desconto = (
                    float(df["Desconto"].min()),
                    float(df["Desconto"].max())
                )
                st.session_state.financiamento = False
                st.session_state.lucro = False
                st.session_state.classificacao = []
                st.session_state.score_minimo = 0
                st.rerun()


        st.subheader("📉 Condições")
        desconto_range = st.slider("Desconto (%)",
            float(df["Desconto"].min()),
            float(df["Desconto"].max()),
            st.session_state.get("desconto", (float(df["Desconto"].min()), float(df["Desconto"].max()))),
            key="desconto"
        )
        financiamento = st.checkbox("Aceita Financiamento", key="financiamento")
        lucro = st.checkbox("Lucro Potencial Positivo", key="lucro")

        st.markdown("---")
        st.subheader("📌 Localização")
        estados = st.multiselect("Estado", sorted(df["Estado"].dropna().unique()), default=st.session_state.get("estados", ["GO"]), key="estados")
        cidades = st.multiselect("Cidade", sorted(df["Cidade"].dropna().unique()), key="cidades")

        st.markdown("---")
        st.subheader("🏷️ Detalhes do Imóvel")
        modalidades = st.multiselect("Modalidade", sorted(df["Modalidade"].dropna().unique()), key="modalidades")
        tipos = st.multiselect("Tipo", sorted(df["Tipo"].dropna().unique()), key="tipos")



        st.markdown("---")
        st.subheader("🎯 Score")
        score_minimo = st.slider("Score mínimo (%)", 0, 100, value=st.session_state.get("score_minimo", 0), key="score_minimo")

    return modalidades, estados, cidades, tipos, desconto_range, financiamento, lucro, score_minimo


