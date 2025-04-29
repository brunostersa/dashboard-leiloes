import streamlit as st
from firebase_admin import db
from auth.cadastro import hash_senha, verificar_senha


def exibir_login():
    st.markdown("## 🔐 Login")

    with st.form("login_form"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        user_id = email.replace(".", "_").replace("@", "_")
        ref = db.reference(f"/usuarios/{user_id}")
        user_data = ref.get()

        if user_data is None:
            st.error("Usuário não encontrado.")
            st.stop()

        if not verificar_senha(senha, user_data.get("senha")):
            st.error("Senha incorreta.")
            st.stop()

        st.session_state.user_email = email
        st.success("Login realizado com sucesso.")
        st.rerun()

    if st.button("Ainda não tem conta? Cadastre-se"):
        st.session_state.exibir_cadastro = True
        st.rerun()

    st.stop()
