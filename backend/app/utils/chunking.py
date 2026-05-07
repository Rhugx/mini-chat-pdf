from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(pages):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    final_chunks = []

    for page_data in pages:

        page_number = page_data["page"]

        text = page_data["text"]

        chunks = splitter.split_text(text)

        for chunk in chunks:

            final_chunks.append(
                {
                    "page": page_number,
                    "content": chunk
                }
            )

    return final_chunks