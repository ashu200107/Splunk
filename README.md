# ⚡ Splunk Enterprise Administrator Masterclass & Cyber Range

[![Splunk Certified Admin](https://img.shields.io/badge/Splunk%20Certified-Administrator-orange?style=for-the-badge&logo=splunk)](https://www.splunk.com/)
[![Cyber Range](https://img.shields.io/badge/Cyber%20Range-TryHackMe%20%7C%20HTB%20Style-red?style=for-the-badge&logo=hackthebox)](./Labs/00_Splunk_Cyber_Arena_Overview.md)
[![Obsidian Second Brain](https://img.shields.io/badge/Obsidian-Second%20Brain-purple?style=for-the-badge&logo=obsidian)](https://obsidian.md/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> **Welcome to the Definitive Splunk Administrator Knowledge Base & Gamified Training Range.**  
> Built as an enterprise-grade Obsidian Second Brain, complete with deep zero-assumption architectural notes, 3D isometric blueprints, production configuration stanzas, and **TryHackMe / Hack The Box style Hands-On Cyber Range Challenge Rooms**.

---

## 🗺️ Master 3D Architecture Blueprint

![Enterprise Multi-Tier 3D Architecture](./assets/01_enterprise_architecture_3d.jpg)
*Figure 1: Full Enterprise Multi-Tier Architecture (Universal & Heavy Forwarders, Indexer Cluster, Search Head Cluster, and Management Plane)*

---

## 🎮 Hands-On Splunk Cyber Range (TryHackMe / HTB Style)

Ditch passive theory! Step into high-stakes P1 incidents, debug broken cluster topologies, audit configurations, and capture administrative flags (`FLAG{...}`):

👉 **[Master Cyber Range Arena & Player Hub](./Labs/00_Splunk_Cyber_Arena_Overview.md)** 🚀

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ARENA STATS: 13 Active Challenge Rooms across Phase 1 & Phase 2     │
│ 💎 TOTAL XP: 2,750 XP Available            🎖️ RANK: Splunk SysAdmin   │
└────────────────────────────────────────────────────────────────────────┘
```

| Track | Room ID & Title | Topic / Incident Triage | Reward |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **[Room P1-01: Machine Data Decoder](./Labs/Room_P1_01_Machine_Data_and_Schema_on_Read.md)** | Rogue payment gateway, Schema-on-Read, 5 Metadata Keys, `_raw` | `150 XP` |
| **Phase 1** | **[Room P1-02: Core Architecture Recon](./Labs/Room_P1_02_Core_Architecture_and_Components.md)** | Component audit, UF vs HF limitations, TSIDX trees, Map-Reduce | `200 XP` |
| **Phase 1** | **[Room P1-03: 4-Stage Pipeline Backpressure](./Labs/Room_P1_03_Data_Pipeline_and_Backpressure.md)** | Ingestion gridlock, Fishbucket `btprobe`, `outputs.conf useACK=true` | `200 XP` |
| **Phase 1** | **[Room P1-04: The Btool Detective](./Labs/Room_P1_04_Directory_Structure_and_Btool_Detective.md)** | Overwritten config triage, S-A-A-S precedence, `btool --debug` | `200 XP` |
| **Phase 1** | **[Room P1-05: Storage & Cold Thaw](./Labs/Room_P1_05_Bucket_Lifecycle_and_Cold_Storage_Thawing.md)** | Legal subpoena: thawing frozen buckets, `splunk rebuild .tsidx` | `250 XP` |
| **Phase 1** | **[Room P1-06: Licensing & Quota Breach](./Labs/Room_P1_06_Licensing_Mechanics_and_Quota_Breach.md)** | 100GB debug burst, uncompressed metering, free replicas, 5 warnings | `200 XP` |
| **Phase 1** | **[Room P1-07: Port Matrix & Firewall Defense](./Labs/Room_P1_07_Ports_Protocols_and_Firewall_Hardening.md)** | Zero-trust lockout: Ports 9997, 8089, 8191, Netcat (`nc -zvw3`) | `200 XP` |
| **Phase 2** | **[Room P2-01: Linux Kernel Hardening & IOPS](./Labs/Room_P2_01_Linux_Kernel_Tuning_and_1200_IOPS.md)** | Sluggish Indexer: disable THP via Systemd, ulimits 64k, 1200 IOPS | `200 XP` |
| **Phase 2** | **[Room P2-02: Splunk Linux Deployment](./Labs/Room_P2_02_Splunk_Enterprise_Linux_Deployment_and_Systemd.md)** | Non-root `splunk`, `user-seed.conf`, native Systemd boot-start | `200 XP` |
| **Phase 2** | **[Room P2-03: UF Fleet Rollout & ACK](./Labs/Room_P2_03_Universal_Forwarder_Fleet_Deployment_and_ACK.md)** | Nginx edge logs, silent `--accept-license`, 30s auto load balancing | `200 XP` |
| **Phase 2** | **[Room 01: Heavy Forwarder Port Clash](./Labs/Room_01_Heavy_Forwarder_Infiltration_and_Port_Clash.md)** | Port 8089 ➔ 8090 offset, `[indexAndForward] index = false`, PII regex | `200 XP` |
| **Phase 2** | **[Room 02: License Vault Heist](./Labs/Room_02_License_Vault_Heist_and_72Hr_Survival.md)** | Severed WAN outage, `server.conf` slave pairing, 72-hour grace period | `250 XP` |
| **Phase 2** | **[Room 03: MC Queue Jam Triage](./Labs/Room_03_Monitoring_Console_Mission_Control.md)** | Ingestion lag P1: `indexQueue` (Disk IOPS) vs `parsingQueue` (CPU/Regex) | `300 XP` |

---

## 📚 Second Brain Curriculum Structure

### 🧭 [00 - Master Dashboard & Roadmap](./00%20-%20Master%20Dashboard%20&%20Roadmap)
- 🗺️ **[90-Day Master Roadmap](./00%20-%20Master%20Dashboard%20&%20Roadmap/00_90_Day_Master_Roadmap.md)**: 11-Phase blueprint covering architecture, deployment, clustering, RBAC, and disaster recovery.
- 📊 **[Progress & Mastery Tracker](./00%20-%20Master%20Dashboard%20&%20Roadmap/01_Progress_Tracker.md)**: Live scorecard tracking evaluated chapter quizzes and remediation logs.

### 📗 [01 - Phase 1: Splunk Fundamentals](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals)
- 📄 **[Ch 01: What is Splunk & Machine Data?](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_01_What_is_Splunk_and_Machine_Data.md)**
- 📄 **[Ch 02: Core Architecture & Components](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_02_Splunk_Core_Architecture_and_Components.md)**
- 📄 **[Ch 03: The End-to-End Data Pipeline](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_03_The_End_to_End_Data_Pipeline.md)**
- 📄 **[Ch 04: Directory Structure & Config Precedence](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_04_Splunk_Directory_Structure_and_Config_Precedence.md)**
- 📄 **[Ch 05: Index Storage & Bucket Lifecycle](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_05_Index_Storage_Architecture_and_Bucket_Lifecycle.md)**
- 📄 **[Ch 06: Splunk Licensing Mechanics](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_06_Splunk_Licensing_Mechanics.md)**
- 📄 **[Ch 07: Ports, Protocols & Firewall Matrix](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_07_Splunk_Ports_Protocols_and_Firewall_Matrix.md)**
- 📄 **[Ch 08: Phase 1 Master Revision Sheet](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_08_Phase_1_Master_Revision_Notes.md)**
- 🗂️ **[Ch 09: Phase 1 Master Flashcards Deck (41 Cards)](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_09_Phase_1_Master_Flashcards.md)**
- 🎯 **[Ch 10: Phase 1 Master Assessment Exam](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_10_Phase_1_Master_Assessment_Exam.md)**
- 🛠️ **[Ch 11: Phase 1 Targeted Remediation Guide](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Chapter_11_Phase_1_Targeted_Review_Guide.md)**
- 📕 **[Phase 1 Complete Handbook PDF](./01%20-%20Phase%201%20-%20Splunk%20Fundamentals/Splunk_Enterprise_Phase_1_Complete_Handbook.pdf)**

### 📙 [02 - Phase 2: Enterprise Installation & Topology Setup](./02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup)
- 📄 **[Ch 01: Hardware Sizing & Linux Kernel Tuning](./02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/Chapter_01_Hardware_Sizing_and_Linux_Kernel_Tuning.md)**
- 📄 **[Ch 02: Enterprise Linux Step-by-Step Installation](./02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/Chapter_02_Step_by_Step_Splunk_Enterprise_Installation.md)**
- 📄 **[Ch 03: Universal Forwarder (UF) Rollout](./02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/Chapter_03_Universal_Forwarder_Installation_and_Config.md)**
- 📄 **[Ch 04: Heavy Forwarder (HF) Deployment & Routing](./02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/Chapter_04_Heavy_Forwarder_Deployment_and_Routing.md)**
- 📄 **[Ch 05: License Manager Pairing & Pools](./02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/Chapter_05_License_Manager_Pairing_and_Pools.md)**
- 📄 **[Ch 06: Monitoring Console (MC) Distributed Setup](./02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/Chapter_06_Monitoring_Console_Setup_and_Telemetry.md)**

---

## 🖼️ 3D Visual Gallery Highlights

| 4-Stage Ingestion Pipeline | Storage Bucket Lifecycle |
| :---: | :---: |
| ![4-Stage Pipeline](./assets/02_data_pipeline_4phases_3d.jpg) | ![Bucket Lifecycle](./assets/03_indexer_storage_buckets_3d.jpg) |

| License Master Vault & Slaves | Monitoring Console Mission Control |
| :---: | :---: |
| ![License Manager 3D](./assets/23_license_manager_3d.jpg) | ![Monitoring Console 3D](./assets/24_monitoring_console_3d.jpg) |

---

## 🛠️ How to Clone & Use with Obsidian

```bash
# Clone the repository
git clone https://github.com/ashu200107/Splunk.git

# Open in Obsidian:
# File -> Open Folder as Vault -> Select the cloned 'Splunk' directory!
```

---
*Built with ❤️ for Aspiring Enterprise Splunk Architects & Administrators.*
