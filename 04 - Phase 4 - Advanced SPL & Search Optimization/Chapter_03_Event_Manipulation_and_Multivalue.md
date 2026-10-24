# 🔬 Chapter 03 (Phase 4): Event Manipulation & Multivalue Fields — `eval`, `rex`, `spath`, `mvexpand` & `nomv`

> **The Splunk Administrator's Definitive Handbook** | Phase 4: Advanced SPL & Search Optimization  
> **Day:** 31 | **Milestone:** Data Surgery & Complex Field Engineering  
> **Current Rank:** Principal Splunk Architect (4,000 XP) $\rightarrow$ *Promotion Target: Master Splunk Architect (6,550+ XP)*  
> **Second Brain File:** `Chapter_03_Event_Manipulation_and_Multivalue.md`  
> **Interactive Cyber Range Lab:** [Room P4-03: Multivalue JSON Surgery](../Labs/Room_P4_03_Multivalue_JSON_Surgery.md) `[250 XP]`

---

## 🔬 1. The Everyday Analogy: The Precision Surgical Station & Genetic Dissection

Imagine a forensic scientist analyzing a sealed, multi-layered biological specimen container:

1. **The Scalpel & Chemical Reagents (`eval`):**  
   You measure the temperature, calculate the mass ratio, convert Fahrenheit to Celsius, and apply conditional tags: *"If protein concentration > 80, classify as High-Grade, otherwise Normal."*
2. **The Micro-Laser (`rex`):**  
   Inside the handwritten laboratory notes on the container, there is an embedded serial code hidden in paragraphs of text (`SAMPLE-ID: TX-9042-B`). You calibrate a precision laser to slice out only that exact sequence and place it into a labeled petri dish.
3. **The Microscopic Dissector (`spath`):**  
   Inside the container sits a complex, nested Russian nesting doll (a JSON object). You don't take a hammer to it; you use microscopic calipers to reach through Layer 1 (`order`), down to Layer 2 (`customer`), and extract Layer 3 (`roles[0]`) cleanly without scratching anything else.
4. **The Clone Pod (`mvexpand`):**  
   The specimen contains a single petri dish holding **5 distinct bacterial strains** (a multivalue array). If you need to perform an independent genetic test on each strain separately, you feed the petri dish into a cloning chamber that **duplicates the entire container 5 times**, so each clone holds exactly one distinct strain!

In Splunk, mastering event manipulation means you can take any complex, nested, non-standard, or dirty log stream and dissect it with surgical precision in real time.

---

## 🗺️ 2. The 3D Master Architectural Blueprint

![Splunk Event Manipulation 3D Lab](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_eval_rex_spath_multivalue_3d_1792230146575.jpg)
*Figure 4.3: 3D Architectural Blueprint of the Splunk Event Manipulation and Multivalue Processing Laboratory, showing streaming precision lasers (eval, rex, spath) dissecting and cloning complex nested structures.*

---

## 🔄 3. The 5-Step Event Surgery Pipeline

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      THE 5-STEP EVENT SURGERY PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. STREAM INTAKE (Raw Event Buffer)                                                     │
│    • Ingestion streams arrive with unstructured _raw text and semi-structured payloads. │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. FIELD ENRICHMENT & CASTING (eval)                                                    │
│    • Evaluates mathematical formulas, conditional logic (case, if, coalesce), and       │
│      string transformations concurrently on the Indexers (Distributable Streaming).     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. AD-HOC PATTERN EXTRACTION (rex)                                                      │
│    • Applies PCRE regex to capture non-extracted fields using named groups (?<name>...).│
│    • Or executes in-flight masking using sed syntax (mode=sed "s/.../.../g").           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. NESTED STRUCTURE EXTRACTION (spath)                                                  │
│    • Recursively navigates XML and JSON paths (e.g., path=payment.card.type).           │
│    • Creates structured Splunk multivalue fields from nested arrays.                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. MULTIVALUE EXPANSION / CONSOLIDATION (mvexpand / nomv)                               │
│    • mvexpand clones the event row for every element in an array for individual stats.  │
│    • nomv collapses an array back into a single newline-separated string.               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 The `eval` Command: The Swiss Army Knife of SPL

