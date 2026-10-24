# 🎮 Room P4-10: Job Inspector Forensics

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-10: Job Inspector Forensics            ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: Search Profiling, LIS Ratio & Telemetry  💎 REWARD: 300 XP     │
│ ⏱️ ESTIMATED TIME: 40 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Triage of Degraded Enterprise Search Engine!**  
> An executive cyber-risk dashboard panel has slowed to a crawl, taking over **140 seconds** to complete:  
> ```spl
> index=* *fail*
> | eval is_login_failure = if(like(_raw, "%failed%"), 1, 0)
> | where is_login_failure == 1
> | stats count by host, user
> ```
> Users across all departments are complaining of search queue delays.  
> 
> As the Principal Splunk Architect, you must:
> 1. Open the Search Job Inspector and analyze the pathological Scan-to-Event (LIS) ratio.
> 2. Diagnose the root cause of high execution times in `command.search.index` and `command.search.kv`.
> 3. Detect the straggler indexer peer in `peers.csv`.
> 4. Refactor the search into an optimized, sub-second query and capture all 4 flags!

---

## 🗺️ Mission Architecture & Target Environment

![Job Inspector 3D Pit Wall](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_search_job_inspector_telemetry_3d_1792231850480.jpg)
*Figure P4-10.1: Search Job Inspector Diagnostic Telemetry Console.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          shc-captain-01 (192.168.1.10:8000)                   │
│ • Dispatch Path:        /opt/splunk/var/run/splunk/dispatch/1792231900.842/  │
│ • Remote Search Peers:  idx-01, idx-02, idx-03                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Analyzing the Pathological LIS Ratio (70 XP)

### 📖 Incident Details
Inspect `info.csv` in the search dispatch directory:
```bash
cat /opt/splunk/var/run/splunk/dispatch/1792231900.842/info.csv
```
Telemetry reveals:
```csv
scanCount,eventCount,resultCount,runDuration
42500000,50000,120,142.84
```
Calculate the efficiency ratio:
$$\text{Ratio} = \frac{42,500,000}{50,000} = 850 : 1$$

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What does an astronomical Scan-to-Event ratio of $850:1$ indicate about the search design?  
*(Answer Format: Splunk read millions of events from **** only to discard *** percent of them due to unconstrained wildcards or late filtering)*

<details>
<summary>💡 Need a Hint?</summary>
disk, 99
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Splunk read millions of events from disk only to discard 99 percent of them due to unconstrained wildcards or late filtering</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{LIS_RATIO_850_TO_1_DISK_WASTE_EXPOSED}
```

---

## 🎯 TASK 2: Diagnosing `command.search.kv` Overhead (75 XP)

### 📖 Incident Details
Inspect the Execution Costs breakdown in the Job Inspector:
```text
Execution Costs:
├── command.search.index: 84.2s (58.9%)
├── command.search.kv:    42.1s (29.5%)
└── dispatch.evaluate:     1.2s ( 0.8%)
```
The query evaluated `like(_raw, "%failed%")` and extracted 120 unneeded fields in Verbose Mode!

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which execution cost component represents the time spent running regular expressions and extracting Schema-on-Read fields from raw event text?  
*(Answer Format: `command.search.**`)*

<details>
<summary>💡 Need a Hint?</summary>
command.search.kv
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>command.search.kv</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{COMMAND_SEARCH_KV_SCHEMA_ON_READ_BOTTLENECK}
```

---

## 🎯 TASK 3: Identifying the Straggler Indexer Peer (75 XP)

### 📖 Incident Details
Inspect `peers.csv` inside the dispatch folder:
```csv
peer,status,total_time,processed_events
idx-01.corp,Complete,4.12,14166666
idx-02.corp,Complete,4.28,14166666
idx-03.corp,Complete,84.20,14166668
```
Indexer `idx-03` took 84 seconds while peers completed in 4 seconds due to a degraded spinning-disk storage volume!

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which file in the search dispatch directory lists each remote search peer along with its individual execution duration and event processing count?  
*(Answer Format: `*****.***`)*

<details>
<summary>💡 Need a Hint?</summary>
peers.csv
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>peers.csv</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{PEERS_CSV_STRAGGLER_NODE_DISCOVERED}
```

---

## 🎯 TASK 4: Achieving a $1.0 : 1$ Ratio via SPL Refactoring (80 XP)

### 📖 Incident Details
Refactor the catastrophic query using the 8 Golden Rules:
1. Target the specific index and sourcetype (`index=auth sourcetype=okta:sso`).
2. Replace `*fail*` and `like()` with exact indexed term `action="failure"`.
3. Enforce **Fast Mode**:

```spl
index=auth sourcetype=okta:sso action=failure
| stats count by host, user
```
New Telemetry in Job Inspector:
```csv
scanCount,eventCount,resultCount,runDuration
50000,50000,120,0.48
```
$$\text{Ratio} = \frac{50,000}{50,000} = 1.0 : 1 \quad (\text{Perfect Performance!})$$

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the ideal Scan-to-Event (LIS) ratio that proves an indexer read only the exact events that satisfied the query?  
*(Answer Format: `*.* : *`)*

<details>
<summary>💡 Need a Hint?</summary>
1.0 : 1
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>1.0 : 1</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{ONE_TO_ONE_PERFECT_LIS_EFFICIENCY_VICTORY}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-10 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{LIS_RATIO_850_TO_1_DISK_WASTE_EXPOSED}                ║
║ [X] FLAG 2.1: FLAG{COMMAND_SEARCH_KV_SCHEMA_ON_READ_BOTTLENECK}          ║
║ [X] FLAG 3.1: FLAG{PEERS_CSV_STRAGGLER_NODE_DISCOVERED}                  ║
║ [X] FLAG 4.1: FLAG{ONE_TO_ONE_PERFECT_LIS_EFFICIENCY_VICTORY}           ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You mastered Search Job Inspector telemetry, eliminated disk-thrashing anti-patterns, and isolated cluster stragglers.  
> **Total XP Awarded:** `+300 XP`!  
> Next Mission: **[Chapter 11: Phase 4 Capstone Lab & Master Milestone Exam](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_11_Phase_4_Capstone_Lab_and_Exam.md)**!
