import inspect
import traceback

print("P4.65C_FUNCTION_PROBE")

targets = [
    ("app.memory.memory_graph", [
        "save_message",
        "retrieve_relevant_memory",
        "retrieve_user_profile",
        "retrieve_project_context",
    ]),
    ("app.retrieval.semantic_provider", [
        "semantic_search",
        "retrieve",
        "search",
        "query",
    ]),
    ("app.runtime.semantic_answer_engine", [
        "answer_semantically",
    ]),
]

for module_name, names in targets:
    print("\n" + "=" * 90)
    print("MODULE:", module_name)
    print("=" * 90)

    try:
        mod = __import__(module_name, fromlist=["*"])
        print("IMPORT_OK:", module_name)
        print("FILE:", getattr(mod, "__file__", None))

        for name in names:
            obj = getattr(mod, name, None)
            if obj is None:
                print("MISSING:", name)
                continue

            print("FOUND:", name)
            try:
                print("SIGNATURE:", inspect.signature(obj))
            except Exception as e:
                print("SIGNATURE_ERROR:", repr(e))

    except Exception:
        print("IMPORT_ERROR:")
        print(traceback.format_exc())

print("\nP4.65C_FUNCTION_PROBE_COMPLETE")
