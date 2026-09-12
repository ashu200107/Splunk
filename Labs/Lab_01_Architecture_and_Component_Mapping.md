# 🧪 Lab 01: Enterprise Architecture Topology Design & Pipeline Mapping

> **Phase 1:** Splunk Fundamentals  
> **Associated Lesson:** Day 01 Core Anatomy & End-to-End Pipeline  
> **Objective:** Design, map, and validate the end-to-end data pipeline for a multi-tier enterprise architecture across all 4 difficulty levels.

---

## 📸 Architecture & Pipeline Visuals

|                   Enterprise 3D Architecture                    |                   4-Stage Ingestion Pipeline                   |
| :-------------------------------------------------------------: | :------------------------------------------------------------: |
| ![3D Architecture](../assets/01_enterprise_architecture_3d.jpg) | ![4-Stage Pipeline](../assets/02_data_pipeline_4phases_3d.jpg) |
|                 *Figure 1: Multi-Tier Topology*                 |                  *Figure 2: Ingestion Stages*                  |

---

## 🎯 Lab Overview
In this lab, you will design the exact data flow and component tiering for a financial enterprise processing **5 TB of security, application, and infrastructure logs per day**. You will determine where each parsing and forwarding decision occurs, identify port configurations, and simulate configuration validation commands.

---

## 🏗️ Architecture Design Scenario

**Enterprise Specifications:**
- **Tier 1 (Endpoints):** 2,000 Linux web servers, 500 Windows Active Directory domain controllers.
- **Tier 2 (Perimeter / API):** 50 Cisco ASA firewalls emitting UDP 514 syslog, AWS CloudTrail/VPC flow logs arriving via SQS/S3.
- **Tier 3 (Indexers):** 12-node Indexer Cluster with single-site Replication Factor (RF=3) and Search Factor (SF=2).
- **Tier 4 (Search):** 3-node Search Head Cluster (SHC) for SOC analysts and IT Operations.
- **Management:** 1 dedicated Deployment Server (DS), 1 Cluster Manager (CM), 1 Deployer, 1 Monitoring Console (MC), 1 License Manager (LM).

---

## 🪜 Exercise Breakdown by Difficulty Level

### 🟢 Level 1: Beginner — Component & Responsibility Mapping
**Objective:** Match each incoming data stream with the correct collection mechanism and processing tier.

1. **Linux Web Servers (`/var/log/nginx/access.log`):**
   - **Forwarder Type:** Universal Forwarder
   - **Protocol/Port:** Port 9997 (Splunk-to-Splunk TCP)
   - **Where does event breaking happen?** On the **Indexer** tier during the Parsing Phase.

2. **Cisco ASA Firewall Syslog (UDP 514):**
   - **Forwarder Type:** Dedicated Heavy Forwarder pair behind a load balancer (or `syslog-ng` / `rsyslog` writing to disk monitored by UF).
   - **Why?** UDP traffic has no delivery guarantees; placing an HF close to network firewalls captures the stream, applies regex routing, and forwards over TCP 9997 with ACK enabled.

3. **AWS CloudTrail JSON Events:**
   - **Collection Mechanism:** Splunk Add-on for AWS running on a Heavy Forwarder / IDXC HEC endpoint.

---

### 🟡 Level 2: Intermediate — Port Matrix & Firewall Rule Definition
**Objective:** Define the complete firewall port requirements to secure the enterprise topology.

Complete the matrix:
| Source Tier | Destination Tier | Destination Port | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **All Forwarders (UF/HF)** | Indexer Cluster Peers | `9997` | TCP | Raw data ingestion (S2S) |
| **All Forwarders (UF/HF)** | Deployment Server (DS) | `8089` | HTTPS/TCP | Management heartbeat & App downloads |
| **Search Head Cluster** | Indexer Cluster Peers | `8089` | HTTPS/TCP | Dispatched SPL map-reduce queries |
| **Cluster Manager (CM)** | Indexer Cluster Peers | `8089` | HTTPS/TCP | Heartbeat, peer state, bucket fixups |
| **Indexer Peers** | Indexer Peers | `9887` | TCP | Inter-indexer bucket replication |
| **Deployer** | Search Head Cluster | `8089` | HTTPS/TCP | SHC configuration bundle push |
| **End Users / Web** | Search Heads | `8000` | HTTPS/TCP | Splunk Web UI |
| **Indexers / SHs** | License Manager (LM) | `8089` | HTTPS/TCP | License usage reporting |

