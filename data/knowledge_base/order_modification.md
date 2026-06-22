# Order modification before dispatch

Policy code: MOD-012

If a customer wants to change their order (size, color, quantity, shipping
address) before it has dispatched:

1. Check order status in logistics dashboard — if status is "processing"
   or "pending," modification is possible
2. If status is already "dispatched" or "shipped," modification is not
   possible — the customer must wait for delivery and use the standard
   return/refund process instead, or redirect the shipment through the
   courier's own redirect service if available for that courier (not
   guaranteed, varies by courier)
3. Address changes after dispatch carry the highest risk of the package
   being lost — if redirect fails and package becomes untrackable, follow
   lost package process (LOG-011)
4. No fee applies for modifications made before dispatch

This is unrelated to refund policy — a pre-dispatch modification is not a
refund event and does not consume any part of the customer's refund window.
