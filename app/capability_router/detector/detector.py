class ModalityDetector:
    def detect(self, input_data):
        if "image" in input_data.lower():
            return "vision"
        if "video" in input_data.lower():
            return "video"
        return "text"
