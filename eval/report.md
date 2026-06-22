# Evaluation Report

**Date:** 2026-06-22 16:25
**Model:** llama-3.3-70b-versatile
**Embeddings:** jina-embeddings-v3
**Total cases:** 30

---

## Overall Metrics

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Retrieval Hit Rate @3 | 100.0% | ≥90% | ✅ PASS |
| Answer Correctness | 80.8% | ≥85% | ❌ FAIL |
| Escalation Accuracy | 100.0% | ≥90% | ✅ PASS |
| Avg Faithfulness | 98.3% | ≥85% | ✅ PASS |
| **Confident + Wrong Rate** | **16.7%** | **<5%** | **❌ FAIL** |

## Latency

| Percentile | Latency |
|------------|---------|
| p50 | 2970ms |
| p95 | 3631ms | ❌ |
| p99 | 4034ms |

## Calibration Matrix

| Category | Count |
|----------|-------|
| confident_correct | 21 |
| confident_wrong | 5 ⚠️ |
| escalated_correctly | 4 |
| escalated_unnecessarily | 0 |
| cautious_correct | 0 |
| cautious_wrong | 0 |

---

## 🔴 EVAL FAILED

**Failure reasons:**
- Confident+wrong rate (16.7%) exceeds 5% threshold

## Per-Case Results

| ID | Category | Confidence | Hit | Correct | Escalation | Latency | Calibration |
|-----|----------|-----------|-----|---------|------------|---------|-------------|
| GT-01 | clear | 1.00 | ✓ | ✓ | ✓ | 1651ms | confident_correct |
| GT-02 | clear | 1.00 | ✓ | ✓ | ✓ | 804ms | confident_correct |
| GT-03 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 824ms | confident_correct |
| GT-04 | clear | 0.90 | ✓ | ✓ | ✓ | 1161ms | confident_correct |
| GT-05 | clear | 0.90 | ✓ | ✓ | ✓ | 1127ms | confident_correct |
| GT-06 | ambiguous | 1.00 | ✓ | ✗ | ✓ | 1405ms | confident_wrong |
| GT-07 | clear | 0.90 | ✓ | ✓ | ✓ | 3155ms | confident_correct |
| GT-08 | clear | 0.90 | ✓ | ✗ | ✓ | 3040ms | confident_wrong |
| GT-09 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 3213ms | confident_correct |
| GT-10 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 3597ms | confident_correct |
| GT-11 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 4034ms | confident_correct |
| GT-12 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 3020ms | confident_correct |
| GT-13 | clear | 0.90 | ✓ | ✓ | ✓ | 3254ms | confident_correct |
| GT-14 | clear | 1.00 | ✓ | ✓ | ✓ | 3042ms | confident_correct |
| GT-15 | clear | 1.00 | ✓ | ✗ | ✓ | 2938ms | confident_wrong |
| GT-16 | clear | 0.90 | ✓ | ✗ | ✓ | 2939ms | confident_wrong |
| GT-17 | clear | 0.90 | ✓ | ✓ | ✓ | 2474ms | confident_correct |
| GT-18 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 3457ms | confident_correct |
| GT-19 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 2522ms | confident_correct |
| GT-20 | clear | 0.90 | ✓ | ✓ | ✓ | 2884ms | confident_correct |
| GT-21 | clear | 1.00 | ✓ | ✓ | ✓ | 2978ms | confident_correct |
| GT-22 | clear | 0.90 | ✓ | ✓ | ✓ | 3631ms | confident_correct |
| GT-23 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 3143ms | confident_correct |
| GT-24 | out_of_scope | 0.00 | ✓ | ✓ | ✓ | 2888ms | escalated_correctly |
| GT-25 | out_of_scope | 0.00 | ✓ | ✓ | ✓ | 2118ms | escalated_correctly |
| GT-26 | out_of_scope | 0.00 | ✓ | ✓ | ✓ | 3020ms | escalated_correctly |
| GT-27 | out_of_scope | 0.00 | ✓ | ✓ | ✓ | 2118ms | escalated_correctly |
| GT-28 | ambiguous | 0.90 | ✓ | ✓ | ✓ | 2970ms | confident_correct |
| GT-29 | clear | 1.00 | ✓ | ✗ | ✓ | 2949ms | confident_wrong |
| GT-30 | clear | 1.00 | ✓ | ✓ | ✓ | 3060ms | confident_correct |

## Failure Details

### GT-06 — ambiguous
**Question:** Delivery shows as delivered but customer says they never got it, what process do we follow?
**Expected source:** lost_package_process.md
**Expected keywords:** ['lost', 'reshipment']
**Expected escalation:** False
**Actual answer:** This situation is treated as a lost package, not a delay. Follow the lost package process (LOG-011) instead of the delivery delay process....
**Actual confidence:** 1.0
**Actual sources:** ['delivery_delay_process.md', 'case_0188_partial_shipment.md', 'lost_package_process.md']
**Actual escalation:** False

### GT-08 — clear
**Question:** Customer was charged twice for the same order, what's the precedent?
**Expected source:** case_0142_duplicate_charge.md
**Expected keywords:** ['refund', 'gateway']
**Expected escalation:** False
**Actual answer:** The duplicate charge should be refunded in full, regardless of the standard 14-day refund window, as this is considered a billing error under ESC-002. Only one item is shipped and no store credit is n...
**Actual confidence:** 0.9
**Actual sources:** ['case_0142_duplicate_charge.md', 'case_0211_currency_dispute.md', 'case_0156_gift_refund.md']
**Actual escalation:** False

### GT-15 — clear
**Question:** Is phone number alone enough to verify a customer?
**Expected source:** account_verification.md
**Expected keywords:** ['not sufficient', 'not enough']
**Expected escalation:** False
**Actual answer:** No, phone number alone is not sufficient verification, as it can be spoofed or shared within households....
**Actual confidence:** 1.0
**Actual sources:** ['account_verification.md', 'case_0203_deletion_mid_complaint.md', 'case_0156_gift_refund.md']
**Actual escalation:** False

### GT-16 — clear
**Question:** Customer cancelling premium wants a refund for unused days this cycle, can we do that?
**Expected source:** subscription_cancellation.md
**Expected keywords:** ['no partial refund', 'end of']
**Expected escalation:** False
**Actual answer:** No, we cannot issue a refund for unused days in the current cycle unless the customer cites a specific service failure as the cancellation reason....
**Actual confidence:** 0.9
**Actual sources:** ['subscription_cancellation.md', 'case_0163_tier_downgrade.md', 'refund_policy_standard.md']
**Actual escalation:** False

### GT-29 — clear
**Question:** A customer's order is still in processing status and they want to change the size, is that allowed?
**Expected source:** order_modification.md
**Expected keywords:** ['possible', 'processing']
**Expected escalation:** False
**Actual answer:** Yes, order modification is allowed since the order status is 'processing'. The customer can change the size of their order without any fee....
**Actual confidence:** 1.0
**Actual sources:** ['order_modification.md', 'case_0156_gift_refund.md', 'case_0163_tier_downgrade.md']
**Actual escalation:** False
