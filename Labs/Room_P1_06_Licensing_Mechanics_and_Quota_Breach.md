# 🎮 Room P1-06: Enterprise Licensing & Quota Breach Simulation

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: Licensing & Quota Simulation      ⭐ DIFFICULTY: Medium        │
│ 🎯 TOPIC: Metering, Quota Violations & Free💎 REWARD: 200 XP            │
│ ⏱️ ESTIMATED TIME: 30 Mins                🛡️ CATEGORY: Licensing       │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** The 100 GB Midnight Burst!  
> At 23:59 PM, a developer deployed a broken script that dumped a 100 GB debugging trace into the `dev_logs` index within 30 minutes.  
> Your enterprise has a **50 GB/day** license quota.  
> The next morning, the IT Director is panicking:  
> *"Our license quota was blown by 200%! Did Splunk drop our production e-commerce logs? Are we out of compliance?!"*  
> Your mission as the enterprise administrator is to calculate how Splunk meters data, verify what counts against the license (and what is 100% free), audit the 5-warning violation threshold, and demonstrate how license pools protect critical departments.

---

## 🗺️ Mission Architecture & Licensing Rules

![Licensing Rules 3D](../assets/23_license_manager_3d.jpg)
*Figure 6.1: Central License Master Quota Pool & Slave Communication*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 💰 WHAT COUNTS VS WHAT IS 100% FREE                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ 💵 METERS AGAINST LICENSE:                                                   │
│   • Uncompressed raw bytes of incoming events at the Indexing Phase.         │
│                                                                              │
│ 🆓 100% FREE (ZERO LICENSE CONSUMPTION):                                     │
│   • Splunk Internal Indexes (_internal, _introspection, _audit, _telemetry). │
│   • Cluster Bucket Replications (RF=3 copies across Indexer Peers).          │
│   • Summary Indexing data (_summary).                                        │
│   • Search-time field extractions & lookups.                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: How Splunk Measures Data (Uncompressed Metering) (50 XP)

### 📖 Technical Recon
A common misconception is that Splunk licenses data based on compressed size on disk.  
In reality:
Splunk meters the **uncompressed size of the raw event text** as it enters the Indexing Phase.
If an event is 1,000 ASCII characters, it counts as exactly 1,000 bytes against the daily license, even if gzip compresses it to 200 bytes on disk.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
At what exact point and in what format does Splunk measure daily license volume?  
- [A] At the Forwarder before sending, using the compressed network packet size.
- [B] At the Indexer, based on the uncompressed raw bytes of the event payload.
- [C] At the Search Head, based on the number of search results returned.
- [D] Once a month, based on total disk space consumed by TSIDX files.

<details>
<summary>💡 Need a Hint?</summary>
Where is data officially committed into indexes, and is it measured before or after compression?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] At the Indexer, based on the uncompressed raw byte size of the event. Splunk measures data volume before it is written and compressed into disk buckets.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{UNCOMPRESSED_RAW_BYTE_METERING}
```

---

## 🎯 TASK 2: Free Ingestion Allowances (50 XP)

### 📖 Scenario Context
Your Indexer Cluster indexes 1 TB of application logs. Because Replication Factor is set to **RF=3**, Splunk creates 3 copies of every bucket across 3 different indexer servers (3 TB written to disk).  
A financial auditor claims you need a 3 TB license.

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Do replicated bucket copies created by an Indexer Cluster (RF=3) consume additional Splunk enterprise license quota?  
- [A] Yes, a 1 TB stream with RF=3 requires a 3 TB license.
- [B] No, replicated cluster copies are 100% exempt from license consumption.
- [C] Only if the replica is in a different datacenter.
- [D] Yes, but only 50% of the replica volume counts.

<details>
<summary>💡 Need a Hint?</summary>
Splunk charges for indexing data once. Do backup/replica copies count?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] No. Replicated bucket copies (RF=2, RF=3) and internal indexes (<code>_internal</code>, <code>_audit</code>) are 100% free from license counting.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{CLUSTER_REPLICAS_ARE_HUNDRED_PERCENT_FREE}
```

---

## 🎯 TASK 3: The 5-Warning Violation Threshold (50 XP)

### 📖 Scenario Context
Yesterday, the daily 50 GB quota was exceeded by 100 GB.  
The CISO wants to know if Splunk dropped any incoming logs during the breach.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
When an enterprise exceeds its daily license quota on a single day, what happens to incoming data streams?  
- [A] Splunk immediately terminates forwarder connections and drops incoming logs.
- [B] Splunk continues indexing 100% of incoming logs without interruption, and logs a single daily warning.
- [C] Splunk automatically deletes the oldest index.
- [D] Splunk switches to read-only mode for indexing.

<details>
<summary>💡 Need a Hint?</summary>
Remember Splunk's core architectural guarantee: data indexing NEVER stops on quota breach!
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] Continuous indexing. Splunk records a warning. A pool lock occurs ONLY if 5 warnings accumulate in a rolling 30-day window, and even then, indexing continues!
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{INDEXING_NEVER_STOPS_ON_QUOTA_BREACH}
```

---

## 🎯 TASK 4: The Rolling 30-Day Window (50 XP)

### 📖 Technical Recon
A warning expires and rolls off your record **30 days** after it was triggered.  
If you receive:
- Day 1: Warning 1
- Day 5: Warning 2
- Day 12: Warning 3
- Day 20: Warning 4
- Day 32: (Warning 1 rolls off! Active warnings = 3).
- Day 33: Warning received (Active warnings = 4).  
$\rightarrow$ Search remains active! You only lock if $\ge 5$ warnings exist concurrently within the rolling 30-day window.

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
If an enterprise license pool experiences 5 warnings in a rolling 30-day period, what functionality is disabled?  
- [A] Data indexing is halted.
- [B] Forwarders are blocked from sending data.
- [C] Historical search queries via the Web UI / REST API are disabled.
- [D] The operating system is shut down.

<details>
<summary>💡 Need a Hint?</summary>
Can analysts run SPL queries when a license violation occurs?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [C] Historical search queries are disabled. Searching produces a "License violation" banner until an emergency reset key or license extension is applied.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{SEARCH_LOCKED_INDEXING_ALIVE}
```

---

## 🏆 Room P1-06 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM P1-06 COMPLETE                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 200 / 200 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Uncompressed Metering Rule, Cluster Replicas Free,  │
│   No-Data-Loss Invariant, 5-Warning 30-Day Rolling Enforcement         │
│                                                                        │
│ ➡️ NEXT ROOM: Room P1-07 — Network Port Matrix & Firewall Defense      │
└────────────────────────────────────────────────────────────────────────┘
```
