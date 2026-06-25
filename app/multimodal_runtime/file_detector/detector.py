class FileTypeDetector:
    def detect(self, filename):
        ext = filename.split('.')[-1].lower()

        if ext in ['jpg','png','webp','jpeg']:
            return 'image'
        if ext in ['mp4','mov','avi','mkv']:
            return 'video'
        if ext in ['mp3','wav','m4a']:
            return 'audio'
        if ext in ['pdf','docx','txt','csv','xlsx']:
            return 'document'
        return 'unknown'