---

### 🟠 Level 3: Advanced — Pipeline Parsing & Data Transformation Rules
**Objective:** Trace where specific configuration stanzas must be placed in a distributed environment with UFs, HFs, and Indexers.

Given the following configuration needs, determine on which component tier the configuration file **must** reside:

1. **`[monitor:///var/log/app.log]`** (Specifies file path to monitor):
   - 📍 **Resides on:** **Universal Forwarder (UF)** in `inputs.conf`.
2. **`TIME_PREFIX = ^\[` & `TIME_FORMAT = %Y-%m-%d %H:%M:%S`** (Timestamp extraction):
   - 📍 **Resides on:** **Indexer** (or Heavy Forwarder if HF is used in the path) in `props.conf`.
3. **`LINE_BREAKER = ([\r\n]+)\d{4}-\d{2}-\d{2}`** (Event breaking):
   - 📍 **Resides on:** **Indexer** (or HF) in `props.conf`. *Never on UF!*
4. **`EXTRACT-user = User=(?<username>\w+)`** (Search-time field extraction):
   - 📍 **Resides on:** **Search Head** in `props.conf`.
5. **`[tcpout:idx_cluster]`** (Indexer IP addresses & load-balancing):
   - 📍 **Resides on:** **Universal Forwarder** and **Heavy Forwarder** in `outputs.conf`.

---

### 🔴 Level 4: Enterprise Production — Configuration Verification & Troubleshooting Simulation
**Objective:** Simulate command-line verification and identify configuration flaws that will cause production incidents.

#### Step 1: Configuration Validation Commands
When you make changes to configuration files, execute:
```bash
# Check for stanza syntax errors across all configuration files
/opt/splunk/bin/splunk btool check

# Verify which props.conf stanza is actively winning precedence for sourcetype 'cisco:asa'
/opt/splunk/bin/splunk btool props list cisco:asa --debug
```

#### Step 2: Spot the Production Flaw
Review the following `outputs.conf` deployed to 1,000 Universal Forwarders:
```ini
# FLAGGED CONFIGURATION:
[tcpout]
defaultGroup = indexers

[tcpout:indexers]
server = 10.100.1.50:9997
autoLB = false
```

**🚨 Failure Analysis:**
1. **Single Point of Failure (SPOF):** Only 1 indexer IP (`10.100.1.50`) is defined instead of a comma-separated list of all indexer peers.
2. **Auto-Load Balancing Disabled (`autoLB = false`):** Forwarders will stick to a single indexer indefinitely, creating severe data skew where one indexer hits 100% disk/CPU while other indexers remain completely idle.
3. **Missing Indexer ACK:** If `10.100.1.50` restarts, in-flight data will be lost silently because `useACK = true` is omitted.

**✅ Corrected Production Configuration:**
```ini
[tcpout]
defaultGroup = enterprise_indexers
maxQueueSize = 50MB

[tcpout:enterprise_indexers]
server = 10.100.1.50:9997, 10.100.1.51:9997, 10.100.1.52:9997, 10.100.1.53:9997
autoLB = true
autoLBFrequency = 30
useACK = true
```

---

## 🔍 Validation Checklist
- [x] Identified all 4 data pipeline phases (Input, Parsing, Indexing, Search).
- [x] Verified that event breaking (`LINE_BREAKER`) belongs on the parsing tier, not the UF.
- [x] Mapped the standard Splunk enterprise port matrix.
- [x] Verified `btool` syntax and debug commands.
