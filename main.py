import streamlit as st
from firebase_auth import exibir_login_cadastro
from session_utils import carregar_usuario, limpar_sessao
import dashboard

st.set_page_config(page_title="Imóveis Caixa", layout="wide")

# VERIFICA LOGIN
user = st.session_state.get("user_email") or carregar_usuario()

if not user or not st.session_state.get("logged_in"):
    exibir_login_cadastro()
    st.stop()

st.subheader("📊 Painel de Oportunidades - Imóveis Caixa")

# === Linha com dois botões: Recarregar Dados e Sair ===
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f"👋 Bem-vindo, **{user}**")
    if st.button("🚪 Sair"):
        limpar_sessao()
        st.session_state.clear()
        st.rerun()

with col2:
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.success("Dados recarregados!")
        st.rerun()



# DASHBOARD
dashboard.mostrar_dashboard()
