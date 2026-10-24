# 🎮 Room P5-03: The Admin Shadow Provisioner

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-03: The Admin Shadow Provisioner        ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: etc/passwd, Password Hardening & Tokens  💎 REWARD: 200 XP     │
│ ⏱️ ESTIMATED TIME: 35 Mins                         🛡️ CATEGORY: Security │
│ 🏆 PREREQUISITE: Room P5-01 & Room P5-02                               │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Red Alert — Rogue Shadow Account Detected in Cluster!**  
> During an automated configuration compliance scan, the SOC detected an anomaly on the primary Search Head: an unauthorized user named `shadow_operator` was provisioned directly into `$SPLUNK_HOME/etc/passwd` with full `admin` privileges!  
>  
> Simultaneously, the organization failed its PCI-DSS password governance audit because the instance allows 4-character weak passwords and lacks account lockout protection.  
>  
> Your mission as the Lead Splunk Security Administrator:  
> 1. Investigate `$SPLUNK_HOME/etc/passwd` and unmask the rogue user.  
> 2. Evict and purge the backdoor account using the Splunk CLI.  
> 3. Enforce enterprise password policies and lockout limits in `authentication.conf`.  
> 4. Enable token-based authentication in `tokens.conf`, issue a hardened service token, and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

![Shadow Provisioner 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_native_auth_rest_tokens_3d_1792232829189.jpg)
*Figure P5-3.1: Splunk Native Authentication Vault, Password Governance, and Token Issuance Engine.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          sh-prod-01 (10.0.10.20:8000 / :8089)                 │
│ • User Password File:   /opt/splunk/etc/passwd                               │
│ • Password Policy File: /opt/splunk/etc/system/local/authentication.conf     │
│ • Token Config File:    /opt/splunk/etc/system/local/tokens.conf             │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Hunting the Shadow Account in `etc/passwd` (50 XP)

### 📖 Incident Details
Log in to the Search Head and inspect `/opt/splunk/etc/passwd`:
```bash
cat /opt/splunk/etc/passwd
```

Output:
```text
:admin:$6$8q9W7K1z2L03Vb7X$T5l8qV512...::Administrator:admin:admin@corp.internal::
:soc_tier1:$6$pM2T8A1b4K91Nc3Z$P1l9sY890...::Tier 1 SOC Analyst:user;soc_tier1:soc1@corp.internal::
:shadow_operator:$6$zX991A44L01288bB$99A1K...::System Diagnostic:admin:shadow@darknet.io::
```

Notice the entry `:shadow_operator:...:admin:shadow@darknet.io::`! It was granted `admin` privileges and points to an external adversary domain.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
In Splunk's colon-delimited `/opt/splunk/etc/passwd` file, which 1-based field number stores the user's assigned role(s)?  
*(Answer Format: `*`)*

<details>
<summary>💡 Need a Hint?</summary>
Count the colon fields: :username(1):hash(2):reserved(3):realname(4):roles(5):email(6):reserved(7):
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>5</code> — Roles are stored in field 5 of the colon-separated line.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{SHADOW_OPERATOR_BACKDOOR_IDENTIFIED}
```

---

## 🎯 TASK 2: Purging the Account via the Splunk CLI (50 XP)

### 📖 Tactical Objective
Never manually edit `/opt/splunk/etc/passwd` using `vi` or `sed` while `splunkd` is running. Use the authorized CLI utility to cleanly invalidate the user in memory and on disk.

### 🛠️ Execution Command
```bash
/opt/splunk/bin/splunk remove user shadow_operator -auth admin:SplunkAdmin123!
```

Verify deletion:
```bash
/opt/splunk/bin/splunk list user -auth admin:SplunkAdmin123! | grep -i "shadow_operator"
```
The command should return empty output.

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the exact CLI subcommand to permanently delete a local user account in Splunk Enterprise?  
*(Answer Format: `****** ****`)*

<details>
<summary>💡 Need a Hint?</summary>
remove user
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>remove user</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{CLI_USER_PURGE_SUCCESSFUL_LEAST_PRIVILEGE}
```

---

## 🎯 TASK 3: Hardening Password Governance in `authentication.conf` (50 XP)

### 📖 Tactical Objective
Enforce PCI-DSS 4.0 compliant password rules to prevent brute-force attacks and enforce complex passphrases.

### 🛠️ Hands-on Configuration
Create or modify `/opt/splunk/etc/system/local/authentication.conf`:

```ini
[password_rules]
minPasswordLength = 14
minPasswordUppercase = 1
minPasswordLowercase = 1
minPasswordDigits = 1
minPasswordSpecial = 1
passwordHistoryCount = 24
expirePasswordDays = 90
lockoutThreshold = 5
lockoutMins = 15
lockoutDurationMins = 30
```

Reload the authentication subsystem immediately without restarting `splunkd`:
```bash
/opt/splunk/bin/splunk reload auth -auth admin:SplunkAdmin123!
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which parameter in `authentication.conf` defines how many consecutive failed login attempts will lock an account?  
*(Answer Format: `****************`)*

<details>
<summary>💡 Need a Hint?</summary>
lockoutThreshold
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>lockoutThreshold</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{PASSWORD_RULES_HARDENED_LOCKOUT_ENFORCED}
```

---

## 🎯 TASK 4: Token-Based Automation & REST JWT Issuance (50 XP)

### 📖 Tactical Objective
Migrate legacy scripts from hardcoded admin passwords to cryptographically signed JWT Bearer tokens.

### 🛠️ Step 1: Enable Token Auth in `tokens.conf`
File: `/opt/splunk/etc/system/local/tokens.conf`
```ini
[token_auth]
disabled = false
```

Reload tokens:
```bash
/opt/splunk/bin/splunk reload auth -auth admin:SplunkAdmin123!
```

### 🛠️ Step 2: Mint a Dedicated Automation Token
Execute via cURL to the management port (8089):
```bash
curl -k -u admin:SplunkAdmin123! https://10.0.10.20:8089/services/authorization/tokens \
  -d name="soc_automation_worker" \
  -d audience="splunk_search_heads" \
  -d user="soc_tier1" \
  -d expires_on="+30d" \
  -d output_mode=json
```

Capture the resulting token and test search capability:
```bash
curl -k -H "Authorization: Bearer <TOKEN_STRING>" \
  https://10.0.10.20:8089/services/search/jobs -d search="search index=_audit | head 1"
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
In which configuration file must `[token_auth]` be configured with `disabled = false` to enable JWT token-based authentication?  
*(Answer Format: `***********`)*

<details>
<summary>💡 Need a Hint?</summary>
tokens.conf
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>tokens.conf</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{N4T1V3_P4SSWD_H4RD3N3D_J3NK1NS_T0K3N}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Protect `/etc/passwd`**: Never hand-edit the raw passwd file while `splunkd` is active; always manage users via CLI or the REST API.
2. **Defend Against Brute Force**: Set `lockoutThreshold = 5` and `minPasswordLength = 14` in `authentication.conf` to meet SOC2/PCI-DSS standards.
3. **Automate with Tokens**: Modern Splunk deployments use scoped JWT tokens via `tokens.conf` instead of storing cleartext administrative passwords in scripts.
