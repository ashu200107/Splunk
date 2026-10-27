# 🎮 Room P7-02: Single-Site Indexer Cluster Forge

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P7-02: Single-Site Indexer Cluster Forge    ⭐ DIFFICULTY: Med  │
│ 🎯 TOPIC: Cluster Manager, RF=3, SF=2 & Peer Failover                   │
│ 💎 REWARD: 250 XP                                  🛡️ CATEGORY: High Avail│
│ ⏱️ ESTIMATED TIME: 40 Mins                                              │
│ 🏆 PREREQUISITE: Room P7-01                                            │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical High-Availability Mission — The Zero-Downtime Cluster!**  
> The enterprise infrastructure board has mandated a strict zero-data-loss architecture:  
>  
> The existing standalone indexers must be forged into a resilient **Single-Site Indexer Cluster**:  
> 1. The Cluster Manager (`cm-prod-01`) must enforce **Replication Factor $RF=3$** and **Search Factor $SF=2$**.  
> 2. Three peer indexers (`idx-01`, `idx-02`, and `idx-03`) must be joined to the cluster over dedicated high-speed Replication Port 9887.  
> 3. The Search Head (`sh-prod-01`) must be configured to discover peers dynamically from the Cluster Manager, preventing duplicate search results.  
> 4. To certify disaster readiness, you will simulate the sudden catastrophic power failure of `idx-01` and verify that the Cluster Manager automatically promotes a secondary copy to **Primary** within 500 milliseconds!  
>  
> Your mission as the Principal High-Availability Cluster Architect:  
> 1. Configure and boot the Cluster Manager control plane.  
> 2. Bind replication ports and symmetric authentication keys on all peer indexers.  
> 3. Connect the Search Head to the cluster.  
> 4. Execute a live failure test, verify cluster fixup policies, and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Cluster Manager:      cm-prod-01 (10.100.5.10:8089)                        │
│ • Peer Indexer 01:      idx-01 (10.100.5.21:8089 / S2S: 9997 / Repl: 9887)   │
│ • Peer Indexer 02:      idx-02 (10.100.5.22:8089 / S2S: 9997 / Repl: 9887)   │
│ • Peer Indexer 03:      idx-03 (10.100.5.23:8089 / S2S: 9997 / Repl: 9887)   │
│ • Search Head:          sh-prod-01 (10.100.1.10:8089)                        │
│ • Symmetric Cluster Key:SecureClusterSecret2026!                             │
│ • Target Policies:      Replication Factor = 3, Search Factor = 2            │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: Configure the Cluster Manager](https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Configurethemaster)  
> - 📖 [Splunk Docs: Configure Peer Nodes](https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Configurepeers)  
> - 📖 [Splunk Docs: Connect Search Heads to Indexer Clusters](https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Connectthesearchhead)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 8.1 (Configure single-site indexer cluster manager and peer nodes) & Objective 8.2 (Define and differentiate Replication Factor and Search Factor).

---

## 🎯 TASK 1: Initializing the Cluster Manager Control Plane (50 XP)

### 📖 Execution Steps
Log in to `cm-prod-01` and configure cluster manager mode via the CLI:

```bash
/opt/splunk/bin/splunk edit cluster-config \
  -mode master \
  -replication_factor 3 \
  -search_factor 2 \
  -secret SecureClusterSecret2026! \
  -auth admin:SecureSplunkPass2026!
```

Restart `splunkd` on the Cluster Manager:
```bash
/opt/splunk/bin/splunk restart
```

Inspect the generated configuration:
```bash
cat /opt/splunk/etc/system/local/server.conf | grep -A 6 "\[clustering\]"
```

Output confirms:
```ini
[clustering]
mode = master
replication_factor = 3
search_factor = 2
pass4SymmKey = $7$w8K... (Encrypted Hash)
```

### 🚩 Flag 1 Verification
What command configures an instance as a Cluster Manager with $RF=3$ and $SF=2$?

<details>
<summary>💡 Need a hint?</summary>
Use <code>splunk edit cluster-config -mode master ...</code>.
</details>

**Flag:** `FLAG{SPLUNK_CLUSTER_MANAGER_INITIALIZED}`

---

## 🎯 TASK 2: Binding Replication Ports & Joining Peer Nodes (75 XP)

### 📖 Execution Steps
On each peer indexer (`idx-01`, `idx-02`, and `idx-03`), configure slave mode and open Replication Port 9887:

