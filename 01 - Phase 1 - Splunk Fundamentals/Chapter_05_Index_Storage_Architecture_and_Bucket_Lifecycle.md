# 📖 Chapter 05: Index Storage Architecture & The Bucket Lifecycle

> **The Splunk Administrator's Handbook** | Phase 1: Splunk Fundamentals  
> **Target Audience:** Complete Beginners to Enterprise Administrators  
> **Prerequisites:** Chapters 01, 02, 03, & 04

---

## 📸 1. Visual 3D Indexer Storage Architecture & Bucket Lifecycle

![3D Visual of Indexer Storage & Bucket Lifecycle](../assets/03_indexer_storage_buckets_3d.jpg)
*Figure 5.1: 3D Visual of Hot, Warm, Cold, and Frozen Bucket Transitions Across Storage Tiers (`![[03_indexer_storage_buckets_3d.jpg]]`)*

---

## 🗄️ 2. What is an Index? (Explained Simply)

### 🏢 The Master Analogy: "The Dedicated Filing Cabinets"

Imagine a large corporation with **10,000,000 documents**:
- Web server clicks
- Firewall & Antivirus alerts
- Confidential HR Payroll records
- Temporary debug logs

If you dump all 10,000,000 documents into **one single giant wooden box** (the default `main` index):
1. **Searching is painfully slow:** Finding a single firewall alert means searching through millions of unrelated web logs.
2. **Zero Security:** A junior IT intern searching for website errors could see confidential executive salary records!
3. **Impossible Retention:** You want to keep Security logs for **7 years** (compliance), but Web debug logs for only **14 days**. In a single box, you cannot delete one without destroying the other!

```text
┌────────────────────────────────────────────────────────────────────────┐
│               WHY WE CREATE DEDICATED SPLUNK INDEXES                   │
├────────────────────────────────────────────────────────────────────────┤
│ ❌ WITHOUT Dedicated Indexes (One Giant Messy Box):                    │
│    [ All Logs Mixed Together: Web + Security + Payroll + Debug ]       │
│    • Slow searches | No data security | Impossible cleanup             │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ WITH Dedicated Splunk Indexes (Categorized Filing Cabinets):        │
│                                                                        │
│    ┌───────────────┐   ┌────────────────┐   ┌───────────────────────┐  │
│    │  index = web  │   │index = security│   │   index = payroll     │  │
│    │               │   │                │   │                       │  │
│    │ Web Traffic   │   │ Firewall & SOC │   │ Confidential HR/Salaries│
│    │ Keep: 30 Days │   │ Keep: 365 Days │   │ Keep: 7 Years (Locked)│  │
│    └───────────────┘   └────────────────┘   └───────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

### ⚡ The 4 Superpowers of Creating Multiple Indexes

```text
┌────────────────────────────────────────────────────────────────────────┐
│                 THE 4 SUPERPOWERS OF SPLUNK INDEXES                    │
├───────────────────────────────┬────────────────────────────────────────┤
│ 1. 🚀 Blazing Search Speed    │ When you search 'index=security',      │
│                               │ Splunk opens ONLY the security cabinet │
│                               │ and ignores 95% of other data on disk! │
├───────────────────────────────┼────────────────────────────────────────┤
│ 2. 🔒 Strict Security (RBAC)  │ You can grant SOC analysts access to   │
│                               │ 'index=security' while locking down    │
│                               │ 'index=payroll' to HR managers only.   │
├───────────────────────────────┼────────────────────────────────────────┤
│ 3. ⏳ Custom Retention Rules  │ Set different data lifespans:          │
│    (Data Aging)               │ • index=security ──► 365 days          │
│                               │ • index=web      ──► 30 days           │
│                               │ • index=testing  ──► 7 days            │
├───────────────────────────────┼────────────────────────────────────────┤
│ 4. 💾 Storage Size Limits     │ Cap 'index=testing' to 50 GB maximum so│
│                               │ runaway test logs never crash disks!   │
└───────────────────────────────┴────────────────────────────────────────┘
```

---

### 📂 What Does an Index Look Like on the Hard Drive?

In reality, an **Index** is simply a dedicated folder on the Indexer's filesystem inside `/opt/splunk/var/lib/splunk/<index_name>/`:

```text
/opt/splunk/var/lib/splunk/security/
├── db/            <-- Fast NVMe SSD storage: Holds HOT and WARM buckets
├── colddb/        <-- High-capacity HDD storage: Holds COLD buckets
└── thaweddb/      <-- Restored archive folder: Holds THAWED buckets
```

---

### 📖 The Built-in Internal Indexes (The Ones with Underscores `_`)

Splunk creates several internal indexes for its own operations. These always start with an **underscore `_`**:

| Built-in Index | What It Stores | Analogy |
| :--- | :--- | :--- |
| **`_internal`** | Splunk's internal logs (`splunkd.log`, CPU/RAM, license usage) | Splunk's personal medical diary |
| **`_audit`** | Audit trail: Who logged in, who ran what search, config changes | The security CCTV camera |
| **`_introspection`**| Real-time OS resource metrics (CPU, RAM, Disk I/O per process) | The hospital heart monitor |
| **`_thefishbucket`**| Exact file read pointers & MD5 byte tracking database | The reading bookmark |
| **`main`** | The default storage bucket if you forget to specify `index=...` | The "Inbox" catch-all folder |

---

## 3. The Anatomy of a Bucket

An index is physically partitioned into directories called **Buckets**. Each bucket covers a specific window of time (e.g., from March 1st to March 3rd).

```text
/opt/splunk/var/lib/splunk/web_prod/db/db_1773570000_1773483600_12/
├── journal.zst               # Compressed raw text of all events (Zstandard/Gzip)
├── 1773570000-1773483600-12.tsidx  # Inverted index file (maps words to byte offsets)
├── bloomfilter               # Probabilistic filter for microsecond word lookups
├── Hosts.data                # List of unique hosts present in this bucket
├── Sources.data              # List of unique source paths
├── SourceTypes.data          # List of unique sourcetypes
└── bucket_info.csv           # Sizing, event count, and creation metadata
```

### The 3 Core Files Inside Every Bucket:
1. **`journal.zst` (Raw Data Journal):**
   - The immutable, compressed raw log events as they originally arrived.
   - Compression ratio: **$5\times\text{ to }10\times$** (e.g., 100 GB of raw logs compresses to $15\text{--}20\text{ GB}$).
2. **`.tsidx` (Time-Series Inverted Index):**
   - A fast inverted index (like an index in the back of a textbook). It lists every unique keyword/token and the exact line offsets in `journal.zst`.
3. **`bloomfilter`:**
   - A high-speed probabilistic hash table. When a search runs, Splunk checks the bloom filter first. If the bloom filter returns "no", Splunk skips reading the bucket's `.tsidx` from disk entirely, saving massive disk I/O.

---

## 4. The 5 Bucket States & The Storage Lifecycle

Data ages through 5 distinct bucket states as time passes or storage fills up:

```text
  [ Ingestion Stream ]
          │
          ▼
