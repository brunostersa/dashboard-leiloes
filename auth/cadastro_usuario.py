import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# Inicializa Firebase (reutilizável)
if not firebase_admin._apps:
    cred = credentials.Certificate("leiloesdevproject-firebase-adminsdk-fbsvc-fb8c7e8d47.json")
    firebase_admin.initialize_app(cred)

def cadastrar_usuario():
    st.markdown("## 📝 Cadastro de Novo Usuário")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar Senha", type="password")

    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")

    if st.button("📬 Criar Conta"):
        if senha != confirmar:
            st.error("As senhas não coincidem.")
            return
        if not email or not senha or not nome:
            st.warning("Preencha todos os campos obrigatórios.")
            return

        try:
            user = auth.create_user(
                email=email,
                password=senha,
                display_name=nome,
                phone_number=f"+55{telefone}" if telefone else None
            )
            st.success("Usuário cadastrado com sucesso! Agora você pode fazer login.")
        except Exception as e:
            st.error(f"Erro ao cadastrar usuário: {e}")
