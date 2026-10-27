# 🏰 Chapter 02 (Phase 7): Single-Site Indexer Clustering — Replication Factor, Search Factor & Peer Replication

> **The Splunk Administrator's Definitive Handbook** | Phase 7: Distributed Splunk & High-Availability Clusters  
> **Day:** 55 | **Milestone:** Single-Site High-Availability Clustering, Replication Factor ($RF$), Search Factor ($SF$), `server.conf` & Port 9887  
> **Current Rank:** Master Enterprise Fleet Orchestrator (11,350 XP) $\rightarrow$ *Promotion Target: Principal High-Availability Cluster Architect (15,100 XP)*  
> **Second Brain File:** `Chapter_02_Single_Site_Indexer_Clustering.md`  
> **Interactive Cyber Range Lab:** [Room P7-02: Single-Site Indexer Cluster Forge](../Labs/Room_P7_02_Single_Site_Indexer_Clustering.md) `[250 XP]`  
>  
> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: About Indexer Clusters and High Availability](https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Aboutclusters)  
> - 📖 [Splunk Docs: Basic Indexer Cluster Architecture ($RF$ and $SF$)](https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Basicclusterarchitecture)  
> - 📖 [Splunk Docs: Configure the Cluster Manager (Master Node)](https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Configurethemaster)  
> - 📖 [Splunk Docs: Configure Peer Nodes (Slave Nodes)](https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Configurepeers)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Section 8.0 — Indexer Clustering & High Availability (8.1 Configure single-site indexer cluster manager and peer nodes; 8.2 Define and differentiate Replication Factor ($RF$) and Search Factor ($SF$); 8.3 Configure replication ports and shared symmetric cluster keys in `server.conf`).  
> - 🎯 **Splunk Core Certified Power User (SPLK-1002):** Section 5.0 — Understanding Clustered Bucket Storage & Primary Search Copies.

---

## 🏦 1. The Everyday Analogy: The Triplicate Bank Vaults & The Chief Auditor

Imagine a major international commercial bank processing billions of dollars in daily wire transfers:

- **The Disaster of the Single Vault (Standalone Indexer):**  
  If the bank stores every deposit record in a single paper ledger inside a single vault, an electrical fire, pipe burst, or hardware failure destroys the entire bank's financial history overnight! Business stops, regulators fine the institution, and customer trust is obliterated.
- **The Triplicate Ledger Policy (Replication Factor $RF=3$):**  
  To guarantee complete fault tolerance, bank policy mandates:
  - Whenever a teller logs a deposit, three identical physical ledger books must be stored across three separate reinforced vaults (**$RF = 3$**).
  - Even if Vault A suffers a catastrophic structural collapse and Vault B floods simultaneously, **Vault C still holds 100% of the raw financial records**! Zero data loss.
- **The Search Index System (Search Factor $SF=2$):**  
  Raw ledger books are dense and slow to read. To enable rapid auditing:
  - The bank creates high-speed electronic barcode search cards (**`.tsidx` index files**) for two of the vaults (**$SF = 2$**).
  - If an auditor arrives, Vaults A and B can answer questions instantly. If Vault A burns down, Vault B immediately answers all audit queries with zero delay. Meanwhile, Vault C (holding only raw un-indexed ledger microfilm) can quickly regenerate an index card if instructed by the auditor!
- **The Chief Vault Auditor (The Cluster Manager - CM):**  
  The Chief Auditor sits in a command tower monitoring all three vaults. The Chief Auditor never holds physical cash or touches ledger books; instead, the Chief Auditor keeps an in-memory master blueprint of which vault holds which ledger page, continuously verifying that the $RF=3$ and $SF=2$ requirements are fulfilled 24 hours a day.

