# 🏆 Chapter 13 (Phase 3): Phase 3 Capstone — Production Banking Onboarding & Master Milestone Exam

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 28 | **Milestone:** Phase 3 Grand Finale & Master Certification Benchmark  
> **Current Rank:** Splunk Enterprise Architect (3,050 XP) $\rightarrow$ *Graduation Target: Principal Splunk Architect (3,550+ XP)!*  
> **Second Brain File:** `Chapter_13_Phase_3_Capstone_Lab_and_Exam.md`  
> **Interactive Cyber Range Boss Lab:** [Room P3-Capstone: The Banking Log Gauntlet](../Labs/Room_P3_Capstone_Banking_Log_Gauntlet.md) `[500 XP]`

---

## 🏰 1. The Big Picture: The Complete Enterprise Onboarding Blueprint

Over Chapters 01 through 12, you forged every individual gear of the Splunk parsing engine.  
Now, look at how the entire **Production Data Highway** operates in a Fortune 500 enterprise:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      THE ENTERPRISE DATA ONBOARDING LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. THE INTAKE VALVE (Universal Forwarder / Edge Tier)                                   │
│    • inputs.conf monitors recursive application logs with [monitor:///var/log/.../*.log]│
│    • Fishbucket hashes 256-byte CRC DNA fingerprints and tracks seekptr byte offsets    │
│    • crcSalt = <SOURCE> prevents daily CSV header collisions and rotation stalls        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. THE PARSING SURGERY (Heavy Forwarder / Ingestion Tier)                               │
│    • LINE_BREAKER slices multi-line stack traces with C++ compiled laser precision      │
│    • TRUNCATE = 250000 protects large JSON payloads from violent mid-event amputation   │
│    • TIME_PREFIX and TIME_FORMAT burn exact epoch timestamps and eliminate 1970 drift   │
│    • SEDCMD masks 16-digit credit cards (XXXX-XXXX-XXXX-1234) permanently in memory     │
│    • nullQueue incinerates millions of noisy healthchecks to save license quota         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. THE STORAGE COMMIT (Indexer Cluster Tier)                                            │
│    • Clean, compliant, masked raw text is compressed into journal.zst storage vaults    │
│    • Inverted index keywords are compiled into lightning-fast .tsidx card catalogs      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. THE KNOWLEDGE LAYER (Search Head / Analytics Tier)                                   │
│    • EXTRACT- and DELIMS expose structured key-value pairs without modifying disk data │
│    • FIELDALIAS- standardizes vendor fields to CIM standards (client_ip AS src)         │
│    • EVAL- calculates business metrics (latency duration, error categories) on the fly │
│    • Lookups & KV Store MongoDB (Port 8191) enrich machine records with asset owners   │
│    • eventtypes.conf & tags.conf fuel Splunk Enterprise Security (ES) data models!      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ 2. The 3D Master Architectural Blueprint

![Splunk Enterprise Data Onboarding Pipeline 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_phase3_capstone_gauntlet_3d_1792125456722.jpg)
*Figure 3.13: Full 3D Isometric Master Blueprint of the Production End-to-End Splunk Data Onboarding Pipeline.*

---

## 📋 3. The Enterprise Onboarding Golden Configuration Matrix

Here is the exact production configuration stack for a high-volume custom banking application (`fincorp:banking:core`):

### A. Edge Forwarder Configuration:
```ini
# $SPLUNK_HOME/etc/apps/fincorp_inputs/local/inputs.conf (ON UNIVERSAL FORWARDER)
[monitor:///var/log/fincorp/banking/.../*.log]
disabled = false
index = banking_vault
sourcetype = fincorp:banking:core
whitelist = \.(log|json)$
blacklist = (\.(gz|tmp)$|debug)
crcSalt = <SOURCE>
ignoreOlderThan = 14d
```

### B. Ingestion & Parsing Tier Configuration:
```ini
# $SPLUNK_HOME/etc/apps/fincorp_props/local/props.conf (ON HEAVY FORWARDER OR INDEXERS)
[fincorp:banking:core]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}
TRUNCATE = 250000
TIME_PREFIX = ^
MAX_TIMESTAMP_LOOKAHEAD = 32
TIME_FORMAT = %Y-%m-%d %H:%M:%S.%3N
TZ = UTC
MAX_DAYS_AGO = 30
MAX_DAYS_HENCE = 2

# Ingestion-Time Filtering & Masking:
TRANSFORMS-drop_health = discard_kube_healthchecks
SEDCMD-mask_pan = s/\b(?:\d{4}-){3}(\d{4})\b/XXXX-XXXX-XXXX-\1/g
SEDCMD-mask_ssn = s/\b\d{3}-\d{2}-(\d{4})\b/XXX-XX-\1/g

# $SPLUNK_HOME/etc/apps/fincorp_props/local/transforms.conf (ON HEAVY FORWARDER OR INDEXERS)
[discard_kube_healthchecks]
REGEX = (?i)(GET\s+/healthz|kube-probe)
DEST_KEY = queue
FORMAT = nullQueue
```

### C. Search Head Knowledge Layer Configuration:
```ini
# $SPLUNK_HOME/etc/apps/fincorp_search/local/props.conf (ON SEARCH HEAD CLUSTER)
[fincorp:banking:core]
# 1. Search-Time Extraction:
REPORT-extract_kv = parse_banking_keyvalues

# 2. Field Aliasing to CIM Standards:
FIELDALIAS-cim_network = client_ip AS src, server_ip AS dest, port AS dest_port
FIELDALIAS-cim_auth = user_account AS user

# 3. Calculated Fields:
EVAL-duration_sec = round(latency_microsec / 1000000, 2)
EVAL-action = case(status_code=="APPROVED", "success", status_code=="DECLINED", "failure", true(), "unknown")

# 4. Automatic Lookup:
LOOKUP-enrich_branch = branch_directory branch_code OUTPUT branch_name, region, manager

# $SPLUNK_HOME/etc/apps/fincorp_search/local/transforms.conf (ON SEARCH HEAD CLUSTER)
[parse_banking_keyvalues]
DELIMS = " ", "="

[branch_directory]
filename = branch_master_list.csv
case_sensitive_match = false

# $SPLUNK_HOME/etc/apps/fincorp_search/local/eventtypes.conf (ON SEARCH HEAD CLUSTER)
[fincorp_transaction_fraud]
search = sourcetype=fincorp:banking:core status_code="DECLINED" risk_score > 85

# $SPLUNK_HOME/etc/apps/fincorp_search/local/tags.conf (ON SEARCH HEAD CLUSTER)
[eventtype=fincorp_transaction_fraud]
financial = enabled
fraud = enabled
risk = enabled
```

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-Capstone

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ FINAL BOSS ROOM: Room P3-Capstone — The Banking Log Gauntlet       │
│ ⭐ DIFFICULTY: Expert | 💎 REWARD: 500 XP | ⏱️ TIME: 60 Mins           │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 The Ultimate Production Onboarding Mission:**  
> FinCorp Global is launching its next-generation Core Banking Settlement Engine!  
> As the Principal Splunk Architect, you must architect the entire pipeline from scratch:  
> 1. Ingest multi-line logs from 500 edge forwarders without fishbucket collisions.  
> 2. Stop 10,000 EPS healthcheck spam from hitting the 5 TB license quota using `nullQueue`.  
> 3. Enforce 100% PCI-DSS compliant in-memory PAN credit card masking before disk commit.  
> 4. Build CIM-compliant field aliases, calculated latency metrics, and KV Store lookups.  
> 5. Verify the entire cluster runs with 0 queue backpressure!

👉 **[Enter the Final Boss Arena: Room P3-Capstone](../Labs/Room_P3_Capstone_Banking_Log_Gauntlet.md)** `[500 XP]`

---

# 🎓 Phase 3 Master Milestone Exam

Answer these **10 rigorous architectural scenarios** to graduate from Phase 3, earn **+500 XP**, and promote to **Principal Splunk Architect**:

### Question 1 (Fishbucket & Ingestion State)
Explain how Splunk uses the first 256 bytes of a monitored file to calculate its CRC hash, what occurs when an application writes two daily reports with identical 300-byte CSV headers, and what parameter permanently resolves this collision.

### Question 2 (Wildcards & Monitor Path Scope)
What is the functional difference between `[monitor:///var/log/app/*.log]` and `[monitor:///var/log/app/.../*.log]`, and what danger does an unconstrained recursive ellipsis wildcard pose to Linux forwarders?

### Question 3 (Event Breaking Engine Performance)
Why does Splunk strictly mandate `SHOULD_LINEMERGE = false` when using `LINE_BREAKER`, and what is the exact function of Capture Group 1 `([\r\n]+)` in a `LINE_BREAKER` regular expression?

### Question 4 (Timestamp Extraction Mechanics)
Explain the purpose of `MAX_TIMESTAMP_LOOKAHEAD` in `props.conf`. If an Indexer cannot parse a timestamp and all source/header fallbacks fail, what time does Splunk assign to the event, and what is this operational issue called?

### Question 5 (Configuration Placement Across Tiers)
In a distributed Splunk deployment (UF $\rightarrow$ HF $\rightarrow$ Indexer $\rightarrow$ Search Head), on which tier must `LINE_BREAKER`, `SEDCMD`, and `nullQueue` routing execute? What happens if an admin deploys `SEDCMD` to the Search Head?

### Question 6 (Licensing Optimization via `nullQueue`)
How does routing an event to `nullQueue` affect daily license quota metering and disk storage? In a two-stage whitelist filter, in what order must the discard and rescue transforms appear in `props.conf`?

### Question 7 (PCI-DSS Masking Compliance)
Write the exact `SEDCMD` directive in `props.conf` to mask 16-digit credit cards (`4123-4567-8901-2345` $\rightarrow$ `XXXX-XXXX-XXXX-2345`). Why does search-time masking with `eval` fail a regulatory compliance audit?

### Question 8 (Search-Time Field Extractions)
Why is `DELIMS = " ", "="` in `transforms.conf` dramatically faster than regular expressions for extracting key-value pairs? What does `KV_MODE = json` accomplish on a Search Head?

### Question 9 (The Search-Time Execution Sequence)
In Splunk's official 10-step search-time operations sequence, does `FIELDALIAS-` execute before or after `EVAL-`? Can a calculated field use an aliased field name? Can a field alias reference a calculated field?

### Question 10 (CIM Normalization & Data Models)
What are the four core configuration files used to achieve Common Information Model (CIM) compliance? What SPL search command verifies that your events are actively accelerating an Enterprise Security data model?

---
*Respond with your answers to graduate from Phase 3, earn +500 XP, and unlock Phase 4: Advanced SPL & Search Optimization!*
