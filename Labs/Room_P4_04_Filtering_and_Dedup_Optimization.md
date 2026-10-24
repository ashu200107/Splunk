# 🎮 Room P4-04: The LIS Index Filter Optimization

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-04: The LIS Index Filter Optimization  ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: where vs search, dedup, fields & sort    💎 REWARD: 200 XP     │
│ ⏱️ ESTIMATED TIME: 30 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Triage of Runaway Network Triage Search!**  
> A critical firewall audit report is causing Search Head CPU thrashing and failing with timeout errors.  
> The original query looks like this:
> ```spl
> index=network sourcetype=cisco:asa
> | search src=dest
> | sort - _time
> | dedup src
> | tail 20
> | table _time, src, dest, action
> ```
> This search has four severe performance anti-patterns:
> 1. `search src=dest` searches for the literal string `"dest"` rather than comparing fields.
> 2. `sort - _time` runs across 15 million events before filtering.
> 3. `tail 20` forces Splunk to buffer every event into memory before emitting the last 20 rows.
> 4. Unused fields are streamed across the network because `fields +` was omitted.
>
> Your mission is to reconstruct this query, optimize the filtering pipeline, and capture all 4 operational flags!

---

## 🗺️ Mission Architecture & Target Environment

![Filtering & Sorting 3D Engine](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_filtering_sorting_dedup_pipeline_3d_1792230333379.jpg)
*Figure P4-4.1: Pipeline Filtering & Structuring Architecture.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET DATASET SCHEMA                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Index / Sourcetype:   index=network sourcetype=cisco:asa                   │
│ • Sample Fields:        src (Source IP), dest (Destination IP)               │
│                         bytes (Transfer bytes), action (permitted, denied)   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Field-to-Field Comparison with `where` (50 XP)

### 📖 Incident Details
To detect network hairpinning or spoofed traffic, you must identify events where the source IP address is identical to the destination IP address:

```spl
index=network sourcetype=cisco:asa
| where src == dest
| stats count BY src, action
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
Which command and equality operator must be used in Splunk to evaluate whether two distinct fields contain identical values?  
*(Answer Format: `***** field1 ** field2`)*

<details>
<summary>💡 Need a Hint?</summary>
where field1 == field2
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>where field1 == field2</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{WHERE_DOUBLE_EQUALS_FIELD_COMPARISON_VICTORY}
```

---

## 🎯 TASK 2: Memory-Efficient Deduplication with `dedup` (50 XP)

### 📖 Incident Details
You must retain only the single highest-bandwidth event for each source IP (`src`):

```spl
index=network sourcetype=cisco:asa
| dedup src sortby - bytes
| table src, dest, bytes, action
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What argument in the `dedup` command specifies that deduplication should keep the event with the highest value of a secondary field?  
*(Answer Format: `****** - <field>`)*

<details>
<summary>💡 Need a Hint?</summary>
sortby - field
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>sortby - &lt;field&gt;</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{DEDUP_SORTBY_CRITERIA_ENFORCED}
```

---

## 🎯 TASK 3: Indexer Pushdown Field Pruning with `fields +` (50 XP)

### 📖 Incident Details
Cisco ASA firewall logs contain over 40 distinct metadata fields. To reduce the network bandwidth transferred from the Indexers to the Search Head across Port 8089, explicitly retain only the fields needed for the report early in the pipeline:

```spl
index=network sourcetype=cisco:asa
| fields + src, dest, bytes, action
| where src == dest
| dedup src sortby - bytes
| table _time, src, dest, bytes, action
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which command is a Distributable Streaming Command that can be pushed to Indexers to strip unwanted fields from network transmission without stripping the `_raw` payload prematurely?  
*(Answer Format: `****** +`)*

<details>
<summary>💡 Need a Hint?</summary>
fields +
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>fields +</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{FIELDS_PLUS_STREAMING_INDEXER_PUSHDOWN}
```

---

## 🎯 TASK 4: Boundary Limiting Optimization (50 XP)

### 📖 Incident Details
The original search used `| tail 20`, forcing Splunk to scan the entire 15 million events before emitting the last 20 rows.  
Optimize this by reversing the sort order and using `head`:

```spl
index=network sourcetype=cisco:asa
| fields + src, dest, bytes, action
| where src == dest
| sort + _time
| head 20
| table _time, src, dest, bytes, action
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Why does replacing `| tail N` with `| sort + _time | head N` dramatically accelerate search completion?  
*(Answer Format: `head` terminates the search *********** once the limit is satisfied while `tail` must scan *** percent of events)*

<details>
<summary>💡 Need a Hint?</summary>
head terminates immediately; tail must scan 100 percent.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>head terminates the search immediately once the limit is satisfied while tail must scan 100 percent of events</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{HEAD_VS_TAIL_EARLY_TERMINATION_SUPERIORITY}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-04 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{WHERE_DOUBLE_EQUALS_FIELD_COMPARISON_VICTORY}         ║
║ [X] FLAG 2.1: FLAG{DEDUP_SORTBY_CRITERIA_ENFORCED}                       ║
║ [X] FLAG 3.1: FLAG{FIELDS_PLUS_STREAMING_INDEXER_PUSHDOWN}               ║
║ [X] FLAG 4.1: FLAG{HEAD_VS_TAIL_EARLY_TERMINATION_SUPERIORITY}           ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You eliminated four catastrophic search bottlenecks and optimized pipeline throughput by 98%.  
> **Total XP Awarded:** `+200 XP`!  
> Next Mission: **[Chapter 05: Correlation & Multi-Dataset Searching (`transaction` vs `stats`, `join`, `append`, `union`)](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_05_Correlation_and_Multi_Dataset_Searching.md)**!
