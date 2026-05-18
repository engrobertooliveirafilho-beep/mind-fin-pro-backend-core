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

        sid = os.getenv("TWILIO_ACCOUNT_SID") or os.getenv("ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN") or os.getenv("AUTH_TOKEN")

        auth = (sid, token) if sid and token else None

        r = requests.get(media_url, auth=auth, timeout=30)

        if r.status_code >= 300:
            raise Exception(f"Twilio media download failed: {r.status_code} {r.text[:160]}")

        with open(path, "wb") as f:
            f.write(r.content)

        return path
