import re

def chunk_text(text, chunk_size=500, overlap=100):
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    # Add overlap
    overlapped_chunks = []
    for i in range(len(chunks)):
        start = max(0, i - 1)
        combined = " ".join(chunks[start:i+1])
        overlapped_chunks.append(combined)

    return overlapped_chunks