import inspect
import app.main as m

targets=[
"strategic_conversation_authority",
"final_conversational_arbiter",
"resolve_actionable_followup",
"detect_intent",
"decide_turn"
]

for name in targets:
    fn=getattr(m,name,None)
    print("\n"+"="*120)
    print("FN:",name)
    print("OBJ:",fn)
    if callable(fn):
        try:
            print("FILE:",inspect.getsourcefile(fn))
            print(inspect.getsource(fn)[:5000])
        except Exception as e:
            print("ERR",e)
