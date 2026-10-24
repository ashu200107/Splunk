# 🎮 Room P4-08: The Summary Index Accelerator

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-08: The Summary Index Accelerator      ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: Report Acceleration, Summary Index & DMA 💎 REWARD: 300 XP    │
│ ⏱️ ESTIMATED TIME: 40 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Executive Boardroom Dashboard Crisis!**  
> Every Monday morning, the C-suite opens the **1-Year Global Identity & Access Audit Dashboard**.  
> The dashboard scans over **800,000,000 raw events** across the primary authentication index (`index=auth`), causing:
> 1. Dashboard load times exceeding **240 seconds** (frequently failing with browser timeout errors).
> 2. Indexer CPU pinned at 100%, causing ingestion queues to back up.
> 3. Disqualification from Report Acceleration because the previous admin inserted an unneeded `| sort - _time` before the `stats` command!
>
> You are the Principal Splunk Architect. You must audit the query, eliminate the pipeline anti-pattern, build an automated summary indexing pipeline using `sitimechart` and `collect`, and achieve a **sub-second dashboard load time**!

---

## 🗺️ Mission Architecture & Target Environment

![Search Acceleration 3D Engine](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_acceleration_techniques_3d_1792231407213.jpg)
*Figure P4-8.1: Enterprise Search Acceleration & Summary Data Engine.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Indexer Tier:         idx-01..03 (TSIDX Summary Builders)                  │
│ • Raw Source Index:     index=auth sourcetype=okta:sso (800M events / year)  │
│ • Dedicated Summary:    index=summary_auth (Lightweight metric rolls)        │
│ • SLA Requirement:      Query execution time < 1.0 second                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Auditing Report Acceleration Pipeline Eligibility (70 XP)

### 📖 Incident Details
Inspect the broken query powering the executive dashboard:
```spl
index=auth sourcetype=okta:sso
| sort - _time
| stats count by user, action
```
The query is currently disqualified from Report Acceleration.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
Which non-streaming command placed before `stats` in the original query invalidated its eligibility for automatic Report Acceleration?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
sort
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>sort</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{REPORT_ACCELERATION_SORT_DISQUALIFICATION_FIXED}
```

---

## 🎯 TASK 2: Building the Summary Ingestion Pipeline with `collect` (75 XP)

### 📖 Incident Details
Create a scheduled search that runs every hour to pre-calculate authentication failures and ingest them into a dedicated summary index (`index=summary_auth`):

```spl
index=auth sourcetype=okta:sso action=failure
| sitimechart span=1h count, dc(user) AS unique_users, sum(risk_score) AS total_risk
| collect index=summary_auth sourcetype=auth:hourly_rollup marker="environment=prod"
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which summary-enabled transforming command must be used instead of standard `timechart` to preserve exact statistical state when writing to a summary index?  
*(Answer Format: `***********`)*

<details>
<summary>💡 Need a Hint?</summary>
sitimechart
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>sitimechart</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{SITIMECHART_STATE_PRESERVATION_SECURED}
```

---

## 🎯 TASK 3: Verifying TSIDX Summary File Storage (75 XP)

### 📖 Incident Details
On the Indexer cluster (`idx-01`), inspect the physical bucket directory for `index=auth` to verify where Report Acceleration `.tsidx` summary files are written.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Inside which physical directory on an Indexer are Report Acceleration summary files stored?  
*(Answer Format: Inside the individual index ****** directories alongside journal.zst)*

<details>
<summary>💡 Need a Hint?</summary>
bucket
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Inside the individual index bucket directories alongside journal.zst</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{TSIDX_BUCKET_LOCALITY_REPORT_ACCELERATION}
```

---

## 🎯 TASK 4: Sub-Second Dashboard Refactoring (80 XP)

### 📖 Incident Details
Rewrite the C-level dashboard panel query to target the pre-calculated summary index:

```spl
index=summary_auth sourcetype=auth:hourly_rollup
| timechart span=1d sum(count) AS total_failures, sum(sum_risk) AS total_risk_score
```
Execution benchmark: Drops from **240 seconds** down to **0.4 seconds**!

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
By targeting the pre-aggregated summary index, what was the approximate percentage reduction in disk data scanned by the Search Head?  
*(Answer Format: Greater than **.**%)*

<details>
<summary>💡 Need a Hint?</summary>
99.9%
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Greater than 99.9%</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{SUB_SECOND_SUMMARY_INDEX_BOARDROOM_HERO}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-08 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{REPORT_ACCELERATION_SORT_DISQUALIFICATION_FIXED}      ║
║ [X] FLAG 2.1: FLAG{SITIMECHART_STATE_PRESERVATION_SECURED}              ║
║ [X] FLAG 3.1: FLAG{TSIDX_BUCKET_LOCALITY_REPORT_ACCELERATION}             ║
║ [X] FLAG 4.1: FLAG{SUB_SECOND_SUMMARY_INDEX_BOARDROOM_HERO}             ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You salvaged the C-suite dashboard, engineered an enterprise summary index pipeline, and mastered TSIDX acceleration mechanics.  
> **Total XP Awarded:** `+300 XP`!  
> Next Mission: **[Chapter 09: `tstats` Command Mastery (Querying Accelerated TSIDX Directly)](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_09_tstats_Command_Mastery.md)**!
