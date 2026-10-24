# 📘 Chapter 11 (Phase 3): Eventtypes & Tags Architecture

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 26 | **Milestone:** Knowledge Classification & Hierarchical Tagging | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_11_Eventtypes_and_Tags_Architecture.md`  
> **Interactive Cyber Range Lab:** [Room P3-11: Eventtype Tagging Ops](../Labs/Room_P3_11_Eventtype_Tagging_Ops.md) `[200 XP]`

---

## 🏗️ 1. The Simple Explanation: "The Smart Folders & Colored Post-It Sticky Notes"

Imagine you are an office manager managing 500,000 corporate paper receipts, invoices, and contracts:
- If all documents are jumbled in a giant pile, finding "all transactions where a client was unhappy" requires reading hundreds of thousands of pages.
- **Eventtypes** are like **Smart Filing Folders**: You define a rule: *"Any receipt containing the words `REFUND` or `DISPUTE` automatically belongs in the `customer_dispute` folder."* Whenever an event matches that search, Splunk dynamically awards it the badge `eventtype=customer_dispute`.
- **Tags** are like **Neon Colored Post-It Sticky Notes**: You want to flag that certain folders and servers belong to high-priority categories. You stick a **Bright Red Tag labeled `pci`** on the `customer_dispute` folder, and you stick a **Neon Yellow Tag labeled `privileged`** on the `admin` username.
- **The Magic:** When an executive asks for all PCI incidents, you don't need to know the vendor, index, or eventtype—you simply search: **`tag=pci`**!

![Splunk Eventtypes and Tags 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_eventtypes_and_tags_3d_1792124989278.jpg)
*Figure 3.11: The Categorization Chamber — How eventtypes.conf evaluates boolean filters to apply eventtype badges, and tags.conf attaches glowing taxonomic labels.*

---

## 🔍 2. Step-by-Step: The 5-Step Classification Journey

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE 5-STEP JOURNEY OF EVENTTYPES & TAGS                    │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: User Executes Search or Data Model Acceleration Runs           │
│         - SPL: index=web status>=500 OR status=404                     │
│                                                                        │
│ Step 2: Search Head Evaluates eventtypes.conf                          │
│         - Checks all configured eventtype search filters against each  │
│           event matching the search.                                   │
│                                                                        │
│ Step 3: Eventtype Badges Awarded                                       │
│         - If event matches search = status>=500, Splunk assigns field: │
│           eventtype = web_server_error                                 │
│         - (An event can have multiple eventtypes simultaneously!)      │
│                                                                        │
│ Step 4: Search Head Evaluates tags.conf                                │
│         - Looks up tags mapped to field-values and eventtypes:         │
│           • [eventtype=web_server_error] ──► tag = error               │
│           • [status=500]                 ──► tag = critical            │
│                                                                        │
│ Step 5: Tags Injected into Search Head Memory                          │
│         - The event now responds to searches: tag=error, tag=critical! │
│         - Downstream data models ingest the tagged events!             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 3. Eventtypes (`eventtypes.conf`): Smart Search Badges

An **eventtype** is a named search string that categorizes events. It creates a special multi-value field named `eventtype`.

### Syntax:
Path: `$SPLUNK_HOME/etc/apps/<app>/local/eventtypes.conf` (ON SEARCH HEAD)
```ini
[eventtype_name]
search = <boolean_search_filter>
priority = <integer>
```

### Real-World Production Examples:
```ini
# 1. Group all web errors together across Apache, Nginx, and IIS:
[web_errors]
search = sourcetype=*:access (status>=400 AND status<=599)

# 2. Identify potential brute-force authentication activity:
[failed_logins]
search = (sourcetype=linux:secure OR sourcetype=XmlWinEventLog:Security) ("Failed password" OR EventCode=4625)

