from app.modules.usde_core.scientific_os import ScientificOS

USDE_RUNTIME = {
    "status": "BOOTING",
    "scientific_os": None,
    "modules": []
}

def bind_usde_runtime():
    boot = ScientificOS().boot()

    USDE_RUNTIME["status"] = "ONLINE"
    USDE_RUNTIME["scientific_os"] = boot
    USDE_RUNTIME["modules"] = boot["modules"]

    return USDE_RUNTIME
