# 🎮 Room P6-Capstone: Global Fleet Orchestration Gauntlet

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P6-CAPSTONE: Global Fleet Orchestration Gauntlet ⭐ Expert     │
│ 🎯 TOPIC: Phase 6 Final Capstone Assessment (10,000-Node Fleet)        │
│ 💎 REWARD: 500 XP                                  🛡️ CATEGORY: Capstone│
│ ⏱️ ESTIMATED TIME: 60 Mins                                              │
│ 🏆 PREREQUISITE: Complete Rooms P6-01 through P6-06                    │
└────────────────────────────────────────────────────────────────────────┘
```

> **Mission Briefing: Operation Global Fleet Nexus**  
> Welcome to the Phase 6 Final Capstone Gauntlet, Senior Fleet Orchestrator.  
>  
> The enterprise has acquired a multinational retail corporation, instantly expanding your Splunk deployment footprint from 2,000 forwarders to **12,000 forwarders across three continents (Americas, EMEA, APAC)**.  
>  
> A series of catastrophic configuration missteps and infrastructure bottlenecks have brought centralized management to its knees:  
> 1. The central Deployment Server is choking under a 60-second thundering herd polling wave, failing 70% of phoneHome handshakes.  
> 2. Critical PCI DSS log collection apps are not installing on APAC point-of-sale terminals due to broken server class index sequences.  
> 3. Hundreds of newly deployed AWS EC2 instances are colliding onto a single GUID on the Deployment Server console.  
> 4. The automated GitOps CI/CD delivery pipeline has stalled because an illegal `local/` folder and malformed syntax crept into `inputs.conf`.  
> 5. A continuous lookup restart storm is disrupting live payment transaction streams, while a decommissioned legacy poller continues running rogue on 1,500 hosts!  
>  
> You must execute a complete 5-stage fleet restoration, enforce zero-downtime lifecycle controls, and capture all 5 master flags to claim the rank of **Master Enterprise Fleet Orchestrator**!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ ENTERPRISE GLOBAL FLEET TOPOLOGY                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Central Deployment Server:  ds-amer-01 (10.100.5.20:8089)                  │
│ • Regional Staging DS:        ds-emea-01 (10.120.5.20:8089)                  │
│ • Fleet Scale:                12,000 Universal Forwarders                    │
│ • GitOps Staging Root:        /opt/splunk/git-repos/deployment-apps/         │
│ • Production Apps Path:       /opt/splunk/etc/deployment-apps/               │
│ • Central Configuration:      /opt/splunk/etc/system/local/serverclass.conf  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 STAGE 1: High-Scale Polling Optimization & Socket Tuning (100 XP)

### 📖 Incident Brief
With 12,000 forwarders polling every 60 seconds, `ds-amer-01` is being battered by **200 HTTPS connections per second**! CPU is pinned at 100%, and the operating system is rejecting sockets with `errno 24 (Too many open files)`.

### 🛠️ Execution Runbook
1. Tune the global polling baseline app `/opt/splunk/etc/deployment-apps/Org_all_deploymentclient/default/deploymentclient.conf`:
   ```ini
   [deployment-client]
   phoneHomeIntervalInSecs = 900
   ```
2. Tune Linux kernel file descriptors in `/etc/security/limits.conf`:
   ```text
   splunk  soft  nofile  65535
   splunk  hard  nofile  65535
   ```
3. Tune network socket queues in `/etc/sysctl.conf`:
   ```text
   net.core.somaxconn = 4096
   net.ipv4.tcp_tw_reuse = 1
   ```
4. Apply kernel parameters: `sysctl -p`.
5. Incoming request rate drops from 200 req/sec down to **13.3 req/sec**, stabilizing the control plane!

### 🚩 Flag 1 Verification
**Flag:** `FLAG{SPLUNK_CAPSTONE_P6_SCALE_RESCUED}`

---

## 🎯 STAGE 2: Server Class Precision Surgery & Filter Repair (100 XP)

### 📖 Incident Brief
Inspect `/opt/splunk/etc/system/local/serverclass.conf`. The PCI POS terminals in APAC are failing to receive `Splunk_TA_pci_pos`:
```ini
[serverClass:APAC_POS_Terminals]
whitelist.0 = apac-pos-tokyo-*
whitelist.1 = apac-pos-sydney-*
whitelist.3 = apac-pos-singapore-*
[serverClass:APAC_POS_Terminals:app:Splunk_TA_pci_pos]
```

### 🛠️ Execution Runbook
1. Notice the fatal index gap: `whitelist.2` is missing, which causes Splunk to immediately terminate parser evaluation and ignore `whitelist.3`!
2. Renumber `whitelist.3` to `whitelist.2`:
   ```ini
   [serverClass:APAC_POS_Terminals]
   whitelist.0 = apac-pos-tokyo-*
   whitelist.1 = apac-pos-sydney-*
   whitelist.2 = apac-pos-singapore-*
   ```
3. Add the machine architecture filter to prevent pushing x86_64 binaries to ARM appliances:
   ```ini
   machineTypesFilter = linux-x86_64
   ```
4. Perform a surgical precision reload:
   ```bash
   /opt/splunk/bin/splunk reload deploy-server -class APAC_POS_Terminals -auth admin:SecureSplunkPass2026!
   ```

### 🚩 Flag 2 Verification
**Flag:** `FLAG{SPLUNK_CAPSTONE_P6_SERVERCLASS_REPAIRED}`

---

## 🎯 STAGE 3: Cloned VM GUID Collision & DNS Triage (100 XP)

### 📖 Incident Brief
The AWS cloud team provisioned 400 new forwarders from a single EC2 AMI. On `ds-amer-01`, `splunk list deploy-clients` shows only **1 single active forwarder** flickering furiously between 400 private IP addresses!

### 🛠️ Execution Runbook
1. Identify the root cause: The AMI was snapshotted after Splunk was already initialized, duplicating `/opt/splunkforwarder/etc/instance.cfg`.
2. Execute the fleet remediation script across the EC2 forwarders:
   ```bash
   # Remove duplicate GUID file and reboot forwarder daemon
   rm -f /opt/splunkforwarder/etc/instance.cfg
   /opt/splunkforwarder/bin/splunk restart
   ```
3. Verify on `ds-amer-01`:
   ```bash
   /opt/splunk/bin/splunk list deploy-clients | grep "clientName" | wc -l
   ```
   All 400 forwarders now register with independent, globally unique 128-bit GUIDs!

### 🚩 Flag 3 Verification
**Flag:** `FLAG{SPLUNK_CAPSTONE_P6_FLEET_TRIAGED}`

---

## 🎯 STAGE 4: GitOps CI/CD, AppInspect & Automated REST Reload (100 XP)

### 📖 Incident Brief
A contractor committed an untested app `Org_threat_feed` containing an illegal `local/` directory and unclosed brackets in `inputs.conf`, breaking the automated delivery pipeline.

### 🛠️ Execution Runbook
1. In the GitOps repository `/opt/splunk/git-repos/deployment-apps/Org_threat_feed/`:
   ```bash
   # Merge local into default and purge local/
   cat local/inputs.conf >> default/inputs.conf
   rm -rf local/
   ```
2. Run `ksconf` syntax repair and stanza sorting:
   ```bash
   ksconf check .
   ksconf sort --inplace default/inputs.conf
   ```
3. Run Splunk AppInspect quality gate:
   ```bash
   splunk-appinspect inspect . --mode precert
   ```
   Zero failures achieved!
4. Sync to `/opt/splunk/etc/deployment-apps/` and trigger the zero-downtime REST reload:
   ```bash
   curl -k -u admin:SecureSplunkPass2026! \
     -X POST https://ds-amer-01:8089/services/deployment/server/config/_reload
   ```

### 🚩 Flag 4 Verification
**Flag:** `FLAG{SPLUNK_CAPSTONE_P6_GITOPS_AUTOMATED}`

---

## 🎯 STAGE 5: Zero-Downtime Lifecycle & Zombie App Exorcism (100 XP)

### 📖 Incident Brief
1. A threat intelligence CSV lookup app is causing 12,000 forwarders to reboot four times a day because `restartSplunkd = true` is enabled.
2. A decommissioned legacy app `Org_legacy_metric_collector` was removed from `serverclass.conf`, but the forwarders are **still executing its legacy Python collector**!

### 🛠️ Execution Runbook
1. In `serverclass.conf`, update the lookup app to zero-downtime hot reloading:
   ```ini
   [serverClass:Global_Fleet:app:Org_threat_feed]
   restartSplunkd = false
   issueReload = true
   stateOnClient = enabled
   ```
2. Eradicate the orphaned zombie app using the official 3-phase de-provisioning protocol:
   - Re-add the app to `serverclass.conf` with `stateOnClient = disabled` and `restartSplunkd = true`:
     ```ini
     [serverClass:Global_Fleet:app:Org_legacy_metric_collector]
     stateOnClient = disabled
     restartSplunkd = true
     ```
   - Reload the server class:
     ```bash
     /opt/splunk/bin/splunk reload deploy-server -class Global_Fleet -auth admin:SecureSplunkPass2026!
     ```
   - Forwarders phone home, write `state = disabled`, terminate the Python script, and cleanly shut down the legacy input!

### 🚩 Flag 5 Verification
**Flag:** `FLAG{SPLUNK_CAPSTONE_P6_LIFECYCLE_MASTERED}`

---

## 🏆 Capstone Gauntlet Completion & Master Operator Promotion

```text
╔══════════════════════════════════════════════════════════════════════════╗
│               PHASE 6 CAPSTONE GAUNTLET COMPLETION TROPHY                │
╠══════════════════════════════════════════════════════════════════════════╣
│ • Stage 1: High-Scale 10k Sizing & Socket Architecture   [100 XP]        │
│ • Stage 2: Server Class Precision Surgery & Filtering    [100 XP]        │
│ • Stage 3: Cloned GUID Collision & Forwarder Triage       [100 XP]        │
│ • Stage 4: GitOps CI/CD & Automated REST Webhook         [100 XP]        │
│ • Stage 5: Zero-Downtime Lifecycle & Zombie App Exorcism [100 XP]        │
│                                                                          │
│ 🏅 Total Capstone XP Earned: 500 XP                                      │
│ 🏆 Phase 6 Total Points:     2,100 / 2,100 XP (100% COMPLETE!)            │
│ 🌟 CUMULATIVE SCORE:         11,100 XP                                   │
│ 🚀 CERTIFIED RANK:           MASTER ENTERPRISE FLEET ORCHESTRATOR        │
╚══════════════════════════════════════════════════════════════════════════╝
```