```bash
# Execute on idx-01, idx-02, and idx-03
/opt/splunk/bin/splunk edit cluster-config \
  -mode slave \
  -master_uri https://10.100.5.10:8089 \
  -replication_port 9887 \
  -secret SecureClusterSecret2026! \
  -auth admin:SecureSplunkPass2026!

/opt/splunk/bin/splunk restart
```

Now verify on the Cluster Manager (`cm-prod-01`):
```bash
/opt/splunk/bin/splunk list cluster-peers -auth admin:SecureSplunkPass2026!
```

Output:
```text
Peer: idx-01 (10.100.5.21) - Status: Up (Active)
Peer: idx-02 (10.100.5.22) - Status: Up (Active)
Peer: idx-03 (10.100.5.23) - Status: Up (Active)
Total active peers: 3
```

Check cluster health status:
```bash
/opt/splunk/bin/splunk show cluster-status -auth admin:SecureSplunkPass2026!
```
Output:
```text
Replication factor: Met (3/3)
Search factor: Met (2/2)
All data is searchable: Yes
```

### 🚩 Flag 2 Verification
**Flag:** `FLAG{SPLUNK_PEER_REPLICATION_PORT_BOUND}`

---

## 🎯 TASK 3: Connecting Search Head via Cluster Discovery (50 XP)

### 📖 Execution Steps
Log in to the Search Head `sh-prod-01`.  
Instead of adding individual indexers manually via `distsearch.conf`, configure the Search Head in `mode = searchhead` pointing directly to the Cluster Manager:

```bash
/opt/splunk/bin/splunk edit cluster-config \
  -mode searchhead \
  -master_uri https://10.100.5.10:8089 \
  -secret SecureClusterSecret2026! \
  -auth admin:SecureSplunkPass2026!

/opt/splunk/bin/splunk restart
```

Verify dynamic peer discovery on `sh-prod-01`:
```bash
/opt/splunk/bin/splunk list search-server -auth admin:SecureSplunkPass2026!
```
The Search Head automatically discovers all 3 clustered indexers from the Cluster Manager! When new indexers join the cluster in the future, the Search Head discovers them dynamically without requiring any manual configuration!

### 🚩 Flag 3 Verification
**Flag:** `FLAG{SPLUNK_SEARCHHEAD_CLUSTER_ATTACHED}`

---

## 🎯 TASK 4: Simulating Peer Catastrophic Failure & Primary Promotion (75 XP)

### 📖 Failure Simulation
Simulate a sudden physical power loss on `idx-01` by killing the `splunkd` process:
```bash
# On idx-01
pkill -9 splunkd
```

Immediately log in to the Cluster Manager (`cm-prod-01`) and monitor cluster response:
```bash
/opt/splunk/bin/splunk show cluster-status -auth admin:SecureSplunkPass2026!
```

You observe:
```text
Peer idx-01: Offline (Missed 3 heartbeats)
Replication factor: Fixup scheduled (2/3)
Search factor: Met (2/2)
All data is searchable: YES
```

Execute a search query on `sh-prod-01`:
```bash
/opt/splunk/bin/splunk search "index=* | head 10" -auth admin:SecureSplunkPass2026!
```
Output: All queries return complete, accurate results with **zero missing events and zero duplicate records**!  
The Cluster Manager instantaneously promoted the searchable copy on `idx-02` to **Primary**, maintaining 100% search continuity without a single microsecond of downtime!

### 🚩 Flag 4 Verification
**Flag:** `FLAG{SPLUNK_PRIMARY_BUCKET_FAILOVER_MET}`

---

## 🏆 Room Summary & Operator Promotion

```text
╔══════════════════════════════════════════════════════════════════════════╗
│                    ROOM P7-02 COMPLETION CERTIFICATE                     │
╠══════════════════════════════════════════════════════════════════════════╣
│ • Task 1: Cluster Manager Control Plane Initialization [50 XP]           │
│ • Task 2: Peer Replication Port Binding (Port 9887)    [75 XP]           │
│ • Task 3: Dynamic Search Head Cluster Discovery       [50 XP]            │
│ • Task 4: Catastrophic Node Failover & Primary Promo  [75 XP]            │
│                                                                          │
│ 🏅 Total Room XP Earned: 250 XP                                          │
│ 🎖️ Master Status: Splunk High-Availability Clustering Specialist         │
╚══════════════════════════════════════════════════════════════════════════╝
```
