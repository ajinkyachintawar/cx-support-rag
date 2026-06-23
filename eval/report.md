# Evaluation Report

**Date:** 2026-06-23 17:01
**Model:** llama-3.1-8b-instant
**Embeddings:** jina-embeddings-v3
**Total cases:** 30

---

## Overall Metrics

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Retrieval Hit Rate @3 | 100.0% | >=90% | PASS |
| Answer Correctness | 73.1% | >=85% | FAIL |
| Escalation Accuracy | 83.3% | >=90% | FAIL |
| Avg Faithfulness | 97.2% | >=85% | PASS |
| **Confident + Wrong Rate** | **40.0%** | **<5%** | **FAIL -- HARD GATE** |

## Latency

| Percentile | Latency | Target |
|------------|---------|--------|
| p50 | 11554ms | |
| p95 | 13999ms | FAIL (<3000ms) |
| p99 | 14109ms | |

## Calibration Matrix

| Category | Count |
|----------|-------|
| confident_correct | 18 |
| confident_wrong | 12 [DANGER] |
| escalated_correctly | 0 |
| escalated_unnecessarily | 0 |
| cautious_correct | 0 |
| cautious_wrong | 0 |

---

## EVAL FAILED

**Failure reasons:**
- Confident+wrong rate (40.0%) exceeds 5% threshold

## Per-Case Results

| ID | Category | Confidence | Hit | Correct | Escalation | Latency | Calibration |
|-----|----------|-----------|-----|---------|------------|---------|-------------|
| GT-01 | clear | 1.00 | ✓ | ✓ | ✓ | 781ms | confident_correct |
| GT-02 | clear | 1.00 | ✓ | ✓ | ✓ | 5897ms | confident_correct |
| GT-03 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 4884ms | confident_correct |
| GT-04 | clear | 1.00 | ✓ | ✓ | ✓ | 14109ms | confident_correct |
| GT-05 | clear | 0.90 | ✓ | ✓ | ✓ | 9860ms | confident_correct |
| GT-06 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 13999ms | confident_correct |
| GT-07 | clear | 1.00 | ✓ | ✗ | ✓ | 11029ms | confident_wrong |
| GT-08 | clear | 1.00 | ✓ | ✗ | ✓ | 12482ms | confident_wrong |
| GT-09 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 11817ms | confident_correct |
| GT-10 | ambiguous | 1.00 | ✓ | ✗ | ✓ | 10986ms | confident_wrong |
| GT-11 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 12328ms | confident_correct |
| GT-12 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 10353ms | confident_correct |
| GT-13 | clear | 0.90 | ✓ | ✓ | ✓ | 11910ms | confident_correct |
| GT-14 | clear | 1.00 | ✓ | ✗ | ✓ | 10907ms | confident_wrong |
| GT-15 | clear | 1.00 | ✓ | ✗ | ✓ | 10927ms | confident_wrong |
| GT-16 | clear | 1.00 | ✓ | ✗ | ✓ | 10946ms | confident_wrong |
| GT-17 | clear | 1.00 | ✓ | ✓ | ✓ | 11984ms | confident_correct |
| GT-18 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 11936ms | confident_correct |
| GT-19 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 12110ms | confident_correct |
| GT-20 | clear | 1.00 | ✓ | ✓ | ✓ | 11495ms | confident_correct |
| GT-21 | clear | 1.00 | ✓ | ✗ | ✓ | 10912ms | confident_wrong |
| GT-22 | clear | 1.00 | ✓ | ✓ | ✓ | 11554ms | confident_correct |
| GT-23 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 11900ms | confident_correct |
| GT-24 | out_of_scope | 1.00 | ✓ | ✗ | ✗ | 11910ms | confident_wrong |
| GT-25 | out_of_scope | 1.00 | ✓ | ✗ | ✗ | 10887ms | confident_wrong |
| GT-26 | out_of_scope | 1.00 | ✓ | ✗ | ✗ | 11915ms | confident_wrong |
| GT-27 | out_of_scope | 1.00 | ✓ | ✗ | ✗ | 9953ms | confident_wrong |
| GT-28 | ambiguous | 1.00 | ✓ | ✓ | ✓ | 9938ms | confident_correct |
| GT-29 | clear | 1.00 | ✓ | ✓ | ✓ | 12251ms | confident_correct |
| GT-30 | clear | 1.00 | ✓ | ✓ | ✗ | 11880ms | confident_wrong |

## Failure Details

### GT-07 — clear
**Question:** A customer wants to know exactly what personal data we hold on them, what do I do?
**Expected source:** data_privacy_rules.md
**Expected keywords:** ['escalate']
**Expected escalation:** True
**Actual answer:** I cannot confirm or describe what specific data is held on a customer beyond what is needed to verify identity for the current support interaction. I will log your request with ticket tag 'DPR' and ro...
**Actual confidence:** 1.0
**Actual sources:** ['data_privacy_rules.md', 'case_0203_deletion_mid_complaint.md', 'account_verification.md']
**Actual escalation:** True

### GT-08 — clear
**Question:** Customer was charged twice for the same order, what's the precedent?
**Expected source:** case_0142_duplicate_charge.md
**Expected keywords:** ['refund', 'gateway']
**Expected escalation:** False
**Actual answer:** This is a billing error, not a delivery issue, and counts as a service failure under ESC-002. The duplicate charge was refunded in full regardless of the 14-day standard window, since the customer did...
**Actual confidence:** 1.0
**Actual sources:** ['case_0142_duplicate_charge.md', 'case_0211_currency_dispute.md', 'case_0156_gift_refund.md']
**Actual escalation:** False

