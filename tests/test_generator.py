from anomaly_scanner.scanner import Anomaly
from reporting.generator import generate_anomaly_card

def test_generate_anomaly_card():
    anomaly = Anomaly(id="123", description="Unit test anomaly", severity="medium")
    card = generate_anomaly_card(anomaly)

    assert isinstance(card, dict)
    assert card["id"] == "123"
    assert card["description"] == "Unit test anomaly"
    assert card["severity"] == "medium"
