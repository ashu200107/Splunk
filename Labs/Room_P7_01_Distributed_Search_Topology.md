# 🎮 Room P7-01: The Search Head Dispatch Nexus

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P7-01: The Search Head Dispatch Nexus        ⭐ DIFFICULTY: Med  │
│ 🎯 TOPIC: Distributed Search, distsearch.conf & Knowledge Bundles       │
│ 💎 REWARD: 250 XP                                  🛡️ CATEGORY: Dist Ops │
│ ⏱️ ESTIMATED TIME: 35 Mins                                              │
│ 🏆 PREREQUISITE: Complete Phase 6 Capstone                             │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical Performance Emergency — Search Grid Frozen!**  
> An urgent alert has been escalated to the Enterprise Architecture team:  
>  
> At 08:30 AM, executive analysts reported that dashboards in the Security Operations Center (SOC) have completely frozen:  
> 1. Simple search queries like `index=main | head 5` are taking **over 45 seconds** just to dispatch!  
> 2. The Search Head (`sh-prod-01`) reports that two of the primary indexers (`idx-02` and `idx-03`) have transitioned into the dreaded **`Quarantined`** state.  
> 3. Network operations reports that gigabytes of data are saturating the management network between the Search Head and Indexers.  
> 4. A newly provisioned indexer `idx-04` is ready for service, but attempts to register it as a search peer fail with authentication handshake errors.  
>  
> Your mission as the Principal Distributed Search Architect:  
> 1. Authenticate and register `idx-04` into the active search peer pool.  
> 2. Triage the search dispatch pipeline and eradicate a catastrophic 3.2 GB knowledge bundle bloat.  
> 3. Recover the quarantined search peers and restore cluster communications.  
> 4. Validate end-to-end Map-Reduce processing using internal telemetry, capturing all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          sh-prod-01 (10.100.1.10:8089 / Web :8000)            │
│ • Existing Indexers:    idx-01 (10.100.2.11:8089) - Active                   │
│                         idx-02 (10.100.2.12:8089) - Quarantined              │
│                         idx-03 (10.100.2.13:8089) - Quarantined              │
│ • New Indexer:          idx-04 (10.100.2.14:8089) - Pending Pairing          │
│ • Search Head Config:   /opt/splunk/etc/system/local/distsearch.conf         │
│ • Bloated App Path:     /opt/splunk/etc/apps/DA_threat_intelligence/         │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: About Distributed Search](https://docs.splunk.com/Documentation/Splunk/latest/DistSearch/Aboutdistributedsearch)  
> - 📖 [Splunk Docs: distsearch.conf Specification](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Distsearchconf)  
> - 📖 [Splunk Docs: How Knowledge Bundle Replication Works](https://docs.splunk.com/Documentation/Splunk/latest/DistSearch/Howbundlereplicationworks)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 7.1 (Describe distributed search architecture and map-reduce processing) & Objective 7.2 (Configure and optimize search peers via `distsearch.conf` and CLI).

---

## 🎯 TASK 1: Authenticating & Registering the New Search Peer (50 XP)

### 📖 Incident Details
Log in to `sh-prod-01` and list existing search peers:
```bash
/opt/splunk/bin/splunk list search-server -auth admin:SecureSplunkPass2026!
```

Output:
```text
server: https://10.100.2.11:8089 (Status: Active)
server: https://10.100.2.12:8089 (Status: Quarantined)
server: https://10.100.2.13:8089 (Status: Quarantined)
```

The new indexer `idx-04` (`10.100.2.14:8089`) is missing from the distributed search pool.

### 🛠️ Execution Steps
Register `idx-04` using the CLI:
```bash
/opt/splunk/bin/splunk add search-server https://10.100.2.14:8089 \
  -auth admin:SecureSplunkPass2026! \
  -remoteAuth admin:SecureSplunkPass2026!
```

Verify output confirms that cryptographic public keys and mutual trust anchors were exchanged:
```text
Added search server: https://10.100.2.14:8089
Status: Active
```

### 🚩 Flag 1 Verification
What command registers an indexer to a search head over management port 8089?

<details>
<summary>💡 Need a hint?</summary>
Use <code>splunk add search-server https://&lt;ip&gt;:8089</code>.
</details>

**Flag:** `FLAG{SPLUNK_PEER_PAIRING_AUTHENTICATED}`

---

## 🎯 TASK 2: Investigating & Eradicating Knowledge Bundle Bloat (75 XP)

### 📖 Incident Details
Inspect the search head bundle generation log in `splunkd.log`:
```bash
grep -i "bundle" /opt/splunk/var/log/splunk/splunkd.log | tail -n 15
```

You observe:
```text
WARN  BundleWriter - Creating knowledge bundle with total uncompressed size: 3421500 KB (3.26 GB)!
WARN  DistSearch - Uploading bundle to peer idx-02 timed out after 30000ms!
```

A threat intelligence app `DA_threat_intelligence` contains a 3.2 GB raw CSV file:
```bash
ls -lh /opt/splunk/etc/apps/DA_threat_intelligence/lookups/
```
Output:
`global_threat_feed_2026.csv` (Size: 3.2 GB!)

Every search job attempts to compress and replicate this 3.2 GB file over the network to all four indexers, choking the management network.

### 🛠️ Remediation Steps
1. Edit `/opt/splunk/etc/system/local/distsearch.conf` on `sh-prod-01`:
   ```ini
   [replicationBlacklist]
   giant_csv = apps/DA_threat_intelligence/lookups/*.csv
   git_folders = (apps|system)/*/\.git*
   ```
2. Force the Search Head to regenerate a clean knowledge bundle:
   ```bash
   /opt/splunk/bin/splunk reload search-server -auth admin:SecureSplunkPass2026!
   ```
3. Check `splunkd.log`:
   The newly generated bundle is only **1.4 MB**, down from **3.2 GB**!

### 🚩 Flag 2 Verification
**Flag:** `FLAG{SPLUNK_BUNDLE_BLOAT_ELIMINATED}`

---

## 🎯 TASK 3: Recovering the Quarantined Search Peers (50 XP)

### 📖 Incident Details
With the bundle size reduced, `idx-02` and `idx-03` remain in the `Quarantined` state because the Search Head isolated them following consecutive timeout failures.

### 🛠️ Execution Steps
1. Re-enable and test communication to each quarantined peer:
   ```bash
   /opt/splunk/bin/splunk edit search-server https://10.100.2.12:8089 -status active -auth admin:SecureSplunkPass2026!
   /opt/splunk/bin/splunk edit search-server https://10.100.2.13:8089 -status active -auth admin:SecureSplunkPass2026!
   ```
2. Verify all peers return to healthy `Active` status:
   ```bash
   /opt/splunk/bin/splunk list search-server -auth admin:SecureSplunkPass2026!
   ```
   Output:
   ```text
   server: https://10.100.2.11:8089 (Status: Active)
   server: https://10.100.2.12:8089 (Status: Active)
   server: https://10.100.2.13:8089 (Status: Active)
   server: https://10.100.2.14:8089 (Status: Active)
   ```

### 🚩 Flag 3 Verification
**Flag:** `FLAG{SPLUNK_PEER_QUARANTINE_RECOVERED}`

---

## 🎯 TASK 4: Validating Map-Reduce Processing in Job Inspector (75 XP)

### 📖 Incident Details
Run a test distributed query from the Search Head:
```bash
/opt/splunk/bin/splunk search "index=_internal sourcetype=splunkd | stats count by component" -preview false
```

Inspect the dispatch directory telemetry:
```bash
grep -E "peerCount|duration" /opt/splunk/var/run/splunk/dispatch/*/info.csv | tail -n 5
```

Output:
```text
peerCount = 4
duration_ms = 312
```

All 4 indexers executed the Map phase in parallel across their local disk storage, streaming pre-aggregated counts back to `sh-prod-01` in only **312 milliseconds**!

### 🚩 Flag 4 Verification
**Flag:** `FLAG{SPLUNK_MAP_REDUCE_TELEMETRY_VERIFIED}`

---

## 🏆 Room Summary & Operator Promotion

```text
╔══════════════════════════════════════════════════════════════════════════╗
│                    ROOM P7-01 COMPLETION CERTIFICATE                     │
╠══════════════════════════════════════════════════════════════════════════╣
│ • Task 1: Search Peer Mutual TLS Registration         [50 XP]            │
│ • Task 2: 3.2 GB Knowledge Bundle Bloat Eradication   [75 XP]            │
│ • Task 3: Quarantined Peer Diagnostics & Recovery     [50 XP]            │
│ • Task 4: Sub-Second Distributed Map-Reduce Telemetry [75 XP]            │
│                                                                          │
│ 🏅 Total Room XP Earned: 250 XP                                          │
│ 🎖️ Master Status: Splunk Distributed Search Specialist                   │
╚══════════════════════════════════════════════════════════════════════════╝
```