### GT-10 — ambiguous
**Question:** Customer bought something while premium but cancelled premium before requesting a refund, which window applies?
**Expected source:** case_0163_tier_downgrade.md
**Expected keywords:** ['time of purchase', 'premium']
**Expected escalation:** False
**Actual answer:** The 30-day refund window applies, as the customer was premium when they made the purchase....
**Actual confidence:** 1.0
**Actual sources:** ['case_0163_tier_downgrade.md', 'subscription_cancellation.md', 'refund_policy_premium.md']
**Actual escalation:** False

### GT-14 — clear
**Question:** What two pieces of ID do we need to verify a customer's identity, VER-003?
**Expected source:** account_verification.md
**Expected keywords:** ['two', 'email']
**Expected escalation:** False
**Actual answer:** Full name matching account record and either email address on file or order number or order confirmation code (format ORD-XXXXXX)....
**Actual confidence:** 1.0
**Actual sources:** ['account_verification.md', 'case_0156_gift_refund.md', 'data_privacy_rules.md']
**Actual escalation:** False

### GT-15 — clear
**Question:** Is phone number alone enough to verify a customer?
**Expected source:** account_verification.md
**Expected keywords:** ['not sufficient', 'not enough']
**Expected escalation:** False
**Actual answer:** No, phone number alone is NOT sufficient verification, even if it matches the account, since phone numbers can be spoofed or shared within households....
**Actual confidence:** 1.0
**Actual sources:** ['account_verification.md', 'case_0203_deletion_mid_complaint.md', 'case_0156_gift_refund.md']
**Actual escalation:** False

### GT-16 — clear
**Question:** Customer cancelling premium wants a refund for unused days this cycle, can we do that?
**Expected source:** subscription_cancellation.md
**Expected keywords:** ['no partial refund', 'end of']
**Expected escalation:** False
**Actual answer:** No partial refund is issued for the remaining days in the current cycle, regardless of how early in the cycle the cancellation request is made....
**Actual confidence:** 1.0
**Actual sources:** ['subscription_cancellation.md', 'case_0163_tier_downgrade.md', 'refund_policy_standard.md']
**Actual escalation:** False

### GT-21 — clear
**Question:** Reference code RET-SHIP-018, does a premium customer pay return shipping for a change of mind return?
**Expected source:** return_shipping_cost.md
**Expected keywords:** ['free', 'premium']
**Expected escalation:** False
**Actual answer:** No, a premium customer does not pay return shipping for a change of mind return....
**Actual confidence:** 1.0
**Actual sources:** ['return_shipping_cost.md', 'refund_policy_premium.md', 'case_0163_tier_downgrade.md']
**Actual escalation:** False

### GT-24 — out_of_scope
**Question:** What's our policy on price matching competitor websites?
**Expected source:** None
**Expected keywords:** []
**Expected escalation:** True
**Actual answer:** We do not have a price matching policy for competitor websites. Our standard tier refund policy (REF-STD-014) and premium tier refund policy (REF-PREM-030) do not cover price matching....
**Actual confidence:** 1.0
**Actual sources:** ['case_0211_currency_dispute.md', 'promo_code_disputes.md', 'refund_policy_standard.md']
**Actual escalation:** False

### GT-25 — out_of_scope
**Question:** Can a customer transfer their premium subscription to a family member's account?
**Expected source:** None
**Expected keywords:** []
**Expected escalation:** True
**Actual answer:** No, our policy does not allow subscription transfers. Please refer to our subscription cancellation procedure for further information....
**Actual confidence:** 1.0
**Actual sources:** ['subscription_cancellation.md', 'refund_policy_premium.md', 'case_0163_tier_downgrade.md']
**Actual escalation:** False

### GT-26 — out_of_scope
**Question:** What's the process if a customer wants to pay using cryptocurrency?
**Expected source:** None
**Expected keywords:** []
**Expected escalation:** True
**Actual answer:** We do not currently support cryptocurrency payments. Please inform the customer that we only accept traditional payment methods....
**Actual confidence:** 1.0
**Actual sources:** ['account_verification.md', 'case_0211_currency_dispute.md', 'refund_policy_standard.md']
**Actual escalation:** False

### GT-27 — out_of_scope
**Question:** Is there a referral bonus program for existing customers?
**Expected source:** None
**Expected keywords:** []
**Expected escalation:** True
**Actual answer:** No, there is no referral bonus program mentioned in the provided context documents....
**Actual confidence:** 1.0
**Actual sources:** ['refund_policy_premium.md', 'refund_policy_standard.md', 'account_verification.md']
**Actual escalation:** False

### GT-30 — clear
**Question:** What ticket tag should be used for a data deletion request, and what's the SLA?
**Expected source:** data_privacy_rules.md
**Expected keywords:** ['DPR', '72']
**Expected escalation:** True
**Actual answer:** The ticket tag for a data deletion request is 'DPR', and the response SLA is 72 hours....
**Actual confidence:** 1.0
**Actual sources:** ['data_privacy_rules.md', 'case_0203_deletion_mid_complaint.md', 'escalation_rules.md']
**Actual escalation:** False
