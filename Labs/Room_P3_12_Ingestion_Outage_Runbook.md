# 🕹️ Room P3-12: The Ingestion Outage Runbook & Diagnostic Trauma Center

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 12  
> **Difficulty:** Advanced | **XP Reward:** `300 XP` | **Estimated Time:** 40 mins  
> **Target Scenario:** Enterprise Ingestion Trauma Triage & Pipeline Restoration  
> **Prerequisites:** Chapter 12 (Ingestion Pipeline Troubleshooting Runbooks)

---

## 🎯 Mission Briefing

You are the Lead Ingestion & Detection Architect at **FinCorp Global**.  
At 02:00 AM, the NOC triggered an all-hands P1 incident: **The entire enterprise ingestion pipeline is halting!**  
1. Forwarders across 4 datacenters report: `Blocked transmission to output queue`.  
2. Core banking transaction events with dates in format `15.10.2026` are failing date parsing and showing up with `_time` set to `1970-01-01`!  
3. A newly launched analytics dashboard triggered an infinite regex search that is pegging the Search Head Cluster at **100% CPU**.  
4. The Indexers' `parsingQueue` is jammed at **100% full**.

Your mission is to step into the Ingestion Trauma Center, execute production diagnostic runbooks using `_internal`, restore the pipeline, and capture all 5 flags!

---

## 🧭 Task 1: Isolating Queue Bottlenecks via `_internal`

When you log into the Monitoring Console, you notice all forwarders are backed up.  
You run the queue health diagnostic query:
```spl
index=_internal sourcetype=splunkd group=queue name=* 
| timechart max(current_size_kb) by name
```
Result:
- `parsingQueue`: 99.8% full
- `indexQueue`: 4.2% full
- `typingQueue`: 3.1% full

### Question 1.1
Is the bottleneck caused by Disk IOPS or CPU Core Starvation, and which tier of configuration directives is causing the choke?

<details>
<summary>💡 Hint</summary>
When <code>parsingQueue</code> is full while <code>indexQueue</code> is nearly empty, what resource does the parsing pipeline consume?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong> The bottleneck is <strong>CPU Core Starvation</strong>. The parsing pipeline performs event breaking (<code>LINE_BREAKER</code>), regex evaluations, and stream edits (<code>SEDCMD</code>). When <code>parsingQueue</code> jams while <code>indexQueue</code> is empty, it means the disk writes are fast, but the CPU is choked by unanchored or complex regexes!<br/>
<strong>Flag 1:</strong> <code>THM{PARSING_QUEUE_CPU_EXHAUSTION_IDENTIFIED}</code>
</details>

---

## 🧭 Task 2: Curing the Epoch 1970 Timestamp Drift

Banking database logs output dates with periods:
```text
[LOG_START] 15.10.2026-14:20:10.502 [TX_NODE_01] Balance update...
```
Because Splunk's default parser does not recognize dot-separated dates, all events are stamped as `1970-01-01 00:00:00`!

### Question 2.1
Formulate the `props.conf` configuration with `TIME_PREFIX`, `TIME_FORMAT`, and `MAX_DAYS_AGO` to parse this timestamp accurately and drop any rogue events older than 14 days.

<details>
<summary>💡 Hint</summary>
Target <code>\[LOG_START\]\s*</code>. Use <code>TIME_FORMAT = %d.%m.%Y-%H:%M:%S.%3N</code> and <code>MAX_DAYS_AGO = 14</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:db:tx]
TIME_PREFIX = \[LOG_START\]\s*
MAX_TIMESTAMP_LOOKAHEAD = 30
TIME_FORMAT = %d.%m.%Y-%H:%M:%S.%3N
MAX_DAYS_AGO = 14</code></pre>
<strong>Flag 2:</strong> <code>THM{EPOCH_1970_TIMESTAMP_DRIFT_ERADICATED}</code>
</details>

---

## 🧭 Task 3: Fixing Fractured Multi-Line Stack Traces

Application logs from a Python microservice are splitting tracebacks into hundreds of tiny 1-line events:
```text
2026-10-16 02:15:00 ERROR in worker.py:
Traceback (most recent call last):
  File "worker.py", line 42, in process_task
  ConnectionRefusedError: [Errno 111] Connection refused
2026-10-16 02:15:01 INFO Task retrying...
```

### Question 3.1
Write the high-speed `LINE_BREAKER` and `TRUNCATE` configuration to ensure each event begins with `YYYY-MM-DD` and events up to 150 KB are preserved intact.

<details>
<summary>💡 Hint</summary>
Capture newlines with <code>([\r\n]+)</code> and set <code>TRUNCATE = 150000</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:python:worker]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}
TRUNCATE = 150000</code></pre>
<strong>Flag 3:</strong> <code>THM{PYTHON_TRACEBACK_LINE_BREAKER_SEALED}</code>
</details>

---

## 🧭 Task 4: Neutralizing Search Head Catastrophic Backtracking

A developer deployed this extraction on the Search Head:
```ini
EXTRACT-slow_auth = .*(?<session_id>[a-z0-9]{16}).*(?<user_name>[a-z]+).*
```
When running across 2,000,000 events, the search process enters an exponential state explosion, locking all CPU cores.

### Question 4.1
Rewrite this extraction with proper line anchoring (`^`) and non-greedy matching to eliminate backtracking.

<details>
<summary>💡 Hint</summary>
Remove leading and trailing <code>.*</code>. Anchor to the beginning of the string with <code>^</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Optimized Regex:</strong><br/>
<pre><code>EXTRACT-fast_auth = ^\S+\s+session=(?<session_id>[a-z0-9]{16})\s+user=(?<user_name>[a-z]+)</code></pre>
<strong>Flag 4:</strong> <code>THM{BACKTRACKING_CPU_EXPLOSION_DEFUSED}</code>
</details>

---

## 🧭 Task 5: Rescuing Forwarder `TailReader` Stalls via `btprobe`

A critical audit log `/var/log/audit/pci_vault.log` on forwarder `fwd-pci-01` stopped indexing 12 hours ago.  
The log has grown by 500 MB, but the forwarder's `_internal` logs show:
`TailReader - Finished reading file, waiting for data.`

### Question 5.1
Write the exact `btprobe` command to interrogate the fishbucket database on the forwarder to see whether Splunk's seek pointer matches the real file size on disk.

<details>
<summary>💡 Hint</summary>
Invoke <code>splunk cmd btprobe</code> pointing to <code>/opt/splunkforwarder/var/lib/splunk/fishbucket/db</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Command:</strong><br/>
<pre><code>/opt/splunkforwarder/bin/splunk cmd btprobe \
  -d /opt/splunkforwarder/var/lib/splunk/fishbucket/db \
  --file /var/log/audit/pci_vault.log</code></pre>
<strong>Flag 5:</strong> <code>THM{BTPROBE_TAILREADER_SEEKPTR_INTERROGATED}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+300 XP`
- **Key Takeaway:** You have mastered live production queue bottleneck isolation, defeated the 1970 timestamp drift, healed fractured stack traces, and rescued forwarder TailReader stalls!
