# 🎮 Room 03: Monitoring Console — Queue Jam & Telemetry Triage

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: MC Queue Jam & Telemetry Triage   ⭐ DIFFICULTY: Medium-Hard   │
│ 🎯 TOPIC: Monitoring Console & Queues      💎 REWARD: 300 XP            │
│ ⏱️ ESTIMATED TIME: 40 Mins                 🛡️ CATEGORY: Diagnostics     │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Priority 1 Incident — Pipeline Meltdown!  
> At 11:30 AM, the NOC dashboards lit up red.  
> Users report that searches for live data are missing events from the last 45 minutes!  
> The Forwarders are showing TCP connection stalls, and the Indexer CPU utilization is low, but logs are backed up.  
> You must enter the **Monitoring Console (MC)**, verify the cluster topology in Distributed Mode, inspect pipeline queue fill percentages, pinpoint whether the bottleneck is CPU/Regex or Disk IOPS, and resolve the jam!

---

## 🗺️ Mission Architecture & Target Network

![Monitoring Console 3D Mission Control](../assets/24_monitoring_console_3d.jpg)
*Figure 3.1: 3D Mission Control Room (Indexer Bay, Heavy Forwarder Bay, Search Head Bay)*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET SPECIFICATIONS                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Monitoring Console Host: 192.168.1.10:8000 (Splunk Web UI)                 │
│ • Management REST Port:    TCP 8089 (Connecting to all Search Peers)         │
│ • Telemetry Indexes:       `_internal` and `_introspection`                  │
│ • Key Queues:              parsingQueue ➔ indexQueue ➔ disk write            │
│ • Disk IOPS Benchmark:     Minimum 1,200 IOPS per Indexer                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Switching from Standalone to Distributed Mode (75 XP)

### 📖 Scenario Context
Out of the box, the Monitoring Console only monitors itself (`Standalone` mode). In an enterprise cluster, it must be switched to **Distributed Mode** so it can query all Indexers, Search Heads, and Heavy Forwarders over **Port 8089**.

### 🛠️ Interactive Admin Mission
1. Add remote search peers to the MC:
   `Settings` ➔ `Distributed Search` ➔ `Search Peers` ➔ `New Search Peer`
   - URL: `https://192.168.1.100:8089` (Indexer 1)
   - URL: `https://192.168.1.50:8090` (Heavy Forwarder)
2. Switch MC Mode:
   `Settings` ➔ `Monitoring Console` ➔ `General Setup`
   - Toggle: `Standalone` ➔ **`Distributed`**
   - Verify server roles assigned: `indexer`, `search_head`, `heavy_forwarder`, `license_master`.
   - Click **Save**.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What network protocol and destination port does the Monitoring Console use to collect performance telemetry from remote search peers?  
*(Answer Format: `*****:****`)*

<details>
<summary>💡 Need a Hint?</summary>
Think of the Splunk Management REST API port used for administrative heartbeats.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Protocol & Port:</b> <code>HTTPS:8089</code><br/>
The MC communicates with all cluster components over the secure REST API port (8089).
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{MC_TELEMETRY_PORT_8089_HTTPS}
```

---

## 🎯 TASK 2: Queue Jam Forensic Analysis (75 XP)

### 📖 Scenario Context
In Splunk, data flows through memory queues:
$$\text{inputQueue} \longrightarrow \text{parsingQueue} \longrightarrow \text{typingQueue} \longrightarrow \text{indexQueue} \longrightarrow \text{Disk (Hot Buckets)}$$

When a downstream stage is slow, queues back up in reverse like a traffic jam on a highway!

```text
SCENARIO A:
[inputQueue: 100%] <── [parsingQueue: 100%] <── [indexQueue: 5%]
DIAGNOSIS: CPU / Regex / Event Breaking bottleneck!

SCENARIO B:
[inputQueue: 100%] <── [parsingQueue: 100%] <── [indexQueue: 100%]
DIAGNOSIS: Disk I/O / Storage Write bottleneck!
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
You inspect the Monitoring Console `Indexing > Performance > Pipeline Queues` view.  
The **`indexQueue` is pinned at 100% full**, while CPU usage is only 25%. What is the root cause of this backpressure?  
- [A] Network cable is unplugged.
- [B] The Indexer's underlying storage disk is too slow to write data (IOPS bottleneck).
- [C] Splunk Enterprise license key is expired.
- [D] Search Head is running too many subsearches.

