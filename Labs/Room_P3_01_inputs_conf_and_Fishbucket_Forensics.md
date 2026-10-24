# 🕹️ Room P3-01: Fishbucket Forensics & Ingestion Engineering

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 01  
> **Difficulty:** Intermediate | **XP Reward:** `250 XP` | **Estimated Time:** 35 mins  
> **Target Scenario:** Enterprise Web & Vault Cluster Ingestion Failure  
> **Prerequisites:** Chapter 01 (inputs.conf Anatomy & Fishbucket Forensics)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
At 03:15 UTC, the Security Operations Center (SOC) detected unauthorized withdrawals originating from an internal payment vault service. However, when the incident response team queried index `vault_logs` in Splunk:

```spl
index=vault_logs sourcetype="fincorp:vault:auth"
```

**Zero results returned for the last 48 hours!**

The forwarder on the payment gateway (`vault-fwd-01`) is running, but logs are failing to index. Your mission is to dive into the forwarder's filesystem, inspect `inputs.conf`, analyze the fishbucket using `btprobe`, fix the collision, and restore continuous ingestion to capture all 5 forensic flags!

---

## 🧭 Task 1: File Monitor Stanza & Wildcard Reconnaissance

Inspect the current configuration on the forwarder:
```ini
# /opt/splunkforwarder/etc/apps/fincorp_inputs/local/inputs.conf
[monitor:///var/log/fincorp/vault/*/*.log]
disabled = false
index = vault_logs
sourcetype = fincorp:vault:auth
```

The developers created a new subfolder hierarchy:
`/var/log/fincorp/vault/auth/prod/2026/events.log`

### Question 1.1
Why is Splunk failing to detect `/var/log/fincorp/vault/auth/prod/2026/events.log` with the current stanza path `/var/log/fincorp/vault/*/*.log`?

<details>
<summary>💡 Hint</summary>
The single asterisk <code>*</code> only matches a single directory level. How does Splunk define a recursive wildcard that matches any depth?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong> The single asterisk <code>*</code> stops at the first directory boundary. To match recursive subdirectories at any depth, Splunk requires the triple-dot ellipsis <code>...</code> wildcard.<br/>
<strong>Correct Stanza:</strong> <code>[monitor:///var/log/fincorp/vault/.../*.log]</code><br/>
<strong>Flag 1:</strong> <code>THM{ELLIPSIS_RECURSIVE_TRAVERSAL_RESOLVED}</code>
</details>

---

## 🧭 Task 2: Whitelist & Blacklist Regex Surgery

The directory `/var/log/fincorp/vault/` contains legitimate logs, but it is also polluted with:
- Temp lock files (`.swp`, `.tmp`)
- Rotated archives (`auth_202609.log.gz`)
- Debug trace dumps (`debug_trace.log`)

The junior admin wrote this broken filter:
```ini
whitelist = \.log$
blacklist = debug
```

However, rotated archives like `auth_202609.log.gz` are still causing indexing errors, and critical audit JSON files (`audit.json`) are completely ignored!

### Question 2.1
What regex whitelist and blacklist combination ensures only files ending in `.log` and `.json` are ingested, while strictly excluding any files containing `debug` or ending in `.gz` or `.tmp`?

<details>
<summary>💡 Hint</summary>
Remember that Splunk applies the <code>whitelist</code> first. Then the <code>blacklist</code> overrides any whitelisted matches.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Correct Configuration:</strong><br/>
<pre><code>whitelist = \.(log|json)$
blacklist = (debug|\.(gz|tmp)$)</code></pre>
<strong>Flag 2:</strong> <code>THM{REGEX_WHITELIST_SURGICAL_PRECISION}</code>
</details>

---

## 🧭 Task 3: The Identical Header Fishbucket Trap

The payment gateway generates daily financial summary reports:
- `/var/log/fincorp/vault/reports/daily_trans_20261014.csv`
- `/var/log/fincorp/vault/reports/daily_trans_20261015.csv`

Both files have a 300-byte identical CSV column header:
`Timestamp,TransactionID,SourceAccount,DestinationAccount,Amount,Currency,RoutingNumber,AuthStatus,ApprovalCode,TerminalID...`

Splunk indexed the 2026-10-14 report, but the 2026-10-15 report has never appeared in Splunk!

### Question 3.1
Explain why Splunk ignored `daily_trans_20261015.csv`, and state the exact directive added to the stanza to force Splunk to generate a unique CRC for each distinct file path.

<details>
<summary>💡 Hint</summary>
Splunk by default only hashes the first 256 bytes (CRC). Since both files have identical 300-byte headers, their CRCs match. Splunk thinks it already indexed the file!
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> The first 256 bytes of both CSV files are identical. Splunk calculates the exact same CRC hash for both files and assumes the second file is a duplicate of the first.<br/>
<strong>Directive:</strong> <code>crcSalt = &lt;SOURCE&gt;</code> (or alternatively <code>initCrcLength = 1024</code>).<br/>
<strong>Flag 3:</strong> <code>THM{CRCSALT_SOURCE_HASH_COLLISION_DEFEATED}</code>
</details>

---

## 🧭 Task 4: Fishbucket Forensics via `btprobe`

You need to verify whether the forwarder has finished indexing `/var/log/fincorp/vault/emergency_dump.log` or if it's currently stalled mid-file.

### Question 4.1
Write the exact CLI command using `btprobe` to inspect the fishbucket seek pointer for `/var/log/fincorp/vault/emergency_dump.log` on a Linux Universal Forwarder.

<details>
<summary>💡 Hint</summary>
The binary is invoked with <code>splunk cmd btprobe</code>, pointing to the fishbucket database path with <code>-d</code> and the file path with <code>--file</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Command:</strong><br/>
<pre><code>/opt/splunkforwarder/bin/splunk cmd btprobe \
  -d /opt/splunkforwarder/var/lib/splunk/fishbucket/db \
  --file /var/log/fincorp/vault/emergency_dump.log</code></pre>
<strong>Flag 4:</strong> <code>THM{BTPROBE_SEEKPTR_INTERROGATION_SUCCESS}</code>
</details>

---

## 🧭 Task 5: Surgical Single-File Re-Index

The SOC demands that `/var/log/fincorp/vault/emergency_dump.log` be re-indexed from **byte 0**, but you are **forbidden** from restarting Splunk or wiping the entire fishbucket database (as that would cause millions of duplicate events from other log files).

### Question 5.1
What command resets the fishbucket pointer for *only* this single file?

<details>
<summary>💡 Hint</summary>
Add the <code>--reset</code> argument to your <code>btprobe</code> command.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Command:</strong><br/>
<pre><code>/opt/splunkforwarder/bin/splunk cmd btprobe \
  -d /opt/splunkforwarder/var/lib/splunk/fishbucket/db \
  --file /var/log/fincorp/vault/emergency_dump.log \
  --reset</code></pre>
<strong>Flag 5:</strong> <code>THM{SURGICAL_FISHBUCKET_POINTER_FLUSH}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+250 XP`
- **Key Takeaway:** You now possess deep, enterprise-grade mastery over `inputs.conf` monitor patterns, regex whitelist/blacklist filtering, Fishbucket CRC mechanics, and `btprobe` pointer triage!
