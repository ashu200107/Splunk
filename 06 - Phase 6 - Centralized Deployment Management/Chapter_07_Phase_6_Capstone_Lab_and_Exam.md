# 🏆 Chapter 07 (Phase 6): Phase 6 Capstone Lab & Deployment Fleet Master Exam

> **The Splunk Administrator's Definitive Handbook** | Phase 6: Centralized Deployment Management  
> **Day:** 53 | **Milestone:** Phase 6 Capstone Assessment, 10 Enterprise Scenario Drills & Global Fleet Master Exam  
> **Current Rank:** Master Enterprise Fleet Orchestrator (10,600 XP) $\rightarrow$ *Promotion Target: Master Enterprise Fleet Orchestrator (11,100+ XP — Phase 6 Master Certified)*  
> **Second Brain File:** `Chapter_07_Phase_6_Capstone_Lab_and_Exam.md`  
> **Interactive Cyber Range Lab:** [Room P6-Capstone: Global Fleet Orchestration Gauntlet](../Labs/Room_P6_Capstone_Global_Fleet_Orchestration.md) `[500 XP]`  
>  
> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: Plan a Deployment Server Deployment & Sizing](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Planadeployment)  
> - 📖 [Splunk Docs: serverclass.conf Configuration Specification](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Serverclassconf)  
> - 📖 [Splunk Docs: deploymentclient.conf Specification](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Deploymentclientconf)  
> - 📖 [Splunk Docs: Deployment Server REST API Endpoints](https://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTdeploy)  
> - 📖 [Splunk Developer Docs: Test and Validate Apps with Splunk AppInspect](https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Section 6.0 — Deployment Server Management (100% comprehensive mastery across Objectives 6.1, 6.2, 6.3, and 6.4).  
> - 🎯 **Splunk Core Certified Power User (SPLK-1002):** Section 4.0 — Enterprise Knowledge Distribution & App Architecture.

---

## 🌐 1. Executive Summary & Capstone Architecture

Phase 6 synthesized the administration of enterprise Splunk forwarder fleets at massive scale. As an Enterprise Splunk Administrator, your responsibility spans from single-server deployment pairing to coordinating 15,000+ geographically distributed endpoints across multi-cloud environments.

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│               PHASE 6 CAPSTONE ARCHITECTURAL MASTERY MAP                                  │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ENTERPRISE GITOPS & CI/CD CONTROL PLANE                                                 │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Git Repo: splunk-deployment-apps                                                  │   │
│   │ ├── Linting & Normalization: ksconf check && ksconf sort                          │   │
│   │ ├── Quality Gate: splunk-appinspect inspect --mode precert (0 failures)          │   │
│   │ └── Automated Webhook: POST /services/deployment/server/config/_reload            │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │ Automated Sync                              │
│                                             ▼                                             │
│   TIER 1: HIGH-SCALE DEDICATED DEPLOYMENT SERVERS (Port 8089)                             │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ • Dedicated VM (16 vCPU, 32 GB RAM, 10 GbE NIC) — NEVER co-located on Indexer!    │   │
│   │ • OS Sockets: ulimit -n 65535, somaxconn = 4096, tcp_tw_reuse = 1                 │   │
│   │ • serverclass.conf: Granular Whitelist/Blacklist Regex, machineTypesFilter        │   │
│   │ • Bandwidth Throttling: maxBandwidth = 10000 (10 MB/s cap)                        │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │ Staggered phoneHome Window (900s ± 10%)     │
│                                             ▼                                             │
│   TIER 2: GLOBAL UNIVERSAL FORWARDER FLEET (15,000+ Deployment Clients)                   │
│   ┌──────────────────────────────────┐             ┌──────────────────────────────────┐   │
│   │ Linux App Tier (8,000 Nodes)     │             │ Windows Domain Tier (7,000 Nodes)│   │
│   │ • targetUri = ds-amer.corp:8089  │             │ • targetUri = ds-amer.corp:8089  │   │
│   │ • restartSplunkd = true (inputs) │             │ • restartSplunkd = false (lookups│   │
│   │ • Unique instance.cfg GUID       │             │ • stateOnClient = enabled        │   │
│   └──────────────────────────────────┘             └──────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 2. Phase 6 Master Certification Exam: 10 Milestone Scenario Drills

This capstone exam rigorously tests production problem-solving, architectural design, CLI mastery, and error mitigation aligned directly with the **SPLK-1003 Splunk Enterprise Certified Admin** exam blueprint.

---

### Scenario 1: The Co-Location Performance Catastrophe
**Problem Statement:**  
A junior administrator deployed the Splunk Deployment Server role onto an active Production Indexer handling 350 GB/day of ingestion. Two weeks later, forwarders report massive TCP connection timeouts, indexing queues are blocked, and search queries frequently fail.  
**Question:**  
Explain the architectural root cause of this failure and specify the official Splunk sizing recommendation for Deployment Server placement.  
**Official Answer & Technical Explanation:**  
- **Root Cause:** S2S ingestion (TCP 9997) and Deployment Server REST phoneHome polling (TCP 8089) both compete for the same OS file descriptors, network sockets, memory buffers, and CPU cycles. Furthermore, when thousands of forwarders phone home simultaneously, the high SSL/TLS handshake volume exhausts CPU resources, starving the indexing and parsing pipelines.  
- **Official Architecture Rule:** In fleets exceeding **50 forwarders**, the Deployment Server **MUST be hosted on a dedicated, standalone Splunk Enterprise instance**. It must never be co-located with an Indexer or a Search Head.

---

### Scenario 2: High-Scale Request Rate Mathematics
**Problem Statement:**  
An enterprise expands its forwarder fleet from 500 to 12,000 clients. The default `phoneHomeIntervalInSecs = 60` is currently active.  
**Question:**  
1. Calculate the incoming REST connection rate (requests per second) hitting the Deployment Server under default settings.  
2. Propose the optimized `phoneHomeIntervalInSecs` value for a 12,000-node fleet and calculate the new request rate.  
**Official Answer & Technical Explanation:**  
1. **Default Rate:**  
   $$\text{Arrival Rate} = \frac{12,000 \text{ clients}}{60 \text{ seconds}} = 200 \text{ incoming HTTPS connections/second}$$  
   At 200 handshakes/sec, the Deployment Server suffers severe TCP socket exhaustion (`errno 24 Too many open files`) and crashes `splunkd`.  
2. **Optimized Sizing:**  
   For fleets between 5,000 and 15,000 clients, Splunk officially recommends `phoneHomeIntervalInSecs = 900` (15 minutes) to `1800` (30 minutes).  
   $$\text{Optimized Rate (at 900s)} = \frac{12,000 \text{ clients}}{900 \text{ seconds}} = 13.3 \text{ connections/second}$$  
   At 13.3 requests/second, the Deployment Server handles traffic smoothly with negligible CPU and socket overhead.

---

### Scenario 3: The Broken Whitelist Regex Array
**Problem Statement:**  
An administrator authors the following server class stanza to assign an application to web servers:
```ini
[serverClass:WebTier]
whitelist.0 = web-prod-*.corp.local
whitelist.1 = web-dmz-*.corp.local
whitelist.3 = web-api-*.corp.local
[serverClass:WebTier:app:Splunk_TA_nginx]
```
Clients named `web-api-01.corp.local` report that they are not receiving `Splunk_TA_nginx`.  
**Question:**  
Why are the `web-api` hosts excluded, and how must the stanza be corrected?  
**Official Answer & Technical Explanation:**  
- **Root Cause:** Splunk configuration parsers require integer index arrays (`whitelist.<n>` and `blacklist.<n>`) to be **strictly contiguous starting from zero** (`0, 1, 2, ...`). The configuration contains a numerical gap: `whitelist.2` was skipped, jumping straight from `whitelist.1` to `whitelist.3`.  
- When Splunk encounters a numerical gap, **it terminates evaluation of the array immediately**! Thus, `whitelist.3` is completely ignored.  
- **Remediation:** Renumber `whitelist.3` to `whitelist.2`.

---

### Scenario 4: The Golden Template Cloned GUID Collision
**Problem Statement:**  
Following an automated Terraform rollout of 300 AWS EC2 Universal Forwarders, the Deployment Server's `splunk list deploy-clients` output displays only 1 total connected client. Running the command repeatedly shows the IP address and client name alternating every second.  
**Question:**  
Identify the specific file responsible for this behavior and describe the step-by-step remediation runbook.  
**Official Answer & Technical Explanation:**  
- **Responsible File:** `$SPLUNK_HOME/etc/instance.cfg` (which stores the persistent `guid = <UUID>`).  
- **Root Cause:** The AMI / golden image was captured after Splunk had already started on the base machine. Consequently, all 300 instances inherited the identical GUID. The Deployment Server keys its internal forwarder registry on GUID; every check-in simply overwrites the previous client's record!  
- **Remediation Runbook:**  
  1. Stop the forwarder daemon: `/opt/splunkforwarder/bin/splunk stop`.  
  2. Remove the instance configuration file: `rm -f /opt/splunkforwarder/etc/instance.cfg`.  
  3. Start the forwarder daemon: `/opt/splunkforwarder/bin/splunk start`.  
  4. On startup, Splunk detects the absence of `instance.cfg`, generates a brand-new random GUID, and registers as an independent client.

---

### Scenario 5: Surgical Precision Server Class Reload
**Problem Statement:**  
A Deployment Server manages 8,500 clients distributed across 60 server classes. You updated the configuration of an application called `Splunk_TA_pci_compliance` mapped strictly to the server class `SecOps_PCI_Scope`.  
**Question:**  
What CLI command should you run to activate these changes with minimum CPU impact on the Deployment Server?  
**Official Answer & Technical Explanation:**  
- **Command:**  
  ```bash
  $SPLUNK_HOME/bin/splunk reload deploy-server -class SecOps_PCI_Scope
  ```  
- **Explanation:** Running `splunk reload deploy-server` without arguments triggers a global re-scan and checksum recalculation across all 60 server classes and thousands of apps, causing an unnecessary CPU spike. Passing the `-class <name>` argument limits the reload strictly to the affected server class.

---

### Scenario 6: GitOps Directory Precedence Hygiene
**Problem Statement:**  
An engineer packages an application for distribution via the Deployment Server. The application contains configurations in both `$SPLUNK_HOME/etc/deployment-apps/Org_syslog_inputs/default/` and `$SPLUNK_HOME/etc/deployment-apps/Org_syslog_inputs/local/`.  
**Question:**  
Why is including a `local/` folder inside a deployment application considered a severe architectural anti-pattern?  
**Official Answer & Technical Explanation:**  
- When the Deployment Server distributes an app bundle to a forwarder, the bundle lands in `$SPLUNK_HOME/etc/apps/<app_name>/`.  
- According to Splunk configuration file precedence, an app's `local/` directory overrides its own `default/` directory.  
- If deployment apps deliver settings in `local/`, local forwarder administrators or subsequent centralized override apps cannot easily adjust settings without editing the distributed `local/` directory directly, leading to configuration drift and loss of changes during subsequent app bundle updates.  
- **Enterprise Best Practice:** All deployment applications must package settings **strictly under `default/`**.

---

### Scenario 7: App Lifecycle — Lookup Tables vs Ingestion Inputs
**Problem Statement:**  
You are updating two distinct applications in `serverclass.conf`:  
1. `Org_threat_intel_lookups` (Contains a refreshed 30 MB malicious IP CSV table).  
2. `Org_apache_access_inputs` (Contains newly configured file monitor stanzas in `inputs.conf`).  
**Question:**  
Specify the appropriate `restartSplunkd` and `issueReload` settings for each application and justify your decision based on Splunk internal mechanics.  
**Official Answer & Technical Explanation:**  
1. **For `Org_threat_intel_lookups`:**  
   - `restartSplunkd = false`  
   - `issueReload = true`  
   - *Justification:* Lookups are evaluated at search/query time or read dynamically in-flight. Restarting forwarders or search heads for a lookup table update causes unnecessary downtime and triggers restart storms.  
2. **For `Org_apache_access_inputs`:**  
   - `restartSplunkd = true`  
   - `issueReload = false`  
   - *Justification:* New monitor inputs in `inputs.conf` require `splunkd` to allocate new file descriptor handles and initialize file tailing threads, which requires a clean daemon restart.

---

### Scenario 8: The Orphaned App De-provisioning Trap
**Problem Statement:**  
An administrator unlinks the application `Splunk_TA_legacy_audit` from `serverclass.conf` by deleting the stanza:  
`[serverClass:All_Endpoints:app:Splunk_TA_legacy_audit]`.  
The administrator expects the app to disappear from 2,000 forwarders upon their next check-in.  
**Question:**  
What actually happens on the forwarders, and how do you achieve true removal?  
**Official Answer & Technical Explanation:**  
- **Actual Behavior:** Splunk Deployment Server **does NOT automatically delete applications from clients** when they are removed from `serverclass.conf`! The forwarders simply stop receiving updates for that app; the app remains in `$SPLUNK_HOME/etc/apps/Splunk_TA_legacy_audit` and continues collecting data indefinitely!  
- **Correct De-provisioning Protocol:**  
  1. Update `serverclass.conf` with `stateOnClient = disabled` and `restartSplunkd = true`.  
  2. Reload the Deployment Server and wait for all forwarders to check in and disable the app.  
  3. Replace the app directory in `deployment-apps/` with an empty bundle or execute an automated configuration management script (e.g., Ansible) to purge the directory from `$SPLUNK_HOME/etc/apps/`.

---

### Scenario 9: Staged Deployment via `stateOnClient = noop`
**Problem Statement:**  
The SecOps orchestration team wants the Deployment Server to deliver the configuration files for `Org_edr_sensor` to all 5,000 Linux endpoints, but they do NOT want Splunk to enable or start the sensor until the enterprise maintenance window on Saturday night.  
**Question:**  
Which `stateOnClient` setting satisfies this requirement, and how does it function?  
**Official Answer & Technical Explanation:**  
- **Setting:** `stateOnClient = noop`  
- **Mechanism:** `noop` instructs the deployment client to unpack and maintain the application files in `$SPLUNK_HOME/etc/apps/Org_edr_sensor/`, but **prohibits the client from altering the application's operational state** (it will not set `disabled = 0` or `disabled = 1`). This allows external orchestration tools (Ansible, Puppet) or local administrative scripts to toggle the app's state when authorized.

---

### Scenario 10: Monitoring Console Stale Forwarder Telemetry Query
**Problem Statement:**  
The Security Operations Director requires an automated dashboard panel that alerts when any production forwarder has failed to check in with the Deployment Server for longer than 30 minutes.  
**Question:**  
Write the production SPL search query that extracts this telemetry from the Deployment Server internal logs.  
**Official Answer & Technical Explanation:**  
```spl
index=_internal sourcetype=splunkd group=subpools name=deploymentServer
| stats latest(_time) as last_contact by clientName, ip, machineType
| eval minutes_since_contact = round((now() - last_contact) / 60, 1)
| where minutes_since_contact > 30
| table clientName, ip, machineType, minutes_since_contact
| sort - minutes_since_contact
```
- **Explanation:** The Deployment Server logs every client phoneHome handshake under `sourcetype=splunkd group=subpools name=deploymentServer`. Calculating `now() - last_contact` in seconds and converting to minutes surfaces dormant or disconnected forwarders instantly.

---

## 🏆 3. Phase 6 Capstone Cyber Range Arena

To complete Phase 6 and earn your **Master Enterprise Fleet Orchestrator** certification, you must clear the ultimate practical gauntlet:

👉 **[Enter Cyber Range Room P6-Capstone: Global Fleet Orchestration Gauntlet](../Labs/Room_P6_Capstone_Global_Fleet_Orchestration.md)** `[500 XP]`

You will orchestrate a 10,000-node multi-tier fleet, resolve cloned GUID collisions, implement zero-downtime lookup hot-reloads, purge orphaned applications, and automate GitOps CI/CD delivery!

---

## 🎖️ 4. Operator Rank Promotion

```text
╔══════════════════════════════════════════════════════════════════════════╗
│               OFFICIAL SPLUNK CERTIFICATION ADVANCEMENT                  │
╠══════════════════════════════════════════════════════════════════════════╣
│ • Completed Phase:   Phase 6 — Centralized Deployment Management         │
│ • Total Phase Score: 2,100 / 2,100 XP (100% Mastery)                     │
│ • Cumulative XP:     11,100 XP                                           │
│ • Certified Rank:    MASTER ENTERPRISE FLEET ORCHESTRATOR 🚀             │
│ • Next Milestone:    Phase 7 — Distributed Splunk & High-Availability    │
│                      (Indexer Clustering, Search Head Clusters, SmartStore)│
╚══════════════════════════════════════════════════════════════════════════╝
```
