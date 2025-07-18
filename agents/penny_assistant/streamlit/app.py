import streamlit as st
import os
from utils import pdf_upload, rag_query, get_lists, create_list, update_list, delete_list, get_calendar_events, chat, get_memory, evaluate, health_check
from config_setup import config_setup
from debug_utils import debug_utils
from gherkin_feedback import gherkin_feedback

# Environment variables for Cloud Run
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
USER_ID = os.getenv("USER_ID", "demo-user")  # TODO: Replace with real authentication
PORT = int(os.getenv("PORT", 8501))

# Streamlit configuration for Cloud Run
st.set_page_config(
    page_title="Penny Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Health check endpoint (for Cloud Run)
if st.query_params.get("health") == "check":
    st.json({"status": "ok", "service": "penny-assistant-frontend"})
    st.stop()

# Sidebar
st.sidebar.title("Penny Assistant")
st.sidebar.info(f"Backend: {BACKEND_URL}")

# Configuration status in sidebar
st.sidebar.divider()
st.sidebar.subheader("�� Service Status")

try:
    setup_status = config_setup.get_setup_status()
    services = [
        ("📝 Firestore", setup_status.get("firestore", {}).get("configured", False)),
        ("📅 Calendar", setup_status.get("calendar", {}).get("configured", False)),
        ("🤖 Vertex AI", setup_status.get("vertex_ai", {}).get("configured", False)),
        ("🔍 Vector Search", setup_status.get("vector_search", {}).get("configured", False))
    ]

    for service_name, configured in services:
        status_icon = "✅" if configured else "❌"
        st.sidebar.write(f"{status_icon} {service_name}")

    configured_count = sum(1 for _, configured in services if configured)
    if configured_count == 0:
        st.sidebar.warning("⚠️ Using placeholders")
    elif configured_count < len(services):
        st.sidebar.info(f"ℹ️ {configured_count}/{len(services)} configured")
    else:
        st.sidebar.success("🎉 All configured!")
except Exception as e:
    st.sidebar.error(f"⚠️ Configuration error: {str(e)}")

# Navigation
page = st.sidebar.radio("Go to", [
    "PDF Upload", "Lists", "Calendar", "Chat", "Memory", "Evaluation", "Configuration", "Debug", "Feedback"
])

# Main content
if page == "Configuration":
    try:
        config_setup.render_config_page()
    except Exception as e:
        st.error(f"Configuration page error: {str(e)}")
        st.info("Please check the debug page for more information.")

elif page == "Debug":
    try:
        debug_utils.render_debug_page()
    except Exception as e:
        st.error(f"Debug page error: {str(e)}")
        st.info("This is a critical error. Please check the application logs.")

elif page == "Feedback":
    try:
        gherkin_feedback.render_feedback_page()
    except Exception as e:
        st.error(f"Feedback page error: {str(e)}")
        st.info("Please try refreshing the page.")

elif page == "PDF Upload":
    st.title("📄 PDF Upload & RAG")

    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

    if uploaded_file is not None:
        if st.button("Upload and Process"):
            try:
                with st.spinner("Processing PDF..."):
                    result = pdf_upload(uploaded_file, USER_ID)

                    if "error" in result:
                        st.error(f"Upload failed: {result['error']}")
                    else:
                        st.success(f"✅ PDF processed successfully!")
                        st.write(f"**Chunks created:** {result.get('chunks', 0)}")
                        st.write(f"**Storage method:** {result.get('storage_method', 'unknown')}")
                        st.write(f"**Embedding method:** {result.get('embedding_method', 'unknown')}")

                        if result.get('chunk_preview'):
                            st.subheader("Sample chunks:")
                            for i, chunk in enumerate(result['chunk_preview']):
                                st.text_area(f"Chunk {i+1}", chunk, height=100)
            except Exception as e:
                st.error(f"Unexpected error during PDF processing: {str(e)}")

    st.divider()

    # RAG Query
    st.subheader("🔍 Ask Questions About Your PDF")
    query = st.text_input("Enter your question:")

    if st.button("Ask Penny"):
        if query:
            try:
                with st.spinner("Searching..."):
                    result = rag_query(query, USER_ID)

                    if "error" in result:
                        st.error(f"Query failed: {result['error']}")
                    else:
                        st.success("✅ Answer found!")
                        st.write(f"**Answer:** {result.get('answer', 'No answer available')}")
                        st.write(f"**Method:** {result.get('method', 'unknown')}")
                        st.write(f"**Storage method:** {result.get('storage_method', 'unknown')}")

                        if result.get('context'):
                            st.subheader("Context:")
                            for i, context in enumerate(result['context']):
                                st.text_area(f"Context {i+1}", context, height=80)

                        if result.get('sources'):
                            st.subheader("Sources:")
                            for source in result['sources']:
                                st.write(f"• {source}")
            except Exception as e:
                st.error(f"Unexpected error during query: {str(e)}")

elif page == "Lists":
    st.title("📝 Lists Management")

    # Create new list
    st.subheader("Create New List")
    new_list_name = st.text_input("List name:")
    if st.button("Create List"):
        if new_list_name:
            try:
                result = create_list(USER_ID, new_list_name)
                if "error" in result:
                    st.error(f"Failed to create list: {result['error']}")
                else:
                    st.success(f"✅ List '{new_list_name}' created!")
                    st.rerun()
            except Exception as e:
                st.error(f"Unexpected error creating list: {str(e)}")
        else:
            st.warning("Please enter a list name")

    st.divider()

    # View and manage lists
    st.subheader("Your Lists")
    try:
        lists = get_lists(USER_ID)

        if not lists:
            st.info("No lists found. Create your first list above!")
        else:
            # Handle both list of strings and list of dictionaries
            for list_data in lists:
                try:
                    # Check if list_data is a string or dictionary
                    if isinstance(list_data, str):
                        # Handle string format (fallback)
                        list_name = list_data
                        list_id = f"list_{hash(list_data)}"
                        current_items = []
                    elif isinstance(list_data, dict):
                        # Handle dictionary format (expected)
                        list_name = list_data.get('name', 'Unnamed List')
                        list_id = list_data.get('id', f"list_{hash(list_name)}")
                        current_items = list_data.get('items', [])
                    else:
                        # Handle unexpected format
                        list_name = str(list_data)
                        list_id = f"list_{hash(str(list_data))}"
                        current_items = []

                    with st.expander(f"📋 {list_name}"):
                        # Add new item
                        new_item = st.text_input(f"Add item to {list_name}:", key=f"new_item_{list_id}")
                        if st.button("Add Item", key=f"add_{list_id}"):
                            if new_item:
                                try:
                                    updated_items = current_items + [new_item]
                                    result = update_list(list_id, updated_items)
                                    if "error" in result:
                                        st.error(f"Failed to add item: {result['error']}")
                                    else:
                                        st.success("✅ Item added!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Unexpected error adding item: {str(e)}")

                        # Display items
                        if current_items:
                            st.subheader("Items:")
                            for i, item in enumerate(current_items):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"{i+1}. {item}")
                                with col2:
                                    if st.button("Delete", key=f"del_{list_id}_{i}"):
                                        try:
                                            updated_items = current_items[:i] + current_items[i+1:]
                                            result = update_list(list_id, updated_items)
                                            if "error" in result:
                                                st.error(f"Failed to delete item: {result['error']}")
                                            else:
                                                st.success("✅ Item deleted!")
                                                st.rerun()
                                        except Exception as e:
                                            st.error(f"Unexpected error deleting item: {str(e)}")
                        else:
                            st.info("No items in this list yet.")

                        # Delete entire list
                        if st.button("🗑️ Delete List", key=f"delete_list_{list_id}"):
                            try:
                                result = delete_list(list_id)
                                if "error" in result:
                                    st.error(f"Failed to delete list: {result['error']}")
                                else:
                                    st.success("✅ List deleted!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Unexpected error deleting list: {str(e)}")
                except Exception as e:
                    st.error(f"Error processing list: {str(e)}")
                    continue
    except Exception as e:
        st.error(f"Failed to load lists: {str(e)}")
        st.info("Please check your backend connection.")

