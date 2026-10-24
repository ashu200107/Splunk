# 🎮 Room P5-05: The SAML Identity Federation Breakout

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-05: The SAML Identity Federation        ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: SAML 2.0, Okta / Entra ID SSO & Claims   💎 REWARD: 300 XP     │
│ ⏱️ ESTIMATED TIME: 45 Mins                         🛡️ CATEGORY: Security │
│ 🏆 PREREQUISITE: Room P5-01 through Room P5-04                         │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Emergency Incident — Global SSO Authentication Blackout!**  
> At 08:30 this morning, your enterprise switched its central Splunk Search Head authentication from native accounts to Okta SAML 2.0 SSO.  
>  
> Immediately, all 250 SOC security analysts and incident responders were locked out! The Splunk Web UI displays a cryptic error: `SAML Login Failed: Signature verification failure and unmapped role claim`.  
>  
> Your mission as the Lead Splunk Identity Architect:  
> 1. Inspect the captured raw SAML assertion XML in `/tmp/failed_saml_post.xml`.  
> 2. Fix the attribute mapping mismatch between Okta's claims schema and `authentication.conf`.  
> 3. Replace the stale IdP signing certificate with the renewed public certificate.  
> 4. Adjust clock skew tolerances and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          sh-saml-01 (10.200.10.40:8000)                       │
│ • Okta IdP Issuer:      http://www.okta.com/exk891023                        │
│ • ACS Endpoint:         https://sh-saml-01:8000/saml/acs                     │
│ • Config File:          /opt/splunk/etc/system/local/authentication.conf     │
│ • IdP Certificates:     /opt/splunk/etc/auth/idpCerts/                       │
│ • Raw Artifact:         /tmp/failed_saml_post.xml                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Decompiling the SAML Assertion XML (75 XP)

### 📖 Incident Details
Log in to the Search Head and inspect the raw SAML assertion captured during the failed login attempt:
```bash
cat /tmp/failed_saml_post.xml | grep -iE "Attribute Name|Subject|Conditions"
```

Output excerpt:
```xml
<saml2:Subject>
    <saml2:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">analyst_sarah@corp.com</saml2:NameID>
</saml2:Subject>
<saml2:Conditions NotBefore="2026-10-17T10:28:00Z" NotOnOrAfter="2026-10-17T10:33:00Z">
    <saml2:AudienceRestriction>
        <saml2:Audience>splunk-shc-production</saml2:Audience>
    </saml2:AudienceRestriction>
</saml2:Conditions>
<saml2:AttributeStatement>
    <saml2:Attribute Name="http://schemas.microsoft.com/ws/2008/06/identity/claims/groups">
        <saml2:AttributeValue>SOC_Tier2_Analysts</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute Name="email">
        <saml2:AttributeValue>analyst_sarah@corp.com</saml2:AttributeValue>
    </saml2:Attribute>
</saml2:AttributeStatement>
```

Notice that the group claim is named `http://schemas.microsoft.com/ws/2008/06/identity/claims/groups`, but `authentication.conf` was configured with `role = groups`! Because the attribute name did not match, Splunk could not find any roles for Sarah.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
In SAML 2.0 XML specifications, which tag encapsulates user attribute claims such as groups, department, and email?  
*(Answer Format: `************************`)*

<details>
<summary>💡 Need a Hint?</summary>
saml2:AttributeStatement
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>saml2:AttributeStatement</code> (or <code>AttributeStatement</code>)
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{SAML_ATTRIBUTE_STATEMENT_CLAIMS_UNMASKED}
```

---

## 🎯 TASK 2: Aligning Claims Mapping in `authentication.conf` (75 XP)

### 📖 Tactical Objective
Update the `[saml]` stanza in `/opt/splunk/etc/system/local/authentication.conf` to map the exact claims URI provided by the Identity Provider.

### 🛠️ Configuration Fix
```ini
[saml]
role = http://schemas.microsoft.com/ws/2008/06/identity/claims/groups
mail = email
realName = email

# Group to Role Mapping
roleMap_power = SOC_Tier2_Analysts
roleMap_user = All_Corp_Users
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What parameter in the `[saml]` stanza of `authentication.conf` instructs Splunk which SAML attribute name contains the user's assigned group memberships?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
role
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>role</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{CLAIMS_ROLE_ATTRIBUTE_MAPPED_PROPERLY}
```

---

## 🎯 TASK 3: Rectifying Expired IdP Signing Certificates (75 XP)

### 📖 Incident Details
Even after mapping the role attribute, logins fail with:
```text
ERROR SAMLCommon - Signature verification failed against certificate in /opt/splunk/etc/auth/idpCerts/okta_stale.pem
```

The old certificate expired yesterday! The identity team placed the renewed public key at:  
`/opt/splunk/etc/auth/idpCerts/okta_renewed_2026.pem`.

### 🛠️ Tactical Execution
Update `[saml]` in `authentication.conf`:

```ini
[saml]
idpCertPath = $SPLUNK_HOME/etc/auth/idpCerts/okta_renewed_2026.pem
signedAssertion = true
```

Verify certificate fingerprint:
```bash
openssl x509 -in /opt/splunk/etc/auth/idpCerts/okta_renewed_2026.pem -noout -fingerprint -sha256
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which setting in `[saml]` points to the filesystem location of the Identity Provider's public X.509 certificate used for digital signature verification?  
*(Answer Format: `***********`)*

<details>
<summary>💡 Need a Hint?</summary>
idpCertPath
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>idpCertPath</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{IDP_CERT_ROTATION_SUCCESSFUL_VERIFIED}
```

---

## 🎯 TASK 4: Neutralizing Clock Drift with `samlTimeSkew` (75 XP)

### 📖 Tactical Objective
During peak virtualization load, Search Head VM system time drifts by up to 90 seconds. To prevent assertions from being rejected with `Assertion is not yet valid`, configure clock skew buffering.

### 🛠️ Configuration & Live Reload
Add `samlTimeSkew` to `[saml]`:

```ini
[saml]
samlTimeSkew = 180
```

Reload authentication dynamically:
```bash
/opt/splunk/bin/splunk reload auth -auth admin:SplunkAdmin123!
```

Test ACS endpoint responsiveness:
```bash
curl -k -I https://sh-saml-01:8000/saml/acs
```
Returns HTTP 200 / 405 Method Not Allowed (Confirming endpoint is active and awaiting POST)!

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the default unit of measurement (seconds, minutes, or hours) for the `samlTimeSkew` setting in Splunk?  
*(Answer Format: `*******`)*

<details>
<summary>💡 Need a Hint?</summary>
seconds
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>seconds</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{SAML2_0KT4_AS5ERT1ON_S1GN3D_V3R1F13D}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Verify Claims URIs**: Identity Providers frequently output full schema URIs (e.g. `schemas.microsoft.com/.../groups`) rather than simple strings like `role` or `groups`.
2. **Track IdP Cert Expiration**: Monitor IdP signing certificates proactively to avoid catastrophic Monday morning SSO lockouts.
3. **Buffer Virtual Clock Drift**: Always set `samlTimeSkew = 120` to `180` seconds in virtualized cloud environments to prevent NTP timing rejections.
