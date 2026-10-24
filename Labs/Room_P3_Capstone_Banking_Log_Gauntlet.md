# 🎮 Room P3-Capstone: The Banking Log Gauntlet (Phase 3 Boss Arena)

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ FINAL BOSS ROOM: The Banking Log Gauntlet      ⭐ DIFFICULTY: Expert │
│ 🎯 TOPIC: Full Multi-Tier Ingestion & CIM Norm.   💎 REWARD: 500 XP     │
│ ⏱️ ESTIMATED TIME: 60 Mins                         🛡️ CATEGORY: Capstone │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 0 — Mission Critical FinCorp Settlement Engine Onboarding!**  
> FinCorp Global, an international investment bank moving $12 billion daily, is deploying its mission-critical Core Banking Settlement Engine (`fincorp:banking:core`).  
> The previous onboarding attempt caused a massive cluster fire:
> - Thousands of multi-line Java transactions were fragmented into unsearchable 1-line shards.
> - High-frequency Kubernetes `/healthz` pings (15,000 EPS) consumed 45% of the enterprise license in 6 hours.
> - Raw 16-digit credit card primary account numbers (PAN) and Social Security Numbers (SSN) leaked unencrypted into `_raw` disk storage, triggering a Tier-1 PCI-DSS compliance audit breach.
> - Daily rotated CSV audit exports ceased indexing due to Fishbucket CRC collisions.
>
> You have been appointed **Principal Splunk Architect**. You have full root and admin authority across all tiers.  
> Your mission is to construct a flawless, production-grade, hardened ingestion pipeline from the edge Universal Forwarders to the Search Head Cluster.
> Conquer all 5 stages to capture all 5 capstone flags and claim your **Principal Splunk Architect** certification!

---

## 🗺️ Master Architecture & Target Environment

