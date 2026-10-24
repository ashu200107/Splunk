# 🎮 Room P4-06: The Subsearch 10K Ceiling

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-06: The Subsearch 10K Ceiling          ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: Subsearch Limits, format & Anti-Joins   💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 35 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Triage of Stealth Command-and-Control Breach!**  
> An automated Threat Hunting subsearch query designed to detect firewall egress to infected hosts has failed:  
> ```spl
> index=firewall action=allowed
>     [ search index=edr sourcetype=crowdstrike:detection severity=critical
>       | fields infected_ip ]
> ```
> Forensic examination shows that over 14,200 unique IP addresses were flagged by CrowdStrike, but the subsearch silently truncated at **10,000 records**, allowing 4,200 compromised hosts to communicate undetected!  
> 
> You are the Principal Splunk Architect. You must diagnose the truncation limits, inspect the generated boolean strings, build dynamic baselines, and refactor the subsearch for enterprise resilience!

---

## 🗺️ Mission Architecture & Target Environment

![Subsearch 3D Engine](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_subsearches_execution_limits_3d_1792230819228.jpg)
*Figure P4-6.1: Subsearch Execution Engine & Limits Chamber.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET DATASET SCHEMA                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • EDR Log Source:       index=edr sourcetype=crowdstrike:detection           │
│ • Firewall Log Source:  index=firewall sourcetype=paloalto:traffic           │
│ • Limits Stanza:        $SPLUNK_HOME/etc/system/default/limits.conf          │
│                         [subsearch] maxout=10000, maxtime=60                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Diagnosing the Subsearch 10K Ceiling (60 XP)

### 📖 Incident Details
Inspect the search execution telemetry inside `info.csv` for the subsearch.  
You notice that `subsearch_maxout = 10000` was triggered, dropping 4,200 events from the boolean filter string.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the default maximum number of events that can be returned from an inner subsearch query before Splunk truncates the result set?  
*(Answer Format: `**,***`)*

<details>
<summary>💡 Need a Hint?</summary>
10,000 events
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>10,000</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{SUBSEARCH_MAXOUT_10K_CEILING_IDENTIFIED}
```

---

## 🎯 TASK 2: Inspecting Boolean Strings with `format` (60 XP)

### 📖 Incident Details
Verify the exact boolean filter string produced by an inner search before it is injected into the outer query by testing it in isolation with `format`:

```spl
| makeresults count=2
| eval infected_ip=if(_time%2==0, "198.51.100.22", "203.0.113.99")
| fields infected_ip
| format
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What exact command is automatically appended by Splunk to the end of every subsearch to convert tabular field values into a single compound boolean string?  
*(Answer Format: `******`)*

<details>
<summary>💡 Need a Hint?</summary>
format
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>format</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{FORMAT_IMPLICIT_BOOLEAN_GENERATOR}
```

---

## 🎯 TASK 3: Dynamic Anomaly Thresholding with `eval search` (65 XP)

### 📖 Incident Details
Construct a dynamic threshold subsearch where the outer firewall search only returns hosts whose bandwidth transfer exceeds **double the network average**:

```spl
index=firewall
    [ search index=firewall
      | stats avg(bytes) AS avg_bytes
      | eval search = "bytes > " . (avg_bytes * 2)
      | fields search ]
| stats sum(bytes) BY src_ip
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
When constructing a dynamic search clause in a subsearch, what exact field name must you assign in the `eval` statement so that Splunk injects the literal string directly into the outer search bar?  
*(Answer Format: `eval ****** = "..."`)*

<details>
<summary>💡 Need a Hint?</summary>
eval search = "..."
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>eval search = "..."</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{DYNAMIC_EVAL_SEARCH_CLAUSE_INJECTION}
```

---

## 🎯 TASK 4: Anti-Join Negative Searching (65 XP)

### 📖 Incident Details
Detect enterprise workstations that have **never checked into the patch management system** today:

```spl
index=assets type=workstation
    NOT [ search index=patching earliest=@d latest=now status=success
          | fields host ]
| table host, owner, ip_address
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What boolean keyword precedes a subsearch bracket to execute an "Anti-Join", filtering out all events matching the subsearch results?  
*(Answer Format: `***`)*

<details>
<summary>💡 Need a Hint?</summary>
NOT
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>NOT</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{NOT_SUBSEARCH_ANTI_JOIN_MASTERY}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-06 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{SUBSEARCH_MAXOUT_10K_CEILING_IDENTIFIED}              ║
║ [X] FLAG 2.1: FLAG{FORMAT_IMPLICIT_BOOLEAN_GENERATOR}                    ║
║ [X] FLAG 3.1: FLAG{DYNAMIC_EVAL_SEARCH_CLAUSE_INJECTION}                 ║
║ [X] FLAG 4.1: FLAG{NOT_SUBSEARCH_ANTI_JOIN_MASTERY}                      ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You mastered subsearch lifecycle mechanics, boolean format generation, dynamic baseline evaluation, and anti-join queries.  
> **Total XP Awarded:** `+250 XP`!  
> Next Mission: **[Chapter 07: Lookups & KV Store in SPL (`inputlookup`, `outputlookup`, `lookup`, KV Store CRUD)](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_07_Lookups_and_KV_Store_in_SPL.md)**!