In Splunk Enterprise, **Indexer Clustering** provides high-availability storage, eliminating single points of failure while guaranteeing sub-second search continuity across enterprise infrastructure.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│               SINGLE-SITE INDEXER CLUSTER ARCHITECTURE (RF=3, SF=2)                       │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   CLUSTER MANAGER / MASTER NODE (CM-PROD-01) — Control Plane Only                         │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ • Enforces RF=3 and SF=2 cluster policies                                         │   │
│   │ • Tracks peer heartbeats on REST Port 8089                                        │   │
│   │ • Designates Primary Searchable Buckets                                           │   │
│   │ • Schedules bucket fixup tasks if a peer fails                                    │   │
│   └─────────────────────────▲───────────────────▲───────────────────▲─────────────────┘   │
│                             │ REST 8089         │ REST 8089         │ REST 8089           │
│                             ▼                   ▼                   ▼                     │
│   PEER NODES / SLAVE INDEXERS (Data Plane)                                                │
│   ┌───────────────────────────┐   ┌───────────────────────────┐   ┌─────────────────────┐ │
│   │ INDEXER 01 (idx-01)       │   │ INDEXER 02 (idx-02)       │   │ INDEXER 03 (idx-03) │ │
│   │ • Ingests on Port 9997    │   │ • Replication Port: 9887  │   │ • Replication: 9887 │ │
│   │ • Replication Port: 9887  │   │                           │   │                     │ │
│   │ ┌───────────────────────┐ │   │ ┌───────────────────────┐ │   │ ┌─────────────────┐ │ │
│   │ │ BUCKET 1 (PRIMARY)    │ │   │ │ BUCKET 1 (SEARCHABLE) │ │   │ │ BUCKET 1 (COPY) │ │ │
│   │ │ • journal.zst (Raw)   │ │   │ │ • journal.zst (Raw)   │ │   │ │ • journal.zst   │ │ │
│   │ │ • .tsidx (Searchable) │ │   │ │ • .tsidx (Searchable) │ │   │ │   (Raw Only)    │ │ │
│   │ └───────────────────────┘ │   │ └───────────────────────┘ │   │ └─────────────────┘ │ │
│   └─────────────▲─────────────┘   └─────────────▲─────────────┘   └──────────▲──────────┘ │
│                 │                               │                            │            │
│                 │      PEER-TO-PEER REPLICATION │ (Port 9887 TCP)            │            │
│                 └───────────────────────────────┴────────────────────────────┘            │
│                                                                                           │
│   SEARCH HEAD (SH-PROD-01)                                                                │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Queries Cluster Manager for Primary Bucket Map ──> Dispatches search ONLY to      │   │
│   │ Primary copies on idx-01 (or idx-02 if idx-01 is busy/down)!                      │   │
│   └───────────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. The 5-Step Clustered Ingestion & Replication Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               THE 5-STEP CLUSTERED BUCKET REPLICATION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. FORWARDER INGESTION & LOAD BALANCING                                                 │
│    • Universal Forwarder sends raw data stream to `idx-01` over TCP 9997.               │
│    • `useACK = true` ensures forwarder retains events in memory until cluster acknowledges.│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. ORIGIN BUCKET CREATION (On Target Peer)                                              │
│    • `idx-01` processes events through parsing pipeline and writes to open Hot bucket.  │
│    • Creates raw compressed journal (`journal.zst`) and time-series index (`.tsidx`).  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. PEER-TO-PEER RAW REPLICATION (Port 9887)                                             │
│    • To satisfy Replication Factor $RF=3$, `idx-01` immediately streams raw journal     │
│      blocks across high-speed Replication Port 9887 to `idx-02` and `idx-03`.           │
│    • Once `idx-02` and `idx-03` write blocks to disk, `idx-01` sends indexer ACK to UF. │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. BUCKET ROLL & SEARCH FACTOR ($SF$) ENFORCEMENT                                       │
│    • Hot bucket rolls to Warm. `idx-01` notifies Cluster Manager of bucket freeze.      │
│    • Cluster Manager inspects cluster state:                                            │
│      - $RF=3$ satisfied (3 raw copies exist on idx-01, idx-02, idx-03).                 │
│      - To satisfy $SF=2$, CM instructs `idx-02` to generate `.tsidx` index files.       │
│      - `idx-03` retains raw data copy only (saves disk space!).                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. PRIMARY DESIGNATION & SEARCH DISPATCH                                                │
│    • Cluster Manager designates `idx-01` as the **Primary** search copy for Bucket 1.   │
│    • When Search Head queries the cluster, it directs the search strictly to `idx-01`.  │
│    • If `idx-01` suddenly crashes, CM instantaneously promotes `idx-02` to Primary!     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 4. Technical Deep Dive: Factor Math, Stanzas & CLI Commands

### 4.1 Replication Factor ($RF$) vs Search Factor ($SF$)

The mathematical relationship between $RF$ and $SF$ is one of the most critical topics on the **SPLK-1003 Certified Admin Exam**:

$$\text{Replication Factor } (RF) \ge \text{Search Factor } (SF) \ge 1$$

| Metric | Enterprise Default | What It Contains | Failure Tolerance ($N = \text{Factor}$) |
| :--- | :---: | :--- | :--- |
| **Replication Factor ($RF$)** | **3** | Raw event data (`journal.zst`). Guarantees no data loss. | The cluster can tolerate the sudden loss of up to **$RF - 1$ peers** (2 peers if $RF=3$) without losing a single event! |
| **Search Factor ($SF$)** | **2** | Raw data (`journal.zst`) **PLUS** search artifacts (`.tsidx` files). | The cluster can tolerate the sudden loss of up to **$SF - 1$ peers** (1 peer if $SF=2$) without any search interruption or index rebuild! |

