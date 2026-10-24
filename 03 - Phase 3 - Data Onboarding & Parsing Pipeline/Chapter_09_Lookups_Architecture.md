# 📘 Chapter 09 (Phase 3): Lookups Architecture

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 24 | **Milestone:** Data Enrichment & KV Store Database Architecture | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_09_Lookups_Architecture.md`  
> **Interactive Cyber Range Lab:** [Room P3-09: KV Store & Lookup Infiltration](../Labs/Room_P3_09_KV_Store_Lookup_Infiltration.md) `[250 XP]`

---

## 🏗️ 1. The Simple Explanation: "The VIP Rolodex & Relational Bridge"

Imagine you are a security guard monitoring badge swipes at a skyscraper entrance:
- The badge scanner logs only raw numbers: `Badge_ID=98401 Door=4`.
- If a security incident occurs, a list of badge numbers is useless. You need to know: *Who is this person? What department do they work in? What is their security clearance?*
- Instead of forcing the badge reader to write a paragraph of employee bio data on every swipe (which bloats your storage and license!), the guard keeps a **Master Rolodex (Lookup Table)** on their desk.
- Whenever `Badge_ID=98401` appears, the guard glances at the Rolodex and instantly attaches: `name="Sarah Connor" department="Executive Security" clearance="Top Secret"`.
- **This is what Lookups do in Splunk.**
  - Lookups bridge the gap between machine logs and human business context.
  - They enrich raw events at **search time** with static files, dynamic MongoDB collections, or live external APIs without consuming a single byte of license quota!

![Splunk Lookups Architecture 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_lookups_architecture_3d_1792124588117.jpg)
*Figure 3.9: The Data Enrichment Hub — How Search Heads enrich raw streams with static CSV tables, automatic matching, KV Store MongoDB collections, and external scripted lookups.*

---

## 🔍 2. Step-by-Step: The 5-Step Lookup Enrichment Journey

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE 5-STEP JOURNEY OF SEARCH-TIME LOOKUP ENRICHMENT        │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: Raw Event Arrives on Search Head                               │
│         - Text contains: "user_id=usr_9401 status=FAILED"              │
│                                                                        │
│ Step 2: Search Head Identifies Lookup Trigger                          │
│         - SPL includes: | lookup user_directory user_id OUTPUT ...     │
│           OR Automatic Lookup configured in props.conf triggers!       │
│                                                                        │
│ Step 3: Lookup Engine Queries Table in Memory                          │
│         - Searches CSV table, KV Store collection, or external script: │
│           Key: usr_9401 ──► Match Found!                               │
│                                                                        │
│ Step 4: Output Fields Injected into the Event Record                   │
│         - Appends new virtual fields in RAM:                           │
│           full_name = "Alice Walker"                                   │
│           department = "Treasury"                                      │
│           threat_tier = "Critical VIP"                                 │
│                                                                        │
│ Step 5: Downstream SPL Aggregates Across Enriched Context              │
│         - SPL: | stats count by department, threat_tier                │
│         - Instant business intelligence without licensing cost!        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ 3. The 4 Major Lookup Architectures in Splunk

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           THE 4 SPLUNK LOOKUP TYPES                               │
├─────────────────────┬─────────────────────────────────┬───────────────────────────┤
│ LOOKUP TYPE         │ HOW IT WORKS                    │ BEST PRODUCTION USE CASE  │
├─────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ 1. Static CSV       │ Flat `.csv` file stored in      │ Small, unchanging tables  │
│    Lookup           │ `<app>/lookups/`. Cached in RAM.│ (<100 MB): HTTP status    │
│                     │ Portable, simple, read-only.    │ codes, port-to-service.   │
├─────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ 2. Automatic        │ Configured in `props.conf` to   │ Core infrastructure logs: │
│    Lookup           │ run silently on every search    │ enriching `src_ip` with   │
│                     │ without typing `| lookup`.      │ asset owner automatically.│
├─────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ 3. KV Store         │ Embedded MongoDB (`mongod`)     │ Large (>100 MB), dynamic  │
│    Lookup           │ running on port 8191. Supports  │ data: asset inventories,  │
│                     │ real-time reads & writes (CRUD)!│ state tracking, threat IOC│
├─────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ 4. External         │ Executes a Python or Bash script│ Live external queries:    │
│    Scripted Lookup  │ on the Search Head for every    │ VirusTotal IP reputation, │
│                     │ matching event.                 │ active DNS resolution.    │
└─────────────────────┴───────────────────────────────┴───────────────────────────┘
```

---

## 🛠️ 4. The 3-File Handshake: Setting Up an Automatic CSV Lookup

To build a professional automatic lookup, an administrator creates three interconnected files inside an app directory on the **Search Head**:

### File 1: The Raw CSV Data File
Path: `$SPLUNK_HOME/etc/apps/fincorp_app/lookups/employee_directory.csv`
```csv
user_id,employee_name,department,security_clearance
usr_101,John Doe,Engineering,Secret
usr_102,Jane Smith,Finance,Top Secret
usr_103,Bob Vance,Refrigeration,Public
```

