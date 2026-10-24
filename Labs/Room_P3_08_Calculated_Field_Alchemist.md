# 🕹️ Room P3-08: The Calculated Field Alchemist

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 08  
> **Difficulty:** Intermediate | **XP Reward:** `200 XP` | **Estimated Time:** 30 mins  
> **Target Scenario:** Enterprise Executive Dashboard Normalization & Pipeline Sequence Repair  
> **Prerequisites:** Chapter 08 (Calculated Fields, Field Aliases & Sourcetype Renaming)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
The VP of Enterprise Architecture and the CISO launched an executive war room:  
The global **PCI-DSS Threat & Latency Dashboard** has gone haywire:
1. Three separate payment clusters name client IP addresses differently (`client_ip`, `c_ip`, `user_ip`), causing 70% of network traffic to disappear from geo-location maps.
2. The payment SLA panel expects latency in milliseconds (`duration_ms`), but microservices output `latency_microsec`.
3. An intern tried to create a field alias on top of an `EVAL-` field, violating the search-time operations sequence and causing search queries to throw null-pointer errors!

Your mission is to perform surgical knowledge normalization in `props.conf` on the Search Head Cluster, configure `FIELDALIAS-`, build `EVAL-` expressions, harmonize sourcetypes, and capture all 5 flags!

---

## 🧭 Task 1: Multi-Vendor Field Aliasing (`FIELDALIAS-`)

Legacy firewall logs from CheckPoint, Cisco, and Palo Alto use disparate IP field names:
- `checkpoint:firewall` outputs `orig_ip`
- `cisco:asa` outputs `src_ip`
- `pan:traffic` outputs `source_ip`

The Common Information Model (CIM) expects **`src`**.

### Question 1.1
Write the exact `FIELDALIAS-` directives in `props.conf` to alias `orig_ip` in `[checkpoint:firewall]` and `source_ip` in `[pan:traffic]` to `src`.

<details>
<summary>💡 Hint</summary>
Syntax: <code>FIELDALIAS-&lt;class&gt; = &lt;orig_field&gt; AS &lt;alias_field&gt;</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[checkpoint:firewall]
FIELDALIAS-norm_cp = orig_ip AS src

[pan:traffic]
FIELDALIAS-norm_pan = source_ip AS src</code></pre>
<strong>Flag 1:</strong> <code>THM{FIELD_ALIAS_CIM_SRC_STANDARDIZED}</code>
</details>

---

## 🧭 Task 2: Latency Mathematical Transformation via `EVAL-`

The payment API logs transaction duration in microseconds:
`latency_microsec = 2450000` (which equals 2.45 seconds).  
The executive SLA dashboard requires the field **`duration_sec`** rounded to 2 decimal places.

### Question 2.1
Formulate the `EVAL-` directive in `props.conf` that automatically calculates `duration_sec` from `latency_microsec` on every search.

<details>
<summary>💡 Hint</summary>
Divide by <code>1000000</code> and wrap with <code>round(&lt;value&gt;, 2)</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:payment:api]
EVAL-duration_sec = round(latency_microsec / 1000000, 2)</code></pre>
<strong>Flag 2:</strong> <code>THM{EVAL_LATENCY_MICROSECONDS_NORMALIZED}</code>
</details>

---

## 🧭 Task 3: HTTP Error Categorization via `case()`

The operations center needs an automated classification field named `http_category` that groups HTTP status codes:
- Codes $\ge 500$: `"Server Error"`
- Codes $\ge 400$: `"Client Error"`
- Codes $\ge 300$: `"Redirect"`
- All other codes: `"Success"`

### Question 3.1
Write the `EVAL-` directive in `props.conf` using the `case()` function to calculate `http_category` automatically.

<details>
<summary>💡 Hint</summary>
In <code>case()</code>, conditions are evaluated in order. End with <code>true(), "Success"</code> as the default catch-all.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[nginx:access]
EVAL-http_category = case(status>=500, "Server Error", status>=400, "Client Error", status>=300, "Redirect", true(), "Success")</code></pre>
<strong>Flag 3:</strong> <code>THM{CASE_FUNCTION_HTTP_STATUS_CATEGORIZED}</code>
</details>

---

## 🧭 Task 4: Resolving the Search-Time Sequence Violation

An administrator configured the following rules in `props.conf`:

```ini
[custom:web:app]
EVAL-latency_ms = response_time / 1000
FIELDALIAS-latency_map = latency_ms AS duration
```
When running searches for `duration > 500`, Splunk returns **zero results**!

### Question 4.1
Explain why `duration` is empty in search queries, and provide the correct architectural fix.

<details>
<summary>💡 Hint</summary>
Look at the Search Head pipeline order: Does <code>FIELDALIAS-</code> run before or after <code>EVAL-</code>?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> In Splunk's search-time pipeline, <code>FIELDALIAS-</code> executes in Step 5, <strong>BEFORE</strong> <code>EVAL-</code> runs in Step 6. Because <code>latency_ms</code> does not exist when <code>FIELDALIAS-</code> evaluates, the alias creates an empty null field!<br/>
<strong>Correct Fix:</strong> Calculate <code>duration</code> directly using <code>EVAL-</code>:<br/>
<pre><code>EVAL-latency_ms = response_time / 1000
EVAL-duration = response_time / 1000</code></pre>
<strong>Flag 4:</strong> <code>THM{SEARCH_TIME_PRECEDENCE_ORDER_RESTORED}</code>
</details>

---

## 🧭 Task 5: Sourcetype Renaming Harmonization

Your company ingests web access logs from Apache and Nginx under two separate names:
- `apache:httpd:access`
- `nginx:web:access`

Dashboard developers want to search both simultaneously using: `sourcetype=web:access`.

### Question 5.1
Configure `props.conf` to rename both sourcetypes to `web:access` at search time.

<details>
<summary>💡 Hint</summary>
Use the <code>rename = &lt;new_name&gt;</code> directive under each sourcetype stanza.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[apache:httpd:access]
rename = web:access

[nginx:web:access]
rename = web:access</code></pre>
<strong>Flag 5:</strong> <code>THM{SOURCETYPE_RENAMING_UNIFIED_BANNER}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+200 XP`
- **Key Takeaway:** You have mastered search-time normalization via `FIELDALIAS-`, dynamic calculations with `EVAL-`, enforced the strict search-time operations sequence, and harmonized sourcetypes!
