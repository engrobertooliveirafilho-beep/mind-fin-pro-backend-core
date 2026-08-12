import os

k=os.environ["GOOGLE_API_KEY"]

print("LEN=",len(k))
print("PREFIX=",k[:8])
print("SUFFIX=",k[-6:])
