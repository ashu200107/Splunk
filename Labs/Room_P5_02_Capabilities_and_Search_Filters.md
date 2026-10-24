# 🎮 Room P5-02: The Search Filter Sandbox Trap

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-02: The Search Filter Sandbox Trap      ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: srchFilter, srchIndexesAllowed & Clamping 💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 40 Mins                         🛡️ CATEGORY: Security │
│ 🏆 PREREQUISITE: Room P5-01 (RBAC Architecture)                        │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: High-Security Incident — Defense Data Leakage via Filter Bypass!**  
> An external NATO audit team was granted access to your security cluster under the role `role_auditor_eu`.  
> While the role was supposed to restrict their queries to European NATO security telemetry (`index=nato_eu_*`), an auditor inadvertently queried `index=dod_telemetry` and retrieved unredacted US military drone telemetry containing top-secret coordinates!  
>  
> Your mission as the Lead Splunk Security Architect:  
> 1. Audit `authorize.conf` to discover why the `srchFilter` failed to block the unauthorized access.  
> 2. Re-architect index restrictions using explicit `srchIndexesAllowed` and `srchIndexesDefault`.  
> 3. Eliminate the `OR` inheritance vulnerability by detaching the unrestricted parent role.  
> 4. Enforce strict resource clamping (`srchTimeWin` and `rtSrchJobsQuota`) and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

![Search Filter Sandbox Trap 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_capabilities_and_search_filters_3d_1792232655086.jpg)
*Figure P5-2.1: Splunk Search Filter Engine and Row-Level Data Segregation Gateway.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          sh-defense-01 (10.100.20.15:8000)                    │
│ • Configuration File:   /opt/splunk/etc/system/local/authorize.conf          │
│ • Target Role:          [role_auditor_eu]                                    │
│ • Incident Artifact:    /tmp/breach_audit_query.spl                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Deconstructing the `srchFilter` OR-Bypass (60 XP)

### 📖 Incident Details
You examine the live configuration stanza in `/opt/splunk/etc/system/local/authorize.conf`:

```ini
[role_auditor_eu]
importRoles = user
srchIndexesAllowed = *
srchIndexesDefault = nato_eu_sec
srchFilter = region="EU" AND classification="UNCLASSIFIED"
```

The junior administrator thought: *"Since `srchFilter` specifies `region=EU`, the auditor can only see EU data, even though `srchIndexesAllowed = *`."*

However, `importRoles = user` imports the built-in `user` role!  
In Splunk default configurations, the `user` role has:
```ini
[role_user]
srchFilter = 
```
When Splunk combines `role_auditor_eu` and `role_user`, it compiles the filter as:
$$\text{Effective Filter} = (\text{region="EU" AND classification="UNCLASSIFIED"}) \;\mathbf{OR}\; (\text{TRUE}) \equiv \mathbf{TRUE}$$

The restriction was completely bypassed!

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
When a Splunk role imports another role, which Boolean operator is used by the search engine to combine their respective `srchFilter` expressions?  
*(Answer Format: `**`)*

<details>
<summary>💡 Need a Hint?</summary>
OR
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>OR</code> — Inherited search filters combine using <code>OR</code> logic, which means if any inherited role has no filter, all filters are bypassed!
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{SRCH_FILTER_OR_INHERITANCE_BYPASS_EXPOSED}
```

---

## 🎯 TASK 2: Hardening Index Scoping with Allowed Lists (60 XP)

### 📖 Tactical Objective
Never rely solely on `srchFilter` to partition physical indexes. You must clamp `srchIndexesAllowed` to prevent access to classified defense repositories (`dod_telemetry`, `nuclear_ops`, `us_sigint`).

### 🛠️ Hands-on Configuration
Edit `/opt/splunk/etc/system/local/authorize.conf` and update `[role_auditor_eu]`:

```ini
[role_auditor_eu]
# Remove wildcard * and restrict strictly to NATO European indexes
srchIndexesAllowed = nato_eu_sec; nato_eu_fw; nato_eu_intel
srchIndexesDefault = nato_eu_sec
```

Validate with `btool`:
```bash
/opt/splunk/bin/splunk btool authorize list role_auditor_eu --debug
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
If an administrator sets `srchIndexesAllowed = nato_eu_*`, does this grant access to an internal audit index named `_nato_eu_audit`?  
*(Answer Format: `***`)*

