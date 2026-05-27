from pathlib import Path

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

target='''            primary_reply = dispatch_single_runtime(sender_id,message,eldora_primary_runtime_reply(sender_id,message),module="main",function="eldora_primary_runtime_reply")'''

patch='''            primary_reply = dispatch_single_runtime(sender_id,message,eldora_primary_runtime_reply(sender_id,message),module="main",function="eldora_primary_runtime_reply")
            msg=(message or "").lower().strip()
            bad_reply=(not primary_reply) or str(primary_reply).strip().lower() in ["entendi. continua.","entendi.\\n\\ncontinua."]
            if any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você","quem é voce","quem e voce"]) and (bad_reply or "tudo certo" in str(primary_reply).lower()):
                primary_reply="Sou a Eldora 🙂 O que você quer saber?"
            elif any(x in msg for x in ["como você está","como vc está","vc está bem","tudo bem"]) and bad_reply:
                primary_reply="Tudo certo por aqui 🙂 E você?"
            elif ("quanto é" in msg or "x" in msg) and bad_reply:
                primary_reply=safe_reply(message)
            elif any(x in msg for x in ["e depois","depois?"]) and bad_reply:
                primary_reply="Depois mantemos contexto, validamos o fluxo real e seguimos sem reset semântico."'''

assert target in s, "DISPATCH_TARGET_NOT_FOUND"
s=s.replace(target,patch,1)
p.write_text(s,encoding="utf-8")
print("DISPATCH_INTENT_RESCUE_OK")
