def load_state(user_id):
    return {"current_focus":"Eldora Cognitive Runtime","conversation_arc":"implementation","user_energy":"high","relationship_stage":"operational_partner","dominant_project":"MIND","emotional_tone":"focused","last_unresolved_topic":"","continuity_anchor":"prosseguir evolução Eldora"}
def update_state(message, intent, memory):
    s=load_state("default"); s["current_focus"]=intent.get("intent","general"); s["last_unresolved_topic"]=message; return s
def persist_state(user_id, state): return {"persisted":True,"user_id":user_id,"state":state}