<details>
<summary>💡 Need a Hint?</summary>
No
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>No</code> — Wildcards in <code>srchIndexesAllowed</code> deliberately ignore all internal indexes prefixed with an underscore (<code>_*</code>).
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{INDEX_SCOPING_WILDCARD_CLAMPED_SECURELY}
```

---

## 🎯 TASK 3: Neutralizing the Empty Filter Vulnerability (65 XP)

### 📖 Tactical Objective
To eliminate the `OR TRUE` bypass, you must remove `importRoles = user` from `[role_auditor_eu]`, and explicitly grant only the necessary baseline search capabilities directly to the role.

### 🛠️ Hardened Role Architecture
Update `/opt/splunk/etc/system/local/authorize.conf`:

```ini
[role_auditor_eu]
# Explicitly decouple from standard user to eliminate empty srchFilter inheritance
importRoles = 
capabilities = search; schedule_search; get_metadata

srchIndexesAllowed = nato_eu_sec; nato_eu_fw; nato_eu_intel
srchIndexesDefault = nato_eu_sec
srchFilter = (region="EU" AND classification="UNCLASSIFIED")
```

Verify using REST API:
```bash
curl -k -u admin:SplunkAdmin123! https://10.100.20.15:8089/services/authorization/roles/role_auditor_eu?output_mode=json | jq '.entry[0].content.srchFilter'
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What capability must be assigned to `role_auditor_eu` so they can run ad-hoc searches without inheriting the vulnerable `user` role?  
*(Answer Format: `******`)*

<details>
<summary>💡 Need a Hint?</summary>
search
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>search</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{ROW_LEVEL_FILTER_RESTORED_ZERO_BYPASS}
```

---

## 🎯 TASK 4: Resource Clamping & Anti-Starvation Controls (65 XP)

### 📖 Tactical Objective
External auditors have a history of launching unbounded historical searches spanning 10 years, and spawning 20 real-time browser tabs that crash search head memory.

Enforce the following guardrails:
1. Clamp historical search duration to a maximum of 48 hours (`srchTimeWin = 172800`).
2. Strictly disable real-time search concurrency (`rtSrchJobsQuota = 0`).
3. Set standard concurrent search limit to 4 (`srchJobsQuota = 4`).
4. Set search job artifact disk quota to 500 MB (`srchDiskQuota = 500`).

### 🛠️ Production Stanza
```ini
[role_auditor_eu]
importRoles = 
capabilities = search; schedule_search; get_metadata
srchIndexesAllowed = nato_eu_sec; nato_eu_fw; nato_eu_intel
srchIndexesDefault = nato_eu_sec
srchFilter = (region="EU" AND classification="UNCLASSIFIED")

# Resource Clamping & Anti-Starvation
srchJobsQuota = 4
rtSrchJobsQuota = 0
srchDiskQuota = 500
srchTimeWin = 172800
```

Apply changes live without downtime:
```bash
/opt/splunk/bin/splunk reload auth
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What parameter in `authorize.conf` enforces an absolute ceiling on how far back in time (in seconds) a role can execute a search query?  
*(Answer Format: ***********)*

<details>
<summary>💡 Need a Hint?</summary>
srchTimeWin
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>srchTimeWin</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{SRCH_F1LT3R_0R_BYP4SS_PLUGGED_6782}
```

---

## 🏆 Room Summary & Key Takeaways

1. **`srchFilter` combines with `OR`**: If a role inherits any role with an empty filter (like built-in `user`), all row-level restrictions are immediately dissolved.
2. **Layer Defense in Depth**: Use `srchIndexesAllowed` to set the physical perimeter, and `srchFilter` only for granular event masking inside authorized indexes.
3. **Guard Search Resources**: Always apply `srchTimeWin` and set `rtSrchJobsQuota = 0` on non-admin roles to guarantee cluster performance stability.
