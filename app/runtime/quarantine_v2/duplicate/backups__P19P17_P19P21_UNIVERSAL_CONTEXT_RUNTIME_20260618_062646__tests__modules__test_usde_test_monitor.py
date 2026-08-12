from app.modules.usde_core.test_monitor import USDEScientificTestMonitor

def test_usde_test_monitor_discovers_tests():
    r=USDEScientificTestMonitor().discover_tests()

    assert isinstance(r,list)
