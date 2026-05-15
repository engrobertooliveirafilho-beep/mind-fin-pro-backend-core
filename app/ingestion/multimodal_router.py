from app.ingestion.document_parser import DocumentParser
from app.ingestion.image_vision_runtime import ImageVisionRuntime

class MultiModalRouter:

    def __init__(self):
        self.parser = DocumentParser()
        self.vision = ImageVisionRuntime()

    def handle(self, media_type, media_url, local_path=None):

        media_type = str(media_type).lower()

        if "image" in media_type:
            return self.vision.analyze(media_url)

        if local_path:

            if ".pdf" in local_path:
                return self.parser.parse_pdf(local_path)

            if ".docx" in local_path:
                return self.parser.parse_docx(local_path)

            if ".pptx" in local_path:
                return self.parser.parse_pptx(local_path)

            if ".xlsx" in local_path:
                return self.parser.parse_xlsx(local_path)

            if ".txt" in local_path:
                return self.parser.parse_txt(local_path)

        return "Não consegui interpretar o arquivo enviado."