`eval` calculates new fields or overwrites existing fields on an event-by-event basis. Because it is a **Distributable Streaming Command**, Splunk pushes `eval` execution down to all Indexers to execute in parallel across CPU cores.

#### Key Functional Categories:

```spl
# 1. CONDITIONAL LOGIC (case, if, coalesce)
# case() evaluates boolean conditions in order and stops at the first true match:
| eval severity = case(
    status >= 500, "CRITICAL",
    status >= 400, "WARNING",
    status == 200, "NORMAL",
    true(), "UNKNOWN"
)

# if() evaluates simple binary conditions (if(condition, true_val, false_val)):
| eval is_internal = if(cidrmatch("10.0.0.0/8", client_ip), "YES", "NO")

# coalesce() returns the first non-null field in a list:
| eval active_user = coalesce(user_id, login_name, client_guid, "ANONYMOUS")
```

```spl
# 2. STRING MANIPULATION (lower, upper, substr, replace, len)
| eval username = lower(trim(raw_user))
| eval masked_account = replace(account_num, "^\d{8}", "XXXXXXXX")
| eval payload_length = len(_raw)
```

```spl
# 3. TIME CONVERSION (strftime, strptime)
# strptime converts human-readable time strings into numeric Unix epoch seconds:
| eval auth_epoch = strptime(login_time_str, "%Y-%m-%d %H:%M:%S")

# strftime formats Unix epoch seconds into human-readable strings:
| eval human_time = strftime(_time, "%A, %B %d, %Y at %I:%M:%S %p")
```

```spl
# 4. NETWORK & MATHEMATICAL FUNCTIONS (cidrmatch, round, pow)
| eval latency_sec = round(latency_microsec / 1000000, 3)
| where cidrmatch("192.168.0.0/16", dest_ip)
```

---

### 4.2 Inline Regex Extraction & Redaction with `rex`

While `props.conf` (`EXTRACT-`) is used for permanent configuration, `rex` is Splunk's dynamic, ad-hoc search-time regex engine.

#### A. Extracting Fields with Named Capture Groups
```spl
# Extracts dynamic fields 'session_token' and 'auth_status' from _raw:
index=security
| rex "SessionID=(?<session_token>[a-f0-9]{32})\s+Auth=(?<auth_status>\w+)"
```

#### B. Multivalue Extraction with `max_match`
By default, `rex` only extracts the **first match** in an event. If an event contains multiple instances (e.g., multiple infected IPs), specify `max_match=0` (unlimited) to extract all matches into a multivalue field:
```spl
# Extracts every IP listed in a firewall event into a multivalue array 'flagged_ips':
index=firewall
| rex max_match=0 "(?<flagged_ips>\b\d{1,3}(?:\.\d{1,3}){3}\b)"
```

#### C. Search-Time Masking via Sed Mode
```spl
# Redacts sensitive tokens in the search pipeline without modifying underlying disk:
index=web
| rex mode=sed "s/(bearer\s+)[A-Za-z0-9\-\._~\+\/]+=*/\1[REDACTED]/g"
```

---

### 4.3 Structured JSON & XML Parsing with `spath`

If your data contains complex nested JSON or XML payloads that are not automatically extracted by `KV_MODE = json`, **do not write fragile regular expressions**—use `spath`!

```json
// Sample Event:
{
  "transaction": {
    "id": "TX-90214",
    "customer": {
      "name": "Jane Doe",
      "tier": "VIP"
    },
    "items": [
      {"sku": "SKU-100", "price": 45.00},
      {"sku": "SKU-205", "price": 120.00}
    ]
  }
}
```

#### Using `spath` to Traverse Nested Structures:
```spl
# 1. Extract a single deeply nested field:
| spath input=_raw path=transaction.customer.tier output=customer_tier

# 2. Extract an array element:
| spath input=_raw path=transaction.items{0}.sku output=first_sku

# 3. Extract all array elements into a multivalue field:
| spath input=_raw path=transaction.items{}.sku output=all_skus
```

