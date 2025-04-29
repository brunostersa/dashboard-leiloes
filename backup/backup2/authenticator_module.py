import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit as st

def autenticar_usuario():
    with open('auth_config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status is False:
        st.error("Usuário ou senha inválidos.")
        st.stop()
    elif authentication_status is None:
        st.warning("Informe suas credenciais.")
        st.stop()
    else:
        authenticator.logout("Sair", "sidebar")
        st.sidebar.success(f"Usuário logado: {name}")
        return username
