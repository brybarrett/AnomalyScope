def generate_anomaly_card(anomaly):
    """Convert an anomaly object into a simple card (dict)."""
    return {
        "id": anomaly.id,
        "description": anomaly.description,
        "severity": anomaly.severity,
    }
