# 📘 Chapter 07 (Phase 3): Search-Time Field Extractions

> **The Splunk Administrator's Definitive Handbook** | Phase 3: Data Onboarding & Parsing Pipeline  
> **Day:** 22 | **Milestone:** Schema-on-Read & Search-Time Knowledge Architecture | **Current Rank:** Splunk Enterprise Architect (3,050 XP)  
> **Second Brain File:** `Chapter_07_Search_Time_Field_Extractions.md`  
> **Interactive Cyber Range Lab:** [Room P3-07: Search-Time Regex Heist](../Labs/Room_P3_07_Search_Time_Regex_Heist.md) `[250 XP]`

---

## 🏗️ 1. The Simple Explanation: "The Gemologist’s Loupe & Virtual Filter Lens"

Imagine you discover an ancient mountain filled with millions of sparkling rough rocks:
- If a miner took a permanent hammer and carved arbitrary labels into every rock before storing them in a vault, any mistake made during carving would permanently ruin the rock forever.
- Instead, the miner simply washes and stores the raw rocks safely.
- When a gemologist wants to study emeralds, they put on a **special optical lens (a Jeweler's Loupe)**. The lens highlights the green emerald crystals instantly without modifying the physical rock at all!
- **This is what Search-Time Field Extraction is in Splunk.**
  - It is the core embodiment of **Schema-on-Read**.
  - The raw event text stays untouched inside the Indexer's `journal.zst`.
  - When an analyst runs a search, the **Search Head** applies optical regex lenses (`EXTRACT-`, `REPORT-`, `KV_MODE`) to calculate structured fields (`user`, `clientip`, `status`, `bytes`) **on the fly in RAM**!
  - If you improve your regex tomorrow, **5 years of historical data** instantly adopts the new fields without re-indexing a single byte!

![Splunk Search-Time Field Extractions 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_search_time_extractions_3d_1792124200162.jpg)
*Figure 3.7: The Gemologist's Lens Analogy — How Search Heads project structured key-value pairs from raw events using inline regex, transforms delimiters, and KV_MODE.*

---

## 🔍 2. Step-by-Step: The 5-Step Search-Time Extraction Journey

```text
┌────────────────────────────────────────────────────────────────────────┐
│             THE 5-STEP JOURNEY OF SEARCH-TIME FIELD EXTRACTION         │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: User Dispatches Query on Search Head                           │
│         - SPL: index=web sourcetype=nginx:access status>=500           │
│                                                                        │
│ Step 2: Indexer Returns Compressed Raw Events                          │
│         - Indexers stream matching _raw text blocks over port 8089 to  │
│           the Search Head.                                             │
│                                                                        │
│ Step 3: Search Head Evaluates props.conf Rules in Memory               │
│         - Matches [nginx:access] stanza.                               │
│         - Executes Inline Extractions (EXTRACT-)                       │
│         - Calls transforms.conf Extractions (REPORT-)                  │
│         - Parses JSON / XML structures (KV_MODE = json)                │
│                                                                        │
│ Step 4: Named Capture Groups Populate Field Discovery Table            │
│         - Regex groups like (?<client_ip>\d+\.\d+\.\d+\.\d+)           │
│           populate field client_ip in the search UI sidebar.           │
│                                                                        │
│ Step 5: Downstream SPL Commands Process the Dynamic Fields             │
│         - Commands like | stats count by client_ip, status execute     │
│           at lightning speeds in Search Head memory!                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ 3. Schema-on-Read vs Index-Time Fields (Why Index-Time Fields are Dangerous)

Junior administrators often ask: *"Why don't we extract all fields at index time so Splunk doesn't have to calculate regex during searches?"*

```text
┌────────────────────────────────────────────────────────────────────────┐
│               INDEX-TIME FIELDS vs SEARCH-TIME FIELDS                  │
├────────────────────────────────────────────────────────────────────────┤
│ Index-Time Fields (WRITE_META = true / Indexed Extractions):           │
│   ❌ Permanent: Cannot be altered without completely re-indexing data. │
│   ❌ Storage Bloat: Inflates .tsidx dictionary files by 40–100%!       │
│   ❌ Performance Penalty: Slows down indexer disk commit pipeline.    │
│   ⚠️ Use Cases: ONLY for high-cardinality routing keys (e.g. customer) │
├────────────────────────────────────────────────────────────────────────┤
│ Search-Time Fields (EXTRACT / REPORT / KV_MODE) — THE BEST PRACTICE:   │
│   ✅ 100% Flexible: Update, rename, or fix regexes retroactively!      │
│   ✅ Zero Disk Bloat: Adds 0 KB to index storage vaults.              │
│   ✅ Non-Destructive: Raw logs remain 100% authentic for audits.       │
│   ✅ Search-Head Scalable: Workload scales across Search Head Cluster. │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 4. Method 1: Inline Regex Field Extractions (`EXTRACT-` in `props.conf`)

The simplest and fastest method to extract fields from non-standard text.  
It uses **Named Capture Groups**: `(?<field_name>regex_pattern)`

### Syntax:
```ini
# /opt/splunk/etc/apps/<app>/local/props.conf (ON SEARCH HEAD)
[sourcetype_name]
EXTRACT-<class_name> = <regex_with_named_capture_groups>
```

### Real-World Production Example:
Raw Log:
```text
2026-10-16 04:00:12 User=jsmith AuthResult=SUCCESS ClientIP=192.168.1.50 BytesSent=4096 SessionID=sess_94012
```

`props.conf` configuration:
```ini
[fincorp:auth:app]
EXTRACT-auth_fields = User=(?<user>\w+)\s+AuthResult=(?<auth_status>\w+)\s+ClientIP=(?<src_ip>\d+\.\d+\.\d+\.\d+)\s+BytesSent=(?<bytes_out>\d+)
```

*Result in Splunk UI:*
- `user` = `jsmith`
- `auth_status` = `SUCCESS`
- `src_ip` = `192.168.1.50`
- `bytes_out` = `4096`

---

## 🔀 5. Method 2: Transforms-Based Field Extractions (`REPORT-`)

When an extraction requires **reusable logic**, **multiple delimiter sets**, or **multi-value fields**, use `REPORT-` in `props.conf` to invoke `transforms.conf`.

### A. Advanced Regex with `transforms.conf`
```ini
# props.conf (Search Head)
[fincorp:firewall:traffic]
REPORT-extract_fw = parse_firewall_traffic

# transforms.conf (Search Head)
[parse_firewall_traffic]
REGEX = src=(?<src_ip>[^\s]+)\s+dst=(?<dest_ip>[^\s]+)\s+spt=(?<src_port>\d+)\s+dpt=(?<dest_port>\d+)
```

---

### B. Delimited Extractions (`DELIMS`): No Regex Required!
If your data is formatted as simple key-value pairs (e.g. `user=admin ip=10.0.0.1 action=login`), writing regex is wasteful! Use `DELIMS`:

```ini
# props.conf (Search Head)
[custom:keyvalue:app]
REPORT-extract_kv = parse_keyvalue_pairs

# transforms.conf (Search Head)
[parse_keyvalue_pairs]
# First delimiter separates key-value pairs (space)
# Second delimiter separates key from value (equals sign)
DELIMS = " ", "="
```
> **Speed Advantage:** `DELIMS` runs compiled C++ character tokenizers that are **5x to 8x faster** than regex engines!

---

### C. Multi-Value Field Extractions (`MV_ADD`)
Suppose a single log line lists multiple values for the same key:
`Users_Logged_In: alice, bob, charlie, david`

```ini
# transforms.conf (Search Head)
[extract_multiple_users]
REGEX = Users_Logged_In:\s+(?<active_user>[^,\s]+)
# MV_ADD = true instructs Splunk to create a multi-value array!
MV_ADD = true
REPEAT_MATCH = true
```

---

## 📦 6. Method 3: Structured Data Extractions (JSON & XML via `KV_MODE`)

Modern cloud microservices output structured JSON payloads. You **never** need to write regex to parse JSON!

```ini
# props.conf (Search Head)
[fincorp:api:json]
KV_MODE = json
```

### What `KV_MODE = json` Does Automatically:
If an incoming event contains:
```json
{"event": {"user": "admin", "details": {"ip": "10.0.0.1", "action": "LOGIN"}}}
```
Splunk's Search Head automatically extracts:
- `event.user` = `admin`
- `event.details.ip` = `10.0.0.1`
- `event.details.action` = `LOGIN`

### `KV_MODE` Option Reference:
| `KV_MODE` Value | Description & Best Practice |
| :--- | :--- |
| `none` | Disables all search-time automatic field extraction (Fastest search performance). |
| `auto` | Default behavior: extracts standard `key=value` pairs automatically. |
| `json` | Extracts JSON structures and nested sub-objects. |
| `xml` | Extracts XML tags and element hierarchies. |

---

## ⚡ 7. Performance Best Practices: Defeating Catastrophic Backtracking

Poorly written regex can cause the Search Head's CPU to spike to 100% and lock up for minutes due to **catastrophic backtracking**!

### The 3 Regex Optimization Commandments:
1. **Always Anchor to the Beginning:**  
   - ❌ Bad: `EXTRACT-user = User=(?<user>\w+)` (Splunk scans every character in a 10 KB event).  
   - ✅ Good: `EXTRACT-user = ^(?:\S+\s+){3}User=(?<user>\w+)` (Anchors search immediately).
2. **Never Use Greedy `.*` Inside Extractions:**  
   - ❌ Catastrophic: `User=(?<user>.*) IP=(?<ip>.*)`  
   - ✅ Fast & Safe: `User=(?<user>[^\s]+)\s+IP=(?<ip>[^\s]+)`
3. **Use Negated Character Classes:**  
   - Instead of matching `.+?`, match `[^"'\s]+` to stop the regex engine from backtracking.

---

## 🎮 Hands-On Cyber Range Challenge: Room P3-07

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P3-07: Search-Time Regex Heist & Schema-on-Read Mastery        │
│ ⭐ DIFFICULTY: Intermediate | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins    │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Production Incident Briefing:**  
> The SOC Threat Intelligence team is running emergency queries looking for an active advanced persistent threat (APT). However, their SPL queries:
> ```spl
> index=firewall action=blocked | stats count by src_ip, dest_port
> ```
> Return **zero fields** because fields are trapped in unstructured raw text!  
> In addition, a junior analyst configured an unanchored greedy regex that is causing the Search Head Cluster to lock up with 100% CPU spikes!  
> Your mission is to construct high-speed `EXTRACT-` rules, build high-efficiency `DELIMS` parsers, tune `KV_MODE`, eliminate catastrophic backtracking, and capture all 5 flags!

👉 **[Enter the Cyber Range: Room P3-07](../Labs/Room_P3_07_Search_Time_Regex_Heist.md)** `[250 XP]`

---

## 🧠 End-of-Chapter Self-Check Quiz

1. **What is the foundational difference between an Index-Time field extraction and a Search-Time field extraction in Splunk?**
2. **On which architectural tier must `EXTRACT-` and `REPORT-` stanzas be configured to take effect in user searches?**
3. **Write the named capture group regex syntax to extract a numeric HTTP status code into a field named `http_status` from the text `status_code=404`.**
4. **Why is `DELIMS = " ", "="` in `transforms.conf` dramatically faster than equivalent regular expressions for extracting key-value pairs?**
5. **What `KV_MODE` setting should you configure in `props.conf` to automatically extract nested keys from a Kubernetes container logging JSON output?**

---
*Ready to advance to Chapter 08: Calculated Fields (`EVAL-`), Field Aliases (`FIELDALIAS-`), and Sourcetype Renaming?*
