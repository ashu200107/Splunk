# 📚 Phase 1 Targeted Review Guide: Chapters 01 to 07

> **The Splunk Administrator's Remediation Blueprint** | High-Yield Topic Reinforcement  
> **Purpose:** Master the exact gaps identified during the Phase 1 Master Assessment before advancing to Phase 2.

---

## 🗺️ Targeted Review Matrix (Chapters 01 – 07)

```text
┌────────────┬──────────────────────────────────────────┬────────────────────────────────────────────────────────┐
│ CHAPTER    │ HIGH-PRIORITY TOPIC TO REVIEW            │ WHY IT MATTERS IN PRODUCTION & INTERVIEWS              │
├────────────┼──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Chapter 01 │ Fallback Timestamps (No Time in Log)     │ How Splunk assigns _time using file mtime vs current. │
│ Chapter 02 │ Intermediate Forwarders in DMZ & UF Caps │ UFs cannot mask data; Forwarders act as DMZ proxies.   │
│ Chapter 03 │ Parsing Overrides Input & TRUNCATE       │ Downstream transforms rewrite metadata; TRUNCATE cuts. │
│ Chapter 04 │ Fishbucket Reset Disaster & btool check  │ Wiping fishbucket causes duplicates; use followTail=1. │
│ Chapter 05 │ SmartStore Cloud Architecture            │ Local SSD = Cache; Remote S3/GCS = Master Data copy.   │
│ Chapter 06 │ Data Hygiene: Discarding to nullQueue    │ Regex routing in transforms.conf to drop spam for $0. │
│ Chapter 07 │ HEC Port 8088 & Port 8191 vs 8089        │ HEC REST auth token header; KV Store vs REST dispatch. │
└────────────┴──────────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

# 📖 Deep-Dive Review by Chapter

---

## 📌 1. Chapter 01: Timestamp Extraction Fallbacks
🔗 **Note Link:** [Chapter_01_What_is_Splunk_and_Machine_Data.md](./Chapter_01_What_is_Splunk_and_Machine_Data.md)

### 💡 The Core Rule:
If an application generates an event with **no timestamp in its text** (e.g. `User root logged in`):
1. **First Fallback:** Splunk checks the **file's modification time (`mtime`)** on the OS.
2. **Second Fallback:** If `mtime` is unavailable or data is streamed over network ports, Splunk assigns the **current indexing/arrival time** (`DATETIME_CONFIG = CURRENT`).

---

## 📌 2. Chapter 02: Intermediate Forwarders & Forwarder Capabilities
🔗 **Note Link:** [Chapter_02_Splunk_Core_Architecture_and_Components.md](./Chapter_02_Splunk_Core_Architecture_and_Components.md)

### 💡 Two Crucial Rules to Remember:
1. **Universal Forwarders have NO parsing engine:**
   - UFs **cannot** perform regex masking, cannot do event line-breaking, and cannot route to `nullQueue`. They only read raw bytes, attach metadata, and ship.
2. **What is an Intermediate Forwarder?**
   - A Heavy Forwarder (or UF) placed inside a **DMZ (Demilitarized Zone)**.
   - **The Use Case:** Company firewall policies forbid opening direct network traffic (Port 9997) from 10,000 edge application servers into internal core database/indexers.
   - **The Topology:** 10,000 UFs send logs to **2 Intermediate Forwarders in the DMZ**, and only those 2 DMZ machines have firewall access to forward logs to core Indexers.

```text
[10,000 App Servers] ──► [2 DMZ Intermediate Forwarders] ──► (Internal Firewall) ──► [Core Indexers]
```

---

## 📌 3. Chapter 03: Downstream Parsing Overrides & `TRUNCATE`
🔗 **Note Link:** [Chapter_03_The_End_to_End_Data_Pipeline.md](./Chapter_03_The_End_to_End_Data_Pipeline.md)

### 💡 Rule A: Downstream Pipeline Always Wins
- **Input Phase (`inputs.conf` on UF):** Sets initial metadata: `sourcetype = access_combined`.
- **Parsing Phase (`props.conf`/`transforms.conf` on Indexer):** Rewrites it to `sourcetype = access_secure`.
- 🎯 **Result:** The final sourcetype stored permanently in `journal.zst` and `.tsidx` on disk is **`access_secure`**!

### 💡 Rule B: How `TRUNCATE` Actually Works
- Default setting: `TRUNCATE = 10000` (10,000 bytes).
- If a 35,000-byte Java stack trace arrives: Splunk **cuts the event at byte 10,000**. The remaining 25,000 bytes become a **second broken event**.
- **Fix:** Set `TRUNCATE = 50000` (or `TRUNCATE = 0` for unlimited) in `props.conf`.

---

## 📌 4. Chapter 04: The Fishbucket Reset Disaster & `btool check`
🔗 **Note Link:** [Chapter_04_Splunk_Directory_Structure_and_Config_Precedence.md](./Chapter_04_Splunk_Directory_Structure_and_Config_Precedence.md)

### 💡 The Fishbucket Reset Disaster:
- Location: `$SPLUNK_HOME/var/lib/splunk/fishbucket`.
- **What happens if you run `splunk clean eventdata -index _thefishbucket`?**
  - All 256-byte MD5 file tracking pointers are deleted!
  - When Splunk restarts, it assumes **every log file is brand-new** and **re-indexes every file from Byte 0**, causing massive duplicate data and license violations!
- 🛡️ **How to Protect Yourself:**
  - In `inputs.conf`, set:
    ```ini
    [monitor:///var/log/...]
    followTail = 1
    ```
  - `followTail = 1` forces Splunk to ignore past content and read **only newly written lines from this moment forward**.

### 💡 Configuration Syntax Validation Command:
- To scan all `.conf` files across the entire instance for typos, unrecognized settings, or duplicate stanzas:
  ```bash
  /opt/splunk/bin/splunk btool check
  # View file origins alongside errors:
  /opt/splunk/bin/splunk btool check --debug
  ```

---

## 📌 5. Chapter 05: Modern SmartStore Storage Architecture
🔗 **Note Link:** [Chapter_05_Index_Storage_Architecture_and_Bucket_Lifecycle.md](./Chapter_05_Index_Storage_Architecture_and_Bucket_Lifecycle.md)

### 💡 SmartStore Architecture Explained:
In traditional Splunk, Indexers store Hot/Warm on local SSD and Cold on local HDD. In modern cloud/Kubernetes environments, Splunk uses **SmartStore**:
1. **Local Disks (NVMe SSD):** Act strictly as a **Local Cache** holding Hot buckets and actively searched Warm buckets.
2. **Remote Object Storage (AWS S3, GCP GCS, Azure Blob):** Holds the **Authoritative Master Copy of ALL data**.
3. **Cold Buckets:** Are completely eliminated in SmartStore!

---

## 📌 6. Chapter 06: Data Hygiene & Discarding Noise to `nullQueue`
🔗 **Note Link:** [Chapter_06_Splunk_Licensing_Mechanics.md](./Chapter_06_Splunk_Licensing_Mechanics.md)

### 💡 The Production Runbook to Stop License Bleed:
When an application floods millions of useless `DEBUG: keepalive ok` lines, discard them before they hit disk:

1. **In `transforms.conf` (Heavy Forwarder or Indexer):**
   ```ini
   [drop_keepalive_debug]
   REGEX = (?i)DEBUG:\s*connection\s*keepalive\s*ok
   DEST_KEY = queue
   FORMAT = nullQueue
   ```
2. **In `props.conf`:**
   ```ini
   [my_noisy_sourcetype]
   TRANSFORMS-discard_spam = drop_keepalive_debug
   ```
*(Matching events are routed to `nullQueue` and dropped from memory for **\$0 license cost**!)*

---

## 📌 7. Chapter 07: Port Matrix Precision & Scalability Tuning
🔗 **Note Link:** [Chapter_07_Splunk_Ports_Protocols_and_Firewall_Matrix.md](./Chapter_07_Splunk_Ports_Protocols_and_Firewall_Matrix.md)

### 💡 Port Precision:
- **Port `8088` (HTTPS):** HTTP Event Collector (HEC). Requires `Authorization: Splunk <Token-UUID>` header.
- **Port `8089` (HTTPS):** `splunkd` REST API management & Search Head Map-Reduce search dispatch.
- **Port `8191` (TCP):** KV Store (MongoDB) sync between Search Heads in a Search Head Cluster.
- **Port `9997` (TCP):** Splunk-to-Splunk (S2S) log stream ingestion from forwarders to indexers.

### 💡 Deployment Server Scalability Parameter:
When scaling to 20,000 forwarders, the Deployment Server crashes if all forwarders poll every 60s.
- In `deploymentclient.conf` on forwarders:
  ```ini
  [deployment-client]
  phoneHomeIntervalInSecs = 600
  ```
  *(Increases check-in interval from 60s to 10 minutes, relieving 90% of CPU and network load on the Deployment Server!)*

---

## 🏁 Phase 1 Complete!

With these 7 key areas reinforced, your foundational and operational knowledge of Splunk Enterprise Architecture is rock-solid.

👉 **Next Step:** Ready for hands-on Linux administration? Proceed to **[Phase 2: Enterprise Installation & Topology Setup](../02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/00_Phase_2_Overview_and_TOC.md)**!
