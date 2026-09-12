# 🗺️ 90-Day Enterprise Splunk Administrator Mastery Roadmap

> **Target Role:** Enterprise Splunk Administrator / Splunk Consultant / Production Support Engineer  
> **Methodology:** 80/20 Rule + Architecture Depth + Production Scenarios + Lab Execution + Interview Drills  
> **Status:** Active (Phase 1 In Progress)

---

## 📸 Enterprise 3D Architecture Topology

![3D Isometric Enterprise Splunk Architecture](../assets/01_enterprise_architecture_3d.jpg)
*Figure 1: Full Enterprise Multi-Tier Splunk Architecture (UFs, HFs, Indexer Cluster, Search Head Cluster & Management Plane)*

---

## 🎯 The 80/20 Production Focus
In enterprise environments (100GB to 50TB+/day ingestion), **80% of administrator operations and interview scrutiny revolve around:**
1. **End-to-End Splunk Architecture & Data Pipeline** (Input $\rightarrow$ Parsing $\rightarrow$ Indexing $\rightarrow$ Search)
2. **Data Onboarding Mastery** (`inputs.conf`, `props.conf`, `transforms.conf`, event breaking, timestamps, index routing)
3. **Forwarder Tier & Management** (Universal Forwarders, Heavy Forwarders, Deployment Server, Server Classes)
4. **Clustering & High Availability** (Indexer Clusters, Search Head Clusters, SmartStore, Cluster Manager, Deployer)
5. **System Troubleshooting & Health** (Monitoring Console, internal logs `_internal`, `_audit`, `_introspection`, `splunkd.log`, CLI troubleshooting)

---

## 📸 Ingestion Pipeline & Storage Lifecycles

| 4-Stage Ingestion Pipeline | Indexer Storage & Bucket Lifecycle |
| :---: | :---: |
| ![4-Stage Pipeline](../assets/02_data_pipeline_4phases_3d.jpg) | ![Storage & Buckets](../assets/03_indexer_storage_buckets_3d.jpg) |
| *Figure 2: Data flowing from Input to Search* | *Figure 3: Hot $\rightarrow$ Warm $\rightarrow$ Cold $\rightarrow$ Frozen* |

---

## 🎯 Splunk Administrator Cyber Range & Challenge Rooms (THM / HTB Style)

Ditch passive theory! Step into gamified P1 incidents, broken cluster topologies, configuration audits, and capture administrative flags (`FLAG{...}`):
👉 **[Splunk Cyber Range & Challenge Arena Overview](../Labs/00_Splunk_Cyber_Arena_Overview.md)** 🚀

| Track | Challenge Rooms Available | Focus Areas |
| :--- | :--- | :--- |
| **Phase 1 Range (7 Rooms)** | • [P1-01: Machine Data Decoder](../Labs/Room_P1_01_Machine_Data_and_Schema_on_Read.md)<br/>• [P1-02: Core Architecture Recon](../Labs/Room_P1_02_Core_Architecture_and_Components.md)<br/>• [P1-03: 4-Stage Pipeline Backpressure](../Labs/Room_P1_03_Data_Pipeline_and_Backpressure.md)<br/>• [P1-04: The Btool Detective](../Labs/Room_P1_04_Directory_Structure_and_Btool_Detective.md)<br/>• [P1-05: Bucket Storage & Cold Thaw](../Labs/Room_P1_05_Bucket_Lifecycle_and_Cold_Storage_Thawing.md)<br/>• [P1-06: Licensing & Quota Breach](../Labs/Room_P1_06_Licensing_Mechanics_and_Quota_Breach.md)<br/>• [P1-07: Port Matrix & Firewall Defense](../Labs/Room_P1_07_Ports_Protocols_and_Firewall_Hardening.md) | Schema-on-Read, 5 Metadata Keys, TSIDX trees, Map-Reduce, Fishbucket, `useACK=true`, S-A-A-S Precedence, `btool --debug`, `splunk rebuild`, 5-warning rule, Netcat |
| **Phase 2 Range (6 Rooms)** | • [P2-01: Linux Hardening & 1200 IOPS](../Labs/Room_P2_01_Linux_Kernel_Tuning_and_1200_IOPS.md)<br/>• [P2-02: Splunk Linux & Systemd](../Labs/Room_P2_02_Splunk_Enterprise_Linux_Deployment_and_Systemd.md)<br/>• [P2-03: UF Fleet Rollout](../Labs/Room_P2_03_Universal_Forwarder_Fleet_Deployment_and_ACK.md)<br/>• [Room 01: Heavy Forwarder Port Clash](../Labs/Room_01_Heavy_Forwarder_Infiltration_and_Port_Clash.md)<br/>• [Room 02: License Vault Heist](../Labs/Room_02_License_Vault_Heist_and_72Hr_Survival.md)<br/>• [Room 03: MC Queue Jam Triage](../Labs/Room_03_Monitoring_Console_Mission_Control.md) | Disable THP, ulimits 64k, 1200 IOPS `fio`, `user-seed.conf`, Systemd unit, Port 8089 ➔ 8090 offset, `index=false` safeguard, 72-hour grace period, Distributed MC, `indexQueue` vs `parsingQueue` |