elif page == "Calendar":
    st.title("📅 Calendar")

    # Get calendar events
    if st.button("🔄 Refresh Calendar"):
        try:
            with st.spinner("Fetching calendar events..."):
                result = get_calendar_events(USER_ID)

                if "error" in result:
                    st.error(f"Failed to fetch calendar: {result['error']}")
                else:
                    events = result.get('events', [])
                    source = result.get('source', 'unknown')

                    st.success(f"✅ Calendar loaded from {source}")

                    if not events:
                        st.info("No upcoming events found.")
                    else:
                        st.subheader(f"📅 Upcoming Events ({len(events)})")

                        for event in events:
                            try:
                                if isinstance(event, dict):
                                    event_title = event.get('title', 'Untitled Event')
                                    with st.expander(f"📅 {event_title}"):
                                        st.write(f"**Start:** {event.get('start', 'Unknown')}")
                                        st.write(f"**End:** {event.get('end', 'Unknown')}")
                                        if event.get('location'):
                                            st.write(f"**Location:** {event['location']}")
                                        if event.get('description'):
                                            st.write(f"**Description:** {event['description']}")
                                        if event.get('attendees'):
                                            st.write(f"**Attendees:** {', '.join(event['attendees'])}")
                                else:
                                    st.write(f"• {str(event)}")
                            except Exception as e:
                                st.error(f"Error displaying event: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error fetching calendar: {str(e)}")

