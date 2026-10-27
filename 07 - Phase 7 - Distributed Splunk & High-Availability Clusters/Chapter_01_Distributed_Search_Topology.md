# 🔭 Chapter 01 (Phase 7): Distributed Search Topology & Map-Reduce Architecture

> **The Splunk Administrator's Definitive Handbook** | Phase 7: Distributed Splunk & High-Availability Clusters  
> **Day:** 54 | **Milestone:** Distributed Search Mechanics, `distsearch.conf`, Knowledge Bundle Replication & Map-Reduce Pipeline  
> **Current Rank:** Master Enterprise Fleet Orchestrator (11,100 XP) $\rightarrow$ *Promotion Target: Principal High-Availability Cluster Architect (15,100 XP)*  
> **Second Brain File:** `Chapter_01_Distributed_Search_Topology.md`  
> **Interactive Cyber Range Lab:** [Room P7-01: The Search Head Dispatch Nexus](../Labs/Room_P7_01_Distributed_Search_Topology.md) `[250 XP]`  
>  
> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: About Distributed Search Architecture](https://docs.splunk.com/Documentation/Splunk/latest/DistSearch/Aboutdistributedsearch)  
> - 📖 [Splunk Docs: distsearch.conf Specification & Syntax](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Distsearchconf)  
> - 📖 [Splunk Docs: How Knowledge Bundle Replication Works](https://docs.splunk.com/Documentation/Splunk/latest/DistSearch/Howbundlereplicationworks)  
> - 📖 [Splunk Docs: Add and Manage Search Peers via CLI](https://docs.splunk.com/Documentation/Splunk/latest/DistSearch/Addsearchpeers)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Section 7.0 — Distributed Search & Indexer Management (7.1 Describe distributed search architecture and map-reduce processing; 7.2 Configure and optimize search peers via `distsearch.conf` and CLI; 7.3 Troubleshoot knowledge bundle replication and bundle bloat).  
> - 🎯 **Splunk Core Certified Power User (SPLK-1002):** Section 5.0 — Search Processing Optimization in Distributed Environments.

---

## 👨‍🍳 1. The Everyday Analogy: The Executive Head Chef & The Brigade de Cuisine

Imagine the bustling kitchen of a 3-star Michelin restaurant preparing dinner for 500 banquet guests:

- **The Executive Head Chef (The Search Head - SH):**  
  The Head Chef does not run to the walk-in pantry, chop 200 pounds of onions, or grill 500 steaks individually. Instead, when a guest orders a meal (**User submits an SPL Search Job**):
  1. The Head Chef breaks the recipe down into distinct preparation tickets (**Query Parsing & Plan Generation**).
  2. The Head Chef distributes the recipe cards, seasoning guidelines, and plate layouts to all stations (**Knowledge Bundle Replication**).
  3. When dishes come back from the line, the Head Chef inspects the quality, combines the sides, garnishes the plate, and sends it out to the dining room (**The Reduce Phase**).
- **The Line Cooks / Station Chefs (The Search Peers / Indexers - IDXs):**  
  Ten line cooks work in parallel. Each cook has immediate access to their own local refrigerator and griddle (**Local Index Storage & TSIDX Files**).  
  They execute the heavy physical work simultaneously (**The Map Phase**): searching their local pans, filtering bad ingredients, aggregating local counts, and sending only the condensed sauce back to the Head Chef!
- **The Delivery Bottleneck (Knowledge Bundle Bloat):**  
  If the Head Chef insists on printing a 10,000-page encyclopedia of culinary history and hand-carrying it to every line cook before they are allowed to crack an egg, the entire kitchen grinds to a halt! Line cooks stand frozen waiting for the book delivery, and dinner is delayed by hours.

In Splunk Enterprise, **Distributed Search** decouples search management from raw data storage, leveraging parallel processing across dozens of indexers to return answers in fractions of a second.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│               ENTERPRISE DISTRIBUTED SEARCH & MAP-REDUCE ARCHITECTURE                     │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   SPLUNK SEARCH HEAD (SH-PROD-01) — Control & Reduce Plane                                │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 1. User submits query: index=web status=500 | stats count by clientip            │   │
│   │ 2. Distsearch engine generates Knowledge Bundle: etc/apps, etc/system, lookups    │   │
│   │ 3. Distributes bundle tarball to peers via REST (TCP 8089)                        │   │
│   │ 4. Receives streaming map results from peers & aggregates final stats             │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │ REST Dispatch & Bundle Sync                 │
│                                             │ (TCP 8089 HTTPS)                            │
│                     ┌───────────────────────┼───────────────────────┐                     │
│                     ▼                       ▼                       ▼                     │
│   SEARCH PEER 01 (IDX-01)         SEARCH PEER 02 (IDX-02)         SEARCH PEER 03 (IDX-03) │
│   ┌───────────────────────────┐   ┌───────────────────────────┐   ┌─────────────────────┐ │
│   │ • Receives Knowledge      │   │ • Receives Knowledge      │   │ • Receives Knowledge│ │
│   │   Bundle into:            │   │   Bundle into:            │   │   Bundle into:      │ │
│   │   var/run/searchpeers/    │   │   var/run/searchpeers/    │   │   var/run/searchpeer│ │
│   │                           │   │                           │   │                     │ │
│   │ ── MAP PHASE EXECUTION ── │   │ ── MAP PHASE EXECUTION ── │   │ ── MAP EXECUTION ── │ │
│   │ • Scans local TSIDX files │   │ • Scans local TSIDX files │   │ • Scans local TSIDX │ │
│   │ • Filters status=500      │   │ • Filters status=500      │   │ • Filters status=500│ │
│   │ • Local pre-stats by IP   │   │ • Local pre-stats by IP   │   │ • Local pre-stats   │ │
│   └─────────────┬─────────────┘   └─────────────┬─────────────┘   └──────────┬──────────┘ │
│                 │                               │                            │            │
│                 └───────────────────────┬───────┴────────────────────────────┘            │
│                                         │ Intermediate Map Streams                        │
│                                         ▼                                                 │
│   SEARCH HEAD REDUCE PHASE: Final stats merge & table presentation                        │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. The 5-Step Distributed Search Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               THE 5-STEP DISTRIBUTED SEARCH & EXECUTION LIFECYCLE                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. SEARCH HEAD DISPATCH & QUERY PARSING                                                 │
│    • User initiates an SPL query in Splunk Web, CLI, or REST API.                       │
│    • Search Head compiles SPL into an optimized search abstract syntax tree (AST).     │
│    • Identifies streaming commands (Map phase) vs transforming commands (Reduce phase). │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. KNOWLEDGE BUNDLE GENERATION & REPLICATION                                            │
│    • Search Head packages configuration files (`etc/system/`, `etc/apps/`) into a       │
│      compressed tarball (`.bundle` / `.tar.gz`).                                        │
│    • Pushes the bundle to all configured search peers via REST port 8089.               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. REST DISPATCH TO SEARCH PEERS                                                        │
│    • Search Head sends the distributed search job to each peer over HTTPS TCP 8089.     │
│    • Search peers allocate an internal dispatch directory for the job:                  │
│      `$SPLUNK_HOME/var/run/splunk/dispatch/<job_id>/`                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. PEER EXECUTION (THE MAP PHASE)                                                       │
│    • Each search peer independently searches its local storage buckets.                 │
│    • Leverages `.tsidx` index files to identify candidate events rapidly.               │
│    • Applies search-time extractions, field aliases, lookups, and initial filtering.    │
│    • Executes intermediate transformations (e.g. `prestats` computation).              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. SEARCH HEAD AGGREGATION (THE REDUCE PHASE)                                           │
│    • Search peers stream intermediate partial results back to the Search Head.          │
│    • Search Head merges all peer responses, completes secondary operations (sorting,    │
│      formatting, final eval, rendering), and writes the final dataset to user session.  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 4. Technical Deep Dive: Configuration, CLI & Knowledge Bundles

### 4.1 Configuring Distributed Search via `distsearch.conf`

Distributed search behavior is controlled primarily by `$SPLUNK_HOME/etc/system/local/distsearch.conf` on the Search Head:

```ini
[distributedSearch]
# Enable distributed search functionality
disabled = false

# Explicit list of search peers (Indexers) connected to this Search Head
servers = https://idx-01.corp.local:8089, https://idx-02.corp.local:8089, https://idx-03.corp.local:8089

# Timeout in seconds when establishing connection or waiting for peer handshake
statusTimeout = 10
connectionTimeout = 10
sendRcvTimeout = 60

# Share bundles across peers (avoids re-uploading identical bundles)
shareBundles = true

[replicationSettings]
# Replicate configuration bundles to peers over REST
replicationPolicy = classic

# Maximum time (seconds) to wait for a peer to complete bundle download
bundleSendTimeout = 300
```

---

### 4.2 Managing Search Peers via the Splunk CLI

Administrators frequently add, remove, and audit search peers using the command line:

```bash
# 1. Add a new search peer (requires remote admin credentials to exchange trust keys)
/opt/splunk/bin/splunk add search-server https://idx-01.corp.local:8089 \
  -auth admin:LocalAdminPass \
  -remoteAuth admin:RemoteIdxPass

# 2. List all search peers and their operational health status
/opt/splunk/bin/splunk list search-server -auth admin:LocalAdminPass

# 3. Temporarily disable a search peer during maintenance
/opt/splunk/bin/splunk edit search-server https://idx-01.corp.local:8089 -status disabled

# 4. Remove a decommissioned search peer
/opt/splunk/bin/splunk remove search-server https://idx-01.corp.local:8089
```

---

### 4.3 Knowledge Bundle Replication & Bundle Bloat Optimization

The Knowledge Bundle contains search-time knowledge objects (field extractions, lookups, macros, tags) that search peers need to interpret data during the Map phase.

> [!WARNING]
> **The Danger of Knowledge Bundle Bloat:**  
> By default, Splunk includes all files in `$SPLUNK_HOME/etc/apps/` and `$SPLUNK_HOME/etc/system/` in the knowledge bundle.  
> If an administrator places large CSV lookup files (e.g., 2 GB IP threat lists), temporary test files, or Git history directories (`.git/`) into an app, the bundle size balloons to gigabytes!  
> Every new search job triggers a bundle sync over the network, causing severe search latency, disk exhaustion on indexers, and search timeouts.

#### Protecting Against Bundle Bloat in `distsearch.conf`:
```ini
[replicationBlacklist]
# Exclude giant CSV lookups from replicating (read dynamically from NFS/S3 instead)
giant_lookups = apps/*/lookups/*.large.csv

# Exclude all Git repositories and hidden files
git_dirs = (apps|system)/*/\.git*

# Exclude temporary backup and log files
temp_backups = (apps|system)/*/*~
```

---

### 4.4 Diagnostic SPL: Auditing Search Peer Performance

Run these queries on the Search Head to inspect search peer health and identify stragglers:

```spl
# Query 1: Search Peer Latency & Response Times
index=_internal sourcetype=splunkd component=DispatchManager "peer="
| stats avg(elapsed_ms) as avg_latency_ms, max(elapsed_ms) as max_latency_ms by peer
| sort - max_latency_ms

# Query 2: Knowledge Bundle Size & Replication Timing
index=_internal sourcetype=splunkd component=BundleWriter OR component=KeyDist
| stats latest(bundle_size_kb) as bundle_kb, avg(duration_ms) as avg_duration_ms by host
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               5 CRITICAL DISTRIBUTED SEARCH PITFALLS                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. THE KNOWLEDGE BUNDLE TSUNAMI (Bundle Bloat)                                          │
│    • Symptom: Search jobs take 45 seconds before returning the first event.             │
│    • Root Cause: An app contains a 3.5 GB CSV lookup table, bloating the bundle.       │
│    • Fix: Add blacklist rules in `distsearch.conf [replicationBlacklist]`.              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. ASYMMETRIC SEARCH PEER HARDWARE (The Straggler Effect)                               │
│    • Symptom: 9 indexers have 32 vCPU/64 GB RAM, but 1 indexer has 4 vCPU/8 GB RAM.   │
│    • Impact: The entire search query runs at the speed of the slowest indexer!          │
│    • Fix: Ensure homogeneous hardware specifications across all search peers.          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. THE "QUARANTINED" PEER INCIDENT                                                      │
│    • Symptom: A search peer transitions to `Quarantined` state in `splunk list search-server`.│
│    • Root Cause: Peer repeatedly timed out during bundle replication or search execution│
│    • Fix: Check peer network latency, bundle size, and disk I/O on `var/run/searchpeers`│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. PORT 8089 REST ENCRYPTION & CERTIFICATE MISMATCH                                     │
│    • Symptom: `splunk add search-server` fails with `Handshake failed: SSL error`.      │
│    • Root Cause: Search Head and Indexer have incompatible TLS ciphers or self-signed   │
│      certificates without matching CA trust anchors.                                    │
│    • Fix: Verify root CA trust in `server.conf [sslConfig]` across all instances.       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. REPLICATION DIRECTORY DISK EXHAUSTION                                                │
│    • Symptom: Search peers crash with `No space left on device` in `/opt/splunk/var`.  │
│    • Root Cause: Stale unpruned bundle tarballs accumulating in `var/run/searchpeers/`. │
│    • Fix: Verify `bundleCleaningDirectoryThreshold` in `server.conf`.                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 6. Cyber Range Practical Lab: Room P7-01

Ready to troubleshoot distributed search bottlenecks and quarantine broken peers?  
Jump straight into the hands-on simulated arena:

👉 **[Enter Cyber Range Room P7-01: The Search Head Dispatch Nexus](../Labs/Room_P7_01_Distributed_Search_Topology.md)** `[250 XP]`

You will configure search peer pairing over mutual TLS port 8089, diagnose and eradicate a catastrophic 4 GB knowledge bundle bloat, investigate quarantined peers, and capture all 4 operational flags!

---

## 📝 7. End-of-Chapter Self-Check Quiz

### Question 1 (SPLK-1003 Blueprint)
In a Splunk distributed search topology, which component is responsible for compiling the search request, replicating the knowledge bundle, dispatching parallel search jobs to peers, and aggregating the final result set?
- A) The Deployment Server
- B) The Search Head
- C) The Cluster Manager
- D) The Universal Forwarder

### Question 2 (SPLK-1003 Blueprint)
Which Splunk CLI command is used to register a new indexing instance as an active search peer to a Search Head?
- A) `splunk add index-server <peer_ip>:9997`
- B) `splunk add search-server https://<peer_ip>:8089`
- C) `splunk register peer --target <peer_ip>`
- D) `splunk distsearch attach <peer_ip>:8089`

### Question 3 (Performance & Troubleshooting)
Users complain that all searches on the Search Head are experiencing a 30-second initial dispatch delay. Inspection reveals that search peers spend 28 seconds downloading the knowledge bundle before executing the search. What configuration in `distsearch.conf` can resolve this bottleneck?
- A) Increase `phoneHomeIntervalInSecs = 1800`.
- B) Configure `[replicationBlacklist]` to exclude large CSV lookup files and non-essential directories from the replicated bundle.
- C) Set `restartSplunkd = true` on the Search Head.
- D) Disable `distsearch.conf [distributedSearch] shareBundles`.