┌───────────────────┐
│    HOT BUCKET     │  • Location: Ultra-Fast NVMe SSD (homePath)
│   (Active Write)  │  • Status: Open for writes and immediate search.
└─────────┬─────────┘  • Naming: hot_v1_0, hot_v1_1
          │
          │ ── Triggers: Max size (maxDataSize) OR Time expired (maxHotSpanSecs) OR splunk restart
          ▼
┌───────────────────┐
│   WARM BUCKET     │  • Location: Fast SSD (homePath)
│ (Read-Only Search)│  • Status: Read-only; fully searchable.
└─────────┬─────────┘  • Naming: db_<youngest_time>_<oldest_time>_<bucket_id>
          │
          │ ── Trigger: Warm bucket count exceeds maxWarmDBCount
          ▼
┌───────────────────┐
│   COLD BUCKET     │  • Location: High-capacity Storage / HDD / NAS (coldPath)
│(Archived Search)  │  • Status: Still searchable, but on lower-cost storage tier.
└─────────┬─────────┘  • Naming: db_<youngest_time>_<oldest_time>_<bucket_id>
          │
          │ ── Triggers: Retention Age (frozenTimePeriodInSecs) OR Retention Size (maxTotalDataSizeMB)
          ▼
┌───────────────────┐
│   FROZEN BUCKET   │  • Location: Remote Cloud Archive (AWS S3, GCP GCS) OR DELETED
│  (Non-Searchable) │  • Status: TSIDX files erased; raw journal moved to archive or purged.
└─────────┬─────────┘
          │
          │ ── Manual Admin Action: Uncompress and rebuild TSIDX using 'splunk rebuild'
          ▼
┌───────────────────┐
│   THAWED BUCKET   │  • Location: Local Disk (thawedPath)
│(Restored Search)  │  • Status: Temporarily searchable again for compliance/audits.
└───────────────────┘
```

---

## 5. Configuring Indexes & Storage Limits (`indexes.conf`)

Path: `/opt/splunk/etc/apps/org_all_indexes/local/indexes.conf`

```ini
[web_prod]
# Physical Storage Paths
homePath = /opt/splunk/var/lib/splunk/web_prod/db
coldPath = /opt/splunk/var/lib/splunk/web_prod/colddb
thawedPath = /opt/splunk/var/lib/splunk/web_prod/thaweddb

