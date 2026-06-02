# P4.28O — Direct Webhook Runtime

VALIDATION:
- /webhook/whatsapp now defaults to MIND_WEBHOOK_DIRECT_RUNTIME=1
- app/main.py delegates directly to eldora_primary_runtime_reply()
- legacy post-interceptors in app/main.py bypassed by default
- rollback: set MIND_WEBHOOK_DIRECT_RUNTIME=0
- directed broad pytest: 24 passed / 3 skipped / 0 failed

LOCAL_TEMP=SIM
CLOUD_UPLOAD=SIM
