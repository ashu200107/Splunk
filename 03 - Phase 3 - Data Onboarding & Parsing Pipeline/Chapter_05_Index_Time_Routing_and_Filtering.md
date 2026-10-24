# 📘 Chapter 05 (Phase 3): Advanced Index-Time Filtering & Routing

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 20 | **Milestone:** Selective Ingestion & Licensing Cost Optimization | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_05_Index_Time_Routing_and_Filtering.md`  
> **Interactive Cyber Range Lab:** [Room P3-05: The NullQueue Trash Chute & Selective Routing](../Labs/Room_P3_05_NullQueue_Trash_Chute.md) `[250 XP]`

---

## 🏗️ 1. The Simple Explanation: "The Automated Parcel Sorter & Incinerator"

Imagine a massive post office sorting facility processing **10,000,000 packages** a day:
- 40% of those packages are empty junk flyers, repetitive automated healthcheck pings, and debug chatter that nobody will ever read.
- If you pay a shipping fee on every single gram of junk mail (Splunk's daily license quota) and store them in expensive underground vaults, you waste **hundreds of thousands of dollars** every year!
- **This is why Index-Time Routing & Filtering exists.**
  - **`nullQueue` is the Incineration Chute:** It instantly vaporizes junk logs in memory before they are counted against your daily license and before they consume a single byte of disk storage.
  - **Dynamic Routing** is the **Automated Railroad Switch**: It inspects each parcel with optical lasers and steers high-value payment logs to the armored PCI vault (`index=pci`), security logs to the SOC vault (`index=security`), and routine logs to cold storage.

![Splunk Index-Time Routing and nullQueue 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_index_time_routing_nullqueue_3d_1792086885456.jpg)
*Figure 3.5: The Post Office Parcel Sorter Analogy — How optical regex gates drop debug spam into nullQueue and steer valuable logs to their dedicated index vaults.*

---

## 🔍 2. Step-by-Step: The 5-Step Ingestion Routing Journey

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE 5-STEP JOURNEY OF INDEX-TIME ROUTING & FILTERING       │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: Raw Stream Arrives at Parsing Queue (Heavy Forwarder / Indexer)│
│         - Events arrive on port 9997 with initial metadata.            │
│                                                                        │
│ Step 2: props.conf Calls the Routing Sorter                            │
│         - Splunk matches [sourcetype] and executes:                    │
│           TRANSFORMS-filter = discard_healthchecks, route_payments     │
│                                                                        │
│ Step 3: transforms.conf Evaluates the Regex Sorter                     │
│         - Regex scans event payload text.                              │
│         - If MATCH (e.g. GET /healthz HTTP/1.1):                      │
│           • Changes DEST_KEY = queue                                   │
│           • Sets FORMAT = nullQueue                                    │
│                                                                        │
│ Step 4: The nullQueue Vaporization                                     │
│         - Event is immediately dropped from RAM!                       │
│         - License bytes counted: 0 BYTES!                              │
│         - Disk space consumed: 0 BYTES!                                │
│                                                                        │
│ Step 5: Legitimate Events Steered to Target Index                      │
│         - Surviving events have DEST_KEY = _MetaData:Index rewritten:  │
│           FORMAT = pci_compliance_vault                                │
│         - Event proceeds to indexQueue and commits to disk!            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🗑️ 3. The Mechanics of `nullQueue`: Dropping Unwanted Logs

Splunk provides a special in-memory black hole named **`nullQueue`**.  
When an event's target queue is changed from `indexQueue` to `nullQueue`, Splunk discards the event from memory immediately after parsing.

### 💰 Why `nullQueue` is an Administrator's Superpower:
1. **100% License Exemption:** Events dropped to `nullQueue` are discarded **before** license metering occurs. They consume **0 GB** of your daily quota!
2. **IOPS & Disk Savings:** Junk data never touches SSD or NVMe disks, eliminating disk queue bottlenecks.
3. **Search Speed Boost:** Search heads don't have to sift through billions of useless healthcheck logs.

---

## 🛠️ 4. The Two Essential Filtering Strategies

### Pattern A: Blacklist Filtering (Drop Specific Noisy Events)
Use this when you want to keep **95% of events**, but drop specific spam (e.g. repetitive healthchecks or debug lines):

```ini
# props.conf (Heavy Forwarder or Indexer)
[custom:web:app]
TRANSFORMS-drop_spam = discard_healthchecks

