# 🛡️ Chapter 05 (Phase 5): Enterprise SAML 2.0 SSO Federation — Okta, Microsoft Entra ID & Assertion Governance

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 43 | **Milestone:** Enterprise Single Sign-On (SSO), SAML 2.0 Web Browser Flow & IdP Assertion Parsing  
> **Current Rank:** Master Splunk Architect (7,300 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_05_SAML_SSO_Federation.md`  
> **Interactive Cyber Range Lab:** [Room P5-05: The SAML Identity Federation Breakout](../Labs/Room_P5_05_SAML_SSO_Federation.md) `[300 XP]`

---

## 🏰 1. The Everyday Analogy: The International Airport & The Cryptographic e-Passport

Imagine an international airport border crossing:

- **The Problem with Local Checkpoints (Password Fatigue):**  
  If every airline lounge, duty-free shop, security gate, and boarding bridge required you to create and remember a separate username and password, passengers would spend hours resetting passwords, writing them on sticky notes, or missing flights.
- **The Identity Provider (IdP — The Government Passport Office):**  
  Instead, your national government (Okta / Microsoft Entra ID / PingFederate) verifies your biometric identity once and issues you an official, cryptographically signed electronic passport.
- **The Service Provider (SP — The Splunk Search Head):**  
  When you arrive at the VIP airline lounge (Splunk Web UI), the lounge clerk doesn't ask for your personal email password. Instead:
  1. The lounge clerk redirects you to the government border scanner (**AuthnRequest**).
  2. You scan your passport and facial recognition at the government terminal (**MFA Authentication at IdP**).
  3. The government terminal prints a tamper-evident, cryptographically sealed digital manifest (**SAML 2.0 Response with Assertion XML**) signed by the government's private key.
  4. You present this sealed manifest to the lounge receptionist's reader (**Assertion Consumer Service / ACS URL**).
  5. The lounge verifies the signature using the government's public certificate, reads your clearance tag (`role=VIP_Platinum`), and instantly welcomes you in!

In Splunk Enterprise, **SAML 2.0 Federation** offloads credential management, enforces hardware token MFA (FIDO2/YubiKey), and provisions users Just-In-Time (JIT) with zero passwords stored on the Search Head.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│              SAML 2.0 SP-INITIATED SSO FLOW & ATTRIBUTE EXTRACTION ENGINE                 │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   [1. Browse to Splunk Web]       [2. 302 Redirect with AuthnRequest XML]                 │
│         (Port 8000)               ┌──────────────────────────────────────────────────┐    │
│              │                    │ • IssueInstant, AssertionConsumerServiceURL (ACS)│    │
│              ▼                    └─────────────────────────┬────────────────────────┘    │
│      ┌───────────────┐                                      ▼                             │
│      │  USER BROWSER │ ───────────────────────────> ┌───────────────┐                     │
│      │  (Client End) │                              │  IDENTITY IDP  │ (Okta / Entra ID)   │
│      └───────┬───────┘                              │  (Port 443)    │                     │
│              ▲                                      └───────┬───────┘                     │
│              │                                              │                             │
│              │ [4. POST Signed SAMLResponse via Browser]    │ [3. MFA & Credentials]      │
│              │    • Base64 Encoded Assertion XML            │    • User Authenticates     │
│              │    • Signed with IdP Private Key             │    • Embeds SAML Attributes:│
│              │    • InResponseTo validation nonce           │       role, mail, realName  │
│              │                                              ▼                             │
│              └──────────────────────────────────────────────┘                             │
│                                      │                                                    │
│                                      ▼ [5. Assertion Consumer Service (ACS)]              │
│                       ┌──────────────────────────────┐                                    │
│                       │   SPLUNK SEARCH HEAD (SP)    │                                    │
│                       ├──────────────────────────────┤                                    │
│                       │ • Verifies IdP x509 Cert     │                                    │
│                       │ • Parses <saml2:Attribute>   │                                    │
│                       │ • Maps Groups to Roles:      │                                    │
│                       │   'Okta_SOC' ──> [role_power]│                                    │
│                       │ • Just-In-Time (JIT) Session │                                    │
│                       └──────────────────────────────┘                                    │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. The 5-Step SAML 2.0 Federation Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    THE 5-STEP SAML 2.0 FEDERATION LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. SP-INITIATED LOGIN REQUEST                                                           │
│    • User navigates to `https://splunk-sh01.corp.internal:8000`.                        │
│    • Splunk detects `authType = SAML` and generates a signed `AuthnRequest` XML.        │
│    • Returns HTTP 302 Redirect to IdP Single Sign-On URL (e.g. `okta.com/app/sso/saml`).│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. IDENTITY PROVIDER AUTHENTICATION & MFA                                               │
│    • User inputs corporate credentials and completes Push/FIDO2 MFA challenge at IdP.   │
│    • IdP validates user status, conditional access policies, and group memberships.     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. SAML ASSERTION CREATION & CRYPTOGRAPHIC SIGNING                                      │
│    • IdP constructs XML `<saml2:Assertion>` containing:                                 │
│      - `<saml2:Subject>`: User's Principal Name (e.g. `alex@corp.com`).                 │
│      - `<saml2:AttributeStatement>`: Group memberships, email, realName.                │
│    • IdP digitally signs the XML payload using its private cryptographic key.           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. HTTP POST TO ASSERTION CONSUMER SERVICE (ACS)                                        │
│    • IdP delivers an auto-submitting HTML form to user's browser with SAMLResponse.    │
│    • Browser POSTs base64 payload to Splunk: `https://splunk-sh01:8000/saml/acs`.       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. ASSERTION VALIDATION, JIT PROVISIONING & SESSION DISPATCH                            │
│    • Splunk validates signature against stored IdP public certificate (`idpCert.pem`).  │
│    • Verifies timestamps (`NotBefore`, `NotOnOrAfter`) and audience restriction.        │
│    • Maps incoming groups to local Splunk roles defined in `[saml]`.                    │
│    • Provisions user session in memory; search head dashboard renders!                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 Master Architecture of `authentication.conf` for SAML

In Splunk Enterprise, SAML federation is managed in `$SPLUNK_HOME/etc/system/local/authentication.conf`.

#### Master Stanza: `[authentication]`
```ini
[authentication]
authType = SAML
authSettings = saml
```

#### Detailed SAML Configuration Stanza: `[saml]`
```ini
[saml]
# 1. Identity Provider (IdP) Endpoints & Metadata
idpSSOUrl = https://corp-identity.okta.com/app/splunk/sso/saml
idpSLOUrl = https://corp-identity.okta.com/app/splunk/slo/saml
idpCertPath = $SPLUNK_HOME/etc/auth/idpCerts/okta_signing_cert.pem
issuerId = http://www.okta.com/exk9a8b7c6d5e4f3g2h1

# 2. Service Provider (SP - Splunk) Identification
entityId = splunk-shc-production
redirectPort = 8000
redirectAfterLogoutToUrl = https://corp-identity.okta.com

# 3. Attribute Statement Field Mapping
attributeQueryResponse = true
role = http://schemas.microsoft.com/ws/2008/06/identity/claims/groups
realName = displayName
mail = emailAddress

# 4. Cryptographic Assertion Signature Verification
signAuthnRequest = false
signedAssertion = true

# 5. Clock Skew & Security Horizons (in seconds)
samlTimeSkew = 120
```

---

### 4.2 Critical SAML Parameters Reference

| Setting Name | Production Value | Exact Architectural Function |
| :--- | :--- | :--- |
| **`entityId`** | `splunk-shc-production` | Unique URI/URN identifying this Splunk cluster to the IdP. Must match exactly in IdP settings! |
| **`idpSSOUrl`** | `https://<idp>/sso/saml` | The HTTP-Redirect endpoint where unauthenticated users are sent. |
| **`idpCertPath`** | `/opt/splunk/etc/auth/idpCerts/cert.pem` | Public X.509 certificate used to cryptographically verify the IdP's digital signature. |
| **`samlTimeSkew`**| `120` to `300` (seconds) | Tolerable time drift between Splunk host clock and IdP NTP clock. |
| **`role`** | `role` or claims URL | The XML attribute name inside `<saml2:AttributeStatement>` carrying corporate security groups. |
| **`signedAssertion`**| `true` | Mandates that the `<Assertion>` element itself be digitally signed (prevents XML signature wrapping attacks). |

---

### 4.3 SAML Group-to-Role Mapping Syntax

Unlike LDAP which uses a separate `[roleMap_<strategy>]` stanza, SAML maps groups directly inside the `[saml]` stanza or through dedicated role mappings:

```ini
[saml]
...
# Syntax: roleMap_<SplunkRole> = <IdP_Group_1>; <IdP_Group_2>
roleMap_admin = Splunk_Global_Admins; Cloud_Infra_Leads
roleMap_power = SOC_Tier2_Analysts; Detection_Engineers
roleMap_user = All_Enterprise_Employees; Contractors_Auditors
roleMap_soc_analyst_l1 = SOC_Tier1_Triagers
```

#### Default Fallback Role:
If an authenticated IdP user does not belong to any mapped group, you can specify a safe sandbox fallback:
```ini
[saml]
defaultRoleIfMissing = user
```
> [!WARNING]
> Setting `defaultRoleIfMissing = admin` or `power` is an extreme vulnerability! Always default to `user` or leave empty to deny access to unmapped users.

---

### 4.4 Metadata Exchange: SP Metadata vs. IdP Metadata

SAML relies on an initial mutual exchange of XML metadata documents:

1. **Splunk's SP Metadata (`spmetadata.xml`):**  
   Exported from Splunk Web (`Settings -> Users -> Authentication Methods -> SAML Configuration -> Export SP Metadata`) or retrieved via:
   ```text
   https://<splunk_search_head>:8000/saml/spmetadata
   ```
   Provides the IdP with Splunk's:
   - **Assertion Consumer Service (ACS) URL:** `https://splunk-sh:8000/saml/acs`
   - **Single Logout (SLO) URL:** `https://splunk-sh:8000/saml/logout`
   - **Audience / EntityID:** `splunk-shc-production`
2. **IdP Metadata (`idp_metadata.xml`):**  
   Provided by Okta, Azure AD, or PingFederate. Splunk parses this XML to auto-populate `idpSSOUrl`, `issuerId`, and extracts the public X.509 signing certificate into `idpCert.pem`.

---

### 4.5 Forensic Troubleshooting: The SAML Assertion Triage Runbook

When users encounter "SAML Login Failed" or an infinite redirect loop, execute these diagnostics:

```bash
# 1. Search internal splunkd logs for SAML assertion parser errors
index=_internal sourcetype=splunkd (SAMLCommon OR AuthenticationManagerSAML)
| table _time log_level message

# 2. Check for Clock Skew violations
# Look for: "Assertion is not yet valid" or "Assertion has expired"
# Fix: Sync NTP on Search Head: ntpdate -u pool.ntp.org

# 3. Inspect raw base64 SAMLResponse using Browser Developer Tools (Network Tab)
# Copy the SAMLResponse parameter from the POST to /saml/acs, then decode:
echo "<BASE64_STRING>" | base64 -d | xmllint --format -
```

#### Common SAML Error Codes & Cures:
- **`Signature verification failed`**: The IdP rotated its SAML signing certificate, but Splunk's `idpCertPath` still points to the expired certificate!
- **`Audience restriction mismatch`**: Splunk's `entityId` in `authentication.conf` does not match the "Audience" configured in Okta/Azure AD.
- **`No valid roles mapped for user`**: The user authenticated, but their IdP group attribute does not match any `roleMap_<role>` entry.

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

### Pitfall 1: Expired IdP Signing Certificates (The Monday Morning Outage)
- **The Anti-Pattern:** Forgetting that IdP SAML certificates expire every 1, 2, or 3 years.
- **The Disaster:** Over the weekend, Azure AD or Okta rolls over to a newly generated certificate. On Monday at 9:00 AM, all 5,000 employees are locked out with: `Signature verification failed`!
- **The Fix:** Set calendar alerts 60 days before IdP cert expiry. Keep break-glass local accounts active (`admin` on native auth) so administrators can access the system to upload the new certificate.

### Pitfall 2: Neglecting Clock Skew in Virtualized Environments
- **The Anti-Pattern:** Allowing Search Head VM hypervisors to experience NTP time drift (> 2 minutes).
- **The Failure:** SAML assertions include `<Conditions NotBefore="..." NotOnOrAfter="...">`. If Splunk's system clock is 2 minutes fast, Splunk thinks the assertion was issued in the future and rejects it immediately.
- **The Fix:** Enforce chrony/NTP synchronization and set `samlTimeSkew = 180` in `authentication.conf` as a buffer.

### Pitfall 3: Broken Single Logout (SLO) Infinite Redirect Loops
- **The Anti-Pattern:** Misconfiguring `redirectAfterLogoutToUrl` to point back to Splunk Web instead of the IdP portal.
- **The Failure:** When a user clicks "Logout", Splunk terminates the local session and redirects them back to port 8000. Port 8000 sees an unauthenticated user, immediately fires an `AuthnRequest` to Okta, Okta sees an active SSO cookie, and automatically logs them back in! The user cannot log out!
- **The Fix:** Set `redirectAfterLogoutToUrl` to the IdP's explicit logout landing page or corporate intranet portal.

---

## 🛠️ 6. Cyber Range Lab: The SAML Identity Federation Breakout

Test your skills in the dedicated hands-on scenario:  
👉 **[Room P5-05: The SAML Identity Federation Breakout](../Labs/Room_P5_05_SAML_SSO_Federation.md)**

### Mission Brief:
- **Scenario:** The enterprise has rolled out Okta SAML 2.0 SSO to the central Search Head. However, after deployment, all Tier-2 SOC analysts are receiving "Access Denied: No roles mapped", and logins fail with cryptographic signature errors following an emergency IdP certificate rollover!
- **Objective:**
  1. Inspect the decrypted SAML assertion XML in `/tmp/failed_saml_post.xml`.
  2. Identify the role attribute name mismatch (`groups` vs `role`).
  3. Replace the stale IdP signing certificate with the updated `okta_2026_pubkey.pem`.
  4. Fix clock skew rejection and capture the flag `FLAG{SAML2_0KT4_AS5ERT1ON_S1GN3D_V3R1F13D}`.

---

## 🧠 7. End-of-Chapter Self-Check Quiz

#### Q1: In SAML 2.0 terminology, what role does Splunk Enterprise perform when federated with Okta or Microsoft Entra ID?
- **A)** Identity Provider (IdP)
- **B)** Assertion Signer
- **C)** Service Provider (SP)
- **D)** Certificate Authority (CA)

