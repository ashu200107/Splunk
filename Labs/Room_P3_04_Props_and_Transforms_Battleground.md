# 🕹️ Room P3-04: Props & Transforms Battleground

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 04  
> **Difficulty:** Intermediate | **XP Reward:** `250 XP` | **Estimated Time:** 35 mins  
> **Target Scenario:** Enterprise Multi-Tier Configuration Placement Remediation  
> **Prerequisites:** Chapter 04 (props.conf vs transforms.conf Architecture)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
The Compliance Audit team conducted an unannounced PCI-DSS assessment of your Splunk deployment and issued an immediate **SEV-1 Critical Audit Violation**:
- Unmasked customer Credit Card numbers and Social Security numbers are landing in raw text inside index `payments` on the Indexers!
- When asked why, the junior administrator stated: *"I created the `SEDCMD` masking rules and deployed them to the Search Head cluster yesterday!"*
- Meanwhile, searches for `client_ip` and `username` on the Search Head are failing because search-time regexes were placed on the Indexers, and a critical `nullQueue` routing rule on the Heavy Forwarder is failing to trigger.

Your mission is to audit every tier (Universal Forwarder, Heavy Forwarder, Indexer, Search Head), eliminate tier misplacements, restore compliance, and capture all 5 administrative flags!

---

## 🧭 Task 1: Rescuing the Ingestion-Time Masking Misplacement

The administrator placed the following stanza on the Search Head Cluster:

```ini
# /opt/splunk/etc/apps/fincorp_security/local/props.conf (ON SEARCH HEAD)
[fincorp:payment:wire]
SEDCMD-mask_cc = s/\d{4}-\d{4}-\d{4}-(\d{4})/XXXX-XXXX-XXXX-\1/g
LINE_BREAKER = ([\r\n]+)\d{4}-\d{2}-\d{2}
```

### Question 1.1
Explain why `SEDCMD` and `LINE_BREAKER` did not mask credit cards or break lines when deployed to the Search Head, and name the exact tier(s) where these directives MUST be deployed.

<details>
<summary>💡 Hint</summary>
By the time data reaches the Search Head, it is already sliced into events and permanently committed to the Indexer's <code>journal.zst</code> disk vault. Where does index-time parsing occur?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> <code>SEDCMD</code> and <code>LINE_BREAKER</code> are ingestion-time (index-time) directives that operate exclusively in the parsing pipeline before data is written to disk. The Search Head only executes search-time knowledge.<br/>
<strong>Correct Tier:</strong> Heavy Forwarder (if parsing before forwarding) or Indexer Cluster (if receiving raw data from UFs).<br/>
<strong>Flag 1:</strong> <code>THM{INDEX_TIME_PARSING_RESTORED_TO_INDEXER_TIER}</code>
</details>

---

## 🧭 Task 2: Fixing the `REPORT-` vs `TRANSFORMS-` Prefix Clash

On the Heavy Forwarder (`hf-syslog-01`), the administrator attempted to drop noisy healthcheck logs into `nullQueue` using this configuration:

```ini
# /opt/splunk/etc/apps/fincorp_routing/local/props.conf (ON HEAVY FORWARDER)
[fincorp:payment:wire]
REPORT-drop_health = eliminate_healthchecks

# /opt/splunk/etc/apps/fincorp_routing/local/transforms.conf (ON HEAVY FORWARDER)
[eliminate_healthchecks]
REGEX = (GET|POST)\s+/healthz
DEST_KEY = queue
FORMAT = nullQueue
```

However, healthcheck events are still streaming into the Indexers at 10,000 EPS, consuming license quota!

### Question 2.1
What syntax error in `props.conf` prevented the Heavy Forwarder from executing the `transforms.conf` stanza during ingestion?

<details>
<summary>💡 Hint</summary>
<code>REPORT-</code> is used exclusively for search-time field extractions. What prefix is required for index-time routing?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong> The administrator used the search-time prefix <code>REPORT-</code> instead of the index-time prefix <code>TRANSFORMS-</code>.<br/>
<strong>Correct props.conf:</strong><br/>
<pre><code>[fincorp:payment:wire]
TRANSFORMS-drop_health = eliminate_healthchecks</code></pre>
<strong>Flag 2:</strong> <code>THM{TRANSFORMS_INDEX_TIME_PREFIX_ACTIVATED}</code>
</details>

---

