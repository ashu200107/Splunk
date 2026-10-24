# 🎮 Room P4-03: Multivalue JSON Surgery

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-03: Multivalue JSON Surgery            ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: eval, rex, spath, mvexpand & nomv        💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 35 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — CloudTrail Privilege Escalation & C2 Investigation!**  
> An alert from AWS GuardDuty indicates unauthorized API actions originating from a compromised developer role.  
> The raw CloudTrail events (`index=cloud_audit sourcetype=aws:cloudtrail:json`) contain deeply nested JSON structures with arrays of assumed role ARNs, multi-region IP connection lists, and embedded encoded session parameters.  
> 
> As the lead Splunk SOC Engineer, you must perform deep surgical extractions using `spath`, extract malicious external IPs via `rex`, expand the target array using `mvexpand`, and assign risk levels using `eval`.  
> Complete all 4 tasks to capture the flags and secure the cloud perimeter!

---

## 🗺️ Mission Architecture & Target Environment

![Multivalue JSON Surgery 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_eval_rex_spath_multivalue_3d_1792230146575.jpg)
*Figure P4-3.1: Event Manipulation & Multivalue Dissection Station.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET LOG SCHEMA                                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Index / Sourcetype:   index=cloud_audit sourcetype=aws:cloudtrail:json     │
│ • Sample Payload:       {"eventVersion":"1.08","userIdentity":{"type":"IAM", │
│                         "arn":"arn:aws:iam::123456789:user/dev_admin"},      │
│                         "requestParameters":{"securityGroupRuleIds":         │
│                         ["sgr-01a","sgr-02b","sgr-99x"]}}                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Nested JSON Extraction with `spath` (60 XP)

### 📖 Incident Details
Extract the IAM user ARN and all modified security group rule IDs from the nested JSON object into discrete Splunk fields without writing brittle regular expressions:

```spl
index=cloud_audit sourcetype=aws:cloudtrail:json
| spath input=_raw path=userIdentity.arn output=iam_arn
| spath input=_raw path=requestParameters.securityGroupRuleIds{} output=modified_sg_rules
| table _time, iam_arn, modified_sg_rules
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What syntax does `spath` use in the `path` argument to represent that a JSON key is an array and that ALL elements within that array should be extracted into a multivalue field?  
*(Answer Format: `**`)*

<details>
<summary>💡 Need a Hint?</summary>
Empty curly braces {}.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>{}</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{SPATH_CURLY_BRACE_ARRAY_DISSECTION}
```

---

## 🎯 TASK 2: Multivalue Regex Extraction with `rex` (60 XP)

### 📖 Incident Details
The attacker injected an obfuscated list of C2 callback IP addresses inside a custom diagnostic field: `C2_Targets=[185.220.101.5, 194.26.29.112, 45.154.255.88]`.  
A standard `rex` command only extracts `185.220.101.5`. You must extract all three IPs into a multivalue array:

```spl
index=cloud_audit
| rex max_match=0 "(?<c2_ips>\b\d{1,3}(?:\.\d{1,3}){3}\b)"
| table _time, iam_arn, c2_ips
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What exact argument must be added to the `rex` command to tell Splunk to match an unlimited number of occurrences rather than stopping after the first match?  
*(Answer Format: `*********=*`)*

<details>
<summary>💡 Need a Hint?</summary>
max_match=0
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>max_match=0</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{REX_MAX_MATCH_ZERO_MULTIVALUE_POWER}
```

---

## 🎯 TASK 3: Multivalue Expansion with `mvexpand` (65 XP)

### 📖 Incident Details
You must match each extracted C2 IP individually against external threat reputation lookup tables. To do this, expand the `c2_ips` array so that each IP occupies its own discrete event row:

```spl
index=cloud_audit
| rex max_match=0 "(?<c2_ips>\b\d{1,3}(?:\.\d{1,3}){3}\b)"
| mvexpand c2_ips
| stats count BY c2_ips, iam_arn
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which SPL command clones the entire event row for every single value present in a specified multivalue field?  
*(Answer Format: `********`)*

<details>
<summary>💡 Need a Hint?</summary>
mvexpand
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>mvexpand</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{MVEXPAND_ROW_CLONING_EXACT_ALIGNMENT}
```

---

## 🎯 TASK 4: Dynamic Threat Scoring with `eval case()` (65 XP)

### 📖 Incident Details
Categorize the risk of each assumed role session based on IP locality and error code using `eval case()`:

```spl
index=cloud_audit
| eval threat_level = case(
    cidrmatch("10.0.0.0/8", client_ip), "LOW",
    errorCode == "AccessDenied" AND cidrmatch("192.168.0.0/16", client_ip)==false, "HIGH",
    errorCode == "UnauthorizedOperation", "CRITICAL",
    true(), "MEDIUM"
)
| stats count BY threat_level
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What literal fallback expression is placed at the end of an `eval case()` statement to catch all events that did not match any of the preceding boolean conditions?  
*(Answer Format: `******`)*

<details>
<summary>💡 Need a Hint?</summary>
true(), "fallback_value"
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>true()</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{EVAL_CASE_TRUE_DEFAULT_CATCH_ALL}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-03 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{SPATH_CURLY_BRACE_ARRAY_DISSECTION}                  ║
║ [X] FLAG 2.1: FLAG{REX_MAX_MATCH_ZERO_MULTIVALUE_POWER}                  ║
║ [X] FLAG 3.1: FLAG{MVEXPAND_ROW_CLONING_EXACT_ALIGNMENT}                 ║
║ [X] FLAG 4.1: FLAG{EVAL_CASE_TRUE_DEFAULT_CATCH_ALL}                    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You mastered JSON traversal, multivalue regular expressions, array expansion, and conditional threat classification.  
> **Total XP Awarded:** `+250 XP`!  
> Next Mission: **[Chapter 04: Filtering, Sorting & Structuring Results (`where`, `search`, `dedup`, `sort`, `table`, `fields`)](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_04_Filtering_and_Structuring_Results.md)**!
