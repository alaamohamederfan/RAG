import streamlit as st
from dotenv import load_dotenv
import os
import requests
from streamlit_chat import message


def init():

    load_dotenv()


    api_url = "http://localhost:8000"

    if not api_url:
        st.error("API_URL is not set. Please set it in your environment variables.")
        st.stop()

    st.set_page_config(
        page_title="HR Policy Chatbot 🤖",
        page_icon="🤖",
        layout="wide",
    )

    st.header("HR Policy Chatbot 🤖")

def call_chatbot_api(user_message):
    api_url = "http://localhost:8000"

    payload = {"query": user_message}
    headers = {"Content-Type": "application/json"}

    try:
        # Make the API request
        response = requests.post("http://localhost:5129/api/Chatbot/ask", json=payload, headers=headers)
        response.raise_for_status()

        # Parse the response
        response_data = response.json()
        answer = response_data.get("answer", "No response received.")
        return answer

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        if 'response' in locals():
            st.error(f"Response content: {response.text}")
    except Exception as err:
        st.error(f"An error occurred: {err}")

    return "Sorry, I couldn't process that."


def reset_chat_history():
    api_url = "http://localhost:8000"

    try:
        response = requests.post(f"{api_url}/reset")
        response.raise_for_status()
        st.session_state.messages = []
        st.success("Chat history has been reset.")
    except Exception as err:
        st.error(f"Failed to reset chat history: {err}")

def main():
    init()


    if "messages" not in st.session_state:
        st.session_state.messages = []


    with st.sidebar:
        st.subheader("Send a Message")
        with st.form(key='user_input_form', clear_on_submit=True):
            user_input = st.text_input("Your message:")
            submit_button = st.form_submit_button(label='Send')

        if submit_button:
            if user_input.strip():

                st.session_state.messages.append({"role": "user", "content": user_input})


                with st.spinner("Thinking..."):
                    chatbot_response = call_chatbot_api(user_input)

                if chatbot_response:

                    st.session_state.messages.append({"role": "assistant", "content": chatbot_response})


    if st.sidebar.button("Reset Chat"):
        reset_chat_history()


    st.subheader("Conversation")
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"user_{i}")
        elif msg["role"] == "assistant":
            message(msg["content"], is_user=False, key=f"assistant_{i}")

if __name__ == "__main__":
    main()
