import os
import uuid
import requests

class FileDownloader:

    def download(self, media_url, content_type="application/octet-stream"):

        ext = ".bin"

        if "image" in content_type:
            ext = ".jpg"

        elif "pdf" in content_type:
            ext = ".pdf"

        elif "word" in content_type or "docx" in content_type:
            ext = ".docx"

        elif "presentation" in content_type or "pptx" in content_type:
            ext = ".pptx"

        elif "sheet" in content_type or "excel" in content_type or "xlsx" in content_type:
            ext = ".xlsx"

        path = f"/tmp/{uuid.uuid4()}{ext}"

        r = requests.get(media_url, timeout=30)

        with open(path, "wb") as f:
            f.write(r.content)

        return path