#### Q2: What is the purpose of the Assertion Consumer Service (ACS) URL in Splunk?
- **A)** It is the internal port where forwarders send raw syslog events.
- **B)** It is the HTTP endpoint (`/saml/acs`) where the user's browser POSTs the signed SAML assertion XML.
- **C)** It is the background script that deletes expired user sessions.
- **D)** It is the database table where user passwords are encrypted.

#### Q3: Which configuration parameter in `authentication.conf` tolerates minor clock discrepancies between the Splunk Search Head and the Identity Provider?
- **A)** `clockDriftMargin`
- **B)** `samlTimeSkew`
- **C)** `ntpToleranceSeconds`
- **D)** `assertionGracePeriod`

#### Q4: If an IdP issues a SAML assertion with the group claim `SOC_Leads`, which setting in `[saml]` assigns those users to the Splunk `power` role?
- **A)** `roleMap_power = SOC_Leads`
- **B)** `mapGroup_SOC_Leads = power`
- **C)** `role_power = group(SOC_Leads)`
- **D)** `samlRoles = SOC_Leads:power`

#### Q5: What security vulnerability arises if an administrator sets `defaultRoleIfMissing = admin` in `[saml]`?
- **A)** The IdP certificate is revoked immediately.
- **B)** Any authenticated corporate employee who has NO assigned Splunk security group automatically receives full administrative control over the cluster.
- **C)** Splunkd crashes due to an out-of-memory error.
- **D)** Real-time searches are disabled cluster-wide.

---

### 📝 Quiz Answer Key
- **Q1: C** — Splunk is the Service Provider (SP) consuming identities from the IdP.
- **Q2: B** — The ACS URL (`https://<splunk>:8000/saml/acs`) receives and processes the incoming signed SAMLResponse.
- **Q3: B** — `samlTimeSkew` (configured in seconds) offsets clock drifts.
- **Q4: A** — `roleMap_<SplunkRole> = <IdP_Group>` is the standard syntax.
- **Q5: B** — Any unmapped user authenticating through SSO would automatically be elevated to full `admin` privileges.
