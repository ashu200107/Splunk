# 🎮 Room P4-01: The Search Dispatch Heist

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-01: The Search Dispatch Heist          ⭐ DIFFICULTY: Easy-Med│
│ 🎯 TOPIC: Search Modes & Dispatch Forensics       💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 30 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Search Head Out of Inodes & Disk Meltdown!**  
> At 11:30 AM, alerts trigger in the NOC: the primary Search Head (`shc-captain-01`) is experiencing 98% disk utilization on `/opt/splunk/var/run/splunk/dispatch`.  
> Other users report that their scheduled executive reports and SOC alert searches are queuing and failing to run.  
> Investigation reveals that a junior data scientist launched an unconstrained search in **Verbose Mode**:  
> `index=* *error* | eval temp=1 | sort - _time` spanning the last 3 years!  
> As the on-duty Splunk Administrator, you must inspect the dispatch artifacts, locate the runaway Job ID (`sid`), terminate the job, and refactor the search for **Fast Mode** enterprise execution!

---

## 🗺️ Mission Architecture & Target Environment

![Search Dispatch & Engine 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_search_modes_and_dispatch_pipeline_3d_1792125781454.jpg)
*Figure P4-1.1: Target Search Head Dispatch Architecture and Execution Engine.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          shc-captain-01 (192.168.1.10:8000, REST Port 8089)   │
│ • Dispatch Path:        /opt/splunk/var/run/splunk/dispatch/                 │
│ • Runaway SID:          1792125800.142                                       │
│ • Indexer Peers:        idx-01, idx-02 (S2S 9997, Management 8089)           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Dispatch Directory Forensics & Job Inspection (80 XP)

### 📖 Incident Details
Log in to the Search Head via SSH and inspect the contents of the active search dispatch directory:
```bash
cd /opt/splunk/var/run/splunk/dispatch/1792125800.142
ls -lah
```

You observe:
```text
-rw------- 1 splunk splunk 1.2M Oct 16 11:32 audit.log
-rw------- 1 splunk splunk 4.2K Oct 16 11:34 info.csv
-rw------- 1 splunk splunk   18 Oct 16 11:30 status.csv
drwx------ 2 splunk splunk 4.0K Oct 16 11:30 events
-rw------- 1 splunk splunk  74G Oct 16 11:35 events/0.events.gz
```

Because the user initiated the query in **Verbose Mode**, Splunk is extracting every field and writing all 74 GB of uncompressed event payloads into `events/0.events.gz`!

Inspect `info.csv` to evaluate the search performance metrics:
```bash
head -n 2 info.csv
```
The file reveals:
```csv
scanCount,eventCount,resultCount,runDuration,diskUsage
48291040,12840192,12840192,284.19,79459201948
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the name of the file located inside every search dispatch directory that stores search job performance metrics, including `scanCount`, `eventCount`, and total execution duration?  
*(Answer Format: `****.***`)*

<details>
<summary>💡 Need a Hint?</summary>
It's a CSV file named info.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>info.csv</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{DISPATCH_INFO_CSV_FORENSICS_MASTERED}
```

---

## 🎯 TASK 2: Terminating the Runaway Job via CLI & REST API (80 XP)

### 📖 Incident Details
The runaway job is consuming all CPU cores and will crash the filesystem within 10 minutes. You must immediately abort and cancel the job.

### 🛠️ Execution Options
#### Option A: Via Splunk CLI
```bash
/opt/splunk/bin/splunk cancel search 1792125800.142
```

#### Option B: Via REST API over Port 8089
```bash
curl -k -u admin:Changeme! \
  -X POST https://127.0.0.1:8089/services/search/jobs/1792125800.142/control \
  -d action=cancel
```

Verify the search job is removed and the dispatch directory is purged:
```bash
ls /opt/splunk/var/run/splunk/dispatch/1792125800.142
# Result: No such file or directory (reaped by splunkd)
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What REST API control endpoint action parameter is sent via POST to immediately terminate and delete an active Splunk search job?  
*(Answer Format: `action=******`)*

<details>
<summary>💡 Need a Hint?</summary>
action=cancel
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>action=cancel</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{REST_API_PORT_8089_SEARCH_CANCELLED}
```

---

## 🎯 TASK 3: Refactoring for High-Speed Fast Mode Execution (90 XP)

### 📖 Incident Details
The analyst actually only needed to find the hourly error counts across the payment gateway sourcetype for the last 24 hours:

**The Original Horrible Query (300+ seconds, Verbose Mode):**
```spl
index=* *error* | eval temp=1 | sort - _time
```

**The Architect's Optimized Query (0.8 seconds, Fast Mode):**
```spl
index=payment sourcetype=payment:gateway (error OR status>=400)
| timechart span=1h count
```

### 🛠️ Why This Refactoring Succeeds:
1. **Targeted Index & Sourcetype:** Directs Indexers to specific bucket directories instead of scanning all indexes on disk (`index=*`).
2. **Eliminated Leading Wildcard:** Replaced `*error*` with exact keyword tokens `(error OR status>=400)`, allowing Indexers to leverage the `.tsidx` inverted index lexicon instantly.
3. **Replaced Non-Streaming `sort` with Transforming `timechart`:** Aggregates data in memory on Indexers in the Map phase, sending only tiny summarized bucket tallies back to the Search Head!
4. **Fast Mode:** Suppresses extraction of 150 unused fields, reducing Search Head CPU overhead by 92%.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which search mode should always be configured for automated dashboard panels and alert queries that compute statistical metrics to maximize performance and avoid writing raw event files to disk?  
*(Answer Format: **** ****)*

<details>
<summary>💡 Need a Hint?</summary>
Fast Mode
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Fast Mode</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{FAST_MODE_DASHBOARD_PERFORMANCE_UNLOCKED}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-01 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{DISPATCH_INFO_CSV_FORENSICS_MASTERED}                 ║
║ [X] FLAG 2.1: FLAG{REST_API_PORT_8089_SEARCH_CANCELLED}                 ║
║ [X] FLAG 3.1: FLAG{FAST_MODE_DASHBOARD_PERFORMANCE_UNLOCKED}             ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You saved the Search Head from disk exhaustion, mastered the search dispatch lifecycle, and optimized production SPL.  
> **Total XP Awarded:** `+250 XP`!  
> Next Mission: **[Chapter 02: Transforming Commands Architecture (`stats`, `chart`, `timechart`, `top`, `rare`)](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_02_Transforming_Commands_Architecture.md)**!
