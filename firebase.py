import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


@st.cache_resource
def iniciar_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://leiloesdevproject-default-rtdb.firebaseio.com/'
        })

def registrar_usuario(email, nome, telefone):
    iniciar_firebase()
    user_id = email.replace('.', '_')
    ref = db.reference("/usuarios")  # ou o caminho desejado como base
    ref.child(email.replace('.', '_')).set({
        "email": email,
        "nome": nome,
        "telefone": telefone
    })

