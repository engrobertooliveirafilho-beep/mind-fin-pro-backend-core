class Streamer:
    def stream(self, output):
        for chunk in output:
            yield chunk
