from app.eldora.core.admin_guard import admin_routes_enabled

def test_admin_routes_disabled_by_default():
    assert admin_routes_enabled() is False
