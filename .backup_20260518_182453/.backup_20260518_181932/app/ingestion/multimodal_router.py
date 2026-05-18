from app.ingestion.document_parser import DocumentParser
from app.ingestion.image_vision_runtime import ImageVisionRuntime

class MultiModalRouter:

    def __init__(self):
        self.parser = DocumentParser()
        self.vision = ImageVisionRuntime()

    def handle(self, media_type, media_url, local_path=None, user_message=""):

        media_type = str(media_type).lower()
        local_path_lower = str(local_path or "").lower()

        if "image" in media_type:
            return self.vision.analyze(
                image_url=media_url,
                local_path=local_path,
                user_message=user_message
            )

        if local_path:
            if local_path_lower.endswith(".pdf"):
                return self.parser.parse_pdf(local_path)
            if local_path_lower.endswith(".docx"):
                return self.parser.parse_docx(local_path)
            if local_path_lower.endswith(".pptx"):
                return self.parser.parse_pptx(local_path)
            if local_path_lower.endswith(".xlsx"):
                return self.parser.parse_xlsx(local_path)
            if local_path_lower.endswith(".txt"):
                return self.parser.parse_txt(local_path)

        return "Não consegui interpretar o arquivo enviado."
