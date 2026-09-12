# 📄 Phase 1 Master Revision Sheet: Splunk Fundamentals & Architecture

> **The Splunk Administrator's Pocket Cheat Sheet** | Complete Phase 1 Review (Chapters 01–07)  
> **Location:** End of Phase 1 Capstone  
> **Purpose:** Rapid-recall review for production operations, architecture design, and Senior Administrator certification/interviews.

---

# 📑 PAGE 1: Core Architecture, Pipeline & Configuration Precedence

---

## 🏛️ 1. Machine Data & Schema-on-Read (Chapter 01)
- **Machine Data:** Unstructured or semi-structured, high-volume, timestamped logs generated 24/7 by hardware, OS, and applications.
- **The 5 Immutable Default Metadata Fields:**
  1. `_time` (Epoch time in UTC) | 2. `host` (Origin server) | 3. `source` (File path or port) | 4. `sourcetype` (Log structure format) | 5. `index` (Target datastore).
- **Schema-on-Write vs. Schema-on-Read:**
  - *Traditional SQL (Schema-on-Write):* Rigid upfront database design. Unstructured logs fail or require slow ETL migrations.
  - *Splunk (Schema-on-Read):* Ingests raw text immediately without predefined tables. Fields are extracted dynamically at search time using regex.

---

## 🧩 2. Splunk Enterprise Component Roles (Chapter 02)

```text
┌───────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ COMPONENT                 │ PRIMARY ROLE & INTERNAL SPECIFICATIONS                                 │
├───────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Universal Forwarder (UF)  │ Lightweight edge shipper (<2% CPU, ~50MB RAM). No parsing/Python engine│
│ Heavy Forwarder (HF)      │ Full Splunk binary. Parses events, masks PII, routes to third-party.  │
│ Indexer (IDX)             │ Maps keywords (.tsidx), compresses raw logs (journal.zst), stores data.│
│ Search Head (SH)          │ Web UI, user search dispatch (Map), and results aggregation (Reduce).  │
│ Deployment Server (DS)    │ Centralized app & configuration bundle manager for UFs/HFs (Port 8089).│
│ License Manager (LM)      │ Aggregates and meters daily raw ingestion volume across Indexer slaves.│
│ Cluster Manager (CM)      │ Coordinates bucket replication (RF/SF) and peer health across IDXC.    │
│ SHC Deployer              │ Pushes app bundles and configurations to Search Head Cluster members.  │
│ Monitoring Console (MC)   │ Central telemetry, health monitoring, and resource topology dashboard. │
└───────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 3. The 4 Pipeline Phases & Memory Queues (Chapter 03)

```text
[Input Phase] ──► [Parsing Phase] ──► [Indexing Phase] ──► [Search Phase]
 (UF / HF / IDX)   (HF / Indexer)       (Indexer Only)      (Search Head / IDX)
```

1. **Input Phase:** Reads raw stream, chunks data into 64KB blocks, attaches `host`, `source`, `sourcetype`, `index`.
2. **Parsing Phase:** UTF-8 conversion, line breaking (`LINE_BREAKER`), timestamp parsing (`TIME_PREFIX`/`MAX_TIMESTAMP_LOOKAHEAD`), regex masking.
3. **Indexing Phase:** Builds `.tsidx` inverted indexes, writes compressed `journal.zst`, and commits to disk.
4. **Search Phase:** Search Head dispatches SPL to Indexers (Map phase), Indexers filter `.tsidx`, Search Head aggregates (Reduce phase).
- **Queue Sequence on Indexer:** `input_queue` $\rightarrow$ `parsing_queue` $\rightarrow$ `agg_queue` $\rightarrow$ `typing_queue` $\rightarrow$ `index_queue` $\rightarrow$ Disk.
- **Backpressure & Reliability:** When disk I/O saturates, `index_queue` fills to 100%, causing upstream queues to fill in reverse order until the TCP socket pauses. With `useACK = true`, forwarders hold logs in RAM until the indexer confirms disk write.

---

## 🗂️ 4. Directory Structure & S-A-A-S Precedence (Chapter 04)

### 🪜 The S-A-A-S Memory Ladder (Ingestion / System Context):
$$\mathbf{S}\text{ystem Local (1)} \;\succ\; \mathbf{A}\text{pp Local (2)} \;\succ\; \mathbf{A}\text{pp Default (3)} \;\succ\; \mathbf{S}\text{ystem Default (4)}$$

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. $SPLUNK_HOME/etc/system/local/       ◄── HIGHEST PRIORITY           │
│ 2. $SPLUNK_HOME/etc/apps/<app>/local/                                  │
│ 3. $SPLUNK_HOME/etc/apps/<app>/default/                                │
│ 4. $SPLUNK_HOME/etc/system/default/     ◄── LOWEST (Wiped on Upgrade!) │
└────────────────────────────────────────────────────────────────────────┘
```
- **Pizza Customizer Rule (Attribute Merging):** Splunk merges stanzas key-by-key; higher layers override specific keys without wiping the entire stanza.
- **The X-Ray Command:** `splunk btool <conf_name> list --debug` (Inspects effective merged config and origin filepaths).
- **File Tracking (Fishbucket):** `$SPLUNK_HOME/var/lib/splunk/fishbucket` (Tracks 256-byte MD5 hashes and file pointers).

---

# 📑 PAGE 2: Storage Buckets, Licensing & Network Matrix

---

## 🗄️ 5. Index Storage & The 5 Bucket Stages (Chapter 05)

