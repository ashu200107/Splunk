# 📘 Chapter 08 (Phase 3): Calculated Fields, Field Aliases & Sourcetype Renaming

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 23 | **Milestone:** Search-Time Normalization & Knowledge Harmonization | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_08_Calculated_Fields_Aliases_and_Sourcetype_Renaming.md`  
> **Interactive Cyber Range Lab:** [Room P3-08: The Calculated Field Alchemist](../Labs/Room_P3_08_Calculated_Field_Alchemist.md) `[200 XP]`

---

## 🏗️ 1. The Simple Explanation: "The Currency Converter & Universal Nickname Registry"

Imagine you run an international bank receiving financial statements from 50 different countries:
- Japan sends logs with column `yen_amount`, France sends `eur_val`, and the USA sends `usd_total`.
- If your risk analysts had to write custom conversion equations every time they ran a report, dashboards would take days to build and errors would be rampant.
- **This is what Field Aliases, Calculated Fields, and Sourcetype Renaming accomplish in Splunk:**
  - **Field Aliasing (`FIELDALIAS-`)** is the **Universal Nickname Registry**: It tells Splunk that whenever an event mentions `clientip`, `src_host`, or `remote_addr`, it should also respond to the standardized name **`src_ip`**!
  - **Calculated Fields (`EVAL-`)** is the **Automated Currency Converter**: It automatically evaluates mathematical formulas and logic (e.g. converting raw `bytes` to `megabytes` or calculating duration) on every search without the user having to type `| eval` in SPL!
  - **Sourcetype Renaming** is the **Universal Umbrella**: It allows disparate logs (`apache_access`, `nginx_access`, `iis_w3c`) to all be queried simultaneously under the single common name **`sourcetype=web`**!

![Splunk Calculated Fields and Aliases 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_calculated_fields_aliases_3d_1792124400729.jpg)
*Figure 3.8: The Normalization Rings — How Search Heads apply Field Aliasing (Ring 1), Calculated Fields (Ring 2), and Sourcetype Renaming (Ring 3) to harmonize disparate datasets.*

---

## 🔍 2. The 3 Normalization Pillars in `props.conf`

All three of these features live exclusively on the **Search Head** inside `props.conf`:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               THE 3 SEARCH-TIME NORMALIZATION PILLARS                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. FIELD ALIASING (FIELDALIAS-)                                        │
│    • Maps an existing field to a new alias name.                       │
│    • Zero memory duplication: Both old and new names work in SPL!      │
│    • Syntax: FIELDALIAS-<class> = <orig> AS <alias>                    │
├────────────────────────────────────────────────────────────────────────┤
│ 2. CALCULATED FIELDS (EVAL-)                                           │
│    • Evaluates an eval expression automatically for every event.       │
│    • Enriches search results with calculated values (math, case, etc). │
│    • Syntax: EVAL-<field_name> = <eval_expression>                     │
├────────────────────────────────────────────────────────────────────────┤
│ 3. SOURCETYPE RENAMING                                                 │
│    • Directs searches for a renamed sourcetype to target raw events    │
│      while preserving original indexing metadata.                      │
│    • Syntax: [old_sourcetype] \n rename = <new_sourcetype>             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🏷️ 3. Field Aliases (`FIELDALIAS-`): Standardizing Terminology

In enterprise environments, different firewalls and web servers use completely different field names for the same concept:
- Cisco ASA calls it: `src_ip`
- CheckPoint calls it: `orig_ip`
- Palo Alto calls it: `source_ip`

Instead of forcing security analysts to remember all three names, create a **Field Alias** in `props.conf` on the Search Head:

```ini
# props.conf (Search Head)
[checkpoint:firewall]
FIELDALIAS-normalize_cp = orig_ip AS src_ip, dst_ip AS dest_ip, prt AS dest_port

[pan:traffic]
FIELDALIAS-normalize_pan = source_ip AS src_ip, destination_ip AS dest_ip
```

### 🎯 Key Rules for Field Aliasing:
1. **Case-Sensitivity:** Field names are **case-sensitive**! `Orig_IP` is not the same as `orig_ip`.
2. **Both Names Work:** Analysts can search using either `orig_ip=10.0.0.1` OR `src_ip=10.0.0.1`!
3. **Chaining:** You can map multiple fields in a single line separated by commas.

---

## 🧮 4. Calculated Fields (`EVAL-`): Automated Search Enrichment

Instead of training every business analyst to type:
`| eval mb_used = round(bytes/1048576, 2) | eval latency_sec = response_ms / 1000`

Define the calculation once in `props.conf`. Splunk will automatically execute the calculation in memory whenever events with that sourcetype are searched!

```ini
# props.conf (Search Head)
[nginx:access]
# 1. Mathematical conversions:
EVAL-mb_transferred = round(bytes / 1048576, 2)

