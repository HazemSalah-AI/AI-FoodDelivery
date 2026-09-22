# Canonical order workflow

| Current | Next | Allowed actor | Conditions |
|---|---|---|---|
| Pending | Accepted | Owning merchant / Admin | Not already rejected/cancelled |
| Pending | Rejected | Owning merchant / Admin | Nonempty rejection reason; restore stock once |
| Pending | Cancelled | Owning customer / Admin | Restore stock once |
| Accepted | Preparing | Owning merchant / Admin | — |
| Preparing | Ready | Owning merchant / Admin | — |
| Ready | OnDelivery | Accepted assigned driver / Admin | Accepted assignment required |
| OnDelivery | Delivered | Accepted assigned driver / Admin | Close assignment and record delivery |

Delivered, Rejected and Cancelled are terminal. Driver acceptance alone never marks pickup.
Invalid edges return 409, forbidden role actions 403, hidden/other-owner records 404.
Every order transition inserts history and recipient notifications in the same transaction.

Checkout locks the customer, then product rows in increasing ID order. It reads current prices,
reserves stock, copies product names/prices and address, creates Pending/history/notifications,
and clears the cart atomically. A customer-scoped idempotency key makes retries return the
original order; the same key with another address returns 409. Cancellation/rejection locks
the order then products in ID order. Never call the historical SQL seed for this workflow.

Assignment is separate: Admin assigns a fresh available driver to Ready; Pending→Accepted
or Pending→Rejected. Rejection frees the order and driver; Admin assigns again. Accepted→Completed
only when the order becomes Delivered. Partial unique indexes prevent double active assignments.
