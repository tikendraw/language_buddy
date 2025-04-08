import time

import requests
import streamlit as st
from dotenv import load_dotenv

from utils import get_env

load_dotenv('.env')

BACKEND_URL = "http://localhost:8000"  # Replace with your backend URL

st.title("Language Buddy")



with st.sidebar:
    st.header("Config")
    
    learning_language = st.text_input("What Language You want to learn?", value="Spanish")
    native_language = st.text_input("What is your native language?", value="English")
    level = st.selectbox("What is your level?", ["Beginner", "Intermediate", "Advanced"])
    
    st.markdown('<br>', unsafe_allow_html=True)
    model_name = st.text_input('Model name: provider/model-name', value=get_env('MODEL_NAME'))
    if not model_name:
        st.warning("Set Model name")
    
    model_api_key = st.text_input('API KEY', value=get_env('MODEL_API_KEY'), type='password')
    if not model_api_key:
        st.warning("Set API key")
            
    submit = st.button('Submit')

    
    if submit:
        try:
            # Use an initial message (e.g. "Hello") to create the config and get a user_id
            response = requests.post(
                f"{BACKEND_URL}/config",
                params={
                    "learning_language": learning_language,
                    "native_language": native_language,
                    "level": level,
                    "model_provider": model_name.split('/')[0] if model_name else "",
                    "model_name": model_name.split('/')[1] if model_name and len(model_name.split('/')) > 1 else "",
                    "api_key": model_api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            st.session_state['user_id'] = data["user_id"]
            st.success("Configuration submitted and user id set!")
            
            

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")
            



def main():
    if 'user_id' not in st.session_state:
        st.warning("Please submit the configuration in the sidebar before chatting.")
        st.stop()

    # Display chat messages from history on app rerun
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input and use websocket for sending messages
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Send user input over the websocket
        try:
            response = requests.post(f"{BACKEND_URL}/chat/{st.session_state['user_id']}", json={"message": prompt})
            response.raise_for_status()
            data = response.json()
            with st.chat_message("assistant"):
                st.markdown(data["response"])
            st.session_state.messages.append({"role": "assistant", "content": data["response"]})
        except Exception as e:
            st.error(f"Failed to send message: {e}")

        # Give the websocket thread some time to receive the answer
        time.sleep(0.2)
        # st.experimental_rerun()

if __name__ == '__main__':
    main()