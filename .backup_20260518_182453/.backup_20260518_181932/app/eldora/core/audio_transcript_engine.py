from datetime import datetime, timezone

AUDIO_TRANSCRIPTS=[]

def transcript_audio_simulation(text:str):
    item={
        "transcript":text,
        "language":"pt-BR",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    AUDIO_TRANSCRIPTS.append(item)

    return {
        "status":"ok",
        "transcript":item
    }

def transcript_report():
    return {
        "status":"ok",
        "transcripts_total":len(AUDIO_TRANSCRIPTS),
        "items":AUDIO_TRANSCRIPTS[-20:]
    }
