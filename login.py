from session_utils import salvar_usuario

if login_sucesso:
    st.session_state.user_email = email
    salvar_usuario(email)
    st.switch_page("dashboard.py")
