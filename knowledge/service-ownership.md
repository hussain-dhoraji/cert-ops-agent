# Service ownership

Who owns each service's TLS certificate, and where to reach them. The cert-watcher target name is the name the
certificate is reported under.

| Service | cert-watcher target | Owning team | Channel |
|---|---|---|---|
| Payments gateway | `/certs/payments-gateway.crt` | Payments Platform | #payments-ops |
| Customer portal | `/certs/customer-portal.crt` | Web Experience | #web-experience |
| Internal wiki | `/certs/internal-wiki.crt` | IT Operations | #it-ops |

Services not listed here have no registered owner. Raise ownership questions in #it-ops.
