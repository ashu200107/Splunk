# 🛡️ Chapter 04 (Phase 5): Enterprise LDAP & Active Directory Integration — `authentication.conf`, Group Mapping & High-Availability Failover

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 42 | **Milestone:** Enterprise Directory Federation, LDAPS Port 636 & Dynamic Group Mapping  
> **Current Rank:** Master Splunk Architect (7,000 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_04_LDAP_Active_Directory_Integration.md`  
> **Interactive Cyber Range Lab:** [Room P5-04: Active Directory Forest Synchronization](../Labs/Room_P5_04_LDAP_Active_Directory_Integration.md) `[300 XP]`

---

## 🏰 1. The Everyday Analogy: The Global Embassy & The Central Diplomatic Ledger

Imagine an international conglomerate operating embassies in 50 countries:

- **The Problem of Local Passbooks (The Native Auth Scaling Bottleneck):**  
  If each embassy guardhouse maintains its own local paper ledger of employee names and passwords, an employee hired in New York cannot enter the London or Tokyo office. Worse, when an employee is terminated in Tokyo, someone must manually telephone 50 separate embassies to scratch their name off every local book. If an admin forgets even one embassy, a fired rogue employee retains unauthorized access!
- **The Central Diplomatic Directory (Active Directory / LDAP):**  
  Instead, all embassies connect via encrypted satellite radio (LDAPS Port 636) to the **Global Diplomatic Registry (Active Directory)**. When an officer walks up to the London embassy checkpoint:
  1. The officer presents their corporate passport (`alice`).
  2. The guardhouse asks the central directory: *"Does Alice work here, what is her password, and what security teams does she belong to?"*
  3. The directory responds: *"Alice is active; she belongs to the `Security-Operations-Tier2` and `Incident-Response` groups."*
  4. The local embassy maps `Security-Operations-Tier2` directly to their local clearance badge: **`power`**!
- **The Backup Radio Generator (Failover & Fallback):**  
  If the primary satellite link to Washington DC goes down, the embassy automatically flips its radio dial to the backup domain controller in Frankfurt (`ad_corp_secondary`). And if both global links fail during an earthquake, the local guard still has their locked red emergency binder (`admin` in `/etc/passwd`) to enter the building!

In Splunk Enterprise, **LDAP and Active Directory Federation** centralizes credential management, automates onboarding/offboarding, and maps thousands of corporate security groups into least-privilege Splunk roles dynamically.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│              SPLUNK ENTERPRISE LDAP & ACTIVE DIRECTORY FEDERATION ENGINE                  │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌──────────────────────────┐                   ┌────────────────────────────────────┐   │
│   │   ACTIVE DIRECTORY OU    │                   │        SPLUNK SEARCH HEAD          │   │
│   │ (corp.internal / DC=corp)│                   │   (authentication.conf Engine)     │   │
│   └─────────────┬────────────┘                   └─────────────────┬──────────────────┘   │
│                 │                                                  │                      │
│   ┌─────────────┴────────────┐                                     │                      │
│   │ AD Security Groups       │                                     │                      │
│   │  • Splunk_Admins         ├────── LDAPS Port 636 (TLS) ─────────┤ Dynamic Group Map:   │
│   │  • Splunk_SOC_Tier2      │        bindDN: svc_splunk           │  • Splunk_Admins     │
│   │  • Splunk_Users          │        Search: userBaseDN           │    └──> [role_admin] │
│   └──────────────────────────┘                groupBaseDN          │  • Splunk_SOC_Tier2  │
│                                                                    │    └──> [role_power] │
│                                                                    │  • Splunk_Users      │
│                                                                    │    └──> [role_user]  │
│                                                                    │                      │
│   ┌─────────────────────────────────────────────────────────────┐  │                      │
│   │ FAILOVER & RESILIENCE CHAIN (authOrder in authentication.conf)│  │                      │
│   │                                                             │  │                      │
│   │  [Primary DC: dc01.corp (636)]                              │  │                      │
│   │         │ (If unreachable / timeout 15s)                    │  │                      │
│   │         ▼                                                   │  │                      │
│   │  [Secondary DC: dc02.corp (636)]                            │  │                      │
│   │         │ (If both DCs unreachable)                         │  │                      │
│   │         ▼                                                   │  │                      │
│   │  [Local Native Fallback: /opt/splunk/etc/passwd (admin)]    │──┘                      │
│   └─────────────────────────────────────────────────────────────┘                         │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. The 5-Step LDAP / Active Directory Authentication Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               THE 5-STEP LDAP / ACTIVE DIRECTORY AUTHENTICATION LIFECYCLE               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. USER LOGIN SUBMISSION                                                                │
│    • User enters username `jdoe` and corporate password in Splunk Web (port 8000).      │
│    • Splunk consults `authentication.conf` to identify the active auth strategy.        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. SERVICE ACCOUNT BIND (bindDN)                                                        │
│    • Splunk establishes an LDAPS connection to the Domain Controller on port 636.       │
│    • Binds using the dedicated service account: `svc_splunk` with encrypted password.   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. USER LOOKUP & ATTRIBUTE EXTRACTION                                                   │
│    • Splunk queries `userBaseDN` using `userBaseFilter`:                                │
│      `(&(objectClass=user)(sAMAccountName=jdoe))`                                       │
│    • Extracts user's Distinguished Name (`DN`), `mail`, and `displayName`.              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. USER CREDENTIAL BIND (Authentication)                                                │
│    • Splunk attempts a second LDAP bind directly as `jdoe`'s DN using supplied password.│
│    • If Active Directory accepts the bind $\rightarrow$ User is officially authenticated!│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. GROUP MEMBERSHIP QUERY & ROLE MAPPING                                                │
│    • Splunk queries `groupBaseDN` using `groupBaseFilter`:                              │
│      `(&(objectClass=group)(member=CN=jdoe,OU=Users,DC=corp,DC=internal))`             │
│    • Expands nested AD groups if `nestedGroups = 1`.                                    │
│    • Maps AD groups (`Splunk_Admins`) to local Splunk roles (`admin`) via `[roleMap]`. │
│    • User session is established; authorizations from `authorize.conf` are loaded!     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 Master Architecture of `authentication.conf` for LDAP

Splunk configures directory services in `$SPLUNK_HOME/etc/system/local/authentication.conf`.

#### Master Stanza: `[authentication]`
```ini
[authentication]
authType = LDAP
authSettings = ad_corp_primary, ad_corp_secondary
```

- **`authType = LDAP`**: Enables directory services (supports Active Directory, OpenLDAP, Red Hat Directory Server, Oracle Sun ONE).
- **`authSettings`**: Ordered, comma-delimited list of strategies. Splunk checks `ad_corp_primary` first; if it times out, it fails over to `ad_corp_secondary`.

---

### 4.2 Detailed LDAP Strategy Stanza Breakdown

Each strategy name referenced in `authSettings` has its own configuration stanza:

```ini
[ad_corp_primary]
# 1. Connection & Transport Security
host = dc01.corp.internal
port = 636
SSLEnabled = 1
sslVersions = tls1.2
anonymous_referrals = 0

# 2. Service Bind Account (Read-Only Service Account)
bindDN = CN=svc_splunk,OU=ServiceAccounts,DC=corp,DC=internal
bindDNpassword = $7$e4B8... (encrypted by Splunk)

# 3. User Resolution Settings
userBaseDN = OU=Employees,DC=corp,DC=internal
userBaseFilter = (objectClass=user)
userNameAttribute = sAMAccountName
realNameAttribute = displayName
emailAttribute = mail

# 4. Group Resolution & Nested Membership
groupBaseDN = OU=SecurityGroups,DC=corp,DC=internal
groupBaseFilter = (objectClass=group)
groupMemberAttribute = member
groupMappingAttribute = dn
nestedGroups = 1

# 5. Network Timeouts & Performance Caching
network_timeout = 15
connect_timeout = 5
```

#### Critical Setting Reference:
| Setting | Recommended Value (Active Directory) | Purpose & Architectural Function |
| :--- | :--- | :--- |
| `port` / `SSLEnabled` | `636` / `1` | Enforces LDAPS. **Never use plaintext port 389 in production!** |
| `anonymous_referrals` | `0` | Disables chasing external domain referrals; prevents massive login hangs across multi-forest AD architectures. |
| `userNameAttribute` | `sAMAccountName` | Standard AD login attribute (e.g. `jdoe`). For OpenLDAP, use `uid`. |
| `nestedGroups` | `1` | Enables recursive group expansion. If `jdoe` $\in$ `SOC_Tier1` $\in$ `Splunk_Analysts`, Splunk resolves both! |
| `network_timeout` | `15` (seconds) | Maximum wait time for LDAP socket response before initiating failover. |

---

### 4.3 Enterprise Group-to-Role Mapping (`[roleMap_<strategy>]`)

Splunk does not modify your corporate Active Directory. Instead, it matches AD group names to Splunk roles defined in `authorize.conf`:

```ini
[roleMap_ad_corp_primary]
admin = CN=Splunk_Enterprise_Admins,OU=Groups,DC=corp,DC=internal
power = CN=Splunk_Power_Users,OU=Groups,DC=corp,DC=internal; CN=SOC_Tier2_Analysts,OU=Groups,DC=corp,DC=internal
user = CN=Splunk_Standard_Users,OU=Groups,DC=corp,DC=internal; CN=All_IT_Staff,OU=Groups,DC=corp,DC=internal
soc_analyst_l1 = CN=SOC_Tier1_Triage,OU=Groups,DC=corp,DC=internal
```

> [!TIP]
> You can assign multiple AD groups to a single Splunk role using a semicolon (`;`).  
> A user belonging to multiple mapped groups automatically inherits the union of all capabilities and allowed indexes across those roles!

---

### 4.4 High-Availability Multi-Domain Failover & Fallback

In enterprise environments, Active Directory outages must never lock administrators out of their monitoring platform.

```ini
[authentication]
authType = LDAP
authSettings = ad_corp_primary, ad_corp_secondary

[ad_corp_primary]
host = dc01.na.corp.internal
port = 636
SSLEnabled = 1
...

[ad_corp_secondary]
host = dc02.eu.corp.internal
port = 636
SSLEnabled = 1
...
```

#### Native Fallback Mechanics:
When `authType = LDAP` is active:
1. Splunk checks the external directory servers first in the order specified by `authSettings`.
2. If an authentication attempt fails because the LDAP server is **completely unreachable / down**, Splunk falls back to local accounts stored in `/opt/splunk/etc/passwd`!
3. This guarantees that local accounts (such as emergency break-glass `admin`) can always log in during a corporate network partition or domain controller disaster.

---

### 4.5 Production LDAP Diagnostic Runbooks & CLI Troubleshooting

When users report "Invalid username or password" during an AD rollout, execute the following forensic commands:

```bash
# 1. Test raw network connectivity and TLS handshake on port 636
openssl s_client -connect dc01.corp.internal:636 -showcerts

# 2. Test LDAP configuration and service bind via Splunk CLI
/opt/splunk/bin/splunk test-ldap-connection -auth admin:SplunkAdmin123!

# 3. Inspect merged authentication settings using btool
/opt/splunk/bin/splunk btool authentication list --debug

# 4. Tail real-time authentication events in splunkd.log
tail -f /opt/splunk/var/log/splunk/splunkd.log | grep -iE "AuthenticationManagerLDAP|LDAPCommon"
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

### Pitfall 1: Leaving `anonymous_referrals = 1` Enabled
- **The Anti-Pattern:** Setting or leaving `anonymous_referrals = 1` in multi-domain or multi-forest Active Directory topologies.
- **The Failure:** When a search head queries an AD tree, the Domain Controller returns LDAP referral pointers (`chasing referrals`) to cross-domain forests that are blocked by enterprise firewalls. The search head hangs for 60 seconds per login, causing widespread HTTP 504 Gateway Timeouts in the Web UI!
- **The Fix:** Always explicitly set `anonymous_referrals = 0` in all LDAP strategy stanzas.

### Pitfall 2: Using Unencrypted Port 389 (Plaintext LDAP)
- **The Anti-Pattern:** Connecting to Active Directory on port 389 without SSL.
- **The Disaster:** User passwords and the service account `bindDNpassword` travel across the corporate LAN in unencrypted cleartext, easily captured by Wireshark, ARP poisoning, or compromised switches.
- **The Fix:** Always enforce `port = 636`, `SSLEnabled = 1`, and import your corporate Root/Intermediate CA certificates into `$SPLUNK_HOME/etc/auth/certs/` to validate the DC's TLS certificate.

### Pitfall 3: Broad `userBaseDN` & `groupBaseDN` Search Scopes
- **The Anti-Pattern:** Pointing `userBaseDN = DC=corp,DC=internal` at the root of a 200,000-user Active Directory forest.
- **The Failure:** Every single login initiates a recursive LDAP search across 200k objects, saturating Domain Controller CPU and causing Splunk login latencies of 10–20 seconds.
- **The Fix:** Scope `userBaseDN` and `groupBaseDN` strictly to dedicated Organizational Units (e.g. `OU=SplunkUsers,OU=Identities,DC=corp,DC=internal`).

---

## 🛠️ 6. Cyber Range Lab: Active Directory Forest Synchronization

Test your skills in the dedicated hands-on scenario:  
👉 **[Room P5-04: Active Directory Forest Synchronization](../Labs/Room_P5_04_LDAP_Active_Directory_Integration.md)**

### Mission Brief:
- **Scenario:** The enterprise is migrating from local native user management to corporate Microsoft Active Directory (`corp.internal`). You are tasked with configuring `authentication.conf` to connect to `dc01.corp.internal` via secure LDAPS (port 636), enabling nested group expansion, and mapping the AD security group `CN=SecOps_Tier2` to the Splunk `power` role.
- **Objective:**
  1. Construct the `[ad_corp]` strategy stanza in `authentication.conf`.
  2. Implement group mapping in `[roleMap_ad_corp]`.
  3. Validate connectivity using `splunk test-ldap-connection`.
  4. Fix an `anonymous_referrals` latency bug and capture the flag `FLAG{LDAP_P0RT_636_S3CUR3_AD_FEDERAT10N}`.

---

## 🧠 7. End-of-Chapter Self-Check Quiz

#### Q1: Which TCP port is universally utilized for encrypted LDAP over SSL/TLS (LDAPS) connections between Splunk and Active Directory?
- **A)** Port 389
- **B)** Port 636
- **C)** Port 8089
- **D)** Port 9997

