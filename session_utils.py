import json
import os

SESSION_FILE = "session.json"

def salvar_usuario(email):
    with open(SESSION_FILE, "w") as f:
        json.dump({"user_email": email}, f)

def carregar_usuario():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            data = json.load(f)
            return data.get("user_email")
    return None

def limpar_sessao():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
