def stability_tick(state):
    drift = 0.0

    if drift > 0.12:
        return "ROLLBACK"
    return "STABLE"
