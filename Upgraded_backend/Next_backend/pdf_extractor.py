from io import BytesIO
import pdfplumber


def extract_text_from_pdf(content):
    try:
        text_parts = []
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    print(f"Warning: Failed to extract page {page_num + 1}: {e}")
                    continue
        return "\n\n".join(text_parts).lower()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""