## 🧭 Task 3: Relocating Search-Time Knowledge to Search Heads

The following search-time field extraction and lookup were deployed onto the Indexer Cluster:

```ini
# /opt/splunk/etc/apps/fincorp_props/local/props.conf (ON INDEXER CLUSTER)
[fincorp:payment:wire]
EXTRACT-tx_details = TransactionID=(?<tx_id>\w+) Status=(?<tx_status>\w+)
LOOKUP-user_dept = user_directory email AS user OUTPUT department
```

Security analysts querying Splunk on the Search Head complain that `tx_id`, `tx_status`, and `department` are completely missing from their search results!

### Question 3.1
Why are analysts unable to see `tx_id` and `department`, and what action must you take to make these fields visible in searches?

<details>
<summary>💡 Hint</summary>
Where does Splunk evaluate <code>EXTRACT-</code> and <code>LOOKUP-</code>? Do Indexers share their search-time props.conf with Search Heads?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> <code>EXTRACT-</code> and <code>LOOKUP-</code> are evaluated exclusively on Search Heads when users run queries. Deploying them to Indexers does nothing because Indexers only process search commands dispatched by the Search Head.<br/>
<strong>Remediation:</strong> Package the <code>props.conf</code>, <code>transforms.conf</code>, and CSV lookup files into an app deployed to the Search Head Cluster via the Deployer.<br/>
<strong>Flag 3:</strong> <code>THM{SEARCH_HEAD_KNOWLEDGE_LAYER_SYNCHRONIZED}</code>
</details>

---

## 🧭 Task 4: Stanza Precedence Hierarchy Audit

A log file `/var/log/app/payment.log` has metadata:
- `host = payment-worker-01`
- `source = /var/log/app/payment.log`
- `sourcetype = fincorp:payment:wire`

In `props.conf` on the Indexer, three different engineers defined conflicting values:
```ini
[host::payment-worker-01]
TRUNCATE = 5000

[source::/var/log/app/payment.log]
TRUNCATE = 15000

[fincorp:payment:wire]
TRUNCATE = 80000
```

### Question 4.1
What will be the effective `TRUNCATE` limit applied to events from this file, and in what order does Splunk resolve stanza precedence in `props.conf`?

<details>
<summary>💡 Hint</summary>
Remember the hierarchy: Does Sourcetype beat Source? Does Source beat Host?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong> Effective <code>TRUNCATE = 80000</code>.<br/>
<strong>Precedence Order:</strong><br/>
1. <code>[sourcetype]</code> (Highest Priority - Wins!)<br/>
2. <code>[source::...]</code> (Second Priority)<br/>
3. <code>[host::...]</code> (Lowest Priority)<br/>
<strong>Flag 4:</strong> <code>THM{SOURCETYPE_PRECEDENCE_TRIUMPHS_ALL}</code>
</details>

---

## 🧭 Task 5: End-to-End Tier Compliance Verification

### Question 5.1
State the complete architectural pipeline path for a raw log event originating on a Universal Forwarder, passing through a Heavy Forwarder, indexing on an Indexer Cluster, and queried on a Search Head, specifying which tier performs `inputs.conf`, `LINE_BREAKER`, `SEDCMD`, `.tsidx` commit, and `LOOKUP-`.

<details>
<summary>💡 Hint</summary>
Review the 4-tier production architecture table from Chapter 04.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Architectural Pipeline Flow:</strong><br/>
1. <strong>Universal Forwarder:</strong> Ingests raw bytes via <code>inputs.conf</code> and forwards over TCP 9997.<br/>
2. <strong>Heavy Forwarder:</strong> Executes <code>LINE_BREAKER</code> event breaking and <code>SEDCMD</code> in-memory PII masking.<br/>
3. <strong>Indexer:</strong> Writes compressed raw data into <code>journal.zst</code> and builds inverted index keywords in <code>.tsidx</code>.<br/>
4. <strong>Search Head:</strong> Dispatches SPL queries and evaluates <code>LOOKUP-</code> and <code>EXTRACT-</code> at search time.<br/>
<strong>Flag 5:</strong> <code>THM{PERFECT_END_TO_END_TIER_MASTERY}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+250 XP`
- **Key Takeaway:** You have mastered the definitive architectural tier distribution matrix, conquered `TRANSFORMS-` vs `REPORT-` syntax, enforced `props.conf` stanza precedence, and secured PII compliance across the cluster!