### Question 4 (Map-Reduce Architecture)
During the execution of the query `index=firewall action=blocked | stats count by src_ip`, what processing takes place on the search peers during the Map phase?
- A) The search peers render the final bar chart visualization and transmit HTML to the browser.
- B) The search peers scan local index files, filter events matching `index=firewall action=blocked`, calculate pre-aggregated summary counts for each `src_ip`, and transmit intermediate results back to the Search Head.
- C) The search peers stream all raw uncompressed event lines across the network to the Search Head for filtering.
- D) The search peers write the results directly to the KV Store database.

### Question 5 (High-Availability & Status)
When an administrator runs `splunk list search-server`, a search peer displays the status **Quarantined**. What does this status indicate?
- A) The search peer was seized by the operating system antivirus scanner.
- B) The Search Head temporarily isolated the search peer and stopped sending it new search jobs because the peer failed consecutive communication or bundle synchronization attempts.
- C) The search peer's license pool has exceeded its daily indexing quota.
- D) The search peer is running in read-only maintenance mode.

---

### 💡 Answers & In-Depth Explanations

1. **Answer: B**  
   *Explanation:* The Search Head coordinates distributed search: it parses the SPL command, builds the execution plan, sends the knowledge bundle and search dispatch to search peers (Indexers), and consolidates/reduces the final output.
2. **Answer: B**  
   *Explanation:* Search peers are added to a Search Head using the REST management port (typically HTTPS port 8089): `splunk add search-server https://<peer_ip>:8089`.
3. **Answer: B**  
   *Explanation:* Large lookup tables or rogue files inside apps bloat the knowledge bundle. Defining blacklist filters under `[replicationBlacklist]` in `distsearch.conf` prevents large files from being packaged and transferred to indexers, restoring sub-second dispatch performance.
4. **Answer: B**  
   *Explanation:* In the Map phase, search peers execute filtering and intermediate calculations (`prestats`) in parallel across their local disk storage. Only condensed intermediate calculations are transmitted to the Search Head, minimizing network traffic.
5. **Answer: B**  
   *Explanation:* A search peer is marked as "Quarantined" when the Search Head detects repeated connection timeouts, unresponsive sockets, or failed bundle syncs. The Search Head stops routing searches to that peer until it passes consecutive health checks.
