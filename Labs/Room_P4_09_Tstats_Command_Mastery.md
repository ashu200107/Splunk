# 🎮 Room P4-09: The Sub-Second Tstats Gauntlet

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-09: The Sub-Second Tstats Gauntlet     ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: tstats Mastery, summariesonly & CIM DMA 💎 REWARD: 300 XP     │
│ ⏱️ ESTIMATED TIME: 40 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Enterprise Security Alert Lag Emergency!**  
> Splunk Enterprise Security (ES) correlation searches in the Security Operations Center are lagging by 35 minutes!  
> The root cause: An analyst created a custom credential-stuffing detection query that runs every 5 minutes across 50,000,000 raw events:  
> ```spl
> index=auth sourcetype=okta:sso action=failure
> | stats count by user, src
> | where count > 50
> ```
> This search executes full schema-on-read extractions and scans gigabytes of `journal.zst` files, taking **190 seconds** per run!  
> 
> As the Principal Splunk Architect, you must refactor this query to query the accelerated **`Authentication` CIM Data Model** using `tstats summariesonly=t`, strip the object prefixes, and drop the execution time to under **0.5 seconds**!

---

## 🗺️ Mission Architecture & Target Environment

![tstats Engine 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_tstats_command_tsidx_mastery_3d_1792231643284.jpg)
*Figure P4-9.1: Accelerated TSIDX Querying Engine & Data Model Architecture.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Indexer Cluster:      idx-01..03 (Accelerated TSIDX Card Catalogs)         │
│ • CIM Data Model:       Authentication.Authentication (Accelerated 100%)     │
│ • SLA Benchmark:        Execution duration < 0.500 seconds                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Index-Based `tstats` Baseline Verification (70 XP)

### 📖 Incident Details
Verify the overall volume of authentication logs across the cluster using index-level `tstats` without touching raw events:

```spl
| tstats count FROM index=auth BY sourcetype
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What command precedes the pipe in an index-based `tstats` query to generate events directly from `.tsidx` files without scanning indexes?  
*(Answer Format: `| ******`)*

<details>
<summary>💡 Need a Hint?</summary>
| tstats
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>| tstats</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{TSTATS_GENERATING_COMMAND_DIRECT_TSIDX}
```

---

## 🎯 TASK 2: Refactoring into Data Model `tstats` (75 XP)

### 📖 Incident Details
Refactor the slow brute-force query to target the accelerated CIM `Authentication` data model with the `summariesonly=t` flag:

```spl
| tstats summariesonly=t count
  FROM datamodel=Authentication.Authentication
  WHERE Authentication.action="failure"
  BY Authentication.user, Authentication.src
| where count > 50
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What exact parameter must be set in `tstats` to restrict the search exclusively to pre-computed `.tsidx` summaries, preventing slow fallback scans of un-summarized raw buckets?  
*(Answer Format: `*****************=*`)*

<details>
<summary>💡 Need a Hint?</summary>
summariesonly=t (or true)
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>summariesonly=t</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{SUMMARIESONLY_TRUE_PURE_LIGHT_SPEED}
```

---

## 🎯 TASK 3: Normalizing Data Model Object Notation (75 XP)

### 📖 Incident Details
Because `tstats` outputs fields prefixed with the data model object name (e.g., `Authentication.user`), normalize all fields using `rename`:

```spl
| tstats summariesonly=t count
  FROM datamodel=Authentication.Authentication
  WHERE Authentication.action="failure"
  BY Authentication.user, Authentication.src
| rename Authentication.* AS *
| where count > 50
| table user, src, count
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What wildcard SPL command strips the `Authentication.` prefix from all output fields in a single line?  
*(Answer Format: `| rename **************.* AS *`)*

<details>
<summary>💡 Need a Hint?</summary>
| rename Authentication.* AS *
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>| rename Authentication.* AS *</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{RENAME_DATA_MODEL_WILDCARD_CLEANUP}
```

---

## 🎯 TASK 4: Sub-Second Execution Verification (80 XP)

### 📖 Incident Details
Open the Search Job Inspector for your refactored query. Verify the execution duration.  
The search now completes in **0.32 seconds** across 50 million events!

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Why does `tstats` execute in sub-seconds compared to `search`?  
*(Answer Format: It queries the inverted index ******* directly and skips *********** and search-time field extractions)*

<details>
<summary>💡 Need a Hint?</summary>
tsidx, journal.zst
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>It queries the inverted index tsidx directly and skips journal.zst and search-time field extractions</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{SUB_SECOND_TSIDX_MASTERY_ACCOMPLISHED}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-09 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{TSTATS_GENERATING_COMMAND_DIRECT_TSIDX}               ║
║ [X] FLAG 2.1: FLAG{SUMMARIESONLY_TRUE_PURE_LIGHT_SPEED}                  ║
║ [X] FLAG 3.1: FLAG{RENAME_DATA_MODEL_WILDCARD_CLEANUP}                   ║
║ [X] FLAG 4.1: FLAG{SUB_SECOND_TSIDX_MASTERY_ACCOMPLISHED}                ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You eliminated alert lag in the SOC, mastered `tstats` against CIM data models, and engineered sub-second analytics.  
> **Total XP Awarded:** `+300 XP`!  
> Next Mission: **[Chapter 10: Search Job Inspector & Performance Diagnostics](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_10_Job_Inspector_Diagnostics.md)**!
