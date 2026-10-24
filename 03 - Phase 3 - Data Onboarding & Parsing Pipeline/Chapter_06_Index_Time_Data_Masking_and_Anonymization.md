# 📘 Chapter 06 (Phase 3): Index-Time Data Masking & Anonymization

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 21 | **Milestone:** PII & PCI-DSS Compliance Sanitization | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_06_Index_Time_Data_Masking_and_Anonymization.md`  
> **Interactive Cyber Range Lab:** [Room P3-06: PII Redaction Operations](../Labs/Room_P3_06_PII_Redaction_Operations.md) `[250 XP]`

---

## 🏗️ 1. The Simple Explanation: "The Secret Service Redaction Desk"

Imagine a government intelligence agency declassifying top-secret documents before publishing them to the public library:
- If someone takes a black marker and blanks out agent names and undercover phone numbers **before** the book is printed, readers can safely enjoy the book without compromising national security.
- But if the publisher prints the book with real names and just asks readers to *"please close your eyes when reading page 5"*, you have an astronomical security disaster!
- **This is what `SEDCMD` does in Splunk.**
  - **`SEDCMD` is the permanent, indelible black marker.** It runs in RAM during ingestion and permanently rewrites sensitive characters inside `_raw` **before** the event is compressed and written into the Indexer's `journal.zst` storage vault.
  - Once scrubbed by `SEDCMD`, the sensitive data **does not exist anywhere on the Splunk disk**! Even a compromised administrator with root access cannot recover the masked digits.

![Splunk SEDCMD PII Masking 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_sedcmd_pii_masking_3d_1792087088180.jpg)
*Figure 3.6: The Redaction Desk Analogy — How SEDCMD in props.conf permanently scrubs credit cards and SSNs into compliant masked streams before disk commit.*

---

## 🔍 2. Step-by-Step: The 5-Step Ingestion Masking Journey

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE 5-STEP JOURNEY OF INDEX-TIME PII MASKING               │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: Raw Event with Live PII Arrives (Heavy Forwarder / Indexer)    │
│         - Text contains: "cc=4123-4567-8901-2345 ssn=999-00-1234"      │
│                                                                        │
│ Step 2: Splunk Identifies props.conf Stanza                            │
│         - Matches [fincorp:payment:wire]                               │
│         - Discovers SEDCMD-mask_cc and SEDCMD-mask_ssn directives      │
│                                                                        │
│ Step 3: In-Memory Laser Scrubbing (Stream Editor / sed)                │
│         - Splunk applies compiled C++ regular expression in RAM.       │
│         - Preserves last 4 digits for fraud tracking:                  │
│           "4123-4567-8901-2345" ──► "XXXX-XXXX-XXXX-2345"             │
│           "999-00-1234"         ──► "XXX-XX-1234"                      │
│                                                                        │
│ Step 4: The _raw Payload is Permanently Rewritten                      │
│         - The original unmasked string is destroyed in memory!         │
│                                                                        │
│ Step 5: Clean Event Committed to Disk Vault                            │
│         - Masked text is written into journal.zst and .tsidx.          │
│         - 100% compliant with PCI-DSS, HIPAA, and GDPR regulations!    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 3. The Anatomy & Syntax of `SEDCMD`

In `props.conf`, the `SEDCMD` directive uses the classic UNIX stream editor (`sed`) substitution syntax:

```ini
[sourcetype_name]
SEDCMD-<class_name> = s/<regex_pattern>/<replacement_string>/[flags]
```

* **`s/`**: Initiates a substitute command.
* **`<regex_pattern>`**: The target regular expression matching sensitive data.
* **`<replacement_string>`**: The replacement text (or backreferences `\1`, `\2`).
* **`/[flags]`**: Usually `g` (global replacement, so every occurrence in the event is replaced).

> [!NOTE]
> You can have multiple `SEDCMD` directives in the same `props.conf` stanza! Give each one a unique class name:
> ```ini
> SEDCMD-mask_cc  = s/.../.../g
> SEDCMD-mask_ssn = s/.../.../g
> ```

---

## 📋 4. Enterprise Production Masking Recipes (Copy-Paste Blueprints)

### Recipe 1: Credit Card Masking (PCI-DSS Compliant)
Preserves the last 4 digits for customer verification and fraud investigation, while masking the first 12 digits:

```ini
# Matches 16-digit cards with dashes: 4123-4567-8901-2345 -> XXXX-XXXX-XXXX-2345
SEDCMD-mask_cc_dashes = s/\b(?:\d{4}-){3}(\d{4})\b/XXXX-XXXX-XXXX-\1/g

