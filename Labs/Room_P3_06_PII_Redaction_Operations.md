# 🕹️ Room P3-06: PII Redaction Operations & Compliance Surgery

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 06  
> **Difficulty:** Intermediate | **XP Reward:** `250 XP` | **Estimated Time:** 35 mins  
> **Target Scenario:** Regulatory PCI-DSS / GDPR Emergency Compliance Sanitization  
> **Prerequisites:** Chapter 06 (Index-Time Data Masking & Anonymization)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
An external PCI-DSS compliance auditor delivered an emergency finding to your CISO:  
Raw payment gateway events in index `payments` contain **cleartext Visa and Mastercard numbers**, **client Social Security Numbers**, and **JWT authentication tokens**!

The auditor gave your engineering team **24 hours** to eliminate the exposure or face an immediate shutdown of payment processing operations.

Your mission is to formulate surgical `SEDCMD` regexes in `props.conf` on the Heavy Forwarder tier to sanitize all incoming data streams in memory before disk write, verify the raw disk journal is clean, and capture all 5 forensic flags!

---

## 🧭 Task 1: 16-Digit Credit Card Surgical Redaction

A raw payment event arrives as follows:
```text
2026-10-15 09:30:11.102 [POS-GATEWAY-01] SALE APPROVED customer_id=48201 card_number=4123-4567-8901-2345 amount=142.50 currency=USD
```

PCI-DSS Section 3.4 mandates that the Primary Account Number (PAN) must be rendered unreadable, allowing only the last 4 digits to remain visible.

### Question 1.1
Write the exact `SEDCMD` rule to mask the first 12 digits of a dashed 16-digit credit card number with `XXXX-XXXX-XXXX-` while preserving the last 4 digits using a capture group backreference.

<details>
<summary>💡 Hint</summary>
Use <code>\b(?:\d{4}-){3}(\d{4})\b</code> as the regex and replace with <code>XXXX-XXXX-XXXX-\1</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>SEDCMD-mask_cc = s/\b(?:\d{4}-){3}(\d{4})\b/XXXX-XXXX-XXXX-\1/g</code></pre>
<strong>Flag 1:</strong> <code>THM{SEDCMD_PCI_DSS_CREDIT_CARD_SCRUBBED}</code>
</details>

---

## 🧭 Task 2: US Social Security Number (SSN) Sanitization

Customer credit application logs output cleartext Social Security Numbers:
```text
2026-10-15 09:35:00 [LOAN-APP] applicant="Alice Smith" ssn="999-00-1234" credit_score=780
```

Federal privacy regulations mandate that the first 5 digits must be masked with `XXX-XX-`.

### Question 2.1
Formulate the `SEDCMD` rule to replace 9-digit SSNs with `XXX-XX-<last4>` across all incoming loan application logs.

<details>
<summary>💡 Hint</summary>
Match <code>\b\d{3}-\d{2}-(\d{4})\b</code> and replace with <code>XXX-XX-\1</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>SEDCMD-mask_ssn = s/\b\d{3}-\d{2}-(\d{4})\b/XXX-XX-\1/g</code></pre>
<strong>Flag 2:</strong> <code>THM{SSN_FEDERAL_PRIVACY_SAFEGUARDED}</code>
</details>

---

## 🧭 Task 3: Bearer Token & API Key Vaporization

Microservices communicating with cloud lambdas log raw HTTP Authorization headers:
```text
2026-10-15 09:40:00 [GATEWAY] Request: POST /v1/transfer Headers: {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-ID"}
```
If an attacker compromises Splunk, these live bearer tokens can be used to impersonate service accounts and drain accounts!

### Question 3.1
Write the `SEDCMD` rule to replace any Bearer token string with `Bearer [REDACTED]`.

<details>
<summary>💡 Hint</summary>
Use case-insensitivity <code>(?i)</code>, capture <code>(Authorization:\s*"?Bearer\s+)[^\s"']*</code>, and replace with <code>\1[REDACTED]</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>SEDCMD-mask_bearer = s/(?i)(Bearer\s+)[a-zA-Z0-9\.\-_]+/\1[REDACTED]/g</code></pre>
<strong>Flag 3:</strong> <code>THM{BEARER_TOKEN_AUTHENTICATION_SEALED}</code>
</details>

---

## 🧭 Task 4: URL Query String Password Cleansing

Legacy web services log plain text authentication URLs:
```text
https://api.fincorp.local/auth/login?user=admin&password=SuperSecretPassword123&client_id=web
```

### Question 4.1
Formulate the `SEDCMD` rule that matches `password=<value>` in any URL and replaces the value with `password=***MASKED***` without breaking adjacent query parameters (`&client_id=web`).

<details>
<summary>💡 Hint</summary>
Match <code>(?i)(password=)[^&\s]+</code> and replace with <code>\1***MASKED***</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>SEDCMD-mask_url_pwd = s/(?i)(password=)[^&\s]+/\1***MASKED***/g</code></pre>
<strong>Flag 4:</strong> <code>THM{CLEARTEXT_URL_PASSWORD_CLEANSED}</code>
</details>

---

## 🧭 Task 5: Post-Scrubbing Disk Immutability Verification

An auditor suspects that `SEDCMD` only hides data in the UI and that the real credit cards are still recoverable on the Linux filesystem of the Indexers.

### Question 5.1
Explain why a raw Linux `grep` or `strings` command executed against the Indexer's `/opt/splunk/var/lib/splunk/payments/db/hot_v1_0/journal.zst` will NEVER find the unmasked credit card number once `SEDCMD` has processed the data.

<details>
<summary>💡 Hint</summary>
At what pipeline stage does SEDCMD execute, and does Splunk ever write the pre-SEDCMD string to disk?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> <code>SEDCMD</code> executes in the in-memory parsing pipeline on the Heavy Forwarder or Indexer before the event reaches the indexing pipeline. Splunk rewrites the <code>_raw</code> event buffer in RAM; the unmasked raw string is discarded from memory immediately. The Indexer only ever receives and compresses the post-masked string into <code>journal.zst</code>.<br/>
<strong>Flag 5:</strong> <code>THM{IMMUTABLE_DISK_FORENSICS_VERIFIED_CLEAN}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+250 XP`
- **Key Takeaway:** You have mastered in-memory `SEDCMD` stream substitution, established 100% PCI-DSS compliant PAN masking, eliminated cleartext token vulnerabilities, and proven disk immutability!
