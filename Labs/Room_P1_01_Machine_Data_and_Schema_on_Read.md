# 🎮 Room P1-01: The Machine Data Decoder & Schema-on-Read Triage

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: The Machine Data Decoder         ⭐ DIFFICULTY: Easy          │
│ 🎯 TOPIC: Unstructured Logs & Metadata    💎 REWARD: 150 XP            │
│ ⏱️ ESTIMATED TIME: 25 Mins                🛡️ CATEGORY: Ingestion Fund. │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Emergency Incident — The Rogue Payment Gateway!  
> At 08:14 AM, the finance department alerted IT that customers are complaining of double charges.  
> The web servers are generating thousands of unstructured JSON, CSV, and raw syslog lines every minute. Traditional relational databases (RDBMS) failed to ingest the logs because the database schema rejected unknown fields.  
> Your mission as the incoming Splunk Administrator is to ingest this messy, unstructured data stream into Splunk, leverage **Schema-on-Read** to extract fields on the fly, verify the **5 Default Metadata Keys**, and find the rogue transactions!

---

## 🗺️ Mission Architecture & Ingestion Funnel

![Machine Data Ingestion Funnel](../assets/05_machine_data_types_3d.jpg)
*Figure 1.1: The Machine Data Ingestion Funnel (Syslog, JSON, Web Access, Windows Events ➔ Splunk Engine)*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET INCIDENT SPECIFICATIONS                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Ingestion Stream:       /var/log/payment_gateway/transactions.log         │
│ • Data Variety:           Semi-structured JSON + syslog timestamp prefix    │
│ • Schema Requirement:     Schema-on-Read (Zero pre-defined table schemas)   │
│ • Default Metadata Keys:  host, source, sourcetype, index, _time            │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Traditional RDBMS vs Splunk Schema-on-Read (35 XP)

### 📖 Scenario Context
Traditional SQL databases require **Schema-on-Write** (tables, columns, data types must be pre-defined with `CREATE TABLE`). If a software update introduces a new field like `"crypto_wallet_id": "0x7F..."`, SQL crashes or drops the field.  
Splunk uses **Schema-on-Read**:
1. Splunk stores raw text exactly as it was created on disk (`_raw`).
2. Fields are calculated dynamically at search time using regex.
3. If new fields appear, zero reconfiguration or schema alterations are needed!

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the core operational difference between Schema-on-Write (RDBMS) and Schema-on-Read (Splunk)?  
- [A] Schema-on-Write requires database tables and schemas to exist before data can be inserted; Schema-on-Read extracts fields dynamically when a search query is executed.
- [B] Schema-on-Read only works for Windows Event Logs.
- [C] Schema-on-Write is 100x faster than Splunk for unstructured logs.
- [D] Schema-on-Read deletes raw logs after parsing.

<details>
<summary>💡 Need a Hint?</summary>
Think about when the field extraction actually happens: at write time or at query/read time?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [A] Schema-on-Write requires upfront schema definitions. Schema-on-Read stores raw data and applies regex/extractions at query execution time.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{SCHEMA_ON_READ_DYNAMIC_AGILITY}
```

---

## 🎯 TASK 2: The 5 Immutable Metadata Keys (40 XP)

### 📖 Scenario Context
Every single event indexed into Splunk Enterprise—whether from Linux, Windows, Cisco firewalls, or AWS—must be tagged with **5 Default Metadata Keys**. Without these, Splunk cannot organize or locate data.

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ THE 5 DEFAULT METADATA KEYS                                         │
├─────────────────┬──────────────────────────────────────────────────────┤
│ 1. host         │ The originating machine/device hostname or IP.       │
│ 2. source       │ The specific path, file name, or network port.       │
│ 3. sourcetype   │ The data format/type telling Splunk how to parse it. │
│ 4. index        │ The logical repository partition where data lives.   │
│ 5. _time        │ Epoch timestamp extracted from the event payload.    │
└─────────────────┴──────────────────────────────────────────────────────┘
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
An engineer configures a file monitor on `/var/log/apache2/access.log` on host `web-prod-01`.  
Which metadata key determines **how Splunk breaks events into lines and formats timestamps**?  
*(Answer Format: `**********`)*

<details>
<summary>💡 Need a Hint?</summary>
It combines "source" and "type". It dictates `props.conf` stanzas!
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>sourcetype</code><br/>
The <code>sourcetype</code> governs event breaking (<code>LINE_BREAKER</code>), timestamp extraction (<code>TIME_PREFIX</code>), and search-time field extractions.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{SOURCETYPE_RULES_THE_PIPELINE}
```

---

## 🎯 TASK 3: Triage the Raw Event Payload (`_raw` & `_time`) (40 XP)

### 📖 Scenario Context
You open Search & Reporting and inspect the raw incoming event:
```text
2026-09-12 08:14:22.412 UTC host="web-gw-09" status="FAIL" action="DOUBLE_CHARGE" amount="499.00" uid="USR-8821"
```

Splunk stores the original text inside the special internal field named **`_raw`**, and parses the timestamp into **`_time`** as a UNIX epoch value (`1789200862`).

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
In Splunk, what is the default internal field name that stores the exact, unaltered original text string of an event?  
*(Answer Format: `_***`)*

<details>
<summary>💡 Need a Hint?</summary>
It begins with an underscore and has 3 letters.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>_raw</code><br/>
The <code>_raw</code> field preserves the byte-for-byte fidelity of the log for legal and forensic compliance.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{RAW_LOG_DATA_PRESERVATION}
```

---

## 🎯 TASK 4: Ingestion Funnel Audit (35 XP)

### 📖 Scenario Context
To stop the double charges, you run a targeted SPL search to find all events where `action="DOUBLE_CHARGE"`:
```spl
index=payment_prod sourcetype=gateway_json action="DOUBLE_CHARGE"
| stats count by uid, amount
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Why is filtering by `index` and `sourcetype` at the very beginning of a search query considered an essential best practice for an administrator?  
- [A] It allows Splunk to skip searching irrelevant index bucket directories entirely on disk.
- [B] It bypasses the need for an admin password.
- [C] It automatically restarts the indexer.
- [D] It reduces the Splunk license cost per query.

<details>
<summary>💡 Need a Hint?</summary>
Think about disk I/O and bucket partition pruning.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [A] Index and sourcetype filtering enables partition pruning, allowing the Indexer to read only the relevant bucket folders and TSIDX lexicon files.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{INDEX_PARTITION_PRUNING_SPEED}
```

---

## 🏆 Room P1-01 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM P1-01 COMPLETE                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 150 / 150 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Schema-on-Read vs Schema-on-Write, 5 Metadata Keys, │
│   _raw Preservation, Partition Pruning Best Practice                   │
│                                                                        │
│ ➡️ NEXT ROOM: Room P1-02 — Multi-Tier Architecture & Component Recon  │
└────────────────────────────────────────────────────────────────────────┘
```
