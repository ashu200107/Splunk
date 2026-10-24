# 🎮 Room P5-04: Active Directory Forest Synchronization

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-04: Active Directory Forest Sync        ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: authentication.conf, LDAPS (636) & RBAC  💎 REWARD: 300 XP     │
│ ⏱️ ESTIMATED TIME: 45 Mins                         🛡️ CATEGORY: Security │
│ 🏆 PREREQUISITE: Room P5-01, P5-02 & P5-03                             │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Migration Operation — Enterprise Identity Federation!**  
> Your enterprise has mandated migrating all Splunk Search Heads from local native user accounts to centralized Microsoft Active Directory (`corp.internal`).  
>  
> The SOC and Threat Intelligence teams are currently unable to access the search heads because their AD security groups are not mapped to Splunk roles. Additionally, an existing test LDAP configuration is hanging for 45 seconds on every login due to unmanaged cross-forest referral chasing!  
>  
> Your mission as the Lead Splunk Identity Architect:  
> 1. Formulate a production-hardened `[ad_corp_primary]` LDAPS strategy on port 636.  
> 2. Implement recursive group mapping (`nestedGroups = 1`) for SOC analyst groups.  
> 3. Eliminate the referral latency timeout by disabling `anonymous_referrals`.  
> 4. Validate live directory communication and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          sh-fed-01 (10.10.30.50:8000 / :8089)                 │
│ • Domain Controller:    dc01.corp.internal (10.10.30.10:636 LDAPS)           │
│ • Service Account:      CN=svc_splunk,OU=Services,DC=corp,DC=internal        │
│ • Service Password:     LdapServiceBindPass!2026                             │
│ • User Base DN:         OU=Staff,DC=corp,DC=internal                         │
│ • Group Base DN:        OU=SecurityGroups,DC=corp,DC=internal                │
│ • Target Config File:   /opt/splunk/etc/system/local/authentication.conf     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Configuring the Master LDAPS Strategy (75 XP)

### 📖 Incident Details
Log in to the Search Head and create the primary Active Directory strategy in `/opt/splunk/etc/system/local/authentication.conf`:

```ini
[authentication]
authType = LDAP
authSettings = ad_corp_primary

[ad_corp_primary]
host = dc01.corp.internal
port = 636
SSLEnabled = 1
sslVersions = tls1.2
bindDN = CN=svc_splunk,OU=Services,DC=corp,DC=internal
bindDNpassword = LdapServiceBindPass!2026

userBaseDN = OU=Staff,DC=corp,DC=internal
userBaseFilter = (objectClass=user)
userNameAttribute = sAMAccountName
realNameAttribute = displayName
emailAttribute = mail

groupBaseDN = OU=SecurityGroups,DC=corp,DC=internal
groupBaseFilter = (objectClass=group)
groupMemberAttribute = member
groupMappingAttribute = dn
nestedGroups = 1
```

Upon saving and reloading, Splunk automatically encrypts `bindDNpassword` with a `$7$` reversible hash.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What Active Directory attribute is typically mapped to `userNameAttribute` in `authentication.conf` for Windows domain user logins?  
*(Answer Format: `**************`)*

<details>
<summary>💡 Need a Hint?</summary>
sAMAccountName
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>sAMAccountName</code> — Windows Active Directory uses sAMAccountName as the standard pre-Windows 2000 login name attribute.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{LDAPS_PORT_636_STRATEGY_CONFIGURED_SUCCESS}
```

---

## 🎯 TASK 2: Eliminating the 45-Second Login Freeze (75 XP)

### 📖 Incident Details
When users attempt to log in, the authentication subsystem hangs for 45 seconds before succeeding.  
Inspecting `/opt/splunk/var/log/splunk/splunkd.log`:

```text
10-17-2026 10:35:12.441 WARN  AuthenticationManagerLDAP - Chasing referral to ldap://forest-root.corp.internal:389/...
10-17-2026 10:35:37.442 ERROR LDAPCommon - Socket connection timed out while chasing referral.
```

The domain controller returned an external referral to an unreachable forest, and Splunk waited for the default timeout before giving up!

### 🛠️ Remediation
Add `anonymous_referrals = 0` to `[ad_corp_primary]`:

```ini
[ad_corp_primary]
anonymous_referrals = 0
network_timeout = 10
connect_timeout = 5
```

Reload auth:
```bash
/opt/splunk/bin/splunk reload auth -auth admin:SplunkAdmin123!
```
Logins now complete in under 200 milliseconds!

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which parameter must be set to `0` in `authentication.conf` to stop Splunk from chasing external Active Directory forest referrals?  
*(Answer Format: `*******************`)*

<details>
<summary>💡 Need a Hint?</summary>
anonymous_referrals
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>anonymous_referrals</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{ANONYMOUS_REFERRALS_DISABLED_ZERO_LATENCY}
```

