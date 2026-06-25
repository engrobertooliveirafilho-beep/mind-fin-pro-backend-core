class MultiResponseEngine:
    def split_response(self, text):
        return text.split('\n\n')  # logical segmentation

    def stream(self, parts):
        for p in parts:
            yield p
