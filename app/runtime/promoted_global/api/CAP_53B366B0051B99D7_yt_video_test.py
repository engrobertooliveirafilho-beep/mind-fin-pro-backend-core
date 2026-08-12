import os
import urllib.request
import urllib.parse
import urllib.error

key=os.environ["YOUTUBE_API_KEY"]

url="https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode({
    "part":"snippet",
    "id":"dQw4w9WgXcQ",
    "key":key
})

try:
    with urllib.request.urlopen(url,timeout=30) as r:
        print("STATUS=",r.status)
        print(r.read().decode("utf-8")[:500])

except urllib.error.HTTPError as e:
    print("STATUS=",e.code)
    print(e.read().decode("utf-8"))
