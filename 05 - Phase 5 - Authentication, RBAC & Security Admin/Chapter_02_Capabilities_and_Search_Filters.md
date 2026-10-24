# 🛡️ Chapter 02 (Phase 5): Capabilities Management & Granular Search Filters — `srchFilter`, `srchIndexesAllowed` & Row-Level Isolation

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 40 | **Milestone:** Precision Data Masking, Row-Level Isolation & Capability Bitmasks  
> **Current Rank:** Master Splunk Architect (6,550 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_02_Capabilities_and_Search_Filters.md`  
> **Interactive Cyber Range Lab:** [Room P5-02: The Search Filter Sandbox Trap](../Labs/Room_P5_02_Capabilities_and_Search_Filters.md) `[250 XP]`

---

## 🏰 1. The Everyday Analogy: The Classified Archives & The Redaction Stencil

Imagine a massive government intelligence archive:

- **The Index Badge (`srchIndexesAllowed`):**  
  The archive is divided into separate physical vaults: *Domestic Surveillance* (`index=domestic`), *Foreign Signals* (`index=sigint`), and *Internal Affairs* (`index=_audit`). When a field agent enters the facility, the door scanner checks their badge. If the agent only has clearance for `domestic`, the doors to `sigint` remain steel-locked.
- **The Default Reading Desk (`srchIndexesDefault`):**  
  When an agent sits down and asks the clerk "Show me all incident reports from yesterday," without naming a specific vault, the clerk automatically fetches boxes from their default assignment (`domestic`), rather than rummaging through every room in the building.
- **The Automatic Redaction Stencil (`srchFilter`):**  
  Suppose Agent Miller has clearance to enter the *Domestic Surveillance* vault, but she is strictly forbidden from viewing medical records or cases involving VIP politicians. The archive clerk places an **immutable optical stencil over every document** before Agent Miller sees it. If a page mentions `department=vip_protection`, the stencil blacks it out instantly! Agent Miller doesn't even know those records exist—her search query is quietly and transparently modified before the vault librarian ever fetches the pages.
- **The Multi-Clearance Compromise Trap (The Inheritance OR Bug):**  
  If Agent Miller is granted an additional visitor badge that has "No restrictions" (no stencil applied), and she walks into the reading room with both badges pinned to her lapel, the vault rules say: *"Honor the broadest clearance!"* Suddenly, the stencil falls away, and the VIP records she was supposed to be blocked from are wide open!

In Splunk Enterprise, **Capabilities, Index Allotments, and `srchFilter`** form the mathematical shield that enforces multi-tenancy, GDPR/HIPAA compliance, and row-level data segregation across petabyte clusters.

---

## 🗺️ 2. The 3D Master Architectural Blueprint

![Splunk Capabilities and Search Filters 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_capabilities_and_search_filters_3d_1792232655086.jpg)
*Figure 5.2: 3D Architectural Blueprint of the Splunk Search Filter Engine and Capabilities Matrix, showing query packet interception at the Security Gateway, optical index routing through Allowed vs Default prisms, and the automated row-level Boolean constraint injection scanner.*

---

## 🔄 3. The 5-Step Query Interception & Filter Injection Journey

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│              THE 5-STEP QUERY INTERCEPTION & FILTER INJECTION JOURNEY                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. SEARCH SUBMISSION & CAPABILITY VERIFICATION                                          │
│    • User submits: `sourcetype=access_combined status=500`                              │
│    • Dispatch engine checks if user's role possesses `search` capability.               │
│    • Checks concurrency quota (srchJobsQuota) against live running dispatch jobs.       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. DEFAULT INDEX INJECTION ('srchIndexesDefault')                                       │
│    • Since user omitted `index=...`, Splunk injects:                                    │
│      `(index=web OR index=main)` based on the role's `srchIndexesDefault`.              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. ALLOWED INDEX VALIDATION & CLAMPING ('srchIndexesAllowed')                           │
│    • Splunk verifies requested indexes against `srchIndexesAllowed`.                    │
│    • If user ran `index=*`, Splunk clamps `*` to ONLY the explicit allowed list.        │
│    • Internal indexes (`_*`) are blocked unless explicitly specified in allowed list.   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. ROW-LEVEL SECURITY INJECTION ('srchFilter')                                          │
│    • Splunk retrieves `srchFilter` from authorize.conf (e.g. `dept=finance`).           │
│    • Evaluates role inheritance: Filters are combined using (FilterA) OR (FilterB).     │
│    • Rewrites SPL abstract syntax tree: `((index=web) AND (status=500)) AND (dept=fin)`│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. INDEXER DISPATCH & STORAGE BUCKET PRUNING                                            │
│    • Indexers evaluate TSIDX lexicons with the injected constraints.                    │
│    • Non-matching raw events are pruned at the storage tier before reaching search head.│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 Enterprise Capabilities Taxonomy

Capabilities are discrete, atomic permissions assigned to roles in `$SPLUNK_HOME/etc/system/local/authorize.conf`. They control every feature in the Splunk Web UI, CLI, and REST API.

#### The Core Capabilities Matrix

| Capability Category | Key Capability Name | Exact Technical Function & Impact | Risk Level |
| :--- | :--- | :--- | :---: |
| **Search & Execution** | `search` | Fundamental permission to execute any ad-hoc search query. | Low |
| | `schedule_search` | Allows saving searches as scheduled reports or alerts. | Medium |
| | `schedule_rtsearch` | Allows running high-overhead real-time searches. | **High** |
| | `accelerate_datamodel`| Allows configuring and triggering Data Model Acceleration (DMA). | High |
| | `accelerate_search` | Allows enabling report acceleration summary caches. | Medium |
| **Schedule Control** | `edit_search_schedule_priority` | Allows raising search priority to `higher` or `highest`. | High |
| | `edit_search_schedule_window` | Allows widening schedule windows to prevent search concurrency spikes. | Medium |
| **System Administration**| `admin_all_objects` | Master bypass capability; gives access to all apps, knowledge objects, and REST. | **Critical** |
| | `restart_splunkd` | Authorizes restarting the host Splunk daemon via Web or REST. | **Critical** |
| | `indexes_edit` | Allows creating, deleting, and altering index configurations. | **Critical** |
| | `edit_tcp` | Allows opening, closing, and reconfiguring network listening ports (9997, 514). | High |
| | `edit_user` | Allows creating, deleting, and modifying user accounts and passwords. | **Critical** |
| **Forensics & Audit** | `delete` | Unlocks the `| delete` command in SPL to mark records invisible. | **Extreme** |
| | `run_debug_commands`| Unlocks sensitive diagnostic search commands (e.g., `dumpsearches`). | High |

---

### 4.2 Index Scoping: `srchIndexesAllowed` vs. `srchIndexesDefault`

Index scoping determines **which physical data repositories** a user can query.

```ini
[role_regional_security_eu]
importRoles = user
srchIndexesAllowed = security_eu; firewall_eu; _audit
srchIndexesDefault = security_eu
```

#### Critical Scoping Behaviors:
1. **The Wildcard (`*`) Scope:**  
   If `srchIndexesAllowed = *`, the user can query all non-internal indexes. **It does NOT grant access to internal indexes** (`_internal`, `_audit`, `_introspection`).
2. **Internal Index Access (`_*`):**  
   To query internal logs, they must be explicitly listed:
   ```ini
   # Allows all public indexes AND the internal log index
   srchIndexesAllowed = *; _internal; _audit
   ```
3. **The `srchIndexesDefault` Trap:**  
   If a user runs `sourcetype=syslog` (without `index=...`), Splunk only searches the indexes listed in `srchIndexesDefault`.
   > [!IMPORTANT]
   > Every index listed in `srchIndexesDefault` **MUST also be included** in `srchIndexesAllowed`! If `srchIndexesDefault = security` but `security` is absent from `srchIndexesAllowed`, ad-hoc queries without an explicit index clause will trigger an authorization error.

---

### 4.3 Row-Level Data Segregation: `srchFilter`

The `srchFilter` setting in `authorize.conf` restricts a role to a specific subset of events within allowed indexes based on arbitrary Boolean field expressions.

#### Syntax & Configuration Examples:

```ini
# Role 1: Network Admin restricted to Cisco network gear
[role_network_admin]
importRoles = user
srchIndexesAllowed = network; firewall
srchIndexesDefault = network
srchFilter = vendor=cisco OR sourcetype=cisco:*

# Role 2: Tenant Isolation in Managed Service Provider (MSP)
[role_client_acme_corp]
importRoles = user
srchIndexesAllowed = client_logs
srchIndexesDefault = client_logs
srchFilter = (client_id="ACME-9901" OR tenant="acme") AND env=production
```

#### How the SPL Parser Injects `srchFilter`:
When a user assigned `role_client_acme_corp` runs:
```spl
index=client_logs error_code=403 | stats count by user
```
The search parser secretly rewrites the search job AST into:
```spl
(index=client_logs error_code=403) AND ((client_id="ACME-9901" OR tenant="acme") AND env=production) | stats count by user
```

---

### 4.4 The Inheritance OR Rule & Security Bypass Vulnerability

One of the most dangerous architectural pitfalls in Splunk RBAC is **how `srchFilter` evaluates multiple roles**:

$$\text{Final Filter} = (\text{Filter}_{\text{Role 1}}) \;\mathbf{OR}\; (\text{Filter}_{\text{Role 2}}) \;\mathbf{OR}\; \dots \;\mathbf{OR}\; (\text{Filter}_{\text{Role } n})$$

> [!CAUTION]
> **The Empty Filter Security Hole:**  
> If Role A has `srchFilter = dept=finance`, and Role B has **NO** `srchFilter` defined (`srchFilter = ` or inherited from standard `user` where it is empty):
> $$\text{Effective Filter} = (\text{dept=finance}) \;\mathbf{OR}\; (\text{TRUE}) \equiv \mathbf{TRUE}$$
> **The filter is completely nullified!** The user can now see ALL data across all departments!

#### Rules for Safe Filter Inheritance:
1. **Never inherit standard built-in `user` or `power` roles** into a restricted custom role if those built-in roles have empty search filters.
2. Instead, create a clean base role (`[role_base_filtered]`) that sets common capabilities without granting unrestricted search filters.
3. Test every role's effective filter using the REST endpoint:
   ```bash
   curl -k -u admin:Pass123 https://localhost:8089/services/authentication/users/analyst1?output_mode=json | jq '.entry[0].content.roles'
   ```

---

### 4.5 Search Concurrency & Time-Window Clamping

`authorize.conf` also enforces resource guardrails to prevent noisy users from saturating search head and indexer CPU cores:

| Configuration Setting | Default (`user`) | Production Best Practice | Purpose & Cluster Impact |
| :--- | :---: | :---: | :--- |
| `srchJobsQuota` | `3` | `4` to `8` | Maximum concurrent standard historical searches per user. |
| `rtSrchJobsQuota` | `6` | `0` (or `1` for SOC) | Maximum concurrent real-time searches (set to `0` to kill real-time abuse!). |
| `srchDiskQuota` | `100` (MB) | `1000` (1 GB) | Maximum cumulative disk space for search job artifacts in `dispatch/`. |
| `cumulativeSrchJobsQuota`| `0` (disabled) | `30` | Maximum concurrent searches allowed across **all users sharing this role**. |
| `srchTimeWin` | `0` (unlimited) | `86400` (24h) | **Clamps search time range!** Forces searches to be $\le 24$ hours (prevents "All Time" accidental scans). |

```ini
# Production-Hardened Tier-1 SOC Role
[role_soc_analyst_l1]
importRoles = 
capabilities = search; schedule_search
srchIndexesAllowed = security; proxy; edr
srchIndexesDefault = security
srchFilter = classification!=top_secret
srchJobsQuota = 4
rtSrchJobsQuota = 0
srchDiskQuota = 500
srchTimeWin = 604800
# Clamps all searches to max 7 days!
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

### Pitfall 1: Granting Wildcard `*` in Multi-Tenant Environments
- **The Anti-Pattern:** Setting `srchIndexesAllowed = *` on a tenant role, thinking `srchFilter` alone will isolate data.
- **The Failure:** If a rogue or unindexed source writes without the expected filter field (e.g. events missing `client_id`), or if index-level metadata commands like `| metadata type=sourcetypes` are run, data leaks across tenant boundaries.
- **The Fix:** Always restrict `srchIndexesAllowed` to dedicated tenant indexes: `srchIndexesAllowed = tenant_acme_*`.

### Pitfall 2: Neglecting the Cost of Unindexed Terms in `srchFilter`
- **The Anti-Pattern:** Setting `srchFilter = *SECRET_STRING*` (leading wildcards) or complex regex calculations.
- **The Failure:** Because `srchFilter` is prepended to **every single search** executed by that role, every query forces indexers to perform full raw event scans, spiking CPU to 100%.
- **The Fix:** Ensure fields used in `srchFilter` are indexed fields (like `index`, `host`, `source`, `sourcetype`) or top-level indexed tokens.

### Pitfall 3: Real-Time Search Quota Starvation
- **The Anti-Pattern:** Leaving `rtSrchJobsQuota` enabled for regular users.
- **The Failure:** 10 analysts open live-tail dashboards. Each real-time search permanently pins 1 CPU core on the search head and 1 core per indexer. Within an hour, scheduled alert searches fail due to `Search concurrency limit reached`.
- **The Fix:** Explicitly set `rtSrchJobsQuota = 0` for all non-executive roles.

---

## 🛠️ 6. Cyber Range Lab: The Search Filter Sandbox Trap

Test your skills in the dedicated hands-on scenario:  
👉 **[Room P5-02: The Search Filter Sandbox Trap](../Labs/Room_P5_02_Capabilities_and_Search_Filters.md)**

### Mission Brief:
- **Scenario:** A defense contractor has hired your architecture team to audit their multi-tenant Splunk deployment. An external auditor assigned the role `role_auditor_eu` managed to view unredacted US military drone telemetry in `index=dod_telemetry`.
- **Objective:**
  1. Inspect `authorize.conf` and identify the inheritance flaw causing the `srchFilter` bypass.
  2. Clamp the role's index access to strictly European NATO logs (`index=nato_eu_*`).
  3. Enforce a 48-hour search time window (`srchTimeWin = 172800`) and eliminate real-time search privileges.
  4. Recover the flag `FLAG{SRCH_F1LT3R_0R_BYP4SS_PLUGGED_6782}`.

---

## 🧠 7. End-of-Chapter Self-Check Quiz

#### Q1: If a role has `srchIndexesAllowed = *`, can a user assigned this role run `index=_internal sourcetype=splunkd`?
- **A)** Yes, because `*` matches all characters including underscores.
- **B)** No, because wildcard `*` explicitly excludes all internal indexes starting with an underscore (`_*`).
- **C)** Yes, but only if they have the `admin_all_objects` capability.
- **D)** Only if `srchIndexesDefault` also contains `_internal`.

