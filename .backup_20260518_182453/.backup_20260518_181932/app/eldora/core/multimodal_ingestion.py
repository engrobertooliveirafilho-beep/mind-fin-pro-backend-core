from pathlib import Path
from pypdf import PdfReader
from docx import Document

SUPPORTED_EXTENSIONS = [
    ".txt",".pdf",".docx",".md"
]

def extract_text(path: str):
    p = Path(path)

    if not p.exists():
        return {
            "status":"error",
            "detail":"file_not_found"
        }

    ext = p.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        return {
            "status":"error",
            "detail":"unsupported_extension"
        }

    try:
        if ext == ".txt" or ext == ".md":
            content = p.read_text(encoding="utf-8", errors="ignore")

        elif ext == ".pdf":
            reader = PdfReader(path)
            pages=[]
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            content="\n".join(pages)

        elif ext == ".docx":
            doc=Document(path)
            content="\n".join([x.text for x in doc.paragraphs])

        else:
            content=""

        return {
            "status":"ok",
            "path":str(p),
            "extension":ext,
            "characters":len(content),
            "content":content[:5000]
        }

    except Exception as e:
        return {
            "status":"error",
            "detail":str(e)
        }
