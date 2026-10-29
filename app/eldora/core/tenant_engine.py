TENANTS = {
    "default": {"tenant_id": "default", "name": "Default Tenant", "status": "active"}
}

def resolve_tenant(tenant_id: str | None = None):
    key = tenant_id or "default"
    # Never silently map an unknown tenant to the default tenant.
    tenant = TENANTS.get(key)
    if tenant is None:
        return {"tenant_id": key, "status": "not_found"}
    return dict(tenant)
