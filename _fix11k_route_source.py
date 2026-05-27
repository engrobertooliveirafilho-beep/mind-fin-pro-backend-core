import inspect
import app.main as m

for r in m.app.routes:
    path=getattr(r,"path",None)
    methods=getattr(r,"methods",None)
    endpoint=getattr(r,"endpoint",None)
    if path and "webhook" in path.lower():
        print("PATH=",path)
        print("METHODS=",methods)
        print("ENDPOINT=",endpoint)
        print("ENDPOINT_NAME=",getattr(endpoint,"__name__",None))
        print("MODULE=",getattr(endpoint,"__module__",None))
        print("SOURCE_FILE=",inspect.getsourcefile(endpoint))
        print("FIRST_LINE=",endpoint.__code__.co_firstlineno if hasattr(endpoint,"__code__") else None)
        print(inspect.getsource(endpoint)[:4000])
        print("="*100)
