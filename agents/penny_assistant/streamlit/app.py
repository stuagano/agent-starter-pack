import streamlit as st
import os
from utils import pdf_upload, rag_query, get_lists, create_list, update_list, delete_list, get_calendar_events, chat, get_memory, evaluate

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
USER_ID = "demo-user"  # TODO: Replace with real authentication

st.set_page_config(page_title="Penny Assistant", layout="wide")
st.sidebar.title("Penny Assistant")
page = st.sidebar.radio("Go to", [
    "PDF Upload", "Lists", "Calendar", "Chat", "Memory", "Evaluation"
])

def pdf_upload_page():
    st.header("Upload PDF Documents")
    # PDF file uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file and st.button("Upload"):
        result = pdf_upload(uploaded_file, USER_ID)
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.success(f"PDF uploaded and processed. Chunks: {result.get('chunks', '?')}")
            # Display chunk preview if available
            if 'chunk_preview' in result:
                st.markdown("**Preview of first chunks:**")
                for i, chunk in enumerate(result['chunk_preview']):
                    st.code(chunk, language='text')
                    if i >= 2:
                        break
    st.markdown("---")
    st.subheader("Ask Questions (RAG)")
    # RAG query input
    query = st.text_input("Ask a question about your PDFs:")
    if st.button("Query") and query:
        result = rag_query(query, USER_ID)
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.write(f"**Answer:** {result.get('answer', '[No answer]')}")
            # Show retrieved context/chunks if available
            if 'context' in result:
                st.markdown("**Retrieved context:**")
                for i, ctx in enumerate(result['context']):
                    st.code(ctx, language='text')
                    if i >= 2:
                        break

def lists_page():
    st.header("Manage Your Lists")
    # List creation
    with st.form("create_list_form"):
        new_list_name = st.text_input("New List Name")
        submitted = st.form_submit_button("Create List")
        if submitted and new_list_name:
            result = create_list(USER_ID, new_list_name)
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success(f"List '{new_list_name}' created!")
                st.experimental_rerun()
    # List display and editing
    lists = get_lists(USER_ID)
    if not lists:
        st.info("No lists found.")
    else:
        for l in lists:
            st.subheader(l["name"])
            items = l.get("items", [])
            # Mark complete and reorder
            if f"edit_state_{l['id']}" not in st.session_state:
                st.session_state[f"edit_state_{l['id']}"] = [(item, False) for item in items]
            edit_state = st.session_state[f"edit_state_{l['id']}"]
            for i, (item, completed) in enumerate(edit_state):
                cols = st.columns([0.05, 0.7, 0.1, 0.1, 0.05])
                with cols[0]:
                    checked = st.checkbox("", value=completed, key=f"check_{l['id']}_{i}")
                with cols[1]:
                    new_text = st.text_input("", value=item, key=f"item_{l['id']}_{i}")
                with cols[2]:
                    if st.button("⬆️", key=f"up_{l['id']}_{i}") and i > 0:
                        edit_state[i], edit_state[i-1] = edit_state[i-1], edit_state[i]
                        st.experimental_rerun()
                with cols[3]:
                    if st.button("⬇️", key=f"down_{l['id']}_{i}") and i < len(edit_state)-1:
                        edit_state[i], edit_state[i+1] = edit_state[i+1], edit_state[i]
                        st.experimental_rerun()
                with cols[4]:
                    if st.button("❌", key=f"del_{l['id']}_{i}"):
                        edit_state.pop(i)
                        st.experimental_rerun()
                edit_state[i] = (new_text, checked)
            # Add new item
            if st.button(f"Add Item to {l['name']}", key=f"add_{l['id']}"):
                edit_state.append(("", False))
                st.experimental_rerun()
            # Save changes
            if st.button(f"Save {l['name']}", key=f"save_{l['id']}"):
                new_items = [item for item, _ in edit_state]
                result = update_list(l["id"], new_items)
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("List updated!")
                    st.experimental_rerun()
            # Delete list
            if st.button(f"Delete {l['name']}", key=f"delete_{l['id']}"):
                result = delete_list(l["id"])
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("List deleted!")
                    st.experimental_rerun()

