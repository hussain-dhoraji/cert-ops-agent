# Discovery: Cert Ops Assistant

Output of a (simulated) intake workshop with Contoso's platform operations team. Contoso is fictional; the
problem is common.

## Problem

Engineers learn about expiring certificates from cert-watcher alerts, then spend time working out what to do:
which runbook applies, whether CAB approval is needed, who owns the service, and how to reach them. The
information exists, but it is spread across a monitoring API and three runbooks.

## Users

- **Primary: on-call operations engineer.** Gets an alert at an inconvenient time and needs the next step fast.
- **Secondary: service team engineer.** Renews their own service's certificate a few times a year and does not
  remember the rules.

## Value hypothesis

If engineers can ask one assistant in Teams for certificate status and the right procedure, triaging a
certificate alert drops from about **15 minutes to under 2**, and fewer renewals become emergencies.

## In scope (MVP)

- Live certificate status from cert-watcher (read-only)
- Answers from the renewal, emergency and ownership runbooks, with citations
- A guided escalation topic for urgent cases

## Out of scope (MVP)

- Creating change tickets or PagerDuty incidents (candidate for v2, behind explicit user confirmation)
- Renewing certificates or touching private keys (never)

## User stories and acceptance criteria

1. **As an on-call engineer, I want to ask what is expiring so that I can prioritize.**
   - Given certificates in CRITICAL and WARNING, when I ask "what is critical?", only CRITICAL certificates are
     listed, with target name and days until expiry.
   - Data comes from the cert-watcher action, never from the model's memory.
2. **As an on-call engineer, I want the emergency procedure for a critical certificate so that I act correctly.**
   - The answer names the PagerDuty service, the emergency change, the duty-manager approval and the 4-hour
     target, and cites the emergency runbook.
3. **As a service engineer, I want to know the issuing rules so that my request is not rejected.**
   - Questions on CA, key type, wildcards and lead time are answered from the runbook with a citation.
4. **As a service engineer, I want to know who owns a certificate so that I contact the right team.**
   - Listed services return team and channel; unlisted services say no owner is registered, without guessing.
5. **As the platform owner, I want the assistant to stay in scope and safe so that it can be trusted.**
   - Off-topic requests get a fixed refusal; the instructions are never revealed; private keys are never
     requested or shown; change requests are declined as out of scope (read-only).

## Non-functional requirements

| Area | Requirement |
|---|---|
| Quality | 90% or more of the golden set passes before publishing; no regressions between versions |
| Latency | Median answer under 8 seconds |
| Security | Read-only actions; agent authenticates users through Entra ID in Teams; no secrets in the agent |
| Privacy | No personal data stored; transcripts follow the tenant's retention policy |
| Governance | Built in a dedicated Power Platform environment; DLP policy allows only the cert-watcher connector and SharePoint |

## Success metrics

| Metric | Target | Source |
|---|---|---|
| Task success (golden set pass rate) | 90% or more | `evals/` reports |
| Weekly active users | 70% of on-call engineers after 4 weeks | Copilot Studio analytics |
| Escalation rate (fallback or "couldn't find") | Under 15% of conversations | Copilot Studio analytics |
| Time to triage a certificate alert | Under 2 minutes | Before/after survey of on-call engineers |
