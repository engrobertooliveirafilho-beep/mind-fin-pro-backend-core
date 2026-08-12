import os, sys
from pathlib import Path
from supabase import create_client

url=os.environ.get('SUPABASE_URL','').strip()
key=os.environ.get('SUPABASE_SERVICE_ROLE_KEY','').strip()
bucket=os.environ.get('SUPABASE_BUCKET','').strip() or 'mind-workspace'
zp=Path(r'''C:\MIND_MONO\mind-platform\services\mind-fin-pro-backend\_deploy\TELEMETRY\MIND_NEXT_STEP\MIND_RUNTIME_PROOF_VIDEO_PACK_20260207_070142.zip''')

if not url or not key:
    print('MISSING_ENV', {'SUPABASE_URL':bool(url),'SUPABASE_SERVICE_ROLE_KEY':bool(key)})
    sys.exit(2)
if not zp.exists():
    print('ZIP_NOT_FOUND', str(zp))
    sys.exit(3)

sb=create_client(url,key)
dest=f"mind_runtime_proofs/video/{zp.name}"

with zp.open('rb') as f:
    data=f.read()

# upsert=True to overwrite if needed
res = sb.storage.from_(bucket).upload(dest, data, {"content-type":"application/zip", "upsert":"true"})
print('UPLOAD_OK', {'bucket':bucket,'dest':dest,'size':len(data)})
