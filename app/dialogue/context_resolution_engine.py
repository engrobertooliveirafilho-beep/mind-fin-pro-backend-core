from app.dialogue.conversation_continuity_runtime import get
def resolve(sender_id,user_text):
    st=get(sender_id)
    low=(user_text or "").lower()
    topic=st.get("active_topic","")
    if any(x in low for x in ["isso","esse","agora","e ai","e aí","como ficou","sentiu diferença","qual score","e depois"]):
        return topic or "conversa_geral"
    return topic
