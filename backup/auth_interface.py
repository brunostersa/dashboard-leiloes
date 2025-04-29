import streamlit as st
import requests
import json

FIREBASE_API_KEY = "AIzaSyCWAJNm53jK1LAi8j_4S_BQYShatS4jvw8"

FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

def cadastrar_usuario(email, senha):
    payload = {
        "email": email,
        "password": senha,
        "returnSecureToken": True
    }
    response = requests.post(FIREBASE_SIGNUP_URL, data=json.dumps(payload))
    return response.json()

def login_usuario(email, senha):
    payload = {
        "email": email,
        "password": senha,
        "returnSecureToken": True
    }
    response = requests.post(FIREBASE_SIGNIN_URL, data=json.dumps(payload))
    return response.json()

def exibir_login_cadastro():
    st.title("🔐 Login / Cadastro")
    aba = st.radio("Escolha uma opção:", ["Login", "Cadastro"])

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if aba == "Cadastro":
        if st.button("Cadastrar"):
            resultado = cadastrar_usuario(email, senha)
            if "error" in resultado:
                st.error(f"Erro: {resultado['error']['message']}")
            else:
                st.success("Cadastro realizado com sucesso!")
                st.session_state.user_email = email
                st.rerun()
    else:
        if st.button("Entrar"):
            resultado = login_usuario(email, senha)
            if "error" in resultado:
                st.error(f"Erro: {resultado['error']['message']}")
            else:
                st.success("Login realizado com sucesso!")
                st.session_state.user_email = email
                st.rerun()

    if "user_email" not in st.session_state:
        st.stop()

    return st.session_state.user_email
