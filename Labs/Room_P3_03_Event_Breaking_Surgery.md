# 🕹️ Room P3-03: The Event Breaking Surgery & Timestamp Rescue

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 03  
> **Difficulty:** Intermediate | **XP Reward:** `250 XP` | **Estimated Time:** 35 mins  
> **Target Scenario:** Mission-Critical Banking Java Stack Trace & Timestamp Triage  
> **Prerequisites:** Chapter 03 (Event Breaking & Timestamp Recognition)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
The core payment gateway application (`fin-payment-prod`) underwent a major v4.2 upgrade. Immediately after launch, the SOC and Application Support teams flooded your desk with urgent incident tickets:
1. **The Fractured Stack Trace Nightmare:** A single database deadlock error spanning 45 lines of Java stack trace is being indexed as 45 separate single-line events in Splunk!
2. **The 10 KB Payload Amputation:** Large XML transaction receipts (>15 KB) are being violently cut in half, breaking JSON and XML parsers.
3. **The 30-Day Time-Travel Drift:** Events occurring on `06/07/2026` (July 6th) are showing up in Splunk as `07/06/2026` (June 7th), completely breaking real-time alerting!

Your mission is to perform surgical configuration edits in `props.conf` to reconstruct the events, eliminate truncation, enforce strict timestamp recognition, and capture all 5 forensic flags!

---

## 🧭 Task 1: Reconstructing Multi-Line Java Stack Traces

Here is a raw sample of the broken application log stream:

```text
2026-10-15 14:20:10.502 [Thread-4] ERROR com.fincorp.vault.PaymentProcessor - Transaction #84920 Failed
java.sql.SQLException: Connection timeout after 30000ms
	at com.fincorp.db.Pool.getConnection(Pool.java:142)
	at com.fincorp.vault.PaymentProcessor.execute(PaymentProcessor.java:88)
	at java.lang.Thread.run(Thread.java:834)
2026-10-15 14:20:11.100 [Thread-5] INFO com.fincorp.vault.PaymentProcessor - Retrying Transaction #84920
```

Currently, Splunk is breaking on every single newline, indexing the stack trace lines (`at com.fincorp...`) as orphaned standalone events without timestamps!

### Question 1.1
Write the exact `props.conf` configuration stanza to ensure each event begins with the date `YYYY-MM-DD` using high-performance `LINE_BREAKER`, while completely disabling the slow `SHOULD_LINEMERGE` engine.

<details>
<summary>💡 Hint</summary>
Set <code>SHOULD_LINEMERGE = false</code>. In <code>LINE_BREAKER</code>, use a capture group for newlines: <code>([\r\n]+)</code> followed by a date regex.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:payment:java]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}</code></pre>
<strong>Flag 1:</strong> <code>THM{LINE_BREAKER_MULTILINE_FRACTURE_HEALED}</code>
</details>

---

## 🧭 Task 2: Defeating the 10 KB Event Truncation

The payment gateway logs serialized XML payment payloads for high-value corporate transfers. These payloads regularly measure **25,000 to 40,000 bytes**.  
When searching Splunk, developers notice that all XML events abruptly stop at character 10,000, leaving unclosed tags like `<Transactio...` and generating a second orphaned fragment event!

### Question 2.1
What directive in `props.conf` controls the maximum event byte boundary, and what value should you assign to safely support events up to 100 KB?

<details>
<summary>💡 Hint</summary>
The directive is <code>TRUNCATE</code>. 100 KB in bytes is <code>100000</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong> <code>TRUNCATE = 100000</code><br/>
<strong>Flag 2:</strong> <code>THM{TRUNCATE_BOUNDARY_EXPANDED_100KB}</code>
</details>

---

## 🧭 Task 3: Laser Timestamp Acquisition via `TIME_PREFIX`

The log format contains a noisy header before the actual timestamp:
```text
[INSTANCE=prod-app-09] [CLUSTER=us-east-1] [EVENT_TIME: 2026-10-15 14:20:10.502] Message text...
```
Because Splunk's default scanner has to parse through `INSTANCE` and `CLUSTER` strings on every event, Indexer CPU utilization in `parsingQueue` is running at 94%!

### Question 3.1
Configure `TIME_PREFIX` and `MAX_TIMESTAMP_LOOKAHEAD` to instantly jump to the `EVENT_TIME:` marker and constrain the character search window.

<details>
<summary>💡 Hint</summary>
Target <code>\[EVENT_TIME:\s*</code> with <code>TIME_PREFIX</code> and limit lookahead to 30 characters.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Configuration:</strong><br/>
<pre><code>TIME_PREFIX = \[EVENT_TIME:\s*
MAX_TIMESTAMP_LOOKAHEAD = 30</code></pre>
<strong>Flag 3:</strong> <code>THM{LASER_TARGETED_TIME_PREFIX_ACQUIRED}</code>
</details>

---

## 🧭 Task 4: Inverted Date Format Remediation (`TIME_FORMAT`)

Raw log lines from the European payment cluster use the UK format (`DD/MM/YYYY`):
`15/10/2026 14:20:10.502` (October 15, 2026).  
However, events from early July (`06/07/2026`) were misinterpreted by Splunk's default parser as US format (`MM/DD/YYYY` $\rightarrow$ June 7, 2026), sending events back 30 days into the past!

### Question 4.1
Write the exact POSIX `strftime` string for `TIME_FORMAT` that strictly enforces Day/Month/Year with millisecond precision.

<details>
<summary>💡 Hint</summary>
<code>%d</code> is day, <code>%m</code> is month, <code>%Y</code> is 4-digit year, and <code>%3N</code> is 3-digit millisecond.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>TIME_FORMAT = %d/%m/%Y %H:%M:%S.%3N</code></pre>
<strong>Flag 4:</strong> <code>THM{STRICT_STRFTIME_DATE_INVERSION_DEFEATED}</code>
</details>

---

## 🧭 Task 5: Timezone Stabilization with `TZ`

The payment nodes run inside Docker containers where the local OS clock is set to Eastern Standard Time (`EST`), but logs are output without a timezone offset:
`2026-10-15 14:20:10.502`  
Because the Indexer runs in London (`UTC`), Splunk misinterprets the event time, causing a 5-hour lag in real-time alert searches!

### Question 5.1
What directive in `props.conf` pins the incoming stream to US Eastern Standard Time, regardless of what timezone the Indexer or Forwarder OS is set to?

<details>
<summary>💡 Hint</summary>
The directive is <code>TZ</code> and accepts standard Olson timezone database names.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>TZ = America/New_York</code></pre>
<strong>Flag 5:</strong> <code>THM{TIMEZONE_STABILIZED_AMERICA_NEW_YORK}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+250 XP`
- **Key Takeaway:** You have mastered multi-line `LINE_BREAKER` regex boundary mechanics, eliminated `TRUNCATE` data amputations, and deployed zero-overhead `TIME_PREFIX` / `TIME_FORMAT` timestamp parsers!