---

## 📅 Roadmap Overview (11 Phases / 90 Days)

| Phase | Focus Area | Timeline | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Splunk Fundamentals & Architecture | Days 1–7 | Component breakdown, Data lifecycle, Licensing, Directory layout |
| **Phase 2** | Enterprise Installation & Topology Setup | Days 8–15 | Splunk Enterprise, UF, HF, License Manager, Deployment Server, Monitoring Console |
| **Phase 3** | Deep Data Onboarding & Parsing Pipeline | Days 16–28 | `inputs.conf`, `props.conf`, `transforms.conf`, Event breaking, Regex extractions, Index-time vs Search-time |
| **Phase 4** | Advanced SPL & Search Optimization | Days 29–38 | Statistical commands, Subsearches, Joins, Lookups, Data models, tstats, Acceleration |
| **Phase 5** | Authentication, RBAC & Security Administration | Days 39–46 | Users, Roles, Capabilities, LDAP/SAML, SSL/TLS certificates, Splunk hardening |
| **Phase 6** | Centralized Deployment Management | Days 47–53 | Deployment Server, Server Classes, App deployment precedence, App versioning |
| **Phase 7** | Distributed Splunk & High-Availability Clusters | Days 54–66 | Indexer Clustering (RF/SF, Bucket replication), Search Head Clustering (Raft, Deployer), SmartStore |
| **Phase 8** | Monitoring Console & Performance Tuning | Days 67–73 | Monitoring Console, Resource contention (CPU/RAM/Disk IOPS), Search concurrency, Pipe sizing |
| **Phase 9** | Enterprise Troubleshooting Runbooks | Days 74–80 | `_internal` queries, pipeline bottlenecks, silent drops, parsing loops, license breaches |
| **Phase 10** | Enterprise Operations & Production Runbooks | Days 81–85 | Upgrades, Migrations, Backup/DR, Retention policies, Maintenance windows |
| **Phase 11** | Mock Interviews, Architecture Design & Scenario Drills | Days 86–90 | Real-time troubleshooting scenarios, Live interview simulations, Resume polish |

---

## 📋 Detailed Day-by-Day Syllabus

