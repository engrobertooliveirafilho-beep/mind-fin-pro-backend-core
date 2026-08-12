import time
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

LOG = "_evidence/daemon_log.txt"

while True:
    try:
        r = run_cognitive_pipeline(
            "whatsapp:+5519996166906",
            "quero lançar a Eldora com plano e simulação de risco"
        )

        with open(LOG, "a", encoding="utf-8") as f:
            f.write(str(r.get("intent")) + "\n")

    except Exception as e:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("ERROR: " + str(e) + "\n")

    time.sleep(10)
