
from xml.sax.saxutils import escape
class ResponseBuilder:
    def twiml(self, reply):
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escape(reply or "OK")}</Message></Response>'
