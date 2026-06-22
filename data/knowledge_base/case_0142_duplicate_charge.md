# Resolved case — duplicate charge from payment retry

Case ID: CASE-0142

Situation: Customer was charged twice for the same order. Investigation
showed the payment gateway timed out on the first attempt and the customer
resubmitted, but the first charge had actually succeeded silently before
the timeout message displayed.

Resolution: This is a billing error, not a delivery issue, and counts as a
service failure under ESC-002. The duplicate charge was refunded in full
regardless of the 14-day standard window, since the customer did not
request two items. Only one item is shipped. No store credit needed since
this is a straightforward billing correction, not a goodwill gesture.

Note for future agents: check the payment gateway logs before assuming the
customer made an error — gateway timeout-but-succeeded is a known recurring
issue, not user error. Do not ask the customer to "wait and see if it
resolves," refund immediately once confirmed as duplicate.