#### Q2: If both primary and secondary LDAP domain controllers are down and unreachable, how does Splunk handle local accounts configured in `/opt/splunk/etc/passwd`?
- **A)** Splunk rejects all logins until LDAP services are restored.
- **B)** Splunk automatically falls back to native authentication, allowing local users (like emergency `admin`) to log in.
- **C)** Splunk deletes local users to prevent split-brain inconsistencies.
- **D)** Splunk switches to unencrypted guest mode.

#### Q3: Which setting in an LDAP strategy stanza enables Splunk to resolve users who belong to security groups that are themselves members of another security group?
- **A)** `recursiveGroupMap = 1`
- **B)** `nestedGroups = 1`
- **C)** `deepGroupSearch = true`
- **D)** `groupExpansion = all`

#### Q4: Why is it strongly recommended to set `anonymous_referrals = 0` when connecting Splunk to Microsoft Active Directory?
- **A)** It prevents Splunk from sending user passwords to the domain controller.
- **B)** It prevents the LDAP client from attempting to contact unreachable cross-domain forest references, which cause severe login hangs.
- **C)** It forces all users to use multi-factor authentication.
- **D)** It disables logging of failed login attempts in Active Directory.

#### Q5: What is the purpose of the `bindDN` and `bindDNpassword` settings in `authentication.conf`?
- **A)** They specify the master root password for the local Splunk Linux server.
- **B)** They configure an encrypted tunnel for forwarder-to-indexer data ingestion.
- **C)** They provide read-only credentials for Splunk to connect to Active Directory and search for user and group objects.
- **D)** They encrypt the TSIDX bucket lexicons on disk.

---

### 📝 Quiz Answer Key
- **Q1: B** — Port 636 is the standard port for LDAPS. Port 389 is plaintext LDAP.
- **Q2: B** — Splunk incorporates native fallback resilience: if external directory servers are unreachable, local accounts in `/etc/passwd` remain functional.
- **Q3: B** — `nestedGroups = 1` instructs Splunk to recursively traverse child-parent group hierarchies in AD.
- **Q4: B** — Disabling `anonymous_referrals` stops Splunk from getting stuck trying to resolve out-of-boundary domain referrals across corporate firewalls.
- **Q5: C** — `bindDN` is the dedicated read-only service account identity used by Splunk to query the directory service.