# Matches 16-digit cards without dashes: 4123456789012345 -> XXXXXXXXXXXX2345
SEDCMD-mask_cc_nodash = s/\b\d{12}(\d{4})\b/XXXXXXXXXXXX\1/g
```

---

### Recipe 2: US Social Security Number (SSN) Masking
Replaces the first 5 digits with `XXX-XX-` while preserving the last 4:

```ini
# 999-00-1234 -> XXX-XX-1234
SEDCMD-mask_ssn = s/\b\d{3}-\d{2}-(\d{4})\b/XXX-XX-\1/g
```

---

### Recipe 3: API Keys & Bearer Token Redaction
Vaporizes secrets in HTTP headers and JSON bodies:

```ini
# Authorization: Bearer eyJhbGciOi... -> Authorization: Bearer [REDACTED]
SEDCMD-mask_bearer = s/(?i)(Authorization:\s*Bearer\s+)[^\s"']*/\1[REDACTED]/g

# "api_key": "sec_984f1092a..." -> "api_key": "[REDACTED]"
SEDCMD-mask_apikey = s/(?i)("api_key"\s*:\s*")[^"]+/\1[REDACTED]/g
```

---

### Recipe 4: User Password Redaction in URLs / Query Strings
```ini
# password=SecretPassword123& -> password=***MASKED***&
SEDCMD-mask_passwd = s/(?i)(password|passwd|pwd)=[^&\s]*/\1=***MASKED***/g
```

---

## 🚨 5. Ingestion-Time Masking vs Search-Time Masking: The Audit Trap!

| Feature | Index-Time Masking (`SEDCMD`) | Search-Time Masking (`eval` / `rex`) |
| :--- | :--- | :--- |
| **Where it Runs** | Heavy Forwarder or Indexer | Search Head |
| **Disk State** | Raw PII is **destroyed before disk commit** | Raw PII **lives permanently in cleartext on disk**! |
| **Audit Compliance** | 🟢 **100% PCI-DSS & GDPR Compliant** | 🔴 **Automatic Audit Failure!** |
| **Security Risk** | Zero. Even disk forensic recovery finds nothing. | Severe. Any user with raw search access can view raw cards! |
| **Performance** | Incurred once at ingest time (fast C++). | Repeated on every single user search (slows SPL). |

> [!CAUTION]
> **The Auditor's Trap:**  
> Never claim you are PCI-DSS compliant by creating an `eval cc_number="XXXX"` field extraction on a Search Head! Any compliance auditor will run a direct query on `_raw` or inspect `/var/lib/splunk/<index>/db/` and immediately issue a catastrophic security violation!

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-06

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-06: PII Redaction Operations & Compliance Surgery           │
│ ⭐ DIFFICULTY: Intermediate | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins    │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> A banking regulator just notified your CISO that cleartext credit card numbers and client social security numbers were discovered inside raw logs on your production Splunk indexers!  
> You have 30 minutes to:
> 1. Formulate exact `SEDCMD` regexes to mask 16-digit cards (preserving last 4 digits).
> 2. Redact 9-digit SSNs.
> 3. Scrub sensitive API keys and JWT Bearer tokens from incoming HTTP collector feeds.
> 4. Ensure these rules are correctly placed on the Heavy Forwarder tier to prevent disk commit!

👉 **[Enter the Cyber Range: Room P3-06](../Labs/Room_P3_06_PII_Redaction_Operations.md)** `[250 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **What UNIX tool's substitution syntax does Splunk adopt for `SEDCMD` in `props.conf`?**
2. **Write the exact `SEDCMD` rule to replace 9-digit Social Security Numbers (`123-45-6789`) with `XXX-XX-6789`.**
3. **If `SEDCMD` is configured on a Search Head, will it mask data written to the Indexer's `journal.zst`? Why or why not?**
4. **Why is search-time masking with `eval` considered a compliance violation under PCI-DSS?**
5. **What flag must be placed at the very end of a `SEDCMD` substitution statement to ensure all occurrences of a sensitive pattern within an event are replaced?**

---
*Ready to advance to Chapter 07: Search-Time Field Extractions (Inline Regex vs Transforms, JSON/XML Handling)?*
