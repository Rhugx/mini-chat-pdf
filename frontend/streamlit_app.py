import streamlit as st
import requests

BASE_URL = "http://backend:8000"

st.set_page_config(
    page_title="AI PDF Chat",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI PDF Chat Assistant")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "doc_id" not in st.session_state:
    st.session_state.doc_id = None


# Sidebar
with st.sidebar:
    st.header("📤 Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"]
    )

    if uploaded_file:

        files = {
            "file": uploaded_file
        }

        with st.spinner("Uploading and processing PDF..."):

            response = requests.post(
                f"{BASE_URL}/upload-pdf",
                files=files
            )

        if response.status_code == 200:

            data = response.json()

            st.session_state.doc_id = data["doc_id"]

            st.success("✅ PDF uploaded successfully!")

        else:
            st.error("❌ Upload failed")


# Main Chat Area
st.subheader("💬 Chat with your PDF")


# Display previous chat messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask something about your PDF...")
st.caption(
    "⚠ Beta Version: This AI assistant is currently under testing. "
    "Use clear prompts for best results."
)


if question:

    # Ensure PDF uploaded
    if not st.session_state.doc_id:

        st.warning("⚠ Please upload a PDF first.")

    else:

        # Store user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # Display user message
        with st.chat_message("user"):
            st.markdown(question)

        # Generate AI response
        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                payload = {
                    "question": question,
                    "doc_id": st.session_state.doc_id
                }

                response = requests.post(
                    f"{BASE_URL}/ask",
                    json=payload
                )

                if response.status_code == 200:

                    answer = response.json()["answer"]

                    st.markdown(answer)

                    # Store assistant response
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                else:

                    st.error("❌ Failed to get response")