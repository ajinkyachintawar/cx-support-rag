# Resolved case — multi-item order arrived with one item missing

Case ID: CASE-0188

Situation: Customer ordered 3 items in a single order, package arrived but
only 2 items were inside. Tracking showed the full order as "delivered."

Resolution: This is neither a delay nor a full lost package — it is a
partial shipment error, handled as a hybrid case. The missing single item
was treated under lost package process (LOG-011) logic for that item only:
immediate reshipment of the missing item at no cost, no need to escalate
since it was the customer's first occurrence. The 2 items that did arrive
are not affected and no refund applies to those.

Note for future agents: do not apply lost package process to the entire
order if only some items are missing — isolate the resolution to the
missing item(s) only. Check the packing slip in the logistics dashboard to
confirm what was actually packed before assuming courier error.
