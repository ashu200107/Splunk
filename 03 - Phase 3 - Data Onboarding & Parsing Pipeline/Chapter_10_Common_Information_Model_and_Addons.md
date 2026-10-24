# 📘 Chapter 10 (Phase 3): Common Information Model (CIM) & Add-ons

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 25 | **Milestone:** Enterprise Security Normalization & CIM Data Models | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_10_Common_Information_Model_and_Addons.md`  
> **Interactive Cyber Range Lab:** [Room P3-10: CIM Normalization Arena](../Labs/Room_P3_10_CIM_Normalization_Arena.md) `[300 XP]`

---

## 🏗️ 1. The Simple Explanation: "The Universal Electrical Adapter & Diplomatic Protocol"

Imagine you travel across 20 countries with your laptop:
- In the UK, plugs have three rectangular prongs; in Europe, two round prongs; in the US, two flat blades.
- If you had to buy 20 different laptops for 20 countries, you would go bankrupt. Instead, you carry **one Universal Travel Adapter**.
- **This is what the Common Information Model (CIM) is in Splunk.**
  - If your enterprise uses Cisco firewalls, Palo Alto networks, Fortinet gateways, and AWS VPC Flow logs, each vendor names IP fields differently (`src_ip`, `SourceIp`, `orig_addr`, `c_ip`).
  - Without CIM, a security analyst building a ransomware detection alert must write a 50-line search combining 15 vendor queries with `OR`.
  - **With CIM**, all network logs are mapped into the **Universal Data Model (`Network_Traffic`)** with standardized fields: **`src`**, **`dest`**, **`dest_port`**, and **`action`**!
  - Now, the analyst writes **ONE single query** that detects threats across all 20 firewall vendors simultaneously!

![Splunk CIM Normalization 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_cim_normalization_3d_1792124795129.jpg)
*Figure 3.10: The CIM Normalization Hub — How Technology Add-ons (TAs) standardize multi-vendor streams into unified data models powering Splunk Enterprise Security.*

---

## 🔍 2. Step-by-Step: The 5-Step CIM Normalization Flow

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE 5-STEP JOURNEY OF CIM NORMALIZATION                    │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: Raw Vendor Logs Arrive on Indexers                             │
│         - Cisco: "src_ip=10.0.0.1 dst_ip=198.51.100.2 action=Permitted"│
│         - Palo:  "src=10.0.0.1 dst=198.51.100.2 act=allow"            │
│                                                                        │
│ Step 2: Technology Add-on (TA) Extracts Raw Fields                     │
│         - props.conf extracts raw field values.                        │
│                                                                        │
│ Step 3: Field Aliases Standardize Variable Names                       │
│         - Cisco: src_ip AS src, dst_ip AS dest                         │
│         - Palo:  src AS src, dst AS dest                               │
│                                                                        │
│ Step 4: Eventtypes & Tags Categorize the Event                         │
│         - Cisco events tagged: tag=network, tag=communicate           │
│         - Palo events tagged:  tag=network, tag=communicate           │
│                                                                        │
│ Step 5: Data Model Acceleration (DMA) Ingests Normalized Records       │
│         - The Network_Traffic data model accelerates both streams!     │
│         - Splunk Enterprise Security (ES) dashboards light up!         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ 3. The 4 Components of the CIM Architecture

To make custom application data CIM-compliant, you configure four interconnected pieces on the **Search Head**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 4-PIECE CIM ENGINE                            │
├────────────────────────────────────────────────────────────────────────┤
│ 1. EXTRACT- (props.conf)                                               │
│    • Pulls raw fields out of messy text.                               │
├────────────────────────────────────────────────────────────────────────┤
│ 2. FIELDALIAS- (props.conf)                                            │
│    • Re-maps vendor field names into certified CIM fields:             │
│      client_ip AS src, remote_host AS dest, log_user AS user           │
├────────────────────────────────────────────────────────────────────────┤
│ 3. EVENTTYPE (eventtypes.conf)                                         │
│    • Groups events by category:                                        │
│      [fincorp_vpn_auth]                                                │
│      search = sourcetype=fincorp:vpn "AUTHENTICATION"                  │
├────────────────────────────────────────────────────────────────────────┤
│ 4. TAGS (tags.conf)                                                    │
│    • Attaches standard CIM taxonomic tags to the eventtype:            │
│      [eventtype=fincorp_vpn_auth]                                      │
│      authentication = enabled                                          │
│      privileged = enabled                                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 4. The Major CIM Data Models in Enterprise Splunk

| CIM Data Model | Purpose & Data Sources | Required CIM Fields | Required Tags |
| :--- | :--- | :--- | :--- |
| **`Authentication`** | Logins, SSO, Active Directory, MFA, SSH | `user`, `src`, `dest`, `action` (`success`/`failure`) | `tag=authentication` |
| **`Network_Traffic`** | Firewalls, Switches, Routers, NetFlow | `src`, `dest`, `dest_port`, `action` (`allowed`/`blocked`) | `tag=network`, `tag=communicate` |
| **`Web`** | Web servers, Proxies, CDNs, WAFs | `src`, `dest`, `http_method`, `status`, `url` | `tag=web`, `tag=proxy` |
| **`Change`** | CloudTrail, Auditd, File Integrity, IAM | `user`, `command`, `object`, `action` (`created`/`deleted`) | `tag=change` |
| **`Malware`** | Antivirus, EDR, CrowdStrike, Defender | `file_name`, `file_hash`, `dest`, `action` | `tag=malware`, `tag=attack` |

---

## 🧩 5. Technology Add-ons (TAs): Pre-Packaged CIM Compliance

A **Technology Add-on (TA)** is a specialized Splunk app downloaded from Splunkbase (e.g. `Splunk_TA_cisco-asa`, `Splunk_TA_paloalto`, `Splunk_TA_windows`).

### What is Inside an Official TA?
An official TA contains **zero dashboards and zero user reports**. It is purely an ingestion and normalization engine:
- `default/props.conf`: Built-in event breaking, timestamp parsing, and field extractions.
- `default/transforms.conf`: Delimiters, lookups, and regex engines.
- `default/eventtypes.conf` & `tags.conf`: Certified CIM tags.

> [!TIP]
> **Enterprise Best Practice:**  
> Whenever deploying a new hardware or cloud vendor in your enterprise, **install their official TA first**. Deploy the TA to:
> 1. **Heavy Forwarders & Indexers:** For index-time parsing (`props.conf`, `transforms.conf`).
> 2. **Search Heads:** For search-time field extractions, lookups, and CIM tags!

---

## 🔍 6. How to Validate CIM Compliance via SPL

To verify whether your newly onboarded logs comply with the Common Information Model, run a `tstats` query against the accelerated data model:

```spl
| datamodel Network_Traffic All_Traffic search 
| stats count by All_Traffic.action, All_Traffic.src, All_Traffic.dest, All_Traffic.vendor_product
```

If your logs return counts in this query with populated `src`, `dest`, and `action` fields, **your data is 100% CIM-compliant** and will immediately feed Splunk Enterprise Security correlation searches!

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-10

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-10: CIM Normalization Arena & Enterprise Security Setup     │
│ ⭐ DIFFICULTY: Advanced | 💎 REWARD: 300 XP | ⏱️ TIME: 40 Mins        │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> FinCorp Global deployed a new multi-million dollar **Splunk Enterprise Security (ES)** instance.  
> However, the CISO's executive dashboard shows **0 Security Incidents**, despite the corporate network undergoing an active brute-force password attack!  
> Triage reveals:
> 1. The custom VPN authentication logs are missing the required `authentication` and `privileged` CIM tags.
> 2. Firewall events use non-standard field names `client_address` and `target_port`, which the `Network_Traffic` data model ignores.
> 3. Login actions output `STATUS=OK` and `STATUS=REJECTED` instead of CIM standard `action=success` and `action=failure`.  
> Your mission is to build the complete 4-piece CIM normalization pipeline, pass the CIM validation check, and capture all 5 flags!

👉 **[Enter the Cyber Range: Room P3-10](../Labs/Room_P3_10_CIM_Normalization_Arena.md)** `[300 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **Why does Splunk Enterprise Security (ES) require data sources to be compliant with the Common Information Model (CIM)?**
2. **What are the four configuration files in Splunk that together establish CIM compliance for an onboarded log source?**
3. **In the `Authentication` data model, what are the only two valid standardized values allowed for the `action` field?**
4. **What is the functional difference between an App (like Splunk Enterprise Security) and a Technology Add-on (TA)?**
5. **Write the SPL command using the `datamodel` search command to verify that web proxy logs are correctly populating the `Web` data model.**

---
*Ready to advance to Chapter 11: Eventtypes and Tags Classification Architecture?*
