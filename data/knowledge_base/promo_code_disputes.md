# Promo code dispute handling

Policy code: PROMO-021

When a customer says a promo code did not apply at checkout:

1. Verify the code in the internal promo management tool — check expiry
   date, minimum order value requirement, and whether it's single-use or
   multi-use
2. If the code was valid and should have applied but the system failed to
   apply it (a known checkout bug, ticket reference SYS-4471), honor the
   discount retroactively as a partial refund equal to the discount amount
3. If the code had expired or the order did not meet minimum value, the
   code correctly did not apply — politely explain this, no compensation
4. Promo code issues are billing corrections, not refund-policy matters —
   the 14-day or 30-day refund windows (REF-STD-014 / REF-PREM-030) do not
   apply since this is not a request to return the item, only to correct
   the price charged

Promo code disputes do not require supervisor escalation unless the
customer disputes the verification tool's result itself.