#### Q2: Role Alpha has `srchFilter = department=hr`. Role Beta has no `srchFilter` defined (`srchFilter = `). What happens if User Sarah is assigned both Role Alpha and Role Beta?
- **A)** Sarah is restricted to `department=hr` because security filters are most restrictive.
- **B)** Sarah gets an authorization syntax error when searching.
- **C)** The filters combine via `OR` logic: `(department=hr) OR (TRUE)`, completely nullifying the restriction.
- **D)** Splunk alternates filters based on the time of day.

#### Q3: Which capability allows an analyst to run searches with priority over standard users, preventing their ad-hoc jobs from being queued?
- **A)** `accelerate_search`
- **B)** `edit_search_schedule_priority`
- **C)** `admin_all_objects`
- **D)** `search_high_priority`

#### Q4: If a role has `srchTimeWin = 86400`, what happens when a user attempts to select "All Time" in the Splunk time picker?
- **A)** The search fails immediately with a fatal permission denied error.
- **B)** Splunk clamps the search time range to the last 24 hours (86,400 seconds) from now.
- **C)** Splunk runs the search across all time, but limits output to 86,400 events.
- **D)** The query is dispatched as a real-time rolling window search.

#### Q5: What is the primary difference between `srchIndexesAllowed` and `srchIndexesDefault`?
- **A)** `srchIndexesAllowed` controls index creation; `srchIndexesDefault` controls index deletion.
- **B)** `srchIndexesAllowed` dictates all indexes a user is permitted to search; `srchIndexesDefault` specifies which indexes are queried when `index=...` is omitted.
- **C)** `srchIndexesDefault` is only used for scheduled reports; `srchIndexesAllowed` is for ad-hoc searching.
- **D)** There is no difference; they are aliases for the same configuration setting.

---

### 📝 Quiz Answer Key
- **Q1: B** — The wildcard `*` matches all standard indexes, but deliberately excludes internal indexes (`_*`) such as `_internal` and `_audit`.
- **Q2: C** — Inherited search filters are joined with `OR`. An empty filter evaluates to `TRUE`, bypassing all restrictions.
- **Q3: B** — `edit_search_schedule_priority` allows raising search priority.
- **Q4: B** — `srchTimeWin` clamps the maximum permissible time boundary backward from `now()`.
- **Q5: B** — `srchIndexesAllowed` sets the overall authorization boundary, while `srchIndexesDefault` supplies the fallback index if none is specified in SPL.
