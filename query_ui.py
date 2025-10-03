#!/usr/bin/env python3.11
import streamlit as st
import requests

st.set_page_config(page_title="Invoice Q&A", layout="wide")

st.markdown("""
<style>
    .main {background-color: #f6f9fc;}
    .stButton>button {
        background-color: #635bff;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 500;
    }
    .stButton>button:hover {background-color: #0a2540;}
    h1 {color: #0a2540; font-weight: 600;}
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .user-message {background-color: #f0f0f0;}
    .assistant-message {background-color: #e8f4f8;}
</style>
""", unsafe_allow_html=True)

st.title("💬 Invoice Q&A with Pathway RAG")
st.markdown("Ask questions about your invoice documents")

if "messages" not in st.session_state:
    st.session_state.messages = []

RAG_ENDPOINT = "http://127.0.0.1:8080/v1/pw_ai_answer"

for message in st.session_state.messages:
    role_class = "user-message" if message["role"] == "user" else "assistant-message"
    st.markdown(f"""
    <div class="chat-message {role_class}">
        <b>{"You" if message["role"] == "user" else "Assistant"}:</b><br>
        {message["content"]}
    </div>
    """, unsafe_allow_html=True)

query = st.text_input("Ask a question about the invoice:", placeholder="What is the invoice number?")

if st.button("Send") and query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                RAG_ENDPOINT,
                headers={"Content-Type": "application/json"},
                json={"prompt": query},
                timeout=30
            )

            if response.status_code == 200:
                answer = response.json().get("response", "No response received")
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to RAG server: {str(e)}")

    st.rerun()

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.markdown("---")
st.caption("💡 Make sure the Pathway RAG server is running on port 8080")
st.caption("Run: `/opt/anaconda3/bin/python3.11 rag_query.py`")
