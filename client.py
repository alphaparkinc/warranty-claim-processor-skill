"""
warranty-claim-processor-skill: Client SDK
Process and validate warranty claims with eligibility checks and fraud detection.
"""
from __future__ import annotations
from typing import Optional
from datetime import datetime, date

WARRANTY_MONTHS_DEFAULT = {"electronics": 12, "appliances": 24, "clothing": 3, "furniture": 12, "toys": 6, "beauty": 0, "default": 12}

FRAUD_SIGNALS = [
    ("multiple_claims",    "Customer has filed 3+ previous claims"),
    ("new_account",        "Account less than 30 days old"),
    ("no_proof",           "No proof of purchase provided"),
    ("claim_near_expiry",  "Claim filed within 7 days of warranty expiry"),
    ("high_value_item",    "High-value item claim without receipt"),
    ("vague_description",  "Issue description is very short or vague"),
]

RESOLUTION_OPTIONS = {
    "replacement": "Ship a replacement product at no charge within 5-7 business days.",
    "repair":      "Send the item to our service center for repair at no charge.",
    "refund":      "Issue a full refund to the original payment method within 3-5 business days.",
    "store_credit":"Issue store credit equal to the purchase price plus 10% goodwill bonus.",
    "partial_refund": "Issue a partial refund reflecting the remaining warranty period.",
}

DECISION_REASONS = {
    "approved":         "Claim is within warranty period, eligibility criteria met, low fraud risk.",
    "denied_expired":   "Warranty period has expired. The claim date is beyond the coverage window.",
    "denied_no_proof":  "Claim denied: no valid proof of purchase provided.",
    "review_required":  "Claim flagged for manual review due to elevated fraud risk signals.",
}


class WarrantyClaimClient:
    """
    SDK for processing e-commerce warranty claims.
    Validates eligibility, scores fraud risk, and generates claim decisions.
    """

    def process(
        self,
        claim: dict,
        product: dict,
        customer: Optional[dict] = None,
    ) -> dict:
        """
        Process a warranty claim.

        Args:
            claim:   {
                       product_id, purchase_date (YYYY-MM-DD), claim_date (YYYY-MM-DD),
                       issue_description (str), proof_provided (bool)
                     }
            product: {name, warranty_months (int), category, price (float)}
            customer:{past_claims (int), account_age_months (int), total_orders (int)}

        Returns:
            dict with decision, eligibility, fraud_risk, resolution_options
        """
        cust = customer or {}

        # Parse dates
        try:
            purchase = datetime.fromisoformat(claim.get("purchase_date", "2024-01-01")).date()
        except ValueError:
            purchase = date.today()
        try:
            claim_dt = datetime.fromisoformat(claim.get("claim_date", str(date.today()))).date()
        except ValueError:
            claim_dt = date.today()

        cat = str(product.get("category", "default")).lower()
        warranty_months = int(product.get("warranty_months", WARRANTY_MONTHS_DEFAULT.get(cat, 12)))
        price = float(product.get("price", 0))

        # Eligibility
        days_owned = (claim_dt - purchase).days
        warranty_days = warranty_months * 30
        is_eligible = 0 <= days_owned <= warranty_days
        days_remaining = max(0, warranty_days - days_owned)
        near_expiry = 0 < days_remaining <= 7

        eligibility = {
            "purchase_date": str(purchase),
            "claim_date": str(claim_dt),
            "days_owned": days_owned,
            "warranty_months": warranty_months,
            "warranty_expiry": str(purchase.replace(day=min(purchase.day, 28)) if False else date.fromordinal(purchase.toordinal() + warranty_days)),
            "within_warranty": is_eligible,
            "days_remaining": days_remaining,
        }

        if not is_eligible:
            return {
                "decision": "denied",
                "decision_reason": DECISION_REASONS["denied_expired"],
                "eligibility": eligibility,
                "fraud_risk": None,
                "resolution_options": [],
            }

        # Fraud detection
        fraud_signals = []
        fraud_score = 0

        past_claims = int(cust.get("past_claims", 0))
        if past_claims >= 3:
            fraud_signals.append(FRAUD_SIGNALS[0][1])
            fraud_score += 30

        account_age = int(cust.get("account_age_months", 12))
        if account_age < 1:
            fraud_signals.append(FRAUD_SIGNALS[1][1])
            fraud_score += 25

        if not claim.get("proof_provided"):
            fraud_signals.append(FRAUD_SIGNALS[2][1])
            fraud_score += 20
            if price > 100:
                fraud_signals.append(FRAUD_SIGNALS[4][1])
                fraud_score += 15

        if near_expiry:
            fraud_signals.append(FRAUD_SIGNALS[3][1])
            fraud_score += 10

        issue_desc = str(claim.get("issue_description", ""))
        if len(issue_desc) < 15:
            fraud_signals.append(FRAUD_SIGNALS[5][1])
            fraud_score += 10

        fraud_risk = {
            "fraud_score": min(fraud_score, 100),
            "risk_level": "high" if fraud_score >= 50 else "medium" if fraud_score >= 25 else "low",
            "signals": fraud_signals,
        }

        # Decision
        if fraud_score >= 50:
            decision = "review_required"
            reason = DECISION_REASONS["review_required"]
        elif not claim.get("proof_provided") and price > 200:
            decision = "denied"
            reason = DECISION_REASONS["denied_no_proof"]
        else:
            decision = "approved"
            reason = DECISION_REASONS["approved"]

        # Resolution options
        resolutions = []
        if decision == "approved":
            if cat in ("electronics", "appliances"):
                resolutions = [RESOLUTION_OPTIONS["replacement"], RESOLUTION_OPTIONS["repair"], RESOLUTION_OPTIONS["store_credit"]]
            elif price > 50:
                resolutions = [RESOLUTION_OPTIONS["replacement"], RESOLUTION_OPTIONS["store_credit"], RESOLUTION_OPTIONS["refund"]]
            else:
                resolutions = [RESOLUTION_OPTIONS["refund"], RESOLUTION_OPTIONS["store_credit"]]

        return {
            "decision": decision,
            "decision_reason": reason,
            "eligibility": eligibility,
            "fraud_risk": fraud_risk,
            "resolution_options": resolutions,
            "recommended_resolution": resolutions[0] if resolutions else None,
        }
