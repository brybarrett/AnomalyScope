# ensure src/ is on path via pytest.ini; import without "src."
from anomaly_scanner.scanner import run_scan

def test_run_scan():
    anomalies = run_scan()
    assert len(anomalies) > 0
    assert anomalies[0].id == "001"
