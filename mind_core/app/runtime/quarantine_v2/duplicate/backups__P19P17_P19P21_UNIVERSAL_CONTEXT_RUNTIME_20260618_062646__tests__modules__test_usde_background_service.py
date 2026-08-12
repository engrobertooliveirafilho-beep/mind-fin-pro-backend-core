from app.modules.usde_core.scientific_background_service import ScientificBackgroundService

def test_background_service():
    r=ScientificBackgroundService().start(
        {"events":1000}
    )

    assert r["service_status"]=="COMPLETED"
    assert r["executed"]==5
