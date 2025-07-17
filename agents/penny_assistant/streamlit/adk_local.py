import streamlit as st
import requests

API_URL = "http://localhost:8081"

st.set_page_config(page_title="Penny ADK Local", layout="wide")

st.sidebar.title("Penny ADK Local")
page = st.sidebar.radio("Go to", ["Chat", "Memory"])

if page == "Chat":
    st.header("Chat with Penny (Local ADK)")
    if "history" not in st.session_state:
        st.session_state["history"] = []
    user_input = st.text_input("You:", key="user_input")
    if st.button("Send") and user_input:
        try:
            resp = requests.post(f"{API_URL}/chat", json={"message": user_input})
            resp.raise_for_status()
            answer = resp.json().get("response", "[No response]")
            st.session_state["history"].append((user_input, answer))
        except Exception as e:
            st.error(f"Error: {e}")
    for user, bot in reversed(st.session_state["history"]):
        st.markdown(f"**You:** {user}")
        st.markdown(f"**Penny:** {bot}")
elif page == "Memory":
    st.header("MemoryBank Contents (Local ADK)")
    if st.button("Refresh") or "memory" not in st.session_state:
        try:
            resp = requests.get(f"{API_URL}/memory")
            resp.raise_for_status()
            st.session_state["memory"] = resp.json().get("memory", {})
        except Exception as e:
            st.error(f"Error: {e}")
    st.json(st.session_state.get("memory", {})) 