![Phase 3 Capstone Architecture 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_phase3_capstone_gauntlet_3d_1792125456722.jpg)
*Figure P3-C.1: The Production End-to-End Multi-Tier Ingestion & Knowledge Highway.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Forwarder Tier (UF):  uf-edge-01.fincorp.internal (Universal Forwarder 9.x)│
│ • Parsing Tier (HF):    hf-ingest-01.fincorp.internal (Port 9997 In / Out)   │
│ • Indexer Tier (IDX):   idx-cluster-01..03 (Index: banking_vault, Port 9997) │
│ • Search Tier (SHC):    shc-captain-01:8000 (Knowledge & CIM Acceleration)    │
│ • Monitored Target:     /var/log/fincorp/banking/.../*.log (Multi-tier app)  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Edge Forwarder Intake & Anti-Collision Monitoring (100 XP)

### 📖 Incident Details
The Universal Forwarder on `uf-edge-01` must recursively monitor all `.log` and `.json` transaction records inside `/var/log/fincorp/banking/` and its subdirectories.  
However, the application writes daily settlement CSV extracts that share an identical 180-byte header line. Yesterday's daily file failed to ingest because the forwarder's Fishbucket calculated an identical 256-byte CRC hash! Furthermore, temporary `.tmp` files and compressed `.gz` archives must never be monitored.

### 🛠️ Hands-on Architecture
Configure the production inputs app on the Universal Forwarder:
`/opt/splunkforwarder/etc/apps/fincorp_uf_inputs/local/inputs.conf`

```ini
[monitor:///var/log/fincorp/banking/.../*.log]
disabled = false
index = banking_vault
sourcetype = fincorp:banking:core
whitelist = \.(log|json)$
blacklist = (\.(gz|tmp)$|debug)
crcSalt = <SOURCE>
ignoreOlderThan = 14d
```

Verify your configuration with `btool`:
```bash
/opt/splunkforwarder/bin/splunk btool inputs list --debug | grep -A 8 "banking"
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What exact setting in `inputs.conf` forces the fishbucket to incorporate the unique file path into the CRC hash calculation, guaranteeing identical daily CSV headers will never collide?  
*(Answer Format: `******* = <******>`)*

<details>
<summary>💡 Need a Hint?</summary>
It salts the CRC hashing algorithm with the literal string &lt;SOURCE&gt;.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>crcSalt = &lt;SOURCE&gt;</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{CRC_SALT_SOURCE_ZERO_COLLISIONS_SECURED}
```

---

## 🎯 TASK 2: High-Performance Event Breaking & Timestamp Precision (100 XP)

### 📖 Incident Details
The banking logs contain nested JSON payloads and Java stack traces spanning up to 45 lines. The default `chunk_size` and line-merging engine was fragmenting single transactions across multiple events, creating corrupt timestamps and false 1970 event dates.

Sample raw event from the application:
```text
2026-10-16 04:15:32.842 UTC [THREAD-POOL-42] INFO  FinSettlementEngine - TransactionID=TX998231 ClientIP=198.51.100.45 ServerIP=10.0.12.8 Port=443 User=c_morgan AccountID=ACC-88219 Status=APPROVED LatencyMicroSec=142000 PAN=4532-1192-8491-9021 SSN=981-22-4910 BranchCode=BR-801
Payload: {
   "action": "WIRE_TRANSFER",
   "amount": 450000.00,
   "currency": "USD",
   "beneficiary": "Apex International Ltd"
}
```

### 🛠️ Hands-on Architecture
Deploy the event-breaking parser to the ingestion tier (`hf-ingest-01` or Indexers):
`/opt/splunk/etc/apps/fincorp_parsing/local/props.conf`

```ini
[fincorp:banking:core]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}
TRUNCATE = 250000
TIME_PREFIX = ^
MAX_TIMESTAMP_LOOKAHEAD = 35
TIME_FORMAT = %Y-%m-%d %H:%M:%S.%3N %Z
TZ = UTC
MAX_DAYS_AGO = 30
MAX_DAYS_HENCE = 2
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Why is `SHOULD_LINEMERGE = false` mandatory when implementing regex-driven `LINE_BREAKER` in production?  
*(Answer Format: Disables the ****** ****** line-merging engine and executes high-speed ***** compiled regex breaking)*

<details>
<summary>💡 Need a Hint?</summary>
It bypasses the legacy Python/Perl-style regex line-merging engine and uses the compiled C++ engine.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Disables the legacy memory line-merging engine and executes high-speed C++ compiled regex breaking</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{LINE_BREAKER_COMPILED_CPP_PRECISION_ACHIEVED}
```

---

## 🎯 TASK 3: Ingestion-Time Filtering & In-Memory PCI-DSS Masking (100 XP)

### 📖 Incident Details
1. **Healthcheck Avalanche:** Kubernetes liveness probes generate `GET /healthz HTTP/1.1 200 OK` at 15,000 EPS. These events carry zero analytical value and must be incinerated before hitting the licensing meter.
2. **PCI-DSS Compliance Mandate:** The Payment Card Industry Data Security Standard (PCI-DSS 4.0) mandates that Primary Account Numbers (16-digit credit cards) and Social Security Numbers must **never** be committed to disk storage in plaintext.

### 🛠️ Hands-on Architecture
Update `/opt/splunk/etc/apps/fincorp_parsing/local/props.conf`:
```ini
[fincorp:banking:core]
TRANSFORMS-drop_health = drop_k8s_healthchecks
SEDCMD-mask_pan = s/\b(?:\d{4}-){3}(\d{4})\b/XXXX-XXXX-XXXX-\1/g
SEDCMD-mask_ssn = s/\b\d{3}-\d{2}-(\d{4})\b/XXX-XX-\1/g
```

Create `/opt/splunk/etc/apps/fincorp_parsing/local/transforms.conf`:
```ini
[drop_k8s_healthchecks]
REGEX = (?i)(GET\s+/healthz|kube-probe)
DEST_KEY = queue
FORMAT = nullQueue
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
On which Splunk architecture tier MUST `SEDCMD` and `nullQueue` transforms be deployed, and what occurs if they are mistakenly placed on the Search Head?  
*(Answer Format: Deployed on the ******* tier (HF or IDX); placing on SH causes plaintext PII to commit to **** and license to be *****)*

<details>
<summary>💡 Need a Hint?</summary>
Parsing occurs on the Indexing or Heavy Forwarder tier. Search Heads do not parse raw data streams.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Deployed on the parsing tier (HF or IDX); placing on SH causes plaintext PII to commit to disk and license to be billed</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{NULLQUEUE_INCINERATOR_AND_SEDCMD_VAULT_ACTIVE}
```

---

## 🎯 TASK 4: Search Head Knowledge Layer & CIM Normalization (100 XP)

### 📖 Incident Details
Security analysts and financial fraud officers access data through the Search Head Cluster (`shc-captain-01`).  
They require:
1. High-speed key-value extraction without regex overhead.
2. Field aliasing to conform with the **Splunk Common Information Model (CIM)** `Network_Traffic` and `Authentication` data models:
   - `ClientIP` $\rightarrow$ `src`
   - `ServerIP` $\rightarrow$ `dest`
   - `Port` $\rightarrow$ `dest_port`
   - `User` $\rightarrow$ `user`
3. Calculated fields:
   - `duration_sec`: Convert `LatencyMicroSec` to fractional seconds (`round(LatencyMicroSec / 1000000, 3)`).
   - `action`: Normalize `Status` (`APPROVED` $\rightarrow$ `success`, `DECLINED` $\rightarrow$ `failure`).
4. Automatic enrichment via `branch_master_list.csv` lookup:
   - Input: `BranchCode`
   - Output: `branch_name`, `region`, `risk_tier`

### 🛠️ Hands-on Architecture
Configure `/opt/splunk/etc/apps/fincorp_search/local/props.conf` on the Search Head:
```ini
[fincorp:banking:core]
REPORT-extract_kv = extract_banking_delims
FIELDALIAS-cim_network = ClientIP AS src, ServerIP AS dest, Port AS dest_port
FIELDALIAS-cim_auth = User AS user
EVAL-duration_sec = round(LatencyMicroSec / 1000000, 3)
EVAL-action = case(Status=="APPROVED", "success", Status=="DECLINED", "failure", true(), "unknown")
LOOKUP-enrich_branch = branch_directory BranchCode OUTPUT branch_name, region, risk_tier
```

Configure `/opt/splunk/etc/apps/fincorp_search/local/transforms.conf`:
```ini
[extract_banking_delims]
DELIMS = " ", "="

[branch_directory]
filename = branch_master_list.csv
case_sensitive_match = false
```

Deploy lookup table `/opt/splunk/etc/apps/fincorp_search/lookups/branch_master_list.csv`:
```csv
BranchCode,branch_name,region,risk_tier
BR-801,Wall Street Headquarters,US-East,Low
BR-802,Canary Wharf Financial,EMEA,Medium
BR-803,Singapore Marina Bay,APAC,Low
BR-804,Zurich Vault Exchange,EMEA,High
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
In Splunk's official 10-step search-time execution pipeline, what allows `EVAL-action` to evaluate `Status` or an aliased field reliably?  
*(Answer Format: Field Aliases execute at Step * and Calculated Fields execute at Step *)*

<details>
<summary>💡 Need a Hint?</summary>
Look at Chapter 08 search-time sequence: Field Aliases run at Step 5, Calculated Fields run at Step 6.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Field Aliases execute at Step 5 and Calculated Fields execute at Step 6</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{CIM_MAPPING_EVAL_PIPELINE_SYNCHRONIZED}
```

---

## 🎯 TASK 5: Enterprise Security Tagging & Data Model Acceleration (100 XP)

### 📖 Incident Details
The SOC requires automated detection of high-risk transactions.  
You must configure eventtypes and tags so that declined transactions with high risk scores are automatically recognized by Splunk Enterprise Security (ES) without modifying queries:
- Query: `sourcetype=fincorp:banking:core Status="DECLINED"`
- Eventtype: `fincorp_declined_transaction`
- Tags: `financial`, `transaction`, `failure`

### 🛠️ Hands-on Architecture
Configure `/opt/splunk/etc/apps/fincorp_search/local/eventtypes.conf`:
```ini
[fincorp_declined_transaction]
search = sourcetype=fincorp:banking:core Status="DECLINED"
```

Configure `/opt/splunk/etc/apps/fincorp_search/local/tags.conf`:
```ini
[eventtype=fincorp_declined_transaction]
financial = enabled
transaction = enabled
failure = enabled
```

Verify with accelerated SPL search:
```spl
index=banking_vault sourcetype=fincorp:banking:core tag=financial tag=failure
| stats count, values(branch_name) by user, src, dest
```

---

### ❓ Challenge Questions — Task 5

#### Question 5.1
Which high-speed command allows you to verify that accelerated `.tsidx` data model summaries are actively populating for your normalized events?  
*(Answer Format: | ******)*

<details>
<summary>💡 Need a Hint?</summary>
The command that queries accelerated index-time summary tsidx files directly without raw event extraction.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>| tstats</code>
</details>

**🚩 Capture the Flag 5.1:**
```text
FLAG{TSTATS_ES_DATA_MODEL_ACCELERATED_VICTORY}
```

---

## 🏆 Final Boss Flag Submission & Phase 3 Graduation

Combine all five mission flags to claim your Phase 3 Grand Finale Trophy:

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               PHASE 3 CAPSTONE BOSS COMPLETION TROPHY                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{CRC_SALT_SOURCE_ZERO_COLLISIONS_SECURED}             ║
║ [X] FLAG 2.1: FLAG{LINE_BREAKER_COMPILED_CPP_PRECISION_ACHIEVED}         ║
║ [X] FLAG 3.1: FLAG{NULLQUEUE_INCINERATOR_AND_SEDCMD_VAULT_ACTIVE}        ║
║ [X] FLAG 4.1: FLAG{CIM_MAPPING_EVAL_PIPELINE_SYNCHRONIZED}               ║
║ [X] FLAG 5.1: FLAG{TSTATS_ES_DATA_MODEL_ACCELERATED_VICTORY}             ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 CONGRATULATIONS OPERATOR!**  
> You have conquered the Banking Log Gauntlet, mastered the Splunk Data Onboarding & Parsing Pipeline, and earned **+500 XP**!  
> Next Step: Complete the **10 Master Milestone Exam Questions** in Chapter 13 to earn your official promotion to **Principal Splunk Architect** and unlock **Phase 4: Advanced SPL & Search Optimization**!