---

## 🎯 TASK 3: Mapping Security Groups to Roles (75 XP)

### 📖 Tactical Objective
Map the following Active Directory Security Groups to Splunk roles:
1. `CN=Splunk_Enterprise_Admins,OU=SecurityGroups,DC=corp,DC=internal` $\rightarrow$ `admin`
2. `CN=SecOps_Tier2_Analysts,OU=SecurityGroups,DC=corp,DC=internal` $\rightarrow$ `power`
3. `CN=All_Corporate_Users,OU=SecurityGroups,DC=corp,DC=internal` $\rightarrow$ `user`

### 🛠️ Configuration Stanza
Add the role map stanza to `/opt/splunk/etc/system/local/authentication.conf`:

```ini
[roleMap_ad_corp_primary]
admin = CN=Splunk_Enterprise_Admins,OU=SecurityGroups,DC=corp,DC=internal
power = CN=SecOps_Tier2_Analysts,OU=SecurityGroups,DC=corp,DC=internal
user = CN=All_Corporate_Users,OU=SecurityGroups,DC=corp,DC=internal
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What is the exact naming convention for the stanza in `authentication.conf` that maps Active Directory groups to Splunk roles for a strategy named `ad_corp_primary`?  
*(Answer Format: `*************************`)*

<details>
<summary>💡 Need a Hint?</summary>
[roleMap_ad_corp_primary]
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>[roleMap_ad_corp_primary]</code> (or <code>roleMap_ad_corp_primary</code>)
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{DYNAMIC_GROUP_ROLE_MAPPING_ESTABLISHED}
```

---

## 🎯 TASK 4: Validating Directory Connectivity via CLI (75 XP)

### 📖 Tactical Objective
Verify the end-to-end directory handshake and user resolution without logging out of the Web UI.

### 🛠️ Verification Execution
Execute the dedicated Splunk diagnostic CLI command:

```bash
/opt/splunk/bin/splunk test-ldap-connection -auth admin:SplunkAdmin123!
```

Sample expected output:
```text
Connecting to ldaps://dc01.corp.internal:636 ... Connected.
Binding with bindDN: CN=svc_splunk,OU=Services,DC=corp,DC=internal ... Bind Successful.
Querying userBaseDN: OU=Staff,DC=corp,DC=internal ... Found 450 users.
Querying groupBaseDN: OU=SecurityGroups,DC=corp,DC=internal ... Found 28 groups.
LDAP configuration is VALID.
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What dedicated Splunk CLI utility validates the host, port, bindDN credentials, and base DN queries for active LDAP strategies?  
*(Answer Format: `****-****-**********`)*

<details>
<summary>💡 Need a Hint?</summary>
test-ldap-connection
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>test-ldap-connection</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{LDAP_P0RT_636_S3CUR3_AD_FEDERAT10N}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Always Use LDAPS (Port 636)**: Plaintext LDAP (port 389) sends passwords across the wire in cleartext; enforce TLS 1.2 on port 636.
2. **Disable Anonymous Referrals**: `anonymous_referrals = 0` is the single most critical setting to prevent multi-forest login delays and timeouts.
3. **Recursive Nested Groups**: Set `nestedGroups = 1` so that users inheriting parent AD security groups receive their full Splunk role assignments.
