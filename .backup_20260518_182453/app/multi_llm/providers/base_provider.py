import os, time, requests

class GenericHTTPProvider:
    def __init__(self, name, env_key, endpoint="", headers_fn=None, payload_fn=None, extract_fn=None):
        self.name=name
        self.api_key=os.getenv(env_key,"")
        self.endpoint=endpoint
        self.headers_fn=headers_fn
        self.payload_fn=payload_fn
        self.extract_fn=extract_fn

    def health(self):
        return bool(self.api_key)

    def chat(self, message):
        if not self.endpoint:
            return {"provider":self.name,"latency_ms":0,"response":f"{self.name.upper()}_ADAPTER_READY_NO_CHAT_ENDPOINT"}
        t0=time.time()
        r=requests.post(self.endpoint,headers=self.headers_fn(self.api_key),json=self.payload_fn(message),timeout=45)
        dt=round((time.time()-t0)*1000)
        data=r.json()
        return {"provider":self.name,"latency_ms":dt,"response":self.extract_fn(data)}