> [!IMPORTANT]
> **Mathematical Rule:** $SF$ can **NEVER be greater than $RF$**!  
> You cannot index data that has not been replicated. If an administrator sets $SF=3$ and $RF=2$, Splunk will throw a fatal error on startup and refuse to initialize the cluster manager.

---

### 4.2 Storage Capacity Sizing Formula

Clustering increases raw disk requirements. Calculate required disk storage using the official formula:

$$\text{Storage Required} = \text{Daily Ingestion} \times \text{Retention Days} \times \left[ (RF \times \text{Compression Ratio}) + (SF \times \text{Index Ratio}) \right]$$

*Example:*  
- Daily Ingestion = 500 GB/day | Retention = 90 days  
- Compression Ratio = 0.15 (Raw journal is ~15% of original text)  
- Index Ratio = 0.35 (TSIDX files are ~35% of original text)  
- $RF = 3$, $SF = 2$  

$$\text{Multiplier} = (3 \times 0.15) + (2 \times 0.35) = 0.45 + 0.70 = 1.15$$
$$\text{Total Cluster Storage} = 500 \text{ GB} \times 90 \times 1.15 = \mathbf{51,750 \text{ GB (51.75 TB)}}$$

---

### 4.3 Configuring `server.conf` Across Cluster Roles

#### A. On the Cluster Manager (Master Node):
```ini
# /opt/splunk/etc/system/local/server.conf
[clustering]
mode = master
replication_factor = 3
search_factor = 2
pass4SymmKey = EnterpriseClusterSecret2026!
cluster_label = prod_cluster_amer
```

#### B. On Peer Nodes (Slave Indexers):
```ini
# /opt/splunk/etc/system/local/server.conf
[clustering]
mode = slave
master_uri = https://cm-prod-01.corp.local:8089
pass4SymmKey = EnterpriseClusterSecret2026!

# Dedicated High-Speed Port for Bucket Journal Replication
[replication_port://9887]
```

#### C. On Search Heads:
```ini
# /opt/splunk/etc/system/local/server.conf
[clustering]
mode = searchhead
master_uri = https://cm-prod-01.corp.local:8089
pass4SymmKey = EnterpriseClusterSecret2026!
```

---

### 4.4 Essential CLI Commands for Indexer Cluster Administration

