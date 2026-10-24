# 🕹️ Room P3-07: Search-Time Regex Heist & Schema-on-Read Mastery

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 07  
> **Difficulty:** Intermediate | **XP Reward:** `250 XP` | **Estimated Time:** 35 mins  
> **Target Scenario:** SOC Threat Intelligence Outage & Regex CPU Lockup  
> **Prerequisites:** Chapter 07 (Search-Time Field Extractions)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
The SOC Threat Response team escalated a high-priority operational emergency:  
1. Threat intelligence alerts looking for malicious external IPs and command-and-control beacons are returning **zero results** because firewall and proxy logs lack extracted fields!
2. A junior analyst deployed a poorly written unanchored regex to `props.conf` on the Search Head Cluster, causing the search processes (`splunkd`) to hit **100% CPU utilization** and freezing user searches!
3. Cloud microservices sending nested JSON data have raw payloads trapped in `_raw` without individual fields.

Your mission is to perform search-time field extraction surgery in `props.conf` and `transforms.conf` on the Search Head Cluster, optimize regex performance, configure `DELIMS` and `KV_MODE`, and capture all 5 forensic flags!

---

## 🧭 Task 1: Inline Named Capture Group Extraction (`EXTRACT-`)

The legacy proxy firewall outputs raw logs in this format:
```text
2026-10-16 04:10:05.102 PROXY_AUTH client=10.14.2.85 dest=198.51.100.22:443 method=POST status=200 response_ms=45 user="svc_finance"
```

The SOC analyst needs fields:
- `src_ip` (from `client=`)
- `dest_ip` (from `dest=`)
- `dest_port` (from port after colon)
- `user` (from `user="<name>"`)

### Question 1.1
Write the exact `EXTRACT-` directive in `props.conf` using named capture groups `(?<field>pattern)` to extract these 4 fields in a single clean pass.

<details>
<summary>💡 Hint</summary>
Use <code>client=(?&lt;src_ip&gt;[^\s]+) dest=(?&lt;dest_ip&gt;[^:]+):(?&lt;dest_port&gt;\d+)</code> and match user with <code>user="(?&lt;user&gt;[^"]+)"</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:proxy:auth]
EXTRACT-proxy_fields = client=(?<src_ip>\S+)\s+dest=(?<dest_ip>[^:]+):(?<dest_port>\d+).*?user="(?<user>[^"]+)"</code></pre>
<strong>Flag 1:</strong> <code>THM{NAMED_CAPTURE_GROUP_FIELD_HARVEST}</code>
</details>

---

## 🧭 Task 2: High-Performance Key-Value Tokenizing (`DELIMS`)

The identity verification cluster outputs space-delimited key-value pairs:
```text
app=id_vault event_id=8402 user=john_doe role=auditor status=SUCCESS auth_method=MFA
```

Instead of running slow regex engines, the architecture team mandates using compiled C++ delimiter tokenization via `transforms.conf`.

### Question 2.1
Configure `props.conf` and `transforms.conf` using `DELIMS` to automatically extract all key-value pairs without writing any regular expression.

<details>
<summary>💡 Hint</summary>
In <code>props.conf</code>, use <code>REPORT-</code>. In <code>transforms.conf</code>, set <code>DELIMS = " ", "="</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:id:vault]
REPORT-extract_kv = parse_id_vault_pairs</code></pre>
<strong>transforms.conf:</strong><br/>
<pre><code>[parse_id_vault_pairs]
DELIMS = " ", "="</code></pre>
<strong>Flag 2:</strong> <code>THM{DELIMS_TOKENIZER_HIGH_SPEED_EXTRACTION}</code>
</details>

---

## 🧭 Task 3: Multi-Value Field Extractions (`MV_ADD`)

A security scanner logs multiple compromised hostnames in a single event:
```text
VULNERABLE_HOSTS: srv-web-01, srv-db-02, srv-app-04, srv-vpn-01
```
Currently, Splunk extracts only the first host (`srv-web-01`) and ignores the rest!

### Question 3.1
Configure `transforms.conf` to extract all hostnames into a multi-value array field named `compromised_host`.

<details>
<summary>💡 Hint</summary>
Set <code>MV_ADD = true</code> and <code>REPEAT_MATCH = true</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>transforms.conf:</strong><br/>
<pre><code>[extract_vulnerable_hosts]
REGEX = (?:VULNERABLE_HOSTS:|,)\s*(?<compromised_host>[^,\s]+)
MV_ADD = true
REPEAT_MATCH = true</code></pre>
<strong>Flag 3:</strong> <code>THM{MULTI_VALUE_ARRAY_EXTRACTION_SUCCESS}</code>
</details>

---

## 🧭 Task 4: Auto-Extraction of Nested Cloud JSON via `KV_MODE`

The AWS Lambda payments microservice logs complex nested JSON payloads:
```json
{"transaction": {"id": "tx_9482", "amount": 1450.00, "customer": {"id": "cust_12", "country": "DE"}}}
```

### Question 4.1
What single line directive in `props.conf` automatically parses all nested JSON keys without writing any custom extraction rules?

<details>
<summary>💡 Hint</summary>
The directive is <code>KV_MODE</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>[fincorp:lambda:json]
KV_MODE = json</code></pre>
<strong>Flag 4:</strong> <code>THM{KV_MODE_JSON_AUTOMATED_PARSER}</code>
</details>

---

## 🧭 Task 5: Neutralizing Catastrophic Regex Backtracking

The junior analyst wrote this catastrophic regex:
```ini
EXTRACT-bad_extraction = .*(?<session_token>[a-f0-9]{32}).*(?<api_version>v\d+).*
```
When running across 5,000,000 events, the search engine undergoes exponential state backtracking, exhausting Search Head memory and crashing `splunkd`.

### Question 5.1
Rewrite this extraction to anchor the pattern, eliminate all greedy wildcards `.*`, and protect the Search Head from backtracking lockups.

<details>
<summary>💡 Hint</summary>
Anchor with <code>^</code>, remove leading and trailing wildcards, and use non-greedy matching or specific boundary tokens.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Optimized Regex:</strong><br/>
<pre><code>EXTRACT-optimized_session = ^\S+\s+token=(?<session_token>[a-f0-9]{32})\s+ver=(?<api_version>v\d+)</code></pre>
<strong>Flag 5:</strong> <code>THM{CATASTROPHIC_BACKTRACKING_NEUTRALIZED}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+250 XP`
- **Key Takeaway:** You have mastered search-time inline `EXTRACT-` regexes, high-speed `DELIMS` key-value tokenizers, multi-value `MV_ADD` arrays, automated `KV_MODE = json` extractions, and eliminated CPU-killing catastrophic backtracking!
