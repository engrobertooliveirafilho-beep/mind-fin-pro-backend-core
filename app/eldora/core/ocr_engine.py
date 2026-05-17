from datetime import datetime, timezone

OCR_EVENTS=[]

def run_ocr_simulation(content:str):
    item={
        "detected_text":content[:1000],
        "confidence":0.98,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    OCR_EVENTS.append(item)

    return {
        "status":"ok",
        "ocr":item
    }

def ocr_report():
    return {
        "status":"ok",
        "events_total":len(OCR_EVENTS),
        "events":OCR_EVENTS[-20:]
    }
