# Data model

Customers (1) -> Cases (many). Cases (1) -> Interactions, Promises, Interventions, and Feedback (one or many). Use `customer_id` and `case_id` as keys. Keep a separate Date table related to `cases[created_at]` for trend slicing.

