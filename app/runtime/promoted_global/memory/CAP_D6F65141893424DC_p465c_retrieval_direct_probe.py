import traceback

print("P4.65C_RETRIEVAL_DIRECT_PROBE")

try:
    from app.memory.memory_graph import (
        save_message,
        retrieve_relevant_memory,
        retrieve_user_profile,
        retrieve_project_context,
    )

    user = "p465c_retrieval_probe"

    print("\nSAVE_MESSAGE")
    try:
        print(save_message(user, "P4.65C_SENTINEL: Drive knowledge graph retrieval should surface this sentence."))
    except Exception:
        print(traceback.format_exc())

    print("\nRETRIEVE_RELEVANT_MEMORY")
    try:
        print(retrieve_relevant_memory(user, "P4.65C_SENTINEL Drive knowledge graph", limit=5))
    except TypeError:
        try:
            print(retrieve_relevant_memory(user, "P4.65C_SENTINEL Drive knowledge graph"))
        except Exception:
            print(traceback.format_exc())
    except Exception:
        print(traceback.format_exc())

    print("\nRETRIEVE_USER_PROFILE")
    try:
        print(retrieve_user_profile(user))
    except Exception:
        print(traceback.format_exc())

    print("\nRETRIEVE_PROJECT_CONTEXT")
    try:
        print(retrieve_project_context(user))
    except Exception:
        print(traceback.format_exc())

except Exception:
    print("MEMORY_GRAPH_IMPORT_OR_PROBE_ERROR")
    print(traceback.format_exc())

try:
    from app.runtime.cognitive_pipeline import run_cognitive_pipeline
    print("\nPIPELINE_AFTER_SENTINEL")
    print(run_cognitive_pipeline(user, "Use a memória P4.65C_SENTINEL e diga o próximo passo."))
except Exception:
    print("PIPELINE_ERROR")
    print(traceback.format_exc())

print("\nP4.65C_RETRIEVAL_DIRECT_PROBE_COMPLETE")
