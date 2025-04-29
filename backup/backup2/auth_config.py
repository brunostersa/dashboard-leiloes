import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

def exibir_login():
    if "user_email" not in st.session_state:
        st.markdown("## 🔐 Login / Cadastro")

        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("E-mail")
            telefone = st.text_input("Telefone")
        with col2:
            nome = st.text_input("Nome Completo")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Entrar/Cadastrar") and email:
                try:
                    registrar_usuario(email, nome, telefone)
                    st.session_state.user_email = email
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao registrar usuário: {e}")

        st.stop()  # <- ESSA LINHA GARANTE que o restante do app não será executado

    return st.session_state["user_email"]


def registrar_usuario(email, nome, telefone):
    try:
        user_id = email.replace(".", "_").replace("@", "_")
        app = firebase_admin.get_app("leiloes_app")
        ref = db.reference(f"/usuarios/{user_id}", app=app)
        ref.set({
            "email": email,
            "nome": nome,
            "telefone": telefone
        })
    except Exception as e:
        import traceback
        st.text("🔥 DEBUG:")
        st.text(traceback.format_exc())
        raise RuntimeError(f"Erro ao registrar no Firebase: {e}")
