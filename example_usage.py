"""
example_usage.py -- Demonstrates the WarrantyClaimClient SDK.
"""
from client import WarrantyClaimClient

def main():
    client = WarrantyClaimClient()

    print("[1] Approved Claim")
    result = client.process(
        claim={"product_id":"P001","purchase_date":"2026-02-15","claim_date":"2026-07-01",
               "issue_description":"The screen developed a dead pixel cluster after normal use.","proof_provided":True},
        product={"name":"Wireless Earbuds Pro","warranty_months":12,"category":"electronics","price":89.99},
        customer={"past_claims":1,"account_age_months":24,"total_orders":8},
    )
    print(f"Decision: {result['decision'].upper()}")
    print(f"Reason: {result['decision_reason']}")
    print(f"Eligibility: within={result['eligibility']['within_warranty']} | days_remaining={result['eligibility']['days_remaining']}")
    print(f"Fraud Risk: {result['fraud_risk']['risk_level']} (score: {result['fraud_risk']['fraud_score']})")
    print(f"Resolution Options:")
    for opt in result["resolution_options"]:
        print(f"  - {opt[:70]}...")

    print("\n[2] Expired Warranty Claim")
    result2 = client.process(
        claim={"product_id":"P002","purchase_date":"2024-01-01","claim_date":"2026-07-01",
               "issue_description":"Stopped working.","proof_provided":False},
        product={"name":"Bluetooth Speaker","warranty_months":12,"category":"electronics","price":55.00},
    )
    print(f"Decision: {result2['decision'].upper()} | Reason: {result2['decision_reason']}")

    print("\n[3] High Fraud Risk Claim")
    result3 = client.process(
        claim={"product_id":"P003","purchase_date":"2026-06-20","claim_date":"2026-07-01",
               "issue_description":"Bad","proof_provided":False},
        product={"name":"Laptop","warranty_months":12,"category":"electronics","price":999.00},
        customer={"past_claims":5,"account_age_months":0,"total_orders":1},
    )
    print(f"Decision: {result3['decision'].upper()}")
    print(f"Fraud Score: {result3['fraud_risk']['fraud_score']} ({result3['fraud_risk']['risk_level']})")
    print(f"Signals: {result3['fraud_risk']['signals']}")

if __name__ == "__main__":
    main()
