# 🎮 Room P5-Capstone: Enterprise Security Architecture Gauntlet

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-CAPSTONE: Security Architecture Gauntlet ⭐ DIFFICULTY: Expert│
│ 🎯 TOPIC: RBAC, SAML SSO, S2S mTLS & CIS Hardening 💎 REWARD: 500 XP     │
│ ⏱️ ESTIMATED TIME: 60 Mins                         🛡️ CATEGORY: Security │
│ 🏆 PREREQUISITE: Rooms P5-01 through P5-07 (All Phase 5 Rooms)         │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Phase 5 Final Boss Challenge — Operation Ironclad Enclave!**  
> You have arrived at the high-security operations center of **Apex Financial Holdings**.  
> The enterprise infrastructure is facing an imminent regulatory shutdown from financial authorities unless a complete security architecture overhaul is completed before midnight:  
>  
> 1. Third-party auditors are inadvertently viewing raw cardholder records due to an empty-filter `OR` inheritance leak in `authorize.conf`.  
> 2. The Search Head must be transitioned to Okta SAML 2.0 SSO, replacing cleartext passwords with hardware-backed Web SSO.  
> 3. The data pipeline between forwarders and indexers on port 9997 must be upgraded to wire-speed Mutual TLS (mTLS) with strict certificate verification.  
> 4. All indexers must be hardened to CIS benchmarks: demoting root execution, terminating port 8000, and enabling automated `index=_audit` anomaly detection.  
>  
> Complete all 4 comprehensive tasks to secure the cluster and capture the Master Phase 5 Flag!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          sh-prod-01 (10.100.10.10:8000 / :8089)               │
│ • Indexer:              idx-prod-01 (10.100.10.20:9997 / :8089)              │
│ • Universal Forwarder:  uf-atm-01 (10.100.20.50)                             │
│ • Identity Provider:    https://apex-identity.okta.com/app/sso/saml          │
│ • Root CA Path:         /opt/splunk/etc/auth/certs/apexRootCA.pem            │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Sealing the Row-Level Data Leak in `authorize.conf` (125 XP)

### 📖 Incident Details
External compliance auditor `auditor_bob` was assigned role `role_pci_auditor`.  
The configuration stanza was written as:

```ini
[role_pci_auditor]
importRoles = user
srchIndexesAllowed = *
srchFilter = masked_card_number=true
```

Because `role_pci_auditor` imported the built-in `user` role (which has an empty `srchFilter`), Splunk evaluated:
$$\text{Filter} = (\text{masked\_card\_number=true}) \;\mathbf{OR}\; (\text{TRUE}) \equiv \mathbf{TRUE}$$
The auditor was able to search `index=payment_transactions` and read unmasked credit card PANs!

### 🛠️ Tactical Remediation
Edit `/opt/splunk/etc/system/local/authorize.conf`:

```ini
[role_pci_auditor]
# 1. Eliminate the empty filter inheritance
importRoles = 
capabilities = search; schedule_search; get_metadata

# 2. Clamp physical index access strictly to PCI compliance repositories
srchIndexesAllowed = pci_compliance; pci_audit
srchIndexesDefault = pci_compliance

# 3. Enforce airtight row-level filter
srchFilter = masked_card_number=true

# 4. Enforce resource caps
srchJobsQuota = 3
rtSrchJobsQuota = 0
srchDiskQuota = 500
srchTimeWin = 604800
```

Reload auth:
```bash
/opt/splunk/bin/splunk reload auth -auth admin:AdminPass123!
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the primary architectural reason why `role_pci_auditor` must NOT import the default `user` role when enforcing a restrictive `srchFilter`?  
*(Answer Format: `*************************************************`)*

<details>
<summary>💡 Need a Hint?</summary>
The empty filter in user nullifies restrictions via OR
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>The empty filter in user nullifies restrictions via OR</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{CAPSTONE_RBAC_SRCH_FILTER_LEAK_SEALED}
```

---

## 🎯 TASK 2: Federating Search Heads with SAML 2.0 Web SSO (125 XP)

### 📖 Tactical Objective
Deploy SAML 2.0 federation on `sh-prod-01`, mapping Okta's claims attribute to local Splunk roles.

### 🛠️ Configuration
Edit `/opt/splunk/etc/system/local/authentication.conf`:

```ini
[authentication]
authType = SAML
authSettings = saml

[saml]
entityId = splunk-apex-production
idpSSOUrl = https://apex-identity.okta.com/app/sso/saml
idpSLOUrl = https://apex-identity.okta.com/app/slo/saml
idpCertPath = $SPLUNK_HOME/etc/auth/idpCerts/okta_2026.pem
issuerId = http://www.okta.com/exk991288b

# Claims Mapping
attributeQueryResponse = true
role = http://schemas.microsoft.com/ws/2008/06/identity/claims/groups
mail = emailAddress
realName = displayName

# Role Mapping
roleMap_admin = Apex_Enterprise_Admins
roleMap_power = Apex_SOC_Tier2; Apex_Threat_Intel
roleMap_user = Apex_All_Staff
roleMap_pci_auditor = External_PCI_Auditors

# Security & Timing
signedAssertion = true
samlTimeSkew = 180
defaultRoleIfMissing = user
```

