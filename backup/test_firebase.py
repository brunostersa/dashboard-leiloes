import firebase_admin
from firebase_admin import credentials, db

# Use diretamente o arquivo JSON de credencial do Firebase
cred = credentials.Certificate("leiloesdevproject-firebase-adminsdk-fbsvc-fb8c7e8d47.json")  # ajuste o nome do seu arquivo real aqui

# Inicializa o Firebase
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://leiloesdevproject-default-rtdb.firebaseio.com/'
    })


# Função de teste
def registrar_usuario_teste(email, nome, telefone):
    ref = db.reference("/usuarios")
    user_id = email.replace('.', '_')
    ref.child(user_id).set({
        "email": email,
        "nome": nome,
        "telefone": telefone
    })
    print("✅ Usuário registrado com sucesso!")

# Executa
if __name__ == "__main__":
    registrar_usuario_teste("11111.user@gmail.com", "Usuário de Teste", "11999999999")
