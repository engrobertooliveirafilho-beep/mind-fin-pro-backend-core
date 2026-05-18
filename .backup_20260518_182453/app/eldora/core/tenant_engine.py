TENANTS = {
    "default": {
        "tenant_id": "default",
        "name": "Default Tenant",
        "status": "active"
    }
}

def resolve_tenant(tenant_id: str | None = None):
    key = tenant_id or "default"
    return TENANTS.get(key, TENANTS["default"])
