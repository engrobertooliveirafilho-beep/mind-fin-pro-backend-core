from .routes import router

def run_p55n_healthcheck():
    return {
        "status": "P5.5N_READY",
        "routes": ["/p55/bulls/status", "/p55/bulls/ranking", "/p55/bulls/decision"]
    }
