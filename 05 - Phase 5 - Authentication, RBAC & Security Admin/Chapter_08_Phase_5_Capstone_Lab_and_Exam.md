# 🏆 Chapter 08 (Phase 5): Phase 5 Capstone Lab & Master Milestone Assessment Exam

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 46 | **Milestone:** Phase 5 Graduation, Master Milestone Exam & Enterprise Security Rollout  
> **Current Rank:** Master Splunk Architect (8,250 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_08_Phase_5_Capstone_Lab_and_Exam.md`  
> **Interactive Cyber Range Capstone Room:** [Room P5-Capstone: Enterprise Security Architecture Gauntlet](../Labs/Room_P5_Capstone_Enterprise_Security_Architecture.md) `[500 XP]`

---

## 🏰 1. The Capstone Narrative: Operation Ironclad Enclave

You are the Chief Security Architect for **Apex Financial Holdings**, a global fintech conglomerate operating under strict PCI-DSS 4.0, SOC2 Type II, and GDPR compliance mandates.

### The Emergency Directive:
The Chief Information Security Officer (CISO) has initiated **Operation Ironclad Enclave**:
1. **Multi-Tenant Row Isolation:** All third-party payment processors must be segregated using strict `srchFilter` and `srchIndexesAllowed` rules with zero possibility of `OR` inheritance bypasses.
2. **Federated Identity:** Decommission all individual local passwords and federate the Search Head cluster with corporate Microsoft Entra ID (Azure AD) via SAML 2.0 with hardware FIDO2 MFA.
3. **Wire-Speed Mutual TLS (mTLS):** Encrypt all forwarder-to-indexer S2S communications on port 9997 using the company's internal Root CA, mandating bidirectional client certificate verification.
4. **CIS Operating System Hardening:** Eliminate root daemons, shut down port 8000 on indexers, suppress web banners, and activate real-time audit alerting in `index=_audit`.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│               OPERATION IRONCLAD ENCLAVE: END-TO-END SECURITY ARCHITECTURE                │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   IDENTITIES (Entra ID SAML 2.0)                 SPLUNK SEARCH HEAD (sh-prod-01)          │
│   ┌─────────────────────────────┐                ┌────────────────────────────────────┐   │
│   │ Azure AD / Entra ID         │                │ • SAML 2.0 ACS: :8000/saml/acs     │   │
│   │ • Group: SecOps_Tier2       ├─ SAMLResponse ─┤ • JIT User Provisioning            │   │
│   │ • Group: Payment_Auditors   │  (Port 8000)   │ • authorize.conf Role Isolation:   │   │
│   │ • Cert: entra_id_pub.pem    │                │   roleMap_pci_auditor:             │   │
│   └─────────────────────────────┘                │     srchIndexesAllowed = pci_*     │   │
│                                                  │     srchFilter = masked=true       │   │
│                                                  │ • CIS: support_info = false        │   │
│                                                  └─────────────────┬──────────────────┘   │
│                                                                    │                      │
│   INGESTION & MTLS (Port 9997)                                     │ REST Port 8089 (TLS) │
│   ┌─────────────────────────────┐                                  │                      │
│   │ Universal Forwarder (UF)    │                                  ▼                      │
│   │ • clientCert: uf_client.pem │     Mutual TLS (Port 9997)     ┌────────────────────┐   │
│   │ • outputs.conf:             ├──────────────────────────────> │ Splunk Indexer     │   │
│   │   sslVerifyServerCert=true  │   requireClientCert = true     │ (idx-prod-01)      │   │
│   │   sslCommonNameToCheck      │   sslRootCAPath = rootCA.pem   ├────────────────────┤   │
│   └─────────────────────────────┘                                │ • startwebserver=0 │   │
│                                                                  │ • user: splunk     │   │
│                                                                  │ • index=_audit     │   │
│                                                                  └────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. Master Synthesis Checklist for Phase 5

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     PHASE 5 PRODUCTION ARCHITECTURE CHECKLIST                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [✓] 1. RBAC & authorize.conf                                                            │
│     • Custom roles decoupled from built-in roles with empty filters to prevent leaks.   │
│     • Explicit srchIndexesAllowed; never use unrestricted '*' on tenant roles.          │
│     • Strict search limits: srchJobsQuota, srchTimeWin, and rtSrchJobsQuota = 0.        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [✓] 2. Native Auth & Password Governance                                                │
│     • authentication.conf [password_rules]: length 14, complexity, history 24.          │
│     • Account lockout protection: lockoutThreshold = 5, lockoutDurationMins = 30.       │
│     • tokens.conf: JWT bearer token authentication enabled for CI/CD pipelines.         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [✓] 3. Directory Services & SSO Federation                                              │
│     • LDAPS on port 636 with anonymous_referrals = 0 and nestedGroups = 1.              │
│     • SAML 2.0 Web SSO with Okta / Entra ID, ACS URL, and signed assertions.            │
│     • Dynamic group-to-role mappings and clock skew tolerance (samlTimeSkew = 180).     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [✓] 4. Cryptographic Wire Encryption (TLS/mTLS)                                         │
│     • Commercial / Public CA for Web UI HTTPS (port 8000) with HSTS enabled.            │
│     • Enterprise Private CA for S2S Port 9997 with mutual client certificates.          │
│     • Strict server validation: sslVerifyServerCert = true & sslCommonNameToCheck.      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [✓] 5. System Hardening & Forensic Auditing                                             │
│     • Non-root daemon execution under dedicated `splunk:splunk` service account.        │
│     • Port 8000 disabled on Indexers and Forwarders (startwebserver = 0).               │
│     • Continuous compliance surveillance using index=_audit query recipes.              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 4. Phase 5 Master Milestone Assessment Exam (10 Comprehensive Scenarios)

### Scenario 1: The Inherited Filter Leak
**Problem:** A security analyst is assigned two roles: `role_soc_level1` (which has `srchFilter = vendor=cisco`) and `role_general_staff` (which has no `srchFilter` defined). When searching `index=network`, the analyst is able to view Palo Alto and Fortinet firewall logs.  
**Analysis & Solution:**  
In Splunk, inherited search filters are combined across roles using **`OR` logic**:
$$\text{Filter} = (\text{vendor=cisco}) \;\mathbf{OR}\; (\text{TRUE}) \equiv \mathbf{TRUE}$$
Because `role_general_staff` has an empty filter, it evaluates to `TRUE`, completely nullifying the restriction. To fix this, create a clean base role with no empty search filters, or ensure that any role assigned to restricted users includes an explicit search filter.

---

### Scenario 2: Index Scoping with Wildcards
**Problem:** An auditor assigned a role with `srchIndexesAllowed = *` attempts to execute:  
`index=_audit action=login_attempt`  
and receives the error: `Permission denied for index=_audit`. Why?  
**Analysis & Solution:**  
In Splunk, the wildcard asterisk (`*`) in `srchIndexesAllowed` matches **all standard public indexes**, but explicitly **excludes all internal system indexes starting with an underscore** (`_*`). To grant access to audit logs, `_audit` must be explicitly listed:  
`srchIndexesAllowed = *; _audit`

---

### Scenario 3: Emergency Break-Glass Local Access During SSO Outage
**Problem:** The corporate Okta Identity Provider experiences a global cloud outage. The Search Head has `authType = SAML`. How can the Lead Splunk Administrator log in to triage scheduled alerts?  
**Analysis & Solution:**  
Splunk supports native fallback for local administrative accounts. The admin navigates directly to the local bypass URL:  
`https://<splunk_search_head>:8000/en-US/account/login?loginType=splunk`  
This presents the native Splunk authentication dialog, allowing the local `admin` account stored in `/opt/splunk/etc/passwd` to authenticate successfully even when external SSO is completely down!

---

### Scenario 4: LDAP Multi-Forest Referral Timeout
**Problem:** Users experience a 60-second delay every time they log in to Splunk Web using Active Directory. The `splunkd.log` shows: `Socket connection timed out while chasing referral`.  
**Analysis & Solution:**  
Active Directory domain controllers return LDAP referrals to cross-forest domains that are blocked by internal network firewalls. By default, Splunk attempts to contact these referred domains. Setting:  
`anonymous_referrals = 0`  
in the strategy stanza of `authentication.conf` forces Splunk to ignore external referrals, instantly reducing login latency to under 200 ms.

---

### Scenario 5: SAML Clock Drift Rejection
**Problem:** Following a host migration of the Search Head virtual machine, all SAML logins fail with: `Assertion is not yet valid`. System clocks on both machines are synchronized to NTP, but the VM clock is 45 seconds ahead of the IdP clock.  
**Analysis & Solution:**  
SAML assertions specify a strict `<Conditions NotBefore="...">` timestamp. If the Search Head receives the assertion before the `NotBefore` instant according to its local clock, it rejects the assertion as premature. Configuring:  
`samlTimeSkew = 180`  
in `[saml]` inside `authentication.conf` provides a 3-minute grace buffer, resolving virtualized clock drift.

---

### Scenario 6: The Man-in-the-Middle Forwarder Threat
**Problem:** An attacker places a rogue laptop on the corporate network and configures an indexer listening on port 9997 with a self-signed certificate. Corporate Universal Forwarders immediately connect to the attacker's laptop and stream sensitive financial logs. What setting was missing on the forwarders?  
**Analysis & Solution:**  
The forwarders had `sslVerifyServerCert = false` (or omitted) in `outputs.conf`. When this setting is missing or false, forwarders do NOT validate the certificate presented by the indexer. To eliminate this attack:
1. Set `sslVerifyServerCert = true`.
2. Configure `sslRootCAPath = /opt/splunk/etc/auth/certs/corpRootCA.pem`.
3. Set `sslCommonNameToCheck = idx*.corp.internal`.

---

### Scenario 7: Mutual TLS Forwarder Rejection
**Problem:** An administrator enables `requireClientCert = true` on the indexer's `inputs.conf`. Immediately, 500 forwarders stop sending data, and indexer logs show `SSL alert number 42: bad certificate`.  
**Analysis & Solution:**  
The forwarders were configured for one-way TLS; they lacked a valid `clientCert` and private key signed by the Root CA specified in the indexer's `sslRootCAPath`. Mutual TLS requires **both** sides to present certificates. The administrator must deploy client certificate bundles (`clientCert = uf_client.pem`) to all forwarders via the Deployment Server before enabling `requireClientCert = true` on indexers.

---

### Scenario 8: Low-Port Binding Without Root
**Problem:** A security policy strictly prohibits running Splunk as `root`. However, a Heavy Forwarder must listen directly on UDP port 514 to receive high-speed firewall syslog data. Starting `splunkd` as user `splunk` throws: `Permission denied: cannot bind to port 514`.  
**Analysis & Solution:**  
Linux restricts ports $< 1024$ to root by default. Rather than running the entire daemon as root, the administrator grants the specific Linux kernel capability to the `splunkd` binary:  
```bash
setcap 'cap_net_bind_service=+ep' /opt/splunk/bin/splunkd
```
Alternatively, configure Splunk to listen on an unprivileged port (e.g. 1514) and redirect traffic using `iptables` or `firewalld`:  
```bash
firewall-cmd --add-forward-port=port=514:proto=udp:toport=1514
```

---

### Scenario 9: Attack Surface Minimization on Tiered Nodes
**Problem:** A security audit discovers that 24 dedicated Indexers and 6 Heavy Forwarders are exposing port 8000 on the network, running unauthenticated Splunk Web instances.  
**Analysis & Solution:**  
Splunk Web is only required on dedicated Search Heads. To close the attack surface on all Indexers and Forwarders, deploy a configuration app containing:  
File: `$SPLUNK_HOME/etc/apps/org_all_indexer_hardening/local/web.conf`  
```ini
[settings]
startwebserver = 0
```
Restart `splunkd`. Port 8000 is completely terminated, saving system memory and removing the attack vector.

---

### Scenario 10: Forensically Catching Rogue Configuration Edits
**Problem:** A user account was secretly granted the `can_delete` capability at 02:00 AM. Write an exact SPL search to identify who granted the capability, the target user, and the exact timestamp.  
**Analysis & Solution:**  
Execute against `index=_audit`:  
```spl
index=_audit action IN ("edit_user", "add_user") roles="*can_delete*"
| table _time user action target_user roles
| rename user as "Perpetrator", target_user as "Compromised_Account"
```
This inspects the immutable audit log and pinpoints the administrative identity that authorized the destructive permission.

---

## 🛠️ 5. Capstone Cyber Range Lab: Enterprise Security Architecture Gauntlet

Test your cumulative knowledge in the ultimate hands-on challenge:  
👉 **[Room P5-Capstone: Enterprise Security Architecture Gauntlet](../Labs/Room_P5_Capstone_Enterprise_Security_Architecture.md)**

- **XP Reward:** `500 XP`
- **Estimated Time:** `60 Minutes`
- **Difficulty:** `Expert / Master Architect`
- **Final Master Flag:** `FLAG{PH4S3_5_ENT3RPR1S3_S3CUR1TY_ARCH1T3CT_M4ST3R_9901}`

---

## 🎓 6. Phase 5 Graduation & Promotion Ceremony

```text
╔══════════════════════════════════════════════════════════════════════════════════╗
║               OFFICIAL SPLUNK ENTERPRISE OPERATOR PROMOTION                      ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║   OPERATOR:          venom                                                       ║
║   PREVIOUS RANK:     Master Splunk Architect (6,550 XP)                          ║
║   XP EARNED (PH 5):  +2,450 XP (8 Cyber Range Rooms + Master Milestone Exam)     ║
║   TOTAL XP:          9,000 XP                                                    ║
║                                                                                  ║
║   NEW PROMOTED RANK: 🎖️ SPLUNK SECURITY & CRYPTOGRAPHIC ARCHITECT 🎖️             ║
║                                                                                  ║
║   ACCREDITATIONS:                                                                ║
║   • Mastered authorize.conf RBAC, Inheritance & srchFilter Row-Level Scoping     ║
║   • Mastered Native /etc/passwd Governance, Passphrase Rules & REST JWT Tokens   ║
║   • Mastered Active Directory LDAPS Port 636 & Recursive Nested Group Mapping    ║
║   • Mastered SAML 2.0 Web SSO Identity Federation (Okta / Azure AD / Entra ID)   ║
║   • Mastered Three-Tier End-to-End TLS & Wire-Speed S2S Mutual TLS (mTLS 9997)   ║
║   • Mastered CIS Benchmarks, Non-Root Linux Execution & index=_audit Forensics   ║
║                                                                                  ║
║   NEXT UNLOCKED PHASE: Phase 6 — Centralized Deployment Management (Days 47–53)  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```
