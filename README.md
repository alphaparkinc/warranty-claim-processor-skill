# warranty-claim-processor-skill

> **GenPark AI Agent Skill** -- Process and validate warranty claims with eligibility checks, fraud detection, and resolution options.

## Features

- Warranty eligibility check with days-remaining calculation
- Multi-signal fraud detection: past claims, account age, proof, claim timing, vague descriptions
- Three-way decision: approved / denied / review_required
- Category-aware resolution options (replacement, repair, refund, store credit)
- Near-expiry claim flagging

## Quick Start

```python
from client import WarrantyClaimClient

client = WarrantyClaimClient()
result = client.process(
    claim={"purchase_date":"2026-01-01","claim_date":"2026-07-01","issue_description":"Screen cracked","proof_provided":True},
    product={"warranty_months":12,"category":"electronics","price":150},
    customer={"past_claims":0,"account_age_months":12},
)
print(f"Decision: {result['decision']} | Fraud: {result['fraud_risk']['risk_level']}")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
