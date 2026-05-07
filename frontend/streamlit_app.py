import streamlit as st
import requests
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    page_title="Pro PDF AI Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to fix the layout and prevent page-level jumping
st.markdown("""
    <style>
        /* Remove extra padding at the top of the main area */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 0rem;
        }
        
        /* Ensure the main container doesn't overflow horizontally */
        .main {
            overflow: hidden;
        }

        /* Style for the sticky header area */
        .header-wrapper {
            margin-bottom: 1rem;
        }
        
        /* Adjust the file uploader styling */
        .stFileUploader {
            padding-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

BASE_URL = "http://backend:8000"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_id" not in st.session_state:
    st.session_state.doc_id = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

with st.sidebar:
    st.title("📂 Document Hub")
    st.markdown("Upload your document to begin the AI analysis.")
    
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Only PDF files are supported for now.",
        label_visibility="collapsed"
    )

    if uploaded_file and (st.session_state.pdf_bytes != uploaded_file.getvalue()):
        with st.spinner("Processing document..."):
            try:
                files = {"file": uploaded_file}
                response = requests.post(f"{BASE_URL}/upload-pdf", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.doc_id = data["doc_id"]
                    st.session_state.pdf_bytes = uploaded_file.getvalue()
                    # Clear chat when a new document is uploaded
                    st.session_state.messages = []
                    st.toast("Document processed successfully!", icon="✅")
                else:
                    st.error("Upload failed. Please check backend connection.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Column ratios: 5 for PDF (Fixed), 5 for Chat (Scrollable)
left_col, right_col = st.columns([5, 5], gap="medium")

with left_col:
    st.subheader("📄 Document Preview")
    if st.session_state.pdf_bytes:
        # The PDF viewer is placed here. It stays static while the right side scrolls.
        pdf_viewer(
            input=st.session_state.pdf_bytes,
            width=700,
            height=850  # Fixed height for the viewer
        )
    else:
        st.info("Please upload a PDF in the sidebar to view it here.")
        # Placeholder visual
        st.markdown(
            """
            <div style="height: 750px; border: 2px dashed #ddd; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #aaa;">
                Document Preview Area
            </div>
            """, unsafe_allow_html=True
        )

with right_col:
    st.subheader("💬 AI Assistant")
    
    # This container has a fixed height and will handle its own scrolling.
    # New messages will cause this container to scroll, but the page won't move.
    chat_container = st.container(height=750, border=True)

    with chat_container:
        if not st.session_state.messages:
            st.caption("The conversation history will appear here. Ask a question below.")
        
        # Display existing chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and message.get("sources"):
                    with st.expander("🔍 Citations"):
                        for source in message["sources"]:
                            st.markdown(f"**Page {source['page']}**")
                            st.caption(source["content"])

    # Input remains at the bottom of the column
    question = st.chat_input(
        "Type your question here...", 
        disabled=not st.session_state.doc_id
    )

    if question:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Display the message immediately in the container
        with chat_container:
            with st.chat_message("user"):
                st.markdown(question)
        
        # Get assistant response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing text..."):
                    try:
                        payload = {"question": question, "doc_id": st.session_state.doc_id}
                        resp = requests.post(f"{BASE_URL}/ask", json=payload)
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            ans = data.get("answer", "I couldn't find an answer.")
                            srcs = data.get("sources", [])
                            
                            st.markdown(ans)
                            if srcs:
                                with st.expander("🔍 Citations"):
                                    for s in srcs:
                                        st.markdown(f"**Page {s['page']}**")
                                        st.caption(s["content"])
                            
                            # Update history
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": ans, 
                                "sources": srcs
                            })
                        else:
                            st.error("The assistant is having trouble. Try again later.")
                    except Exception:
                        st.error("Connection error. Is the backend running?")

st.caption("Developed with ❤️ for PDF Intelligence.")