import traceback

from app.runtime.cognitive_pipeline import run_cognitive_pipeline

MEMORIES = [
    "short_memory",
    "social_memory",
    "emotion_memory",
    "relationship_memory",
    "semantic_memory",
    "memory_graph",
]

sender = "p464a_audit"

for memory in MEMORIES:
    print("\n" + "=" * 90)
    print("MEMORY:", memory)
    print("=" * 90)

    try:
        result = run_cognitive_pipeline(
            sender,
            f"[MEMORY_TEST={memory}] qual próximo passo?"
        )

        if isinstance(result, dict):
            print("INTENT:", result.get("intent"))
            print("ANSWER:", str(result.get("answer"))[:1000])
            print("SOCIAL:", result.get("social"))
            print("EMOTION:", result.get("emotion"))
            print("RELATIONSHIP:", result.get("relationship"))
        else:
            print(type(result).__name__)
            print(str(result)[:1000])

    except Exception:
        print(traceback.format_exc())

print("\nP4.64A_COMPLETE")