# 3. Tag high-value banking transactions:
[vip_wire_transfer]
search = index=payments sourcetype=fincorp:wire amount > 1000000
```

### 🚨 The 3 Cardinal Rules of Eventtypes:
1. **NO Pipes (`|`):** You **cannot** use piping commands in an eventtype! Commands like `| stats`, `| sort`, `| eval`, or `| dedup` are strictly forbidden!
2. **NO Subsearches:** You cannot use square-bracket subsearches `[ search ... ]`.
3. **Pure Boolean Filters Only:** Only basic terms, wildcards (`*`), field-value pairs (`status=500`), and boolean operators (`AND`, `OR`, `NOT`).

---

## 🏷️ 4. Tags (`tags.conf`): The Taxonomic Post-It Notes

A **tag** is an arbitrary label attached to:
1. **An Eventtype:** `[eventtype=web_errors] error = enabled`
2. **A Field-Value Pair:** `[host=db-prod-01] database = enabled, critical = enabled`

### Syntax:
Path: `$SPLUNK_HOME/etc/apps/<app>/local/tags.conf` (ON SEARCH HEAD)
```ini
# Attaching tags to an eventtype:
[eventtype=failed_logins]
authentication = enabled
failure = enabled

# Attaching tags to a field-value pair:
[action=blocked]
drop = enabled
firewall = enabled
```

---

## ⚖️ 5. Eventtypes vs Tags: The Definitive Comparison

| Feature | Eventtype (`eventtypes.conf`) | Tag (`tags.conf`) |
| :--- | :--- | :--- |
| **What it Represents** | A **category** of events defined by a search filter. | A **label** attached to a field value or eventtype. |
| **Created From** | Search string (`status=500 OR status=404`) | Direct assignment (`critical = enabled`) |
| **Allows Pipes?** | ❌ Strictly Forbidden! (No `\|`) | N/A (Not a search string) |
| **Output in UI** | Populates the `eventtype` field. | Populates the `tag` and `tag::<field>` fields. |
| **Searching Syntax** | `eventtype=web_errors` | `tag=error` or `tag::eventtype=web_errors` |
| **Primary CIM Role** | Groups vendor events into categories. | Applies CIM domain labels (`authentication`, `network`). |

---

## 🔍 6. How to Search with Tags in SPL

Tags provide immense flexibility in search queries:

```spl
# 1. Search for any event that has the tag "authentication":
tag=authentication

# 2. Search for events with tag "network" AND tag "communicate":
tag=network tag=communicate

# 3. Search for tags attached specifically to a field (tag::<field>):
tag::user=privileged

# 4. Search for tags attached specifically to an eventtype:
tag::eventtype=pci_compliance

# 5. Wildcard tag searches:
tag=pci*
```

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-11

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-11: Eventtype Tagging Ops & Classification Architecture    │
│ ⭐ DIFFICULTY: Intermediate | 💎 REWARD: 200 XP | ⏱️ TIME: 30 Mins    │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> The SOC Threat Hunting desk is struggling to correlate security incidents across Linux, Windows, and Cisco firewalls:  
> 1. An intern attempted to create an eventtype containing `| stats count by user`, causing Splunk to throw an internal syntax error.  
> 2. Windows and Linux authentication failures have disparate event formats and must be unified under eventtype `auth_failures`.  
> 3. Security automation playbooks require all authentication failures to carry the tags `authentication` and `failure` for CIM compliance.  
> Your mission is to fix the eventtype syntax, configure `eventtypes.conf` and `tags.conf`, build multi-tag queries, and capture all 4 flags!

👉 **[Enter the Cyber Range: Room P3-11](../Labs/Room_P3_11_Eventtype_Tagging_Ops.md)** `[200 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **Why is the search string `search = status>=500 | stats count` invalid inside `eventtypes.conf`?**
2. **Can a single Splunk event belong to multiple eventtypes simultaneously?**
3. **In `tags.conf`, how do you attach the tag `pci` to an eventtype named `credit_card_tx`?**
4. **What is the difference in SPL between searching `tag=privileged` versus searching `tag::user=privileged`?**
5. **On which Splunk architectural tier must `eventtypes.conf` and `tags.conf` be configured?**

---
*Ready to advance to Chapter 12: Ingestion Pipeline Troubleshooting Runbooks (Catastrophic Backtracking, Timestamp Drift, Queue Blocks)?*