elif page == "Chat":
    st.title("💬 Chat with Penny")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        try:
            with st.chat_message(message.get("role", "user")):
                st.write(message.get("content", "Empty message"))
        except Exception as e:
            st.error(f"Error displaying message: {str(e)}")

    # Chat input
    if prompt := st.chat_input("Ask Penny anything..."):
        try:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.write(prompt)

            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Penny is thinking..."):
                    result = chat(prompt, USER_ID)

                    if "error" in result:
                        response = f"Sorry, I encountered an error: {result['error']}"
                    else:
                        response = result.get('response', 'I apologize, but I cannot respond at the moment.')

                    st.write(response)

                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Unexpected error in chat: {str(e)}")

elif page == "Memory":
    st.title("🧠 Memory Bank")

    if st.button("🔄 Refresh Memory"):
        try:
            with st.spinner("Loading memory..."):
                result = get_memory()

                if "error" in result:
                    st.error(f"Failed to load memory: {result['error']}")
                else:
                    memory_data = result.get('memory', {})

                    # User preferences
                    if 'user_preferences' in memory_data:
                        st.subheader("👤 User Preferences")
                        prefs = memory_data['user_preferences']
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Theme:** {prefs.get('theme', 'Not set')}")
                            st.write(f"**Language:** {prefs.get('language', 'Not set')}")
                        with col2:
                            st.write(f"**Notifications:** {'Enabled' if prefs.get('notifications') else 'Disabled'}")

                    # Recent queries
                    if 'recent_queries' in memory_data:
                        st.subheader("🔍 Recent Queries")
                        for query in memory_data['recent_queries']:
                            st.write(f"• {query}")

                    # Favorite topics
                    if 'favorite_topics' in memory_data:
                        st.subheader("⭐ Favorite Topics")
                        for topic in memory_data['favorite_topics']:
                            st.write(f"• {topic}")
        except Exception as e:
            st.error(f"Unexpected error loading memory: {str(e)}")

elif page == "Evaluation":
    st.title("📊 Evaluation")

    st.info("This feature allows you to evaluate and improve AI responses.")

    # Sample evaluation data
    sample_data = {
        "data": [
            {"query": "What is machine learning?", "response": "Machine learning is...", "rating": 4},
            {"query": "How to deploy to Cloud Run?", "response": "To deploy to Cloud Run...", "rating": 3}
        ]
    }

    if st.button("🧪 Run Sample Evaluation"):
        try:
            with st.spinner("Running evaluation..."):
                result = evaluate(sample_data)

                if "error" in result:
                    st.error(f"Evaluation failed: {result['error']}")
                else:
                    st.success("✅ Evaluation completed!")

                    # Display metrics
                    metrics = result.get('metrics', {})
                    if metrics:
                        st.subheader("📈 Metrics")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
                            st.metric("Precision", f"{metrics.get('precision', 0):.2%}")
                        with col2:
                            st.metric("Recall", f"{metrics.get('recall', 0):.2%}")
                            st.metric("F1 Score", f"{metrics.get('f1_score', 0):.2%}")

                    # Display details
                    details = result.get('details', {})
                    if details:
                        st.subheader("📋 Details")
                        st.write(f"**Total samples:** {details.get('total_samples', 0)}")
                        st.write(f"**Evaluation time:** {details.get('evaluation_time', 'Unknown')}")
                        st.write(f"**Model version:** {details.get('model_version', 'Unknown')}")
        except Exception as e:
            st.error(f"Unexpected error during evaluation: {str(e)}")

# Footer
st.divider()
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Penny Assistant**")
    st.markdown("Your AI companion")
with col2:
    st.markdown("**Backend Status**")
    try:
        health = health_check()
        if "error" in health:
            st.error("❌ Backend Error")
        else:
            st.success("✅ Backend OK")
    except Exception as e:
        st.error("❌ Backend Unreachable")
with col3:
    st.markdown("**Version**")
    st.markdown("v1.0.0") 