# Hot to Warm Rolling Triggers
maxDataSize = auto_high_volume    # Rolls hot to warm when bucket reaches 10GB (for 64-bit systems)
maxHotSpanSecs = 7776000          # Rolls hot to warm if bucket stays open for 90 days

# Warm to Cold Rolling Triggers
maxWarmDBCount = 300              # Maximum 300 warm buckets; excess rolls to coldPath

# Retention & Cold to Frozen Triggers
frozenTimePeriodInSecs = 31536000 # 365 Days (1 Year) Retention Policy
maxTotalDataSizeMB = 500000       # 500 GB Storage Cap (Rolls oldest to frozen if exceeded)

# Cold to Frozen Action (Archiving Script)
coldToFrozenDir = /mnt/nfs_archive/web_prod/frozen/
# OR: coldToFrozenScript = /opt/splunk/bin/python3 /opt/splunk/bin/scripts/archive_to_s3.py
```

---

## 6. Enterprise Capacity Planning Math

### Sizing Ingest and Storage Requirements:
If an enterprise ingests **$500\text{ GB/day}$** of raw logs and requires a **$90\text{-day}$ retention policy**:

$$\text{Daily Raw Ingest} = 500\text{ GB/day}$$

$$\text{Compression Factor} \approx 50\% \text{ (after indexing overhead + TSIDX)}$$

$$\text{Daily Indexed Storage} = 500\text{ GB} \times 0.5 = 250\text{ GB/day}$$

$$\text{90-Day Standalone Storage} = 250\text{ GB/day} \times 90\text{ days} = 22,500\text{ GB} \approx 22.5\text{ TB}$$

**With Clustered High Availability ($\text{Replication Factor (RF)}=3$):**

$$\text{Total Cluster Storage Required} = 22.5\text{ TB} \times 3 = 67.5\text{ TB}$$

---

## 🧠 Chapter 05 Self-Check Quiz

1. What are the three primary files located inside every Splunk bucket?
2. What are the two events that trigger a **Hot Bucket** to roll into a **Warm Bucket**?
3. What is the difference in searchability between a **Cold Bucket** and a **Frozen Bucket**?
4. If `maxTotalDataSizeMB = 100000` is reached before `frozenTimePeriodInSecs`, what action does Splunk take?
5. How do you make a Frozen bucket searchable again?

---

## 🎮 Hands-On Cyber Range Challenge: Room P1-05 (TryHackMe / HTB Style)

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ARENA MISSION: Room P1-05 — Bucket Storage & Cold Thawing Operation │
│ ⭐ DIFFICULTY: Medium | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins           │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Incident Scenario:**  
> Corporate Legal requires financial logs from 14 months ago for a subpoena.  
> The logs rolled to Frozen and the TSIDX indexes were stripped.  
> You must thaw the archived rawjournal into `thaweddb/` and rebuild the search index within 6 hours!

### 🎯 Mission Checkpoint Questions

#### 1. What happens to Frozen data by default if no archival script or directory is configured?
*(Answer Format: ********* ********)*
<details><summary>💡 Need a Hint?</summary>Does Splunk keep it in /tmp or delete it?</details>
<details><summary>🔓 Reveal Answer</summary><b>Answer:</b> <code>Permanent Deletion</code></details>

#### 2. Which CLI command reconstructs the missing .tsidx search index for a restored bucket?
*(Answer Format: `splunk ******* <bucket_path>`)*
<details><summary>💡 Need a Hint?</summary>A 7-letter verb meaning construct again.</details>
<details><summary>🔓 Reveal Answer</summary><b>Answer:</b> <code>splunk rebuild &lt;bucket_path&gt;</code></details>

#### 3. How do you distinguish a Hot bucket from a Warm bucket by directory name?
*(Answer Format: Hot starts with `*******`; Warm starts with `***`)*
<details><summary>💡 Need a Hint?</summary>hot_v1_ vs db_epoch.</details>
<details><summary>🔓 Reveal Answer</summary><b>Answer:</b> Hot starts with <code>hot_v1_</code>; Warm starts with <code>db_</code></details>

👉 **[Launch Full Interactive Lab: Room P1-05 & Capture All 4 Flags (250 XP)](../Labs/Room_P1_05_Bucket_Lifecycle_and_Cold_Storage_Thawing.md)**
