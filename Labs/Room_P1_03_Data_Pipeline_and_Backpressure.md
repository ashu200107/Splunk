# 🎮 Room P1-03: The 4-Stage Pipeline Backpressure Simulator

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: Pipeline & Backpressure          ⭐ DIFFICULTY: Medium        │
│ 🎯 TOPIC: Input, Parsing, Indexing, Search💎 REWARD: 200 XP            │
│ ⏱️ ESTIMATED TIME: 30 Mins                🛡️ CATEGORY: Data Flow       │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Emergency Incident — Pipeline Gridlock!  
> At 14:20 PM, forwarder queues across 400 web servers went into critical backpressure lock.  
> Memory usage on forwarders is climbing, events are delayed by hours, and logs are backing up to edge disks.  
> Your mission is to simulate and trace the **4-Stage Splunk Ingestion Pipeline**, inspect where event boundaries and timestamps are created, understand how queue backpressure propagates upstream, and activate **`useACK=true`** to guarantee zero data loss.

---

## 🗺️ Mission Architecture & Ingestion Stages

![4-Stage Pipeline 3D](../assets/02_data_pipeline_4phases_3d.jpg)
*Figure 3.1: The 4 Ingestion Pipeline Stages (Input ➔ Parsing ➔ Indexing ➔ Search)*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ ⚙️ PIPELINE STAGE BREAKDOWN                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ 1. INPUT PHASE:    Reads raw byte stream, slices into 64KB blocks (inputs.conf)│
│ 2. PARSING PHASE:  Event breaking, timestamp extraction, regex (props.conf)   │
│ 3. INDEXING PHASE: Writes compressed rawjournal and TSIDX files to disk      │
│ 4. SEARCH PHASE:   Decompresses raw data and extracts search-time fields      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Input Phase & The Fishbucket Tracking Mechanism (50 XP)

![Phase 1 Input Crystal 3D](../assets/14_pipeline_phase1_input_3d.jpg)
*Figure 3.2: Input Phase (64KB Slicing & The Fishbucket)*

### 📖 Technical Recon
When Splunk monitors a file on disk (e.g. `/var/log/syslog`), it doesn't just read it once. It records the SHA-1 hash of the first 256 bytes and the file's current seek pointer in a specialized internal database called the **Fishbucket** (`$SPLUNK_HOME/var/lib/splunk/fishbucket`).

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
If an administrator modifies a monitored log file or replaces it with new data having the same filename, which CLI command can be used to reset the file's tracking pointer in the fishbucket so Splunk re-indexes it?  
*(Answer Format: `splunk btprobe -* *****`)*

<details>
<summary>💡 Need a Hint?</summary>
The binary is `btprobe` (b-tree probe) and the flag is `-d` (delete).
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Command:</b> <code>splunk btprobe -d &lt;fishbucket_path&gt; --file &lt;target_file&gt;</code><br/>
Or restart with <code>splunk clean eventdata -index &lt;index_name&gt;</code> in a test lab.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{FISHBUCKET_BTPROBE_POINTER_RESET}
```

---

## 🎯 TASK 2: Parsing Phase — Event Breaking & Timestamps (50 XP)

![Phase 2 Parsing Crystal 3D](../assets/15_pipeline_phase2_parsing_3d.jpg)
*Figure 3.3: Parsing Phase (Laser Event Breaking & Epoch Timestamp Extraction)*

### 📖 Technical Recon
In the Parsing Phase, Splunk turns continuous unformatted character streams into distinct events.  
Key parameters in `props.conf`:
- `SHOULD_LINEMERGE = false` (Industry standard: use `LINE_BREAKER` for 10x regex speed)
- `LINE_BREAKER = ([\r\n]+)` (Regex matching line breaks)
- `TIME_PREFIX = ^` (Regex pattern preceding the timestamp)
- `MAX_TIMESTAMP_LOOKAHEAD = 32` (Tells Splunk how far into the event to look for the time)

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
On which Splunk component does the Parsing Phase occur when using **Universal Forwarders** to send data directly to an **Indexer Cluster**?  
- [A] On the Universal Forwarder.
- [B] On the Indexer.
- [C] On the Search Head.
- [D] On the Deployment Server.

<details>
<summary>💡 Need a Hint?</summary>
Remember: UF does NOT parse! So where must the stream be parsed?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] On the Indexer. Because UFs cannot parse, the unparsed stream arrives at the Indexer, which executes the Parsing Phase before indexing.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{INDEXER_EXECUTES_PARSING_FOR_UF_STREAM}
```

---

## 🎯 TASK 3: Queue Backpressure Propagation (50 XP)

### 📖 Scenario Context
Data moves through memory queues:
$$\text{Input Queue} \longrightarrow \text{Parsing Queue} \longrightarrow \text{Typing Queue} \longrightarrow \text{Index Queue} \longrightarrow \text{Disk (Storage)}$$

When the disk is too slow:
1. `indexQueue` fills to 100%.
2. `typingQueue` cannot push into `indexQueue` $\rightarrow$ fills to 100%.
3. `parsingQueue` cannot push into `typingQueue` $\rightarrow$ fills to 100%.
4. `inputQueue` fills to 100%.
5. The TCP socket to the Forwarder is **throttled/closed** (Zero Window).
6. The Forwarder pauses reading files from disk!

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
When downstream queues fill to 100%, how does Splunk prevent dropping events in memory?  
*(Choose the correct mechanism)*
- [A] It drops 50% of the events silently.
- [B] It applies upstream backpressure, pausing the input reading stage until downstream queues clear.
- [C] It deletes old search history.
- [D] It reboots the server automatically.

<details>
<summary>💡 Need a Hint?</summary>
Think about hydraulic pressure in plumbing: when a valve closes, pressure backs up upstream.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] Upstream backpressure. Splunk stops pulling bytes from the OS file handle or network socket until memory buffers drain.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{UPSTREAM_BACKPRESSURE_PREVENTS_LOSS}
```

---

## 🎯 TASK 4: Indexer Acknowledgement (`useACK=true`) (50 XP)

### 📖 Technical Recon
By default, a forwarder sends TCP packets and assumes the Indexer received them. If a network switch fails mid-flight or an Indexer crashes before writing to disk, **data in-flight is lost**!  
To guarantee delivery:
In `outputs.conf`:
```ini
[tcpout]
defaultGroup = primary_indexers

[tcpout:primary_indexers]
server = 192.168.1.100:9997
useACK = true
```

With `useACK = true`, the forwarder holds events in its memory buffer until the Indexer sends back an explicit cryptographic acknowledgment that the data was safely committed to disk!

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What key-value setting in `outputs.conf` enables Indexer Acknowledgement to protect in-flight data against network crashes?  
*(Answer Format: `****** = ****`)*

<details>
<summary>💡 Need a Hint?</summary>
ACK stands for Acknowledgement. The value is a boolean true.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Setting:</b> <code>useACK = true</code><br/>
Declared under the <code>[tcpout]</code> or target stanza in <code>outputs.conf</code>.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{USE_ACK_TRUE_IN_FLIGHT_PROTECTION}
```

---

## 🏆 Room P1-03 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM P1-03 COMPLETE                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 200 / 200 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Fishbucket btprobe Tracking, Parsing Allocation,    │
│   Queue Backpressure Chain, outputs.conf useACK=true Safeguard         │
│                                                                        │
│ ➡️ NEXT ROOM: Room P1-04 — Directory Structure & Btool Detective       │
└────────────────────────────────────────────────────────────────────────┘
```
