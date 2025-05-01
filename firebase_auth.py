import streamlit as st
import firebase_admin
from firebase_admin import auth as admin_auth, credentials, db
import pyrebase
import re

# Config Firebase
firebase_config = {
    "apiKey": "AIzaSyCWAJNm53jK1LAi8j_4S_BQYShatS4jvw8",
    "authDomain": "leiloesdevproject.firebaseapp.com",
    "databaseURL": "/lib/logo.png",
    "projectId": "leiloesdevproject",
    "storageBucket": "leiloesdevproject.appspot.com",
    "messagingSenderId": "284763075578",
    "appId": "1:284763075578:web:17b745992b21036e576a43",
    "measurementId": "G-KMMZ3N67BC"
    
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Função de validação de email
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def exibir_login_cadastro():
    

    col_info, col_form = st.columns([1, 1], gap="large")

    with col_info:
        st.image("https://www.clipartmax.com/png/middle/131-1319990_caixa-econ%C3%B4mica-federal-logo-caixa-png.png", width=120)
        st.markdown("## 👋 Bem-vindo ao Painel de Imóveis da Caixa")
        st.write("Explore oportunidades de imóveis com **descontos incríveis**, **financiamento facilitado** e nosso exclusivo sistema de **pontuação inteligente**.")
        st.markdown("### 🔎 Recursos disponíveis:")
        st.markdown("""
        - Filtros personalizados por localização, tipo e modalidade  
        - Score que combina **preço**, **lucro potencial** e **desconto**  
        - Visualização interativa dos dados e exportação
        """)
        st.markdown("---")
        st.markdown("👉 Faça login ou cadastre-se para começar!")

    with col_form:
        st.markdown("## 🔐 Login / Cadastro")
        opcao = st.radio("Escolha uma opção:", ["Login", "Cadastro"], horizontal=True)
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")

        if opcao == "Cadastro":
            if st.button("Cadastrar"):
                if email and senha:
                    if not is_valid_email(email):
                        st.warning("Por favor, insira um e-mail válido.")
                    else:
                        try:
                            user = auth.create_user_with_email_and_password(email, senha)
                            st.session_state.user_email = email
                            st.session_state.logged_in = True
                            st.success("Usuário cadastrado com sucesso! 🎉")
                            st.rerun()
                        except Exception as e:
                            if "EMAIL_EXISTS" in str(e):
                                st.warning("Este e-mail já está cadastrado. Tente fazer login.")
                            else:
                                st.error(f"Erro: {e}")
                else:
                    st.warning("Preencha todos os campos.")

        elif opcao == "Login":
            if st.button("Login"):
                if email and senha:
                    if not is_valid_email(email):
                        st.warning("Por favor, insira um e-mail válido.")
                    else:
                        try:
                            user = auth.sign_in_with_email_and_password(email, senha)
                            st.session_state.user_email = email
                            st.session_state.logged_in = True
                            st.success("Login realizado com sucesso! ✅")
                            st.rerun()
                        except Exception as e:
                            st.error("Erro ao fazer login. Verifique o e-mail e a senha.")
                else:
                    st.warning("Preencha todos os campos.")
