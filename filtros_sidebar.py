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


        financiamento = st.checkbox("Aceita Financiamento", key="financiamento")
        lucro = st.checkbox("Lucro Potencial Positivo", key="lucro")

        st.markdown("---")
        st.subheader("🏷️ Detalhes do Imóvel")
        estados = st.multiselect(
            "Estado",
            sorted(df["Estado"].dropna().unique()),
            default=st.session_state.get("estados", ["GO"]),
            key="estados"
        )
        cidades = st.multiselect("Cidade", sorted(df["Cidade"].dropna().unique()), key="cidades")


        # ⚠️ Aplicar limites de desconto confiáveis
        desconto_filtrado = df[(df["Desconto"] >= -100) & (df["Desconto"] <= 100)]
        min_desc = float(desconto_filtrado["Desconto"].min())
        max_desc = float(desconto_filtrado["Desconto"].max())

        desconto_range = st.slider(
            "Desconto (%)",
            min_value=min_desc,
            max_value=max_desc,
            value=st.session_state.get("desconto", (min_desc, max_desc)),
            key="desconto"
        )
        
        # Valor de venda
        def formatar_valor(valor):
            if valor >= 1_000_000:
                return f"{valor/1_000_000:.2f}M"
            elif valor >= 1_000:
                return f"{valor/1_000:.2f}k"
            else:
                return f"{valor:.2f}"

        # Preço de Venda (normalizado + formatado)
        preco_min = float(df["Preço Venda"].quantile(0.01))
        preco_max = float(df["Preço Venda"].quantile(0.99))

        preco_venda_range = st.slider(
            "💰 Preço de Venda (R$)",
            min_value=preco_min,
            max_value=preco_max,
            value=st.session_state.get("preco_venda", (preco_min, preco_max)),
            key="preco_venda",
            format="%.2f",  # Interno
            label_visibility="visible",
            help="Intervalo baseado nos preços mais comuns",
        )
        
        # Mostrar valor formatado como legenda opcional
        st.markdown(f"💡 Intervalo selecionado: **{formatar_valor(preco_venda_range[0])} – {formatar_valor(preco_venda_range[1])}**")

        # Score
        score_minimo = st.slider("Score mínimo (%)", 0, 100, value=st.session_state.get("score_minimo", 0), key="score_minimo")
        
        modalidades = st.multiselect("Modalidade", sorted(df["Modalidade"].dropna().unique()), key="modalidades")
        tipos = st.multiselect("Tipo", sorted(df["Tipo"].dropna().unique()), key="tipos")

    return modalidades, estados, cidades, tipos, desconto_range, financiamento, lucro, score_minimo, preco_venda_range



    