### 🧱 Phase 1: Splunk Fundamentals & Core Mechanics (Days 1–7)
- **Day 1:** Core Anatomy: What is Machine Data, Splunk Roles (Search Head, Indexer, Forwarders, Management Components), End-to-End Pipeline.
- **Day 2:** Splunk Directory Structure (`$SPLUNK_HOME`), Configuration Precedence Layering (System, Apps, Users, Local vs Default).
- **Day 3:** The Splunk Ingestion Pipelines: Input Pipeline, Parsing Pipeline, Merging Pipeline, Typing Pipeline, Index Pipeline.
- **Day 4:** Data Lifecycle & Index Architecture: Buckets (Hot, Warm, Cold, Frozen, Thawed), Metadata files (`.tsidx`, `journal.zst`, `Sources.data`).
- **Day 5:** Splunk Licensing Mechanics: License pools, Quota calculations, What counts against license vs What is exempt, License warnings/violations.
- **Day 6:** Splunk Ports, Protocols & Firewall Matrix (8000, 8089, 9997, 8088, 8191, 9887, 514).
- **Day 7:** Phase 1 Comprehensive Review, Scenario Drills & Knowledge Benchmark.

### ⚙️ Phase 2: Enterprise Installation & Topology Setup (Days 8–15)
- **Day 8:** Linux OS Sizing, Storage Benchmarks (IOPS requirements), Kernel tuning (`ulimit`, `THP`, dirty pages).
- **Day 9:** Splunk Enterprise Standalone & Distributed Manual Installation via CLI, Systemd Service configuration.
- **Day 10:** Universal Forwarder (UF) Installation, CLI commands, Automation deployment via scripts.
- **Day 11:** Heavy Forwarder (HF) Installation & Architecture: When to use HF vs UF vs HEC.
- **Day 12:** License Manager (LM) Configuration, License master slave pairing, Pool allocation.
- **Day 13:** Monitoring Console (MC) Setup in Distributed Mode, Asset & Instance configuration.
- **Day 14:** HTTP Event Collector (HEC) Setup: Tokens, Load balancing, ACK mechanics, High-throughput logging.
- **Day 15:** Phase 2 Practical Build: Multi-tier Lab topology bring-up.

### 📥 Phase 3: Data Onboarding & Parsing Pipeline (Days 16–28)
- **Day 16:** `inputs.conf` Anatomy: Monitor stanzas, Batch, Scripted inputs, Windows Event Log inputs, Modular inputs.
- **Day 17:** Sourcetype Strategy & Best Practices: Custom vs Add-on sourcetypes, Naming conventions.
- **Day 18:** Line Breaking & Event Timestamping: `SHOULD_LINEMERGE`, `LINE_BREAKER`, `TRUNCATE`, `TIME_PREFIX`, `TIME_FORMAT`, `MAX_TIMESTAMP_LOOKAHEAD`.
- **Day 19:** `props.conf` vs `transforms.conf` Mechanics: Who parses what and where? (UF vs HF vs Indexer).
- **Day 20:** Advanced Index-time Filtering & Routing: Dropping raw logs using regex (`nullQueue`), Selective indexing.
- **Day 21:** Index-time Data Masking & Anonymization (PII/PCI compliance sanitization before disk write).
- **Day 22:** Search-time Field Extractions: Inline Regex vs Transforms, Delimited extractions, JSON/XML handling.
- **Day 23:** Calculated Fields (`EVAL-`), Field Aliases, and Sourcetype Renaming.
- **Day 24:** Lookups: Static CSV Lookups, Automatic Lookups, KV Store Lookups, External Scripted Lookups.
- **Day 25:** Splunk Common Information Model (CIM) & Technology Add-ons (TAs): Data normalisation.
- **Day 26:** Eventtypes and Tags: Classification hierarchies in enterprise environments.
- **Day 27:** Data Onboarding Troubleshooting: Timestamp drift, Line merging failures, Regex catastrophic backtracking.
- **Day 28:** Phase 3 Capstone Lab: Production Onboarding of Multi-line Custom Application Logs.

