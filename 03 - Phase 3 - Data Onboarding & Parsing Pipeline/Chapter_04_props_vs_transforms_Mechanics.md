# 📘 Chapter 04 (Phase 3): props.conf vs transforms.conf Architecture

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 19 | **Milestone:** The Parsing Engine & Tier Distribution Matrix | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_04_props_vs_transforms_Mechanics.md`  
> **Interactive Cyber Range Lab:** [Room P3-04: Props & Transforms Battleground](../Labs/Room_P3_04_Props_and_Transforms_Battleground.md) `[250 XP]`

---

## 🏗️ 1. The Simple Explanation: "The Blueprint vs The Industrial Machine"

Splunk administrators often get confused about why Splunk splits parsing into two distinct configuration files: `props.conf` and `transforms.conf`.

Think of an automobile manufacturing plant:
- **`props.conf` is the Architect’s Blueprint & Routing Slip:** It says: *"When a red sports car frame arrives, send it to Station 4 to install the V8 engine, and send it to Station 7 to apply chrome plating."* `props.conf` doesn't do the welding itself; it decides **WHO** gets worked on and **WHICH** tools to call.
- **`transforms.conf` is the Heavy Industrial Machine:** It is the robotic welding arm and laser cutter. It takes orders from `props.conf` and performs the heavy-duty regex surgery—rewriting fields, masking credit card numbers, routing events to different indexes, or dropping junk into `nullQueue`.

![Splunk props.conf vs transforms.conf 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_props_transforms_tier_matrix_3d_1792086659549.jpg)
*Figure 3.4: The Blueprint & Machinery Analogy — props.conf orchestrates rules while transforms.conf executes deep regex manipulations across enterprise tiers.*

---

## 🔍 2. Step-by-Step: The Handshake Between `props.conf` and `transforms.conf`

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE PROPS.CONF TO TRANSFORMS.CONF HANDSHAKE                │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Raw Event Arrives with Metadata:                                    │
│    sourcetype = fincorp:payment:wire                                   │
│                                                                        │
│ 2. Splunk Opens props.conf and Searches for [fincorp:payment:wire]     │
│    • Finds directive:                                                  │
│      TRANSFORMS-mask_ssn = scrub_social_security                       │
│                                                                        │
│ 3. Splunk Jumps to transforms.conf and Locates [scrub_social_security] │
│    • Executes regex: \d{3}-\d{2}-\d{4}                                 │
│    • Replaces target bytes with XXX-XX-XXXX                            │
│                                                                        │
│ 4. Control Returns to props.conf to Finish Pipeline Execution          │
│    • Event proceeds downstream to the Indexing Queue!                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ 3. The Enterprise Tier Matrix: Who Parses What and Where?

This is **the #1 most critical architectural question** tested on Splunk Enterprise Certified Admin exams:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                    WHERE DO CONFIGURATIONS ACTUALLY EXECUTE?                      │
├───────────────────────┬───────────────────────────────┬───────────────────────────┤
│ SPLUNK COMPONENT TIER │ WHAT EXECUTES HERE?           │ WHAT NEVER RUNS HERE?     │
├───────────────────────┼───────────────────────────────┼───────────────────────────┤
│ Universal Forwarder   │ • inputs.conf (Data capture)  │ • NO props.conf parsing   │
│ (UF - Edge)           │ • outputs.conf (Routing & ACK)│ • NO transforms.conf      │
│                       │ • Basic character encoding    │ • NO regex field extract  │
├───────────────────────┼───────────────────────────────┼───────────────────────────┤
│ Heavy Forwarder (HF)  │ • Full Index-Time Parsing:    │ • Search-time knowledge   │
│ or Indexer Cluster    │   - LINE_BREAKER              │   extractions (EXTRACT-)  │
│ (Parsing/Index Tier)  │   - TIME_PREFIX / TIME_FORMAT │ • Search-time lookups     │
│                       │   - SEDCMD (PII masking)      │ • Calculated fields (EVAL)│
│                       │   - TRANSFORMS- (nullQueue)   │ • Eventtypes & Tags       │
│                       │   - Index-time field routing  │                           │
├───────────────────────┼───────────────────────────────┼───────────────────────────┤
│ Search Head (SH)      │ • Full Search-Time Knowledge: │ • NO LINE_BREAKER         │
│ (Search/Display Tier) │   - EXTRACT- (Inline regex)   │ • NO TIME_FORMAT          │
│                       │   - REPORT- (Search regex)    │ • NO nullQueue routing    │
│                       │   - LOOKUP- (CSV & KV Store)  │ • NO SEDCMD masking       │
│                       │   - EVAL- & FIELDALIAS-       │ (Raw text is already locked│
│                       │   - Data Models & CIM Normal  │  inside index journal!)   │
└───────────────────────┴───────────────────────────────┴───────────────────────────┘
```

---

## ⚖️ 4. Ingestion-Time (Index-Time) vs Search-Time Directives

In `props.conf`, directives are strictly split into two execution eras:

