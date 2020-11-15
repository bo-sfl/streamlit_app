import hashlib
import streamlit as st
from SessionState import session_get

def authentication(usr_name, password):
    '''Valid the uer_name and password'''
    m=hashlib.sha256()
    m.update(str(usr_name).encode())
    m.update(str(password).encode())
    if m.hexdigest() == '7bdc616cc8db6935847e5fb6add88de1f470f96cb5c92d0d0c6ee2ab8acab3a9':
        return True
    return False

def authenticated():
    """Check user authentication with session state"""
    session_state = session_get(user_name='', password='')
    if authentication(session_state.user_name, session_state.password):
        return True
    else:
        _, col2, _ = st.beta_columns(3)
        with col2:
            login_block = st.empty()
            with login_block.beta_container():
                session_state.user_name =  st.text_input("User Name:", value="", type="default")
                session_state.password = st.text_input("Password:", value="", type="password")
                login = st.button("Login")
                auth = authentication(session_state.user_name, session_state.password)
                if session_state.password == "" and session_state.user_name == "":
                    return False

                if not auth:
                    if login:
                        # Only show error message if the user have click the login
                        st.error("The user name and password combination you entered is incorrect")
                    return False
                
                login_block.empty()
                return True