import os, urllib.request, urllib.parse, json, urllib.error

key=os.environ["GOOGLE_API_KEY"]

url="https://www.googleapis.com/serviceusage/v1/services?key=" + urllib.parse.quote(key)

try:
    with urllib.request.urlopen(url, timeout=30) as r:
        print("STATUS=", r.status)
        print(r.read().decode("utf-8")[:1000])
except urllib.error.HTTPError as e:
    print("STATUS=", e.code)
    print(e.read().decode("utf-8"))