# transforms.conf (Heavy Forwarder or Indexer)
[discard_healthchecks]
REGEX = (?i)(GET\s+/healthz|ping_agent|Keep-Alive)
DEST_KEY = queue
FORMAT = nullQueue
```

---

### Pattern B: Whitelist Filtering (Drop EVERYTHING Except Specific VIP Logs)
Use this when an application outputs 10 GB of noisy logs, but your security team only cares about authentication failures (`LOGIN_FAILED`):

```ini
# props.conf
[custom:verbose:app]
# Order matters! Evaluate discard_all FIRST, then rescue_auth_events SECOND!
TRANSFORMS-filter = discard_all_events, rescue_auth_events

# transforms.conf
# 1. Steer all events toward the trash chute:
[discard_all_events]
REGEX = .
DEST_KEY = queue
FORMAT = nullQueue

# 2. Rescue only matching authentication events back to indexQueue!
[rescue_auth_events]
REGEX = (LOGIN_FAILED|SECURITY_VIOLATION|PRIVILEGE_ESCALATION)
DEST_KEY = queue
FORMAT = indexQueue
```

> [!IMPORTANT]
> Notice the order of directives in `TRANSFORMS-filter`:  
> `discard_all_events, rescue_auth_events`  
> Splunk executes them from left to right. First it flags everything for `nullQueue`, and then if the second regex matches, it flips the destination key back to `indexQueue`!

---

## 🔀 5. Dynamic Index Routing: Steering Events by Content

Instead of sending an entire server's logs to one generic index, you can dynamically steer events into different indexes based on keywords inside the log text:

```ini
# props.conf
[fincorp:multipurpose:stream]
TRANSFORMS-route_indexes = route_pci, route_security, route_audit

# transforms.conf
[route_pci]
REGEX = (credit_card|transaction_auth|wire_transfer)
DEST_KEY = _MetaData:Index
FORMAT = pci_vault

[route_security]
REGEX = (failed_login|sudo_escalation|unauthorized)
DEST_KEY = _MetaData:Index
FORMAT = security_vault

[route_audit]
REGEX = (user_logout|profile_update)
DEST_KEY = _MetaData:Index
FORMAT = general_audit
```

> [!WARNING]
> The target index (e.g. `pci_vault`, `security_vault`) **must already exist** in `indexes.conf` on your Indexer Cluster! If Splunk tries to route an event to a non-existent index, the event will fail and generate an internal routing error!

---

## 🌐 6. Routing to Different Indexer Clusters or Third Parties (`_TCP_ROUTING`)

In large multinational enterprises, you may need to route PCI data to a dedicated European indexer cluster, while sending non-PCI data to an indexer cluster in the United States:

```ini
# props.conf
[fincorp:payment:stream]
TRANSFORMS-route_clusters = route_to_europe_cluster

# transforms.conf
[route_to_europe_cluster]
REGEX = (EU_CUSTOMER|IBAN|GDPR)
DEST_KEY = _TCP_ROUTING
FORMAT = europe_indexer_group
```
*(Where `europe_indexer_group` is defined as a `[tcpout:europe_indexer_group]` target in `outputs.conf`).*

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-05

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-05: The NullQueue Trash Chute & Selective Routing           │
│ ⭐ DIFFICULTY: Intermediate | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins    │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> It's Monday morning, and your enterprise Splunk license just suffered a **500 GB Quota Breach Warning**!  
> Triage reveals that a microservice deployment turned on `DEBUG` mode, flooding index `web` with 250,000 healthcheck pings per minute (`GET /api/v1/health HTTP/1.1`).  
> In addition, high-risk wire transfers containing `VIP_HIGH_VALUE_WIRE` are dangerously sitting in unencrypted generic index `web` instead of restricted index `pci_vault`!  
> Your mission is to build regex filters to vaporize the healthcheck flood to `nullQueue`, dynamically route VIP transactions to `pci_vault`, and capture all 5 flags!

👉 **[Enter the Cyber Range: Room P3-05](../Labs/Room_P3_05_NullQueue_Trash_Chute.md)** `[250 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **What is the exact name of Splunk's in-memory discard queue, and how does sending data there impact your daily license consumption?**
2. **In `transforms.conf`, what `DEST_KEY` must be set to route an event to `nullQueue` versus routing an event to a different index?**
3. **When implementing a "Drop everything EXCEPT specific logs" whitelist filter, why must `discard_all` appear before `rescue_events` in the `TRANSFORMS-` line of `props.conf`?**
4. **What happens if a `transforms.conf` routing rule redirects an event to an index that has not been defined in `indexes.conf` on the Indexers?**
5. **On which Splunk architectural tier must `DEST_KEY = queue` and `DEST_KEY = _MetaData:Index` rules be configured to take effect?**

---
*Ready to advance to Chapter 06: Index-Time Data Masking & Anonymization (`SEDCMD` PII/PCI Redaction)?*
