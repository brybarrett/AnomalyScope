import requests
from pydantic import BaseModel

class Anomaly(BaseModel):
    id: str
    description: str
    severity: str

def run_scan() -> list[Anomaly]:
    # TODO: Replace with real anomaly detection logic
    print("[🔍] Running anomaly scan...")
    return [
        Anomaly(id="001", description="Test anomaly", severity="low"),
    ]

def main():
    anomalies = run_scan()
    for a in anomalies:
        print(f"[🚨] {a.id}: {a.description} (Severity: {a.severity})")

if __name__ == "__main__":
    main()
