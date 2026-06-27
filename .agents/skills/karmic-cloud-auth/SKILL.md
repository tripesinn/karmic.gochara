---
name: karmic-cloud-auth
description: Instructions for authenticating and managing quotas for karmic-gochara-cloud.
---

# Karmic Gochara Cloud Authentication & Quotas

When interacting with Google Cloud, Firebase, or any services related to **karmic-gochara-cloud**, you must strictly follow these rules:

1. **Authentication:** Always authenticate using the account `jerome@jeromemalige.fr`.
2. **Quota/Billing:** The quota and billing must be billed to `tripes.inn@gmail.com`. Ensure that the correct quota project is set (e.g., using `gcloud auth application-default set-quota-project` or the respective flag) when running commands.

## When to use this skill
- Whenever executing `gcloud`, `firebase`, or other deployment/infrastructure commands.
- If you encounter authentication or quota/billing errors related to Google Cloud or Firebase.
- When configuring environments or application default credentials (ADC).