```bash
# 1. Inspect cluster replication and search health
/opt/splunk/bin/splunk show cluster-status -auth admin:SecurePass!

# Expected Healthy Output:
# Cluster status: All data is searchable
# Search factor: Met (2/2)
# Replication factor: Met (3/3)
# Generation ID: 14

# 2. List all connected peer nodes and their operational status
/opt/splunk/bin/splunk list cluster-peers -auth admin:SecurePass!

# 3. Gracefully decommission a peer for scheduled maintenance
/opt/splunk/bin/splunk offline --enforce-counts

# 4. Enable Maintenance Mode on Cluster Manager during upgrades
/opt/splunk/bin/splunk set cluster-mode -mode master -maintenance_mode 1
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               5 CRITICAL INDEXER CLUSTERING PITFALLS                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. THE FATAL $SF > RF$ CONFIGURATION ERROR                                              │
│    • Symptom: Splunk Cluster Manager crashes on startup.                                │
│    • Root Cause: Admin set `search_factor = 3` and `replication_factor = 2`.            │
│    • Fix: Ensure $RF \ge SF$ at all times.                                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. REPLICATION PORT 9887 FIREWALL BLOCK                                                 │
│    • Symptom: `show cluster-status` shows `Replication factor: NOT MET (1/3)`.          │
│    • Root Cause: Linux firewalld / AWS Security Group blocked TCP port 9887.            │
│    • Fix: Open TCP port 9887 bi-directionally between all indexer peers.                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. `pass4SymmKey` SECRET MISMATCH                                                       │
│    • Symptom: Indexer fails to join cluster; logs `401 Unauthorized: Invalid Secret`.    │
│    • Root Cause: Plaintext key mistyped before Splunk hashed it into `$7$...`.          │
│    • Fix: Re-enter identical plaintext `pass4SymmKey` on CM and peers and restart.      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. SEARCH HEAD CONNECTED DIRECTLY TO PEERS INSTEAD OF CM                                │
│    • Symptom: Search head returns duplicate search results for every event!             │
│    • Root Cause: Admin added peers manually via `distsearch.conf` instead of pointing   │
│      the Search Head to the Cluster Manager (`mode = searchhead`).                      │
│    • Fix: Let CM manage peer discovery dynamically!                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. SUDDEN PEER POWER-OFF WITHOUT `splunk offline`                                       │
│    • Symptom: Cluster Manager instantly triggers emergency bucket fixup storm.          │
│    • Root Cause: Admin yanked power plug without running `splunk offline`.              │
│    • Fix: Always execute `splunk offline --enforce-counts` before taking a peer down!   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 6. Cyber Range Practical Lab: Room P7-02

Ready to forge a resilient high-availability indexer cluster and survive node crashes?  
Jump straight into the hands-on simulated arena:

👉 **[Enter Cyber Range Room P7-02: Single-Site Indexer Cluster Forge](../Labs/Room_P7_02_Single_Site_Indexer_Clustering.md)** `[250 XP]`

You will configure a Cluster Manager and three peer indexers, initialize replication port 9887, resolve cryptographic symmetric key mismatches, audit primary bucket states, and capture all 4 operational flags!

---

## 📝 7. End-of-Chapter Self-Check Quiz

### Question 1 (SPLK-1003 Blueprint)
In a Splunk Single-Site Indexer Cluster with Replication Factor ($RF$) set to 3 and Search Factor ($SF$) set to 2, what does the Search Factor represent?
- A) The maximum number of concurrent searches the cluster can process per CPU core.
- B) The number of copies of each bucket that contain full search artifacts (`.tsidx` files), enabling immediate query execution without index reconstruction.
- C) The number of Search Heads allowed to connect to the Cluster Manager.
- D) The number of times a search query is duplicated across indexers to verify data integrity.

### Question 2 (Architecture Sizing)
An enterprise cluster operates with $RF = 3$ and $SF = 2$ across 5 peer indexers. What is the maximum number of peer indexers that can fail simultaneously without suffering permanent raw data loss?
- A) 1 peer
- B) 2 peers
- C) 3 peers
- D) 4 peers

### Question 3 (SPLK-1003 Blueprint)
Which configuration stanza and port specification must be defined on an indexer peer node in `server.conf` to allow it to receive replicated bucket journal blocks from other peers?
- A) `[clustering:replication]` on port 9997
- B) `[replication_port://9887]`
- C) `[peerCommunication://8089]`
- D) `[s2s://9887]`

### Question 4 (Configuration Precedence & Errors)
An administrator configures `replication_factor = 2` and `search_factor = 3` in `server.conf` on the Cluster Manager. What occurs when the `splunkd` service attempts to start?
- A) The Cluster Manager starts normally and automatically increases $RF$ to 4.
- B) The Cluster Manager logs a fatal error and refuses to start because $SF$ cannot exceed $RF$.
- C) The Cluster Manager converts the cluster into a Search Head Cluster.
- D) The cluster disables search indexing and enters read-only frozen mode.

### Question 5 (Search Coordination)
How does a clustered Search Head know which indexer peer holds the active copy of a bucket to search, avoiding returning duplicate results?
- A) The Search Head queries all indexers and dedupes the results using MD5 event hashes.
- B) The Search Head contacts the Cluster Manager on port 8089 to retrieve the current map of designated **Primary** bucket copies, directing searches exclusively to the primary peer.
- C) The Search Head broadcasts a multicast query on UDP port 514.
- D) Each indexer peer runs an internal election using the Raft consensus algorithm.

---

### 💡 Answers & In-Depth Explanations

1. **Answer: B**  
   *Explanation:* The Search Factor determines how many copies of a bucket have searchable index files (`.tsidx`). With $SF=2$, two peers hold searchable copies, ensuring that if one peer goes down, searches continue immediately without having to rebuild the index from raw data.
2. **Answer: B**  
   *Explanation:* The cluster can withstand the sudden loss of up to $RF - 1$ peers without raw data loss. Since $RF = 3$, $3 - 1 = 2$ peers can fail simultaneously while the remaining copy on the third peer preserves 100% of the raw data.
3. **Answer: B**  
   *Explanation:* Peer-to-peer raw bucket data replication occurs over a dedicated replication port configured via `[replication_port://<port>]` in `server.conf` (standard port: 9887).
4. **Answer: B**  
   *Explanation:* It is mathematically impossible to have more searchable indexed copies ($SF$) than raw data copies ($RF$). Splunk strictly enforces $RF \ge SF \ge 1$; violating this rule causes a fatal startup validation failure.
5. **Answer: B**  
   *Explanation:* The Cluster Manager designates exactly one copy of every bucket as "Primary". The Search Head queries the Cluster Manager for the primary bucket map and dispatches queries only to the designated primary peers, preventing duplicate event retrieval.