# 2. Categorization using case():
EVAL-http_status_category = case(status>=500, "Server Error", status>=400, "Client Error", status>=300, "Redirect", true(), "Success")

# 3. Default fallback using coalesce():
EVAL-client_identifier = coalesce(authenticated_user, api_key, clientip, "ANONYMOUS")

# 4. Latency normalization:
EVAL-duration_seconds = response_time_ms / 1000
```

---

## 🔄 5. Sourcetype Renaming: The Unified Umbrella

Suppose your enterprise has 1,000 legacy servers sending data as `apache_access_log`, while 500 new servers send data as `nginx_access_log`.  
An analyst wanting to search all web traffic would have to write:
`index=web (sourcetype=apache_access_log OR sourcetype=nginx_access_log)`

With **Sourcetype Renaming**, you harmonize them under a single virtual banner:

```ini
# props.conf (Search Head)
[apache_access_log]
rename = web:access

[nginx_access_log]
rename = web:access
```

### How Searches Behave After Renaming:
1. When an analyst searches: `sourcetype=web:access`, Splunk automatically retrieves events from **both** Apache and Nginx!
2. To find only the original Apache logs, the analyst can still search using the internal field: `_sourcetype=apache_access_log`.

---

## ⏱️ 6. The Holy Grail: Official Search-Time Operations Order of Precedence

Understanding the **exact sequence** in which the Search Head processes knowledge objects prevents hours of troubleshooting:

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE SEARCH HEAD KNOWLEDGE PIPELINE SEQUENCE                │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Index-Time Field Extraction (Metadata: host, source, sourcetype)    │
│    └─► 2. Inline Regex Field Extractions (EXTRACT-)                    │
│        └─► 3. Transforms-Based Field Extractions (REPORT-)             │
│            └─► 4. Automatic Key-Value Extraction (KV_MODE)             │
│                └─► 5. Field Aliasing (FIELDALIAS-)                     │
│                    └─► 6. Calculated Fields (EVAL-)                    │
│                        └─► 7. Lookups (LOOKUP-)                        │
│                            └─► 8. Eventtypes                           │
│                                └─► 9. Tags                             │
└────────────────────────────────────────────────────────────────────────┘
```

### 🚨 The Golden Rule of Pipeline Dependency:
* **Can a Calculated Field (`EVAL-`) use a Field Alias?**  
  👉 **YES!** Because Step 5 (Field Aliases) executes **before** Step 6 (Calculated Fields).
* **Can a Field Alias (`FIELDALIAS-`) alias a Calculated Field?**  
  👉 **NO!** Because Field Aliases execute **before** Calculated Fields exist in memory!
* **Can a Lookup (`LOOKUP-`) use a Calculated Field?**  
  👉 **YES!** Because Step 6 (Calculated Fields) executes **before** Step 7 (Lookups).

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-08

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-08: The Calculated Field Alchemist                          │
│ ⭐ DIFFICULTY: Intermediate | 💎 REWARD: 200 XP | ⏱️ TIME: 30 Mins    │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> Executive leadership demanded an instant corporate dashboard tracking high-value wire transfers and HTTP API health.  
> However:
> 1. Three payment microservices use different field names (`client_ip`, `c_ip`, `user_ip`), causing 60% of data to vanish from the security dashboard.
> 2. Dashboards require latency in seconds, but raw logs provide `latency_microsec`.
> 3. An intern attempted to alias an `EVAL-` field, violating the search-time sequence and breaking alert correlations!  
> Your mission is to configure `FIELDALIAS-`, build dynamic `EVAL-` formulas, harmonize sourcetypes, and capture all 4 flags!

👉 **[Enter the Cyber Range: Room P3-08](../Labs/Room_P3_08_Calculated_Field_Alchemist.md)** `[200 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **On which Splunk architectural tier must `FIELDALIAS-`, `EVAL-`, and `rename = ...` be configured?**
2. **If an event contains field `remote_address="192.168.1.1"`, write the exact `props.conf` line to alias this field as `src_ip`.**
3. **In the search-time pipeline sequence, does `FIELDALIAS-` execute before or after `EVAL-`? Can an `EVAL-` expression calculate values based on an aliased field name?**
4. **Write an `EVAL-` directive in `props.conf` that calculates a new field `megabytes` by dividing the existing field `bytes` by `1048576` and rounding to 2 decimal places.**
5. **If a sourcetype is renamed from `cisco_vpn` to `network:vpn`, what internal field can an analyst query to locate only the original raw `cisco_vpn` events?**

---
*Ready to advance to Chapter 09: Lookups Architecture (Static CSV, Automatic Lookups, KV Store, and Scripted Lookups)?*