### 🏢 What is an Index? (The 4 Superpowers)
An Index is a dedicated folder on disk (`/opt/splunk/var/lib/splunk/<index>/`). Provides: **1. Blazing Search Speed**, **2. Role-Based Access Control (RBAC)**, **3. Custom Data Retention**, and **4. Storage Size Caps**.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                         THE 5 BUCKET LIFECYCLE                         │
├──────────┬─────────────────┬───────────┬───────────────────────────────┤
│ STAGE    │ LOCATION        │ STATUS    │ ROLL TRIGGERS / ACTIONS       │
├──────────┼─────────────────┼───────────┼───────────────────────────────┤
│ HOT      │ Fast NVMe SSD   │ R / W     │ maxDataSize, time, restart    │
│ WARM     │ Fast SSD (home) │ Read-Only │ Warm bucket count > maxWarmDB │
│ COLD     │ High-cap HDD    │ Read-Only │ Retention time or maxTotalMB  │
│ FROZEN   │ S3/NFS/Deleted  │ Unsearch  │ .tsidx stripped; journal saved│
│ THAWED   │ thaweddb/ (SSD) │ Restored  │ 'splunk rebuild' restores idx │
└──────────┴─────────────────┴───────────┴───────────────────────────────┘
```
- **3 Core Bucket Files:**
  1. `journal.zst` (Compressed raw text, $5\times\text{--}10\times$ ratio).
  2. `.tsidx` (Inverted keyword index for microsecond word lookups).
  3. `bloomfilter` (Probabilistic hash table; skips reading unnecessary bucket indexes).
- **Thawing Procedure:** Copy bucket to `thaweddb/` and run `/opt/splunk/bin/splunk rebuild <thawed_bucket_dir>`.

---

## 💳 6. Licensing Mechanics & Quota Management (Chapter 06)
- **Metering Basis:** Measured in uncompressed raw data volume (GB/TB) per rolling 24h window (resets at **Midnight UTC**).
- **What is 100% Free:** Metadata fields, `.tsidx` files, internal indexes (`_internal`, `_audit`), summary indexes, search results, forwarders, and **replicated cluster copies ($\text{RF}=3$ stores 3x, billed 1x)**.
- **License Pools:** Departmental quotas that prevent runaway debug logs from exhausting the enterprise license.
- **Warnings vs. Violations:**
  - 1 Over-quota day = 1 Warning.
  - **5 Warnings in a rolling 30-day window = Hard License Violation**.
  - *Violation Effect:* Search is restricted for non-admins. **Data ingestion NEVER stops and data is NEVER dropped!**
- **Adding Capacity:** Splunk licenses **stack additively** ($1\text{ TB} + 500\text{ GB} = 1.5\text{ TB}$). In emergency lockouts, install a **Reset Key** from Splunk Support.

---

## 🌐 7. Enterprise Port Matrix & Firewall Rules (Chapter 07)

```text
┌───────┬──────────┬─────────────────────────────┬─────────────────────────────────┐
│ PORT  │ PROTOCOL │ SOURCE ──► DESTINATION       │ PRIMARY PURPOSE                 │
├───────┼──────────┼─────────────────────────────┼─────────────────────────────────┤
│ 8000  │ HTTPS    │ Browser ──► Search Head     │ Splunk Web GUI Interface        │
│ 8089  │ HTTPS    │ Forwarder / SH ──► Splunk   │ Management & REST API (Dispatch)│
│ 9997  │ TCP      │ Forwarder ──► Indexer       │ Splunk-to-Splunk (S2S) Ingest   │
│ 8088  │ HTTPS    │ App Servers ──► HEC / IDX   │ HTTP Event Collector (HEC)      │
│ 9887  │ TCP      │ Indexer ◄──► Indexer        │ Clustered Bucket Replication(RF)│
│ 8191  │ TCP      │ Search Head ◄──► Search Head│ KV Store Synchronization        │
│ 514   │ UDP/TCP  │ Network Routers ──► HF      │ Syslog Ingestion Port           │
└───────┴──────────┴─────────────────────────────┴─────────────────────────────────┘
```

### 🧭 Directionality Golden Rule:
- **Forwarders ALWAYS INITIATE outbound connections** to Indexers (`9997`) and Deployment Server (`8089`). The Deployment Server never connects into forwarders!

### 💻 Rapid CLI Network Diagnostics:
```bash
nc -zvw 3 10.100.1.10 9997                     # Test TCP port reachability
curl -k https://10.100.1.10:8089/services/ping # Test REST management port
ss -tulpn | grep 9997                         # Check if local Splunk is listening
```

---

## 🎯 5 Golden Interview Rules (Cheat Sheet Summary)

1. **"Never edit files inside `system/default` or `apps/<app>/default`."** (Always customize in `local/`).
2. **"Never install Heavy Forwarders on general application servers."** (Universal Forwarders are ultra-lightweight).
3. **"Universal Forwarders do not perform event line breaking."** (Occurs in Parsing Phase on HF or Indexer).
4. **"During a License Violation, Splunk NEVER drops incoming logs."** (Ingestion is continuous; only user searches are paused).
5. **"Replication Factor ($\text{RF}=3$) does not triple your license cost."** (License is metered once upon initial ingest).

---

## 🏁 Phase 1 Complete!

👉 **Next Step:** Proceed to **[Phase 2: Enterprise Installation & Topology Setup](../02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/00_Phase_2_Overview_and_TOC.md)**!
