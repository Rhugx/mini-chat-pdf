import streamlit as st
import requests
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    page_title="Pro PDF AI Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        /* Main container styling */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        /* Force the main app to occupy full height without main page scrollbar */
        .main {
            overflow: hidden;
        }

        /* Ensure images and components don't overflow their containers */
        .stColumn > div {
            width: 100% !important;
        }

        /* Custom styling for the PDF preview area */
        .pdf-container {
            border: 1px solid #e6e9ef;
            border-radius: 0.5rem;
            background-color: #f8f9fb;
            overflow: hidden;
            display: flex;
            justify-content: center;
        }
        
        /* Button styling for a more professional feel */
        .stButton button {
            border-radius: 6px;
            font-weight: 500;
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
    st.markdown("Upload a PDF to start a contextual conversation with AI.")
    
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Only PDF files are supported.",
        label_visibility="collapsed"
    )

    if uploaded_file and (st.session_state.pdf_bytes != uploaded_file.getvalue()):
        with st.spinner("Analyzing document structure..."):
            try:
                files = {"file": uploaded_file}
                response = requests.post(f"{BASE_URL}/upload-pdf", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.doc_id = data["doc_id"]
                    st.session_state.pdf_bytes = uploaded_file.getvalue()
                    st.session_state.messages = []  # Reset chat for new context
                    st.toast("Document indexed successfully!", icon="✅")
                else:
                    st.error("Failed to process document. Please try again.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Using [1, 1] ratio ensures both sides have equal real estate on large screens
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("📄 Document Preview")
    
    if st.session_state.pdf_bytes:
        # We wrap the viewer in a div and remove fixed 'width' to let it scale to its container.
        # Fixed height here matches the chat container height for visual alignment.
        st.markdown('<div class="pdf-container">', unsafe_allow_html=True)
        pdf_viewer(
            input=st.session_state.pdf_bytes,
            height=750,  # Defined height to prevent double scrollbars on the page
            width=None,   # Setting width to None allows it to be responsive to the column
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # User-friendly placeholder when no PDF is uploaded
        st.info("Your document will appear here after upload.")
        st.markdown(
            """
            <div style="height: 750px; border: 2px dashed #d1d5db; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #6b7280; background-color: #f9fafb;">
                <p style="font-size: 24px; margin-bottom: 8px;">📑</p>
                <p>Waiting for PDF upload...</p>
            </div>
            """, unsafe_allow_html=True
        )

with right_col:
    st.subheader("💬 AI Assistant")
    
    # The chat container has a fixed height matching the PDF preview.
    # It handles its own vertical scrolling.
    chat_container = st.container(height=750, border=True)

    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                """
                <div style="text-align: center; margin-top: 200px; color: #9ca3af;">
                    <h3>Welcome!</h3>
                    <p>Ask a question about your document to begin.</p>
                </div>
                """, unsafe_allow_html=True
            )
        
        # Rendering existing messages from state
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and message.get("sources"):
                    with st.expander("🔍 Citations"):
                        for source in message["sources"]:
                            st.markdown(f"**Page {source['page']}**")
                            st.caption(source["content"])

    # Input logic for new queries
    question = st.chat_input(
        "Ask a question...", 
        disabled=not st.session_state.doc_id
    )

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Instant feedback in the chat window
        with chat_container:
            with st.chat_message("user"):
                st.markdown(question)
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Consulting document..."):
                    try:
                        payload = {"question": question, "doc_id": st.session_state.doc_id}
                        resp = requests.post(f"{BASE_URL}/ask", json=payload)
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            ans = data.get("answer", "I'm sorry, I couldn't find a relevant answer in the document.")
                            srcs = data.get("sources", [])
                            
                            st.markdown(ans)
                            if srcs:
                                with st.expander("🔍 Citations"):
                                    for s in srcs:
                                        st.markdown(f"**Page {s['page']}**")
                                        st.caption(s["content"])
                            
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": ans, 
                                "sources": srcs
                            })
                        else:
                            st.error("The assistant encountered an error. Please check the backend.")
                    except Exception:
                        st.error("Connection lost. Please ensure the backend server is running.")

st.caption("Developed with ❤️ for Document Intelligence.")