# 🛡️ Chapter 01 (Phase 5): Splunk User & Role Architecture — `authorize.conf`, Inheritance & Custom Roles

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 39 | **Milestone:** Enterprise Access Governance & RBAC Architecture  
> **Current Rank:** Master Splunk Architect (6,550 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_01_User_and_Role_Architecture.md`  
> **Interactive Cyber Range Lab:** [Room P5-01: The RBAC Vault Infiltration](../Labs/Room_P5_01_User_and_Role_Architecture.md) `[250 XP]`

---

## 🏰 1. The Everyday Analogy: The Pentagonal Compound & Tiered Keycard Badges

Imagine a high-security military and intelligence research facility:

- **The Danger of Master Keys (The "Give Everyone Admin" Fallacy):**  
  If the security director hands every new intern, scientist, and maintenance contractor the **Golden Master Skeleton Key** (`admin`), chaos ensues. An intern accidentally trips the power grid, an external auditor views top-secret weapons schematics, and a contractor deletes critical forensic surveillance tapes.
- **The Architect's Tiered Keycard System (Role-Based Access Control):**  
  Instead, the facility issues digital RFID keycard badges programmed with specific clearances:
  - **Standard Visitor (`user`):** Can walk down public hallways and view library records in the reading room.
  - **Senior Investigator (`power`):** Inherits visitor access, plus gains the ability to pin case evidence to public briefing boards and configure automated perimeter alarms.
  - **Facility Commander (`admin`):** Full authority to reprogram door locks, reassign security guards, and commission new research wings.
  - **The Incinerator Specialist (`can_delete`):** A heavily secured, isolated key kept in a locked biohazard safe. It does not grant access to office desks or computers; its **only function is to authorize the shredder to permanently destroy classified files**!

In Splunk, **Role-Based Access Control (RBAC)** governs every action, search, dashboard, and configuration file. By architecting fine-grained roles in `authorize.conf`, you ensure compliance with HIPAA, PCI-DSS, and SOC2 while shielding your cluster from accidental administrative destruction!

---

## 🗺️ 2. The 3D Master Architectural Blueprint

![Splunk RBAC Architecture 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_user_and_role_architecture_3d_1792232469425.jpg)
*Figure 5.1: 3D Architectural Blueprint of the Splunk Role-Based Access Control (RBAC) and Security Authorization Engine, illustrating the layered fortress clearance decks (Admin, Power, User) and the isolated cryptographic can_delete lockbox.*

---

## 🔄 3. The 5-Step Authorization Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      THE 5-STEP SPLUNK AUTHORIZATION LIFECYCLE                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. IDENTITY AUTHENTICATION (Native / LDAP / SAML)                                       │
│    • User presents credentials; authentication provider verifies identity.             │
│    • Splunk matches user's group memberships to assigned roles in authentication.conf.  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. ROLE INHERITANCE RESOLUTION ('importRoles')                                          │
│    • Splunk traverses authorize.conf and builds the complete inheritance graph.         │
│    • Child roles automatically absorb all capabilities of their parent roles.           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. CAPABILITY UNION COMPILATION                                                         │
│    • Splunk combines all granted capabilities into a single consolidated permission     │
│      bitmask (Capabilities are strictly additive).                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. RESOURCE QUOTA ENFORCEMENT                                                           │
│    • Checks concurrent search limits (srchJobsQuota) and disk quotas (srchDiskQuota).   │
│    • Prevents any single user or role from starving the cluster of CPU cores.           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. AUDITED EXECUTION LOGGING                                                            │
│    • All search requests and permission checks are immutably written to index=_audit.   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 The Anatomy of `authorize.conf`

Splunk manages roles and permissions primarily through `$SPLUNK_HOME/etc/system/local/authorize.conf` (or via custom security apps).

Each role is defined by a stanza with the prefix `[role_<role_name>]`:

```ini
# Example: Custom SOC Tier-2 Analyst Role
[role_soc_analyst_tier2]
importRoles = user; power
srchFilter = sourcetype!=pci:cardholder_data
srchIndexesAllowed = network; security; firewall
srchIndexesDefault = security
srchJobsQuota = 6
rtSrchJobsQuota = 2
srchDiskQuota = 500
cumulativeSrchJobsQuota = 50
cumulativeRTSrchJobsQuota = 10
```

---

### 4.2 Splunk's 5 Built-in Default Roles

Every Splunk instance ships with 5 standard, pre-configured roles:

| Role Name | Primary Purpose | Key Capabilities Included | What it CANNOT Do |
| :--- | :--- | :--- | :--- |
| **`admin`** | Full System & App Administrator | `admin_all_objects`, `edit_user`, `indexes_edit`, `restart_splunkd`, `schedule_search` | **Cannot delete events** (by default, `admin` does NOT inherit `can_delete`!) |
| **`power`** | Advanced Analyst & Dashboard Creator | `edit_search_schedule_priority`, `schedule_search`, `embed_report`, creates shared objects | Cannot install apps, configure inputs, or manage user accounts. |
| **`user`** | Standard Analytical User | `search`, `schedule_rtsearch`, creates private alerts, views shared apps | Cannot share objects globally or edit cluster configurations. |
| **`can_delete`** | Emergency Forensic Purging Role | `delete` (Enables the `| delete` command in SPL) | Has **zero search capabilities** by default! Must be paired with a search role to function. |
| **`splunk-system-role`**| Internal Automated Daemons | High-level system automation capabilities | Used internally by `splunkd`; never assign to human users! |

---

### 4.3 Granular Role Inheritance & The Principle of Least Privilege

In Splunk, roles can inherit permissions from one or more other roles via the `importRoles` directive:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        ROLE INHERITANCE DYNAMICS                       │
├────────────────────────────────────────────────────────────────────────┤
│ • Capabilities are ADDITIVE (Unioned):                                 │
│   If Role A has capability "edit_tokens" and Role B has "search", a   │
│   user with both roles receives {"edit_tokens", "search"}.             │
├────────────────────────────────────────────────────────────────────────┤
│ • Resource Quotas Take the HIGHEST Value:                              │
│   If Role A allows 5 concurrent searches and Role B allows 10, the     │
│   user is granted 10 concurrent searches.                              │
├────────────────────────────────────────────────────────────────────────┤
│ • Search Filters are COMBINED WITH AND (Intersected):                  │
│   If Role A has srchFilter: host=web* and Role B has: status=404,     │
│   the user's final search filter is: (host=web*) AND (status=404).     │
└────────────────────────────────────────────────────────────────────────┘
```

#### Production Custom Role Hierarchy:
```ini
# Base Read-Only Security Analyst
[role_soc_level1]
importRoles = user
srchIndexesAllowed = firewall; ids; edr
srchIndexesDefault = firewall
srchJobsQuota = 3

# Senior Incident Responder (Inherits Level 1 + Power)
[role_soc_level2]
importRoles = soc_level1; power
srchIndexesAllowed = firewall; ids; edr; proxy; threat_intel
srchJobsQuota = 8
```

---

### 4.4 Concurrency & Resource Quotas

To prevent rogue searches from starving Search Heads, `authorize.conf` enforces four distinct quota boundaries:

1. **`srchJobsQuota`:**  
   Maximum number of concurrent historical searches an **individual user** assigned to this role can run (default: 3 for `user`, 6 for `power`).
2. **`rtSrchJobsQuota`:**  
   Maximum number of concurrent real-time searches an **individual user** can run (default: 1 for `user`).
3. **`cumulativeSrchJobsQuota`:**  
   Maximum number of concurrent historical searches across **all users combined** who belong to this role.
4. **`srchDiskQuota`:**  
   Maximum disk space in Megabytes (MB) that all active search dispatch artifacts for a user can consume simultaneously (default: 100 MB for `user`, 500 MB for `power`).

---

### 4.5 The Dreaded `can_delete` Role & Forensic Safety

In regulatory environments (HIPAA, PCI-DSS, GDPR), accidentally deleting indexed data can trigger massive fines or legal liability.

```text
┌────────────────────────────────────────────────────────────────────────┐
│               ⚠️ CRITICAL ARCHITECTURAL SAFEGUARD: can_delete          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. By default, the admin role DOES NOT have the delete capability!     │
│ 2. The can_delete role has ONLY ONE capability: delete.                │
│ 3. can_delete cannot search data on its own. To delete an event, you   │
│    must temporarily assign can_delete to an administrative user:       │
│    User venom ➔ Roles: [admin, can_delete]                            │
│ 4. Run the search:                                                     │
│    index=security "compromised_token" | delete                         │
│ 5. IMMEDIATELY REMOVE can_delete from the user account once done!      │
└────────────────────────────────────────────────────────────────────────┘
```

> **🔥 How `| delete` Actually Works Under the Hood:**  
> The `| delete` command **does NOT erase bytes from `journal.zst` on disk**!  
> Instead, it writes a deletion marker into the index's `.tsidx` card catalog, marking the event as hidden from future searches. The raw bytes remain on disk until the bucket rolls to Frozen!

---

## ⚠️ 5. Common Production Pitfalls & Security Vulnerabilities

### Pitfall 1: Granting `admin` to All Security Engineers
- **The Disaster:** A SOC engineer wanting to create an alert was assigned the `admin` role. While testing an app, they accidentally clicked "Restart Splunk," terminating all active searches across 200 SOC analysts during a live incident.
- **The Remedy:** Create a custom `soc_lead` role that inherits `power` and adds only the specific needed capabilities (e.g., `edit_tokens_all`, `schedule_search`).

### Pitfall 2: Leaving `srchDiskQuota` Unbounded
- **The Disaster:** A data scientist runs 20 concurrent Verbose Mode queries with `srchDiskQuota` set to `0` (unlimited).
- **The Impact:** The dispatch directory fills up the root disk partition (`/opt`), causing `splunkd` to halt with `Search crash: no disk space left on device`.

---

## 🎮 Hands-On Cyber Range Challenge: Room P5-01

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ CYBER RANGE: Room P5-01 — The RBAC Vault Infiltration               │
│ ⭐ DIFFICULTY: Easy-Medium | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins      │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Scenario:**  
> An internal security audit reveals that a disgruntled contractor account has unauthorized administrative access and the ability to execute `| delete` commands.  
> 
> You must:
> 1. Audit `/opt/splunk/etc/system/local/authorize.conf`.
> 2. Strip the `can_delete` capability from all user and admin roles.
> 3. Architect a least-privilege role named `external_auditor` that inherits `user`, restricts search to `index=compliance`, and limits concurrent searches to 2.
> 4. Verify user permissions via `btool` and capture all 4 flags!

👉 **[Enter Cyber Range Room P5-01: The RBAC Vault Infiltration](../Labs/Room_P5_01_User_and_Role_Architecture.md)** `[250 XP]`

---

## 🧠 Chapter 01 (Phase 5) Self-Check Quiz

Answer these 5 questions to test your mastery of Splunk User & Role Architecture:

1. **Why does the default `admin` role in Splunk Enterprise lack the `delete` capability, and how is forensic event deletion authorized in production?**
2. **If User Alice is assigned Role A (`srchJobsQuota = 5`) and Role B (`srchJobsQuota = 10`), how many concurrent historical searches can Alice run?**
3. **What is the operational difference between `srchJobsQuota` and `cumulativeSrchJobsQuota` in `authorize.conf`?**
4. **When an administrator uses `importRoles = user; power` in a custom role stanza, what happens to the capabilities of the custom role?**
5. **Does running `index=web "dirty_data" | delete` immediately reclaim physical hard drive space on an Indexer? Explain what actually occurs on disk.**

---
*Respond with your quiz answers to advance to Chapter 02: Capabilities Management & Granular Search Filters (`srchFilter`, `srchIndexesAllowed`)!*