### File 2: The Lookup Definition (`transforms.conf`)
Path: `$SPLUNK_HOME/etc/apps/fincorp_app/local/transforms.conf`
```ini
[employee_lookup_definition]
filename = employee_directory.csv
case_sensitive_match = false
default_match = UNKNOWN
```

### File 3: The Automatic Invocation (`props.conf`)
Path: `$SPLUNK_HOME/etc/apps/fincorp_app/local/props.conf`
```ini
[fincorp:auth:app]
# Syntax: LOOKUP-<class> = <definition_name> <lookup_input> AS <event_field> OUTPUT <lookup_output>
LOOKUP-enrich_employees = employee_lookup_definition user_id AS user OUTPUT employee_name, department, security_clearance
```

> **The Result:** Whenever an analyst searches `sourcetype=fincorp:auth:app`, the fields `employee_name`, `department`, and `security_clearance` appear automatically in the field sidebar with **zero user effort**!

---

## 🍃 5. KV Store Lookups: Enterprise Real-Time MongoDB Database

When lookup tables grow larger than **100 MB** or require **dynamic updates from SPL searches**, flat CSV files break down. Splunk provides an enterprise solution: **KV Store**.

### Why KV Store Beats CSV:
1. **Embedded MongoDB Daemon (`mongod` on TCP Port 8191):** Runs high-performance B-tree indexed queries.
2. **Read & Write via SPL:** Searches can write directly to KV Store using `| outputlookup` and update existing records using key matching!
3. **Multi-Field Primary Keys:** Supports hierarchical indexing for instant lookups.
4. **Replication:** Automatically synchronized across all Search Head Cluster members.

### Setting Up a KV Store Collection:

```ini
# $SPLUNK_HOME/etc/apps/fincorp_app/local/collections.conf
[threat_intel_collection]
enforceTypes = true
field.ip = string
field.threat_score = number
field.last_seen = time

# $SPLUNK_HOME/etc/apps/fincorp_app/local/transforms.conf
[threat_intel_lookup]
external_type = kvstore
collection = threat_intel_collection
fields_list = _key, ip, threat_score, last_seen
```

### Interacting with KV Store via SPL:
```spl
# 1. Insert or update threat intelligence records:
| makeresults 
| eval ip="198.51.100.45", threat_score=95, last_seen=now()
| outputlookup threat_intel_lookup

# 2. Query the entire collection directly:
| inputlookup threat_intel_lookup where threat_score > 80
```

---

## ⚡ 6. Performance & Memory Tuning Best Practices

1. **`max_memtable_bytes` Limit:**  
   By default, Splunk limits in-memory CSV caching to **10 MB** (`limits.conf: [lookup] max_memtable_bytes`). If a CSV exceeds this, Splunk page-swaps to disk, severely degrading search speed. **Migrate tables >50 MB to KV Store!**
2. **Output Filtering:**  
   Always specify `OUTPUT <field1>, <field2>` in `props.conf`. Never use `OUTPUTNEW` or naked `OUTPUT` unless necessary, as extracting unneeded columns wastes Search Head RAM.
3. **Case Sensitivity:**  
   Set `case_sensitive_match = false` in `transforms.conf` unless case differentiation is strictly required.

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-09

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-09: KV Store & Lookup Infiltration                          │
│ ⭐ DIFFICULTY: Intermediate | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins    │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> A critical cyber espionage attack is underway!  
> The SOC analysts need to correlate incoming suspicious firewall connections against a real-time threat intelligence feed.  
> However:
> 1. The automatic employee lookup broke because the input field in the event was renamed from `user_id` to `account_id`.
> 2. An analyst uploaded a 350 MB CSV file that is causing out-of-memory errors on the Search Head Cluster.
> 3. An incident response tracker needs a dynamic KV Store collection that can record compromised IP addresses directly from search queries.  
> Your mission is to fix the automatic lookup mapping, provision a high-speed KV Store collection, verify port 8191 MongoDB status, and capture all 5 flags!

👉 **[Enter the Cyber Range: Room P3-09](../Labs/Room_P3_09_KV_Store_Lookup_Infiltration.md)** `[250 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **What are the three configuration files required to set up an automatic CSV lookup on a Search Head?**
2. **What embedded database engine powers Splunk's KV Store, and what default network port does it listen on?**
3. **What is the primary architectural advantage of using a KV Store lookup over a flat CSV lookup file in a multi-user enterprise environment?**
4. **In `props.conf`, what is the functional difference between `OUTPUT` and `OUTPUTNEW` in a `LOOKUP-` directive?**
5. **What SPL command is used to write or update records directly inside a KV Store lookup collection from search results?**

---
*Ready to advance to Chapter 10: Splunk Common Information Model (CIM) & Technology Add-ons (TAs)?*
