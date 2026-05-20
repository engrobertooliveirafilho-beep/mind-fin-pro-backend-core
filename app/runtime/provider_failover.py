import os

class ProviderFailover:
    def __init__(self, providers=None):
        self.providers=providers or []

    def run(self, prompt: str):
        errors=[]
        for name,fn in self.providers:
            try:
                r=fn(prompt)
                if r:
                    return {"status":"ok","provider":name,"output":r,"errors":errors}
            except Exception as e:
                errors.append({"provider":name,"error":str(e)})
        return {"status":"failed","provider":None,"output":None,"errors":errors}

def failover_selftest():
    f=ProviderFailover([("broken",lambda p: (_ for _ in ()).throw(RuntimeError("forced_fail"))),("local_safe",lambda p: "fallback real operacional")])
    return f.run("teste")
