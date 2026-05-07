from pypdf import PdfReader
import re


def clean_text(text):

    # Remove excessive spaces between letters
    text = re.sub(
        r'(?<=\\w)\\s(?=\\w)',
        '',
        text
    )

    # Normalize spaces
    text = re.sub(
        r'\\s+',
        ' ',
        text
    )

    return text.strip()


def load_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            cleaned = clean_text(extracted)

            text += cleaned + "\\n"

    return text