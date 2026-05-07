from pypdf import PdfReader
import re


def clean_text(text):

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


def load_pdf(file_path):

    reader = PdfReader(file_path)

    pages = []

    for i, page in enumerate(reader.pages):

        extracted = page.extract_text()

        if extracted:

            cleaned = clean_text(extracted)

            pages.append(
                {
                    "page": i + 1,
                    "text": cleaned
                }
            )

    return pages