---

### 4.4 Multivalue Field Architecture: `mvexpand` vs. `nomv`

Splunk allows a single field in an event to hold an ordered array of multiple distinct values.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   MULTIVALUE COMMAND ECOSYSTEM                         │
├────────────────────────────────────────────────────────────────────────┤
│ • mvcount(field):      Returns integer count of values in array.       │
│ • mvindex(field, N):   Retrieves element at index N (0-indexed).       │
│ • mvfilter(predicate): Retains only values matching boolean regex.     │
│ • mvjoin(field, delim):Collapses array into a single delimited string. │
│ • split(str, delim):   Splits a single string into a multivalue array. │
│ • nomv(field):         Forces field to be treated as single-value.     │
│ • mvexpand(field):     Clones the event row for EVERY value in array.  │
└────────────────────────────────────────────────────────────────────────┘
```

#### The `mvexpand` Multiplier Effect:
If you have **10,000 events**, and each event contains a multivalue field `dest_port` with **10 values**, running `| mvexpand dest_port` creates **100,000 separate events in memory**!

```spl
# Example: Analyzing individual user roles:
index=identity
| spath path=user.roles{} output=roles
| mvexpand roles
| stats count BY roles
```

---

## ⚠️ 5. Common Production Pitfalls & Performance Killers

### Pitfall 1: Unbounded `mvexpand` Causing Search Head Out-of-Memory (OOM)
- **The Disaster:** Running `| mvexpand` on a field containing hundreds of values across millions of events.
- **The Limit:** By default, `limits.conf` enforces `max_mem_usage_mb` and `maxresults = 50000` for `mvexpand`. Once breached, `mvexpand` abruptly truncates and silently drops records!
- **The Fix:** Filter your events as early as possible before expanding, or use `stats count by <field>` directly if supported.

### Pitfall 2: Using `rex` Instead of `spath` for JSON
- **Why:** JSON formatting changes (whitespace, newlines, key ordering). A regex written against JSON will fail when a developer adds an extra space or reorders keys. `spath` parses the JSON AST directly and is immune to whitespace variations.

---

## 🎮 Hands-On Cyber Range Challenge: Room P4-03

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ CYBER RANGE: Room P4-03 — Multivalue JSON Surgery                   │
│ ⭐ DIFFICULTY: Medium | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins           │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Scenario:**  
> The SOC is investigating a complex APT command-and-control (C2) beacon event encoded inside nested cloud audit JSON logs.  
> The attacker’s compromised accounts have multiple assigned API privilege scopes and target IP arrays stored as JSON lists.  
> You must:
> 1. Dissect the nested JSON using `spath`.
> 2. Extract embedded base64 session tokens using `rex`.
> 3. Expand the target IP array using `mvexpand` to correlate against threat intelligence.
> 4. Classify risk levels dynamically with `eval case()`.

👉 **[Enter Cyber Range Room P4-03: Multivalue JSON Surgery](../Labs/Room_P4_03_Multivalue_JSON_Surgery.md)** `[250 XP]`

---

## 🧠 Chapter 03 (Phase 4) Self-Check Quiz

Answer these 5 questions to test your mastery of Event Manipulation & Multivalue Fields:

1. **What is the functional difference between `coalesce(fieldA, fieldB, fieldC)` and `case()` in an `eval` statement?**
2. **When using `rex`, what argument must you provide to extract ALL occurrences of a regex pattern in an event into a multivalue field rather than just the first occurrence?**
3. **What is the operational syntax in `spath` to extract all elements from an array named `assigned_roles` nested inside an object named `auth_context`?**
4. **Explain what happens to event counts, memory usage, and Search Head processing when `| mvexpand target_hosts` is executed on 50,000 events where each event contains 20 IP addresses.**
5. **Which command collapses a multivalue field into a single regular string separated by newlines, preventing it from behaving as a multivalue array in downstream pipes?**

---
*Respond with your quiz answers to advance to Chapter 04: Filtering, Sorting & Structuring Results (`where`, `search`, `dedup`, `sort`, `table`, `fields`)!*