### 🔍 Phase 4: Advanced SPL & Search Optimization (Days 29–38)
- **Day 29:** SPL Core Foundations: Fast vs Smart vs Verbose mode, Search pipeline processing mechanics.
- **Day 30:** Transforming Commands: `stats`, `chart`, `timechart`, `top`, `rare`, `contingency`.
- **Day 31:** Manipulating & Formatting Events: `eval`, `rex`, `replace`, `strcat`, `spath`, `mvexpand`, `nomv`.
- **Day 32:** Filtering & Structuring Results: `where`, `search`, `dedup`, `head`, `tail`, `sort`, `table`, `fields`.
- **Day 33:** Correlation & Multi-dataset Searching: `transaction` vs `stats` (Memory footprint comparison), `join`, `append`, `union`.
- **Day 34:** Subsearches: How subsearches work internally, limitations (`maxout`, timeout), optimization alternatives.
- **Day 35:** Lookups & KV Store in SPL: `inputlookup`, `outputlookup`, `lookup`, KV Store CRUD operations.
- **Day 36:** Acceleration Techniques: Report Acceleration, Summary Indexing (`sistats`, `collect`), Data Model Acceleration (DMA).
- **Day 37:** `tstats` Mastery: Querying accelerated data models and `.tsidx` files directly for enterprise speed.
- **Day 38:** Search Job Inspector: Interpreting duration breakdown, scan count vs return count, disk usage, optimization fixes.

### 🛡️ Phase 5: Authentication, RBAC & Security Administration (Days 39–46)
- **Day 39:** Splunk User & Role Architecture: Default roles, Custom roles, Granular inheritance.
- **Day 40:** Capabilities Management: Assigning search restrictions, Index-level access controls, Search filters (`srchFilter`).
- **Day 41:** Native Authentication & Splunk User Management via CLI & REST API.
- **Day 42:** LDAP & Active Directory Integration: User/Group mapping, Failover strategies, `authentication.conf`.
- **Day 43:** SAML SSO Integration (Okta / Azure AD / PingFederate): Metadata exchange, Attribute mapping.
- **Day 44:** Securing Splunk Communications (SSL/TLS): Web UI certificates, Splunk-to-Splunk encryption (`s2s`), UF-to-Indexer TLS.
- **Day 45:** Splunk Hardening & Compliance: Disabling unnecessary ports, CLI access lockdown, `_audit` analysis.
- **Day 46:** Phase 5 Security Audit & Incident Simulation.

### 🚀 Phase 6: Centralized Deployment Management (Days 47–53)
- **Day 47:** Deployment Server (DS) Architecture: Polling interval (`phoneHomeIntervalInSecs`), Client handshake.
- **Day 48:** `serverclass.conf` Deep Dive: Whitelisting/Blacklisting regex, Target repositories, Filter chaining.
- **Day 49:** App Structure & Packaging: Splunk App Directory anatomy, `app.conf`, `default` vs `local`, Clean package creation.
- **Day 50:** Enterprise App Deployment Lifecycle: Dev $\rightarrow$ Test $\rightarrow$ Prod staging, Versioning, Restart policies.
- **Day 51:** Scaling Deployment Server: Large fleet management (10,000+ forwarders), Tiered deployment architecture.
- **Day 52:** Deployment Server Troubleshooting: Forwarders missing check-ins, High CPU on DS, Configuration reload failures.
- **Day 53:** Phase 6 Lab: Automating Multi-tier Server Classes across 50 simulated endpoints.

### 🌐 Phase 7: Distributed Splunk & High-Availability Clusters (Days 54–66)
- **Day 54:** Distributed Search Topology: Search Head to Indexer communication, Map-Reduce search processing.
- **Day 55:** Indexer Clustering Architecture: Single-site Indexer Cluster, Replication Factor (RF), Search Factor (SF).
- **Day 56:** Cluster Manager (CM) Deep Dive: Bucket fixup tasks, Peer heartbeat, Maintenance mode, `server.conf`.
- **Day 57:** Multi-site Indexer Clustering (Disaster Recovery): Site affinity, Site RF/SF (`site_replication_factor`), Inter-site bandwidth.
- **Day 58:** Bucket State Transitions & Rolling Restarts: Master-driven restarts, Searchable rolling upgrades.
- **Day 59:** Indexer Cluster Troubleshooting: Peer offline, Bucket fixup backlogs, Search factor unfulfilled, Replication errors.
- **Day 60:** Search Head Clustering (SHC) Architecture: Raft consensus protocol, Captain election, Member synchronization.
- **Day 61:** SHC Deployer: Bundle push mechanisms, Configuration merging, `shcluster/apps` staging.
- **Day 62:** SHC Operations: Dynamic captaincy, Search artifact replication, User state storage (KV Store clustering).
- **Day 63:** SmartStore Architecture: Remote storage (AWS S3 / GCP GCS / Azure Blob), Cache Manager, Cache eviction algorithms.
- **Day 64:** Upgrades in High-Availability Clusters: Zero-downtime rolling upgrades step-by-step.
- **Day 65:** Disaster Recovery Failover Scenarios: Site loss simulation and recovery operations.
- **Day 66:** Phase 7 Mega-Lab: Deploying and breaking a multi-site Indexer & Search Head Cluster.

