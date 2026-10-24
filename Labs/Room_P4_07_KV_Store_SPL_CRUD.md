# 🎮 Room P4-07: KV Store High-Speed CRUD

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-07: KV Store High-Speed CRUD           ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: inputlookup, outputlookup & KV Store     💎 REWARD: 200 XP     │
│ ⏱️ ESTIMATED TIME: 30 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Active C2 Watchlist Remediation!**  
> The SOC Threat Intelligence team tracks high-risk Command-and-Control (C2) servers in an App Key Value Store collection named `c2_threat_feed`.  
> An automated external alert confirms that an active malicious domain (`evil-ransomware-c2.net`) has been sinkholed and dismantled by law enforcement.  
> 
> You must perform real-time CRUD operations directly in SPL:
> 1. Query the KV Store collection efficiently using disk-level filtering.
> 2. Enrich firewall connection streams using `OUTPUTNEW` safeguards.
> 3. Update the sinkholed record's status to `NEUTRALIZED` using its unique `_key`.
> 4. Verify data integrity and prevent destructive table overwrites!

---

## 🗺️ Mission Architecture & Target Environment

![KV Store 3D Vault](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_lookups_kvstore_spl_crud_3d_1792231127174.jpg)
*Figure P4-7.1: KV Store Cryptographic Vault & SPL CRUD Station.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          shc-captain-01 (192.168.1.10:8000)                   │
│ • KV Store Engine:      Embedded MongoDB listening on Port 8191              │
│ • Target Collection:    c2_threat_feed (collections.conf)                    │
│ • Primary Target Key:   _key = "ioc_c2_4491"                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Filtered Standalone Table Inspection (50 XP)

### 📖 Incident Details
Query the `c2_threat_feed` collection directly. Filter for only active threats associated with ransomware before loading data into memory:

```spl
| inputlookup c2_threat_feed where threat_type="RANSOMWARE" AND status="ACTIVE"
| table _key, domain, ip_address, threat_type, status
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What clause appended directly to `inputlookup` filters rows on disk before the table is loaded into Search Head RAM?  
*(Answer Format: `where <**********>`)*

<details>
<summary>💡 Need a Hint?</summary>
where condition
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>where &lt;condition&gt;</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{INPUTLOOKUP_WHERE_DISK_PRUNING_MASTERY}
```

---

## 🎯 TASK 2: Inline Stream Enrichment with `OUTPUTNEW` (50 XP)

### 📖 Incident Details
Correlate DNS lookup events against the `c2_threat_feed`. Enrich events with `threat_type` and `confidence`, ensuring that existing event fields are never overwritten:

```spl
index=dns sourcetype=bind:query
| lookup c2_threat_feed domain AS query_domain OUTPUTNEW threat_type, confidence
| where isnotnull(threat_type)
| table _time, client_ip, query_domain, threat_type, confidence
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which lookup keyword ensures that extracted fields in the event stream are preserved and never overwritten by incoming lookup fields?  
*(Answer Format: `*********`)*

<details>
<summary>💡 Need a Hint?</summary>
OUTPUTNEW
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>OUTPUTNEW</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{OUTPUTNEW_IMMUTABLE_FIELD_SAFEGUARD}
```

---

## 🎯 TASK 3: KV Store Record Mutation via `_key` (50 XP)

### 📖 Incident Details
Locate record `_key = "ioc_c2_4491"` (`evil-ransomware-c2.net`), update its status to `NEUTRALIZED`, and commit the update back to the KV Store collection without destroying existing records:

```spl
| inputlookup c2_threat_feed where _key="ioc_c2_4491"
| eval status = "NEUTRALIZED",
       remediated_by = "venom",
       remediated_time = strftime(now(), "%Y-%m-%d %H:%M:%S")
| outputlookup c2_threat_feed append=true
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What internal field must be present in search results for `outputlookup append=true` to update an existing document in a KV Store collection rather than creating a duplicate document?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
_key
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>_key</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{KVSTORE_UNDERSCORE_KEY_RECORD_UPSERT}
```

---

## 🎯 TASK 4: Accidental Data Loss Prevention (50 XP)

### 📖 Incident Details
Verify the safe execution parameters of `outputlookup` across all enterprise dashboards and automated alert actions:

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What mandatory parameter must be set in `outputlookup` to prevent Splunk from wiping the entire target lookup table during updates?  
*(Answer Format: `******=true`)*

<details>
<summary>💡 Need a Hint?</summary>
append=true
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>append=true</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{APPEND_TRUE_PREVENTS_DATA_EXTINCTION}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-07 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{INPUTLOOKUP_WHERE_DISK_PRUNING_MASTERY}               ║
║ [X] FLAG 2.1: FLAG{OUTPUTNEW_IMMUTABLE_FIELD_SAFEGUARD}                  ║
║ [X] FLAG 3.1: FLAG{KVSTORE_UNDERSCORE_KEY_RECORD_UPSERT}                 ║
║ [X] FLAG 4.1: FLAG{APPEND_TRUE_PREVENTS_DATA_EXTINCTION}                 ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You mastered SPL lookup manipulation, safe KV Store document mutations, and prevented catastrophic table overwrites.  
> **Total XP Awarded:** `+200 XP`!  
> Next Mission: **[Chapter 08: Enterprise Acceleration Techniques (Report Acceleration, Summary Indexing & DMA)](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_08_Enterprise_Acceleration_Techniques.md)**!
