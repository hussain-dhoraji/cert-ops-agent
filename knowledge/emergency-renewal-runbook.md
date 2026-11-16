# Emergency TLS certificate renewal

Use this runbook when cert-watcher reports a certificate as `CRITICAL` (expires within 7 days) or `EXPIRED`.

## Steps

1. **Page the platform on-call** through the PagerDuty service **platform-oncall**.
2. Raise an **emergency change**. Emergency changes skip the weekly Change Advisory Board; the **duty manager**
   approves them instead.
3. Notify the owning team in its channel (see [service ownership](service-ownership.md)).
4. Renew and deploy following the issuing and key-handling rules in the
   [standard renewal runbook](certificate-renewal-runbook.md). Do not cut corners on key handling because of urgency.
5. Verify with `openssl s_client` and confirm cert-watcher reports the certificate as `OK`.

## Target

The certificate must be **renewed within 4 hours** of the emergency change being opened.

## After the incident

Within 5 business days, the owning team writes a short post-incident review explaining why the standard 30-day
renewal was missed.
