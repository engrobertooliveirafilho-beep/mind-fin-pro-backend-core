def recover_context(state):
    return {
      "topic":state.get("last_topic"),
      "problem":state.get("last_problem"),
      "reply":state.get("last_meaningful_reply"),
      "task":state.get("last_open_task"),
      "open_loop":state.get("open_loop",False)
    }
