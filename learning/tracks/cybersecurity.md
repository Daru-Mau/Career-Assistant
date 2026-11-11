# Cybersecurity Track

Budget: 1 hour per week
Goal: enough applied security knowledge to build and review a web application, not to become a penetration tester.

## OWASP Top 10 checklist

- [ ] Broken access control
- [ ] Cryptographic failures
- [ ] Injection
- [ ] Insecure design
- [ ] Security misconfiguration
- [ ] Vulnerable and outdated components
- [ ] Identification and authentication failures
- [ ] Software and data integrity failures
- [ ] Security logging and monitoring failures
- [ ] Server-side request forgery

## Twelve labs (one per week)

Use PortSwigger Web Security Academy. Write a five-line summary per lab in the project log.

| Week | Lab topic |
|---|---|
| 1 | Authentication: username enumeration and brute force |
| 2 | Access control: IDOR and privilege escalation |
| 3 | SQL injection: UNION and blind |
| 4 | Cross-site scripting: reflected, stored, DOM |
| 5 | CSRF |
| 6 | SSRF |
| 7 | Business logic flaws |
| 8 | File upload vulnerabilities |
| 9 | API testing and JWT flaws |
| 10 | CORS misconfiguration |
| 11 | Clickjacking and security headers |
| 12 | Race conditions |

## Secure coding checklist for the capstone

- [ ] Passwords hashed with a modern algorithm
- [ ] JWT expiry, rotation and revocation considered
- [ ] Role checks on every sensitive endpoint
- [ ] Input validation and output encoding
- [ ] File type, size and content checks on upload
- [ ] Rate limiting on auth and expensive endpoints
- [ ] Secrets in environment variables, never in the repo
- [ ] Dependency scanning and updates
- [ ] Security headers and HTTPS
- [ ] Structured security logs without sensitive data
- [ ] Threat model with assets, actors and mitigations

## Practice

- OWASP Juice Shop: complete the tutorial and at least ten challenges.
- Optional: TryHackMe Pre Security for breadth.
- Optional: picoCTF for a first CTF.

## Done criteria

- Twelve labs completed and summarized.
- The capstone has a security notes file with the checklist above.
- One end-to-end threat model for the capstone.
- No secrets in git history.
- A dependency scan runs in CI.

## Resources

See `../resources.md`. Prioritize PortSwigger Web Security Academy, OWASP Top 10 and the OWASP Cheat Sheet Series.