### A. Ingestion-Time (Index-Time) Directives:
* **When they run:** During data ingestion before bytes hit the hard drive disk.
* **Where they live:** On the **Heavy Forwarder** or **Indexer**.
* **Immutability:** Once written to disk, these changes are **permanent**! If you mask a credit card with `SEDCMD`, the real card number is gone forever.
* **Key Directives:**
  ```ini
  [sourcetype_name]
  SHOULD_LINEMERGE = false
  LINE_BREAKER = ([\r\n]+)\d{4}-
  TRUNCATE = 100000
  TIME_PREFIX = ^
  TIME_FORMAT = %Y-%m-%d %H:%M:%S
  TRANSFORMS-routing = drop_debug_logs, route_vip_customers
  SEDCMD-mask_cc = s/\d{4}-\d{4}-\d{4}-(\d{4})/XXXX-XXXX-XXXX-\1/g
  ```

### B. Search-Time Directives:
* **When they run:** Only when an analyst clicks "Search" on the Search Head.
* **Where they live:** On the **Search Head**.
* **Flexibility:** Completely non-destructive! If you change a regex extraction tomorrow, all historical searches update instantly without re-indexing any data!
* **Key Directives:**
  ```ini
  [sourcetype_name]
  # 1. Inline regex field extraction:
  EXTRACT-user = User=(?<username>\w+) from IP=(?<client_ip>\d+\.\d+\.\d+\.\d+)

  # 2. Advanced regex extraction via transforms.conf:
  REPORT-parse_csv = extract_csv_fields

  # 3. Automatic CSV Lookup:
  LOOKUP-enrich_user = employee_directory_lookup email AS user OUTPUT department, manager

  # 4. Calculated field:
  EVAL-kb_size = bytes / 1024

  # 5. Field Alias:
  FIELDALIAS-ip_mapping = src_ip AS clientip
  ```

---

## 🎯 5. `props.conf` Stanza Matching Precedence

When Splunk evaluates `props.conf`, which stanza wins if multiple stanzas match the same log line?

```text
┌────────────────────────────────────────────────────────────────────────┐
│               PROPS.CONF STANZA PRECEDENCE (HIGHEST TO LOWEST)         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. [sourcetype]                 (HIGHEST PRECEDENCE - WINS OVER ALL!)  │
│ 2. [source::...]                (Second priority - file path matching) │
│ 3. [host::...]                  (LOWEST PRECEDENCE - hostname matching)│
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Production Rule:** Always attach parsing rules to `[<sourcetype>]` stanzas whenever possible. Only use `[source::...]` when you need to assign a sourcetype dynamically from a directory path!

---

## 🛠️ 6. Index-Time `TRANSFORMS-` vs Search-Time `REPORT-`

Notice the prefix used in `props.conf` to invoke `transforms.conf`:

```ini
# --- INGESTION-TIME (Heavy Forwarder / Indexer) ---
# Must use the TRANSFORMS- prefix!
[payment_logs]
TRANSFORMS-filter_junk = drop_healthchecks

# --- SEARCH-TIME (Search Head) ---
# Must use the REPORT- prefix!
[payment_logs]
REPORT-extract_order = extract_order_id_and_price
```

If you mistakenly configure `TRANSFORMS-extract = ...` on a Search Head, Splunk will ignore it during search time!

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-04

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-04: Props & Transforms Battleground                         │
│ ⭐ DIFFICULTY: Intermediate | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins    │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> A rogue configuration deployment broke data parsing across a multi-tier Splunk architecture:  
> 1. An intern deployed `LINE_BREAKER` and `SEDCMD` masking rules to the Search Head cluster, and developers are panicking because credit cards are still landing unmasked on Indexer disks!  
> 2. Search-time CSV lookups were mistakenly configured on the Indexers, consuming indexing memory without providing any fields to search analysts.  
> 3. A `TRANSFORMS-` routing rule on a Heavy Forwarder is failing because the administrator used the search-time prefix `REPORT-` instead.  
> Repair the configuration placement, restore security compliance, and capture all 5 flags!

👉 **[Enter the Cyber Range: Room P3-04](../Labs/Room_P3_04_Props_and_Transforms_Battleground.md)** `[250 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **In a standard distributed Splunk deployment (UF $\rightarrow$ Indexer $\rightarrow$ Search Head), on which tier must `LINE_BREAKER` and `TIME_FORMAT` be configured?**
2. **If you configure an `EXTRACT-field = ...` search-time regex extraction in `props.conf` on an Indexer, will it extract fields on the Search Head? Why or why not?**
3. **What is the difference between `TRANSFORMS-` and `REPORT-` prefixes in `props.conf`?**
4. **Between `[host::web*]`, `[source::/var/log/app.log]`, and `[custom:app]`, which stanza in `props.conf` has the highest evaluation priority?**
5. **Why can `SEDCMD` PII data masking only be executed during ingestion time on a Heavy Forwarder or Indexer, and never on a Search Head?**

---
*Ready to advance to Chapter 05: Index-Time Routing & Filtering (`nullQueue`, selective indexing)?*
