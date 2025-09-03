# Anomaly OPENAI-vs-ANTHROPIC-DIVERGENCE

- **Timestamp:** 2025-09-03T23:44:35Z
- **Severity:** high
- **Description:** Cross-provider drift on prompt with runs=3, temp=0.9. cross_similarity=0.513; openai: mean=0.672, min=0.541; anthropic: mean=0.387, min=0.188.

## Meta
```json
{
  "prompt": "Explain the purpose of AnomalyScope in one concise sentence.",
  "threshold": 0.85,
  "providers": [
    "openai",
    "anthropic"
  ],
  "runs": 3,
  "temperature": 0.9,
  "samples": {
    "openai": [
      "AnomalyScope is a tool designed to detect, analyze, and visualize anomalies in data to enhance decision-making and operational efficiency.",
      "AnomalyScope is a tool designed for detecting and analyzing anomalies in data to enhance security and operational efficiency.",
      "AnomalyScope is designed to automatically detect, analyze, and visualize anomalies in data sets, helping organizations identify and address unusual patterns or behaviors quickly."
    ],
    "anthropic": [
      "AnomalyScope is a data visualization tool designed to help users identify, analyze, and understand anomalies or unusual patterns within complex datasets.",
      "AnomalyScope is a tool designed to help data scientists and analysts detect, investigate, and understand anomalies or unusual patterns within large datasets by providing advanced visualization and analysis capabilities.",
      "AnomalyScope is a diagnostic tool that helps identify and analyze unusual or unexpected patterns in data by providing visual and statistical insights into potential anomalies."
    ]
  },
  "cross_similarity": 0.5133613099039965,
  "within": {
    "openai": {
      "mean": 0.6719070280229159,
      "min": 0.5412541254125413
    },
    "anthropic": {
      "mean": 0.38707092531871773,
      "min": 0.1881720430107527
    }
  }
}
```