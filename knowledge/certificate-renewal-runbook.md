# Standard TLS certificate renewal

Applies to every TLS certificate that Contoso operates. Contoso is a fictional company used for this demo.

## When to renew

- Start the renewal **30 days before expiry**. cert-watcher raises a `WARNING` at 30 days for this reason.
- Certificates that expire within **7 days** (`CRITICAL`) or have already expired (`EXPIRED`) follow the
  [emergency renewal runbook](emergency-renewal-runbook.md) instead.

## Approval

- Production renewals need a change ticket approved by the **Change Advisory Board (CAB)**.
- The CAB meets every **Tuesday**. Submit the ticket by Monday 17:00 to make that week's meeting.
- Non-production renewals need no CAB approval; note the change in the owning team's channel.

## Issuing

- Internal services use the internal CA, **Contoso Issuing CA 2**.
- Internet-facing services use public certificates from **DigiCert**.
- Generate keys as **ECDSA P-256** (preferred) or **RSA 3072**. RSA 2048 is no longer accepted.
- **Wildcard certificates are not permitted** for production services. Request a certificate per hostname, using
  subject alternative names for aliases.

## Handling private keys

- Generate the private key on the target host or in the cluster; it must never leave that environment.
- **Never send private keys by email or chat**, including to vendors. Share the certificate signing request (CSR)
  instead.
- In Kubernetes, store the key and certificate in a `kubernetes.io/tls` Secret.

## Verify the new certificate

After deployment, confirm the served certificate and its expiry:

```bash
openssl s_client -connect <host>:443 -servername <host> </dev/null 2>/dev/null | openssl x509 -noout -subject -enddate
```

cert-watcher picks up the new expiry on its next check and the alert clears.
