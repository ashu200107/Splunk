# 🎮 Room P4-05: The Transaction Memory Meltdown

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-05: The Transaction Memory Meltdown    ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: stats vs transaction, join caps & union  💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 35 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Triage of Search Head OOM Panic!**  
> An executive cyber-risk dashboard is running this catastrophic query every 5 minutes:
> ```spl
> index=web sourcetype=access:cart
> | join user [search index=auth sourcetype=okta:sso | fields user, mfa_status, department]
> | transaction user
> | where duration > 1800
> ```
> This search is wreaking havoc in production:
> 1. The `join` subsearch truncates silently at 50,000 users, missing 70% of enterprise employees.
> 2. The `transaction user` runs completely unconstrained without `maxspan` or `maxpause`, causing Search Head RAM to spike to 95%.
> 3. The entire search takes **185 seconds** and frequently times out.
>
> You are the Principal Splunk Architect. You must diagnose the memory choke points, replace `join` and `transaction` with high-speed multi-index `stats`, and capture all 4 capstone flags!

---

## 🗺️ Mission Architecture & Target Environment

![Transaction vs Stats 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_transaction_vs_stats_correlation_3d_1792230566594.jpg)
*Figure P4-5.1: Multi-Dataset Correlation Architecture & Memory Profiling.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Indexer Cluster:      idx-01..03 (S2S 9997, Distributed Map Phase)         │
│ • Search Head:          shc-captain-01 (Reduce Phase & Join Memory Buffer)   │
│ • Target Datasets:      index=web sourcetype=access:cart                     │
│                         index=auth sourcetype=okta:sso                       │
│ • Common Join Key:      user (Username)                                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Exposing the 50K Silent Truncation in `join` (60 XP)

### 📖 Incident Details
Inspect the Search Job Inspector on the original `join` query.  
You notice that `subsearch_maxout = 50000` is reached, and 124,000 employees are silently excluded from the join table!

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the default maximum number of result rows that a subsearch in a `join` command can emit before Splunk silently truncates results?  
*(Answer Format: `**,***`)*

<details>
<summary>💡 Need a Hint?</summary>
50,000 rows
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>50,000</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{JOIN_50K_SILENT_TRUNCATION_EXPOSED}
```

---

## 🎯 TASK 2: Refactoring with the "Stats as Transaction" Pattern (65 XP)

### 📖 Incident Details
Refactor the checkout session calculation using distributed Map-Reduce `stats` instead of centralized `transaction`. Calculate the duration between the earliest and latest event, total event count, and actions taken:

```spl
(index=web sourcetype=access:cart) OR (index=auth sourcetype=okta:sso)
| stats earliest(_time) AS session_start,
        latest(_time) AS session_end,
        count AS eventcount,
        values(action) AS actions_taken,
        values(mfa_status) AS mfa_status,
        values(department) AS department
        BY user
| eval duration = session_end - session_start
| where duration > 1800
| table user, session_start, duration, eventcount, mfa_status, department
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
In the "Stats as Transaction" pattern, what mathematical formula calculates the session duration in seconds from the aggregated earliest and latest timestamps?  
*(Answer Format: `eval duration = *********** - *************`)*

<details>
<summary>💡 Need a Hint?</summary>
session_end - session_start
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>eval duration = session_end - session_start</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{STATS_AS_TRANSACTION_ZERO_RAM_BLOWUP}
```

---

## 🎯 TASK 3: Enforcing Memory Eviction on `transaction` (60 XP)

### 📖 Incident Details
In scenarios where raw event text (`_raw`) must be preserved for forensic chain-of-custody exports, `transaction` must be constrained with explicit sliding-window boundaries:

```spl
index=auth sourcetype=okta:sso
| transaction user maxspan=1h maxpause=10m
| table _time, user, duration, eventcount, _raw
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which parameter in the `transaction` command closes an active transaction if the quiet period between two consecutive events exceeds a specified time limit?  
*(Answer Format: `********=<time>`)*

<details>
<summary>💡 Need a Hint?</summary>
maxpause
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>maxpause=&lt;time&gt;</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{TRANSACTION_MAXPAUSE_EVICTION_BOUNDS}
```

---

## 🎯 TASK 4: Scalable Multi-Dataset Union (65 XP)

### 📖 Incident Details
Merge separate datasets from disparate security tools without hitting subsearch memory boundaries using `union`:

```spl
| union
    [ search index=pci_compliance status=failure ]
    [ search index=cloud_audit errorCode=AccessDenied ]
| stats count BY host, user
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Which modern SPL command merges multiple datasets and saved searches together in parallel without being subjected to subsearch 50,000-event limits?  
*(Answer Format: `*****`)*

<details>
<summary>💡 Need a Hint?</summary>
union
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>union</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{UNION_MODERN_PARALLEL_DATASET_MERGE}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-05 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{JOIN_50K_SILENT_TRUNCATION_EXPOSED}                   ║
║ [X] FLAG 2.1: FLAG{STATS_AS_TRANSACTION_ZERO_RAM_BLOWUP}                 ║
║ [X] FLAG 3.1: FLAG{TRANSACTION_MAXPAUSE_EVICTION_BOUNDS}                 ║
║ [X] FLAG 4.1: FLAG{UNION_MODERN_PARALLEL_DATASET_MERGE}                  ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You eliminated memory-intensive join bottlenecks, optimized multi-index event correlation, and stabilized the Search Head cluster.  
> **Total XP Awarded:** `+250 XP`!  
> Next Mission: **[Chapter 06: Subsearches Architecture & Optimization](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_06_Subsearches_Architecture_and_Limits.md)**!