def calendar_page():
    st.header("Your Calendar Events")
    # Calendar event list
    if st.button("Refresh Events") or "calendar_events" not in st.session_state:
        result = get_calendar_events(USER_ID)
        st.session_state["calendar_events"] = result.get("events", []) if "error" not in result else []
        if "error" in result:
            st.error(f"Error: {result['error']}")
    events = st.session_state.get("calendar_events", [])
    if not events:
        st.info("No upcoming events found.")
    else:
        for i, event in enumerate(events):
            with st.expander(event.get("title", f"Event {i+1}")):
                st.write(f"**Time:** {event.get('start', 'N/A')} - {event.get('end', 'N/A')}")
                if event.get("location"):
                    st.write(f"**Location:** {event['location']}")
                if event.get("description"):
                    st.write(f"**Description:** {event['description']}")
                if st.button(f"Add to Lists: {event.get('title', f'Event {i+1}')}" , key=f"add_event_{i}"):
                    result = create_list(USER_ID, event.get("title", f"Event {i+1}"))
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.success(f"Event '{event.get('title', f'Event {i+1}')}' added to your lists!")

def chat_page():
    st.header("Chat with Penny")
    # Chat history and input
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.button("Clear Chat History"):
        st.session_state["history"] = []
        st.experimental_rerun()
    user_input = st.text_input("You:", key="user_input")
    if st.button("Send") and user_input:
        result = chat(user_input, USER_ID)
        answer = result.get("response", "[No response]")
        context = result.get("context", None)
        st.session_state["history"].append({"user": user_input, "bot": answer, "context": context})
        st.experimental_rerun()
    for turn in reversed(st.session_state["history"]):
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"**Penny:** {turn['bot']}")
        if turn.get("context"):
            st.markdown("**Context/Sources:**")
            for i, ctx in enumerate(turn["context"]):
                st.code(ctx, language='text')
                if i >= 2:
                    break

def memory_page():
    st.header("MemoryBank Contents")
    # Memory display and refresh
    if st.button("Refresh Memory") or "memory" not in st.session_state:
        result = get_memory()
        st.session_state["memory"] = result.get("memory", {})
        if "error" in result:
            st.error(f"Error: {result['error']}")
    memory = st.session_state.get("memory", {})
    if not memory:
        st.info("No memory found.")
        return
    # Search/filter
    search = st.text_input("Search Memory:")
    filtered = {k: v for k, v in memory.items() if search.lower() in k.lower() or search.lower() in str(v).lower()} if search else memory
    st.write(f"Showing {len(filtered)} of {len(memory)} entries.")
    st.json(filtered)
    # Export
    st.download_button("Export as JSON", data=str(filtered), file_name="memorybank.json", mime="application/json")

def evaluation_page():
    st.header("Evaluation")
    # Upload eval set, run eval, show results
    uploaded_eval = st.file_uploader("Upload Evaluation Set (JSON/CSV)", type=["json", "csv"])
    eval_data = None
    if uploaded_eval:
        try:
            if uploaded_eval.type == "application/json":
                import json
                eval_data = json.load(uploaded_eval)
            elif uploaded_eval.type == "text/csv":
                import pandas as pd
                eval_data = pd.read_csv(uploaded_eval).to_dict(orient="records")
        except Exception as e:
            st.error(f"Failed to parse evaluation file: {e}")
    if eval_data and st.button("Run Evaluation"):
        result = evaluate({"data": eval_data, "user_id": USER_ID})
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.success("Evaluation complete!")
            st.session_state["last_eval_result"] = result
    # Show last evaluation result
    if "last_eval_result" in st.session_state:
        st.subheader("Latest Evaluation Results")
        result = st.session_state["last_eval_result"]
        if "metrics" in result:
            st.write("**Metrics:**")
            for k, v in result["metrics"].items():
                st.write(f"{k}: {v}")
            # If metrics are numeric, show as chart
            try:
                import pandas as pd
                df = pd.DataFrame([result["metrics"]])
                st.bar_chart(df)
            except Exception:
                pass
        if "details" in result:
            st.write("**Details:**")
            st.json(result["details"])
    # Show past runs (if available)
    if "past_evals" in st.session_state:
        st.subheader("Past Evaluation Runs")
        for i, run in enumerate(st.session_state["past_evals"]):
            with st.expander(f"Run {i+1}"):
                st.json(run)

if page == "PDF Upload":
    pdf_upload_page()
elif page == "Lists":
    lists_page()
elif page == "Calendar":
    calendar_page()
elif page == "Chat":
    chat_page()
elif page == "Memory":
    memory_page()
elif page == "Evaluation":
    evaluation_page() 