### 📊 Phase 8: Monitoring Console & Performance Tuning (Days 67–73)
- **Day 67:** Monitoring Console (MC) Dashboards: Resource usage, Indexing performance, Search concurrency.
- **Day 68:** Internal Log Analytics: Mastering `_internal`, `_introspection`, `_audit`, `_telemetry`.
- **Day 69:** Identifying & Fixing Ingestion Bottlenecks: Parsing queue blocked, Indexing queue blocked, TCP queue blocked.
- **Day 70:** Resource Sizing & Capacity Planning: Sizing CPU cores, Memory footprint, Storage IOPS, Forwarder counts.
- **Day 71:** Search Concurrency & Resource Limits: `limits.conf` tuning (`max_searches_per_cpu`, `subsearch` limits).
- **Day 72:** Bucket Sizing & Storage Optimization: `maxDataSize`, `maxWarmDBCount`, `homePath.maxDataSizeMB`, retention sizing.
- **Day 73:** Phase 8 Performance Audit: Tuning a degraded production cluster.

### 🚨 Phase 9: Enterprise Troubleshooting Runbooks (Days 74–80)
- **Day 74:** Root Cause Analysis (RCA) Methodology: The Splunk Administrator diagnostic toolkit (`splunk btool`, `diag`, REST API).
- **Day 75:** Troubleshooting Scenario 1: Data not reaching index (End-to-end triage flow).
- **Day 76:** Troubleshooting Scenario 2: Timestamp drift, out-of-order events, and line truncation.
- **Day 77:** Troubleshooting Scenario 3: High CPU / Out of Memory (OOM) killer on Indexers and Search Heads.
- **Day 78:** Troubleshooting Scenario 4: License warnings, soft/hard violations, and quota breach recovery.
- **Day 79:** Troubleshooting Scenario 5: Search Head Cluster member out of sync / Raft consensus degradation.
- **Day 80:** Troubleshooting Scenario 6: Broken Forwarders, silent network drops, SSL handshake errors.

### 🏭 Phase 10: Real Production Operations (Days 81–85)
- **Day 81:** Daily, Weekly, and Monthly Splunk Administrator Checklist.
- **Day 82:** Splunk Enterprise Major & Minor Version Upgrade Runbook.
- **Day 83:** Index Migration, Data Rebalancing & Storage Re-tiering.
- **Day 84:** Backup Strategy: What configs to backup, KV Store backups, Metadata preservation.
- **Day 85:** Enterprise Change Management: Change windows, Validation scripts, Rollback strategies.

### 🎓 Phase 11: Interview Preparation & Architect Polish (Days 86–90)
- **Day 86:** Top 50 Administrator Technical Questions (Foundations, Config Precedence, Pipelines).
- **Day 87:** Top 30 Scenario & Live Troubleshooting Questions.
- **Day 88:** Top 20 Architecture & Cluster Design Questions.
- **Day 89:** Mock Interview 1: Technical Deep Dive & Whiteboard Architecture.
- **Day 90:** Mock Interview 2: Production Outages, RCA Defense & Final Readiness Evaluation.