<details>
<summary>💡 Need a Hint?</summary>
What does the indexQueue feed directly into?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] Storage disk I/O bottleneck. The indexQueue holds events waiting to be written to raw data journals and TSIDX files on disk. If IOPS is below the required 1,200 IOPS benchmark, indexQueue fills to 100% and halts upstream queues.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{INDEX_QUEUE_100_DISK_IOPS_CHOKE}
```

#### Question 2.2
In another incident, the **`indexQueue` is 0% full**, but the **`parsingQueue` is pinned at 100% full**, and CPU cores on the Heavy Forwarder are running at 99%. What is the root cause?  
*(Answer Format: `*** / ********** bottleneck`)*

<details>
<summary>💡 Need a Hint?</summary>
Think about complex regular expressions, SEDCMD, or catastrophic regex backtracking during line breaking.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>CPU / ReGex / Parsing bottleneck</code><br/>
Complex regex in `props.conf` or unoptimized regex in `transforms.conf` causes severe CPU spikes during parsing, blocking the `parsingQueue`.
</details>

**🚩 Capture the Flag 2.2:**
```text
FLAG{PARSING_QUEUE_REGEX_CPU_CHOKE}
```

---

## 🎯 TASK 3: Forwarder Inactivity & Silent Dropping (75 XP)

### 📖 Scenario Context
In large enterprises, Universal Forwarders on critical servers occasionally stop forwarding data without an alert because the OS rebooted or network routing changed.

### 🛠️ Interactive Admin Mission
In the Monitoring Console (`Forwarders: Deployment` ➔ `Forwarder Monitoring`):
- Splunk queries the `_internal` index:
  ```spl
  index=_internal source=*metrics.log group=tcpin_connections
  | stats max(_time) as last_contact by hostname
  | eval time_since_heartbeat = now() - last_contact
  | where time_since_heartbeat > 900
  ```
- Any forwarder with `time_since_heartbeat > 900` (15 minutes) is flagged as **Missing / Silent**!

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which internal Splunk index and log file track incoming forwarder connection heartbeats and data throughput?  
*(Answer Format: `index=********* source=*metrics.log`)*

<details>
<summary>💡 Need a Hint?</summary>
It starts with an underscore and stores internal diagnostic events.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Index:</b> <code>_internal</code><br/>
The <code>_internal</code> index contains <code>metrics.log</code>, which logs <code>tcpin_connections</code>, queue fill rates, and indexing throughput.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{INDEX_INTERNAL_METRICS_LOG}
```

---

## 🎯 TASK 4: The 1,200 IOPS Benchmark Verification (75 XP)

### 📖 Scenario Context
The storage team claims their virtual SAN storage provides "high performance". However, indexQueue alarms keep firing. You need to prove to the storage team that disk writes are failing Splunk's official reference specification.

### 🛠️ Interactive Admin Mission
Run the Linux `fio` benchmark command against the hot/warm mount point (`/opt/splunk/var/lib/splunk`):
```bash
sudo fio --name=splunk_test --ioengine=libaio --rw=randwrite \
    --bs=4k --numjobs=4 --size=1G --runtime=30 --time_based \
    --filename=/opt/splunk/var/lib/splunk/test.fio
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the minimum sustained random write IOPS benchmark specified by Splunk for mid-to-high volume production Indexers?  
*(Answer Format: `*,*** IOPS`)*

<details>
<summary>💡 Need a Hint?</summary>
One thousand two hundred.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>1,200 IOPS</code><br/>
Splunk's official hardware reference specification mandates at least 1,200 sustained 4k random write IOPS per Indexer to prevent indexQueue saturation.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{TWELVE_HUNDRED_SUSTAINED_IOPS}
```

---

## 🏆 Room 03 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM 03 COMPLETE                         │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 300 / 300 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Distributed Mode Activation, Queue Jam Diagnostics  │
│   (indexQueue vs parsingQueue), metrics.log Telemetry, 1200 IOPS Bench │
│                                                                        │
│ 🏅 PHASE 2 ARENA CLEAR! You have mastered Splunk Enterprise Topology! │
└────────────────────────────────────────────────────────────────────────┘
```
