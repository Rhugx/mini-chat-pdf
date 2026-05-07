import streamlit as st
import requests

st.title("📄 Chat with PDF")

BASE_URL = "http://127.0.0.1:8000"

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    files = {
        "file": (uploaded_file.name, uploaded_file, "application/pdf")
    }

    response = requests.post(f"{BASE_URL}/upload-pdf", files=files)

    if response.status_code == 200:
        data = response.json()

        st.write("DEBUG:", data)

        if "doc_id" in data:
            st.session_state["doc_id"] = data["doc_id"]
            st.success("PDF uploaded successfully!")
        else:
            st.error("doc_id missing from backend")
    else:
        st.error("Upload failed")

# Ask question
question = st.text_input("Ask question")

if st.button("Ask"):
    if "doc_id" not in st.session_state:
        st.error("Upload PDF first")
    else:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={
                "question": question,
                "doc_id": st.session_state["doc_id"]
            }
        )

        if response.status_code == 200:
            st.write(response.json()["answer"])
        else:
            st.error(f"Error: {response.status_code}")