Reload authentication:
```bash
/opt/splunk/bin/splunk reload auth -auth admin:AdminPass123!
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the exact URL path on the Splunk Search Head that serves as the Assertion Consumer Service (ACS) endpoint receiving the incoming browser POST from the IdP?  
*(Answer Format: `/*********`)*

<details>
<summary>💡 Need a Hint?</summary>
/saml/acs
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>/saml/acs</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{CAPSTONE_SAML_OKTA_FEDERATION_ACTIVE}
```

---

## 🎯 TASK 3: Deploying Wire-Speed Mutual TLS on Port 9997 (125 XP)

### 📖 Tactical Objective
Enforce bidirectional cryptographic authentication across the entire forwarder-to-indexer data stream.

### 🛠️ Step 1: Indexer Hardening (`inputs.conf`)
On `idx-prod-01`, edit `/opt/splunk/etc/system/local/inputs.conf`:

```ini
[splunktcp-ssl:9997]
serverCert = /opt/splunk/etc/auth/certs/idx_server.pem
sslPassword = ApexVaultKey2026!
sslRootCAPath = /opt/splunk/etc/auth/certs/apexRootCA.pem
requireClientCert = true
sslVersions = tls1.2, tls1.3
```

### 🛠️ Step 2: Forwarder Hardening (`outputs.conf`)
On `uf-atm-01`, edit `/opt/splunkforwarder/etc/system/local/outputs.conf`:

```ini
[tcpout]
defaultGroup = secure_indexers

[tcpout:secure_indexers]
server = 10.100.10.20:9997
sslVersions = tls1.2, tls1.3
sslRootCAPath = /opt/splunk/etc/auth/certs/apexRootCA.pem
clientCert = /opt/splunk/etc/auth/certs/uf_client.pem
sslPassword = UfClientKeyPass2026!
sslVerifyServerCert = true
sslCommonNameToCheck = idx-prod-01.corp.internal
```

Restart both instances. Verify that the encrypted S2S cooked stream connects successfully and rogue forwarders are rejected with `Connection reset by peer`.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
When mutual TLS is active on port 9997, which configuration file on the Universal Forwarder specifies its identity certificate presented to the indexer?  
*(Answer Format: `************`)*

<details>
<summary>💡 Need a Hint?</summary>
outputs.conf
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>outputs.conf</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{CAPSTONE_MTLS_PORT_9997_AIRTIGHT}
```

---

## 🎯 TASK 4: CIS Operating System Hardening & Audit Forensics (125 XP)

### 📖 Tactical Objective
1. Migrate `idx-prod-01` off root execution to non-root user `splunk`.
2. Disable Splunk Web (`startwebserver = 0`) on `idx-prod-01`.
3. Suppress version disclosure banners on `sh-prod-01` (`support_info = false`).
4. Construct an automated audit search in `index=_audit` to detect unauthorized user escalation.

### 🛠️ Execution Commands
```bash
# 1. Non-root migration on Indexer
/opt/splunk/bin/splunk stop
chown -R splunk:splunk /opt/splunk
chmod 700 /opt/splunk
/opt/splunk/bin/splunk enable boot-start -user splunk --systemd-managed 1
systemctl start Splunkd

# 2. Disable Port 8000 on Indexer
echo -e "[settings]\nstartwebserver = 0" > /opt/splunk/etc/system/local/web.conf
/opt/splunk/bin/splunk restart

# 3. Verify closed socket
ss -tulpn | grep 8000
```

### 🛠️ Forensic SPL Alert
```spl
index=_audit action IN ("edit_user", "add_user") roles="*admin*"
| eval alert_time=strftime(_time, "%Y-%m-%d %H:%M:%S")
| table alert_time user action target_user roles
| sendalert pagerduty
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the final Master Flag recovered upon successfully completing Operation Ironclad Enclave?  
*(Answer Format: `FLAG{...}`)*

<details>
<summary>💡 Need a Hint?</summary>
FLAG{PH4S3_5_ENT3RPR1S3_S3CUR1TY_ARCH1T3CT_M4ST3R_9901}
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>FLAG{PH4S3_5_ENT3RPR1S3_S3CUR1TY_ARCH1T3CT_M4ST3R_9901}</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{PH4S3_5_ENT3RPR1S3_S3CUR1TY_ARCH1T3CT_M4ST3R_9901}
```

---

## 🏆 Capstone Victory & Arena Graduation

Congratulations! You have completed the **Phase 5 Capstone Challenge**.  
Your cluster is fully compliant with PCI-DSS 4.0 and CIS Benchmarks:
- Multi-tenant data segregation with zero leakage.
- Federated Identity with hardware MFA.
- Wire-speed mutual TLS (mTLS) protecting all ingested data.
- Hardened non-root host execution and continuous forensic audit surveillance.
