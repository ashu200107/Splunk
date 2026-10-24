# 🛡️ Chapter 03 (Phase 5): Splunk Native Authentication, Password Policies & REST/Token User Management

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 41 | **Milestone:** Cryptographic Passwd Internals, Password Governance & Automated REST Provisioning  
> **Current Rank:** Master Splunk Architect (6,800 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_03_Native_Auth_and_REST_User_Mgmt.md`  
> **Interactive Cyber Range Lab:** [Room P5-03: The Admin Shadow Provisioner](../Labs/Room_P5_03_Native_Auth_and_REST_User_Mgmt.md) `[200 XP]`

---

## 🏰 1. The Everyday Analogy: The Bank Safe Deposit Box & The Cryptographic Keycards

Imagine an ultra-secure private bank:

- **The Ledger of Wax-Sealed Vaults (`/etc/passwd`):**  
  Behind bulletproof glass sits a master register containing every account holder's name and a one-way mathematical wax seal ($6$ SHA-512 crypt hash). The bank never stores the physical key itself. When a customer arrives and inserts their key, the bank applies the exact same pressure and chemical formula to see if the resulting wax imprint matches the registry. If it matches, the door unlocks!
- **The Automatic Bank Inspector Policy (`[password_rules]`):**  
  The bank board mandates strict rules: every vault key must be at least 12 notches long, contain letters, numbers, and special grooves, cannot match any of the customer's previous 24 keys, and must be re-keyed every 90 days. If an impostor enters the wrong key 5 times consecutively, an iron shutter drops down and locks the vault for 30 minutes!
- **The Digital VIP Pass (Token-Based Authentication):**  
  When an automated armored truck needs to pick up cash 100 times a day, having a human type a master password every single time is risky. Instead, the bank issues a **tamper-evident digital holographic ticket (Splunk JWT Token)**. It has an expiration timestamp, is signed by the bank's private key, and allows the automated truck to perform designated transactions via the pneumatic tube (REST API) without ever exposing the master administrative password!

In Splunk Enterprise, **Native Authentication, Password Hardening Rules, and Token-Based REST APIs** allow administrators to automate CI/CD user provisioning while enforcing zero-trust defense against brute-force attacks.

---

## 🗺️ 2. The 3D Master Architectural Blueprint

![Splunk Native Auth and REST Tokens 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_native_auth_rest_tokens_3d_1792232829189.jpg)
*Figure 5.3: 3D Architectural Blueprint of Splunk Native Authentication, Password Hardening Engine, and the REST API JWT Token Processing Gateway.*

---

## 🔄 3. The 5-Step Native Authentication & Token Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│              THE 5-STEP SPLUNK NATIVE AUTHENTICATION & TOKEN LIFECYCLE                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. CREDENTIAL PRESENTATION (CLI / Web / REST API)                                       │
│    • User presents username + plaintext password, or an HTTP Bearer JWT token.          │
│    • Request arrives at splunkd management port (8089) or Web UI port (8000).           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. PASSWORD POLICY & LOCKOUT VERIFICATION                                               │
│    • Checks if the account has exceeded `lockoutThreshold` in authentication.conf.     │
│    • If locked, immediately rejects with HTTP 401 Unauthorized (Account Locked).        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. CRYPTOGRAPHIC HASH EVALUATION ('/etc/passwd')                                        │
│    • Reads user's stored salt and hash: `$6$<salt>$<sha512_hash>`.                     │
│    • Re-hashes the supplied plaintext password with stored salt.                        │
│    • Constant-time string comparison verifies password without timing leaks.            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. JWT TOKEN ISSUANCE & SESSION MANAGEMENT                                              │
│    • Upon successful authentication, splunkd issues a signed JSON Web Token (JWT)      │
│      or a session key stored in memory cache.                                           │
│    • REST clients receive `token` parameter for persistent headless automation.         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. AUDIT TRAIL LOGGING IN index=_audit                                                  │
│    • Records action: `action=login`, `user=admin`, `status=success`, `clientip=...`     │
│    • Failed attempts log `action=login_attempt`, `status=failure` for SIEM alerting.    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 Internal Anatomy of `$SPLUNK_HOME/etc/passwd`

Splunk stores all native users, password hashes, and assigned roles in a colon-delimited flat file: `$SPLUNK_HOME/etc/passwd`.

```text
:admin:$6$rK9P7V0z7L02Vb6W$W4k8qV512.../Xk7z0Y81==::Administrator:admin:admin@example.com::
:analyst_jane:$6$mQ2T8A1b4K91Nc3Z$P1l9sY890.../Ab3w1Z92==::Jane Doe:power;soc_tier1:jane@fincorp.com::
```

#### Field Breakdown:
$$\text{:username : hash : reserved : full\_name : roles : email : reserved :}$$

- **Field 1 (`username`):** User's login ID.
- **Field 2 (`hash`):** The cryptographic password hash. Modern Splunk releases use SHA-512 crypt prefixed with `$6$`.
- **Field 4 (`full_name`):** Human-readable name.
- **Field 5 (`roles`):** Semicolon-separated list of assigned roles (e.g. `power;soc_tier1`).
- **Field 6 (`email`):** Notification address for scheduled alerts and report delivery.

> [!CAUTION]
> **Never manually hand-edit `/opt/splunk/etc/passwd` while `splunkd` is running!**  
> Splunk caches user objects in memory. Hand-editing can result in hash corruption or race conditions. Always use the CLI, REST API, or reload authentication via `splunk reload auth`.

---

### 4.2 CLI User Administration

Splunk provides full lifecycle user management directly via `$SPLUNK_HOME/bin/splunk`:

```bash
# 1. Add a new user with specific roles and email
/opt/splunk/bin/splunk add user soc_bob -password "P@ssw0rdSecure!2026" \
  -role "user" -role "soc_tier1" \
  -realname "Bob Johnson" -email "bob@defense.gov"

# 2. Modify an existing user's roles and password
/opt/splunk/bin/splunk edit user soc_bob -password "NewC0mpl3xP@ss#88" \
  -role "power" -role "soc_tier2"

# 3. List all users and their assigned roles
/opt/splunk/bin/splunk list user

# 4. Remove a user account
/opt/splunk/bin/splunk remove user soc_bob

# 5. Unlock a locked-out user account
/opt/splunk/bin/splunk unlock-user soc_bob
```

---

### 4.3 Automated User Management via the REST API (Port 8089)

Enterprise automation and CI/CD pipelines provision users programmatically through Splunk's REST API.

#### Endpoint: `/services/authentication/users`

```bash
# Provision a new user via cURL
curl -k -u admin:AdminPassword123! https://10.100.20.15:8089/services/authentication/users \
  -d name="api_automation_svc" \
  -d password="S3cur3TokenPassword#2026" \
  -d roles="power" \
  -d realname="CI/CD Ingestion Service" \
  -d email="devops@company.internal"
```

#### Querying Users via REST with JSON output:
```bash
curl -s -k -u admin:AdminPassword123! \
  https://10.100.20.15:8089/services/authentication/users?output_mode=json | \
  jq '.entry[] | {user: .name, roles: .content.roles, locked: .content.locked-out}'
```

---

### 4.4 Password Policy Enforcement (`authentication.conf`)

By default, Splunk ships with basic password rules. In production and compliance environments (PCI-DSS 4.0, SOC2, HIPAA, NIST 800-63B), you must harden password policies in `$SPLUNK_HOME/etc/system/local/authentication.conf`:

```ini
[password_rules]
# Minimum character length
minPasswordLength = 14

# Character complexity rules
minPasswordUppercase = 1
minPasswordLowercase = 1
minPasswordDigits = 1
minPasswordSpecial = 1

# Password history and reuse prevention
passwordHistoryCount = 24

# Expiration policy (in days)
expirePasswordDays = 90
expireAlertDays = 15

# Brute-force lockout protection
lockoutThreshold = 5
lockoutDurationMins = 30
lockoutMins = 15
```

#### Explanation of Lockout Parameters:
- **`lockoutThreshold = 5`**: An account is locked after 5 consecutive failed login attempts.
- **`lockoutMins = 15`**: Failed attempts must occur within a 15-minute sliding window to trigger lockout.
- **`lockoutDurationMins = 30`**: Once locked, the account remains disabled for 30 minutes before automatic release (or until an administrator executes `splunk unlock-user`). Setting this to `0` locks the account indefinitely until manual admin intervention.

---

### 4.5 Splunk JWT Token Authentication (`tokens.conf`)

In modern Splunk architectures, embedding cleartext administrative passwords in scripts or CI/CD pipelines is strictly prohibited. Splunk supports **cryptographically signed JSON Web Tokens (JWT)**.

#### Step 1: Enable Token Authentication in `tokens.conf`
File: `$SPLUNK_HOME/etc/system/local/tokens.conf`
```ini
[token_auth]
disabled = false
```

#### Step 2: Minting an Automated Service Token via REST
```bash
curl -k -u admin:AdminPassword123! https://10.100.20.15:8089/services/authorization/tokens \
  -d name="jenkins_pipeline_token" \
  -d audience="splunk_search_heads" \
  -d user="api_automation_svc" \
  -d expires_on="+90d" \
  -d output_mode=json
```

#### Step 3: Executing REST Queries Using the Bearer Token
```bash
curl -k -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..." \
  https://10.100.20.15:8089/services/search/jobs -d search="search index=security error | head 10"
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

### Pitfall 1: Emergency Admin Password Reset via Direct File Deletion
- **The Anti-Pattern:** Administrators who forget the `admin` password delete `$SPLUNK_HOME/etc/passwd` completely.
- **The Disaster:** Deleting `/etc/passwd` wipes **ALL native users, custom service accounts, and assigned roles** across the entire cluster!
- **The Clean Procedure:**
  1. Move the old file aside: `mv /opt/splunk/etc/passwd /opt/splunk/etc/passwd.bak`.
  2. Create a temporary seed file: `/opt/splunk/etc/system/local/user-seed.conf`:
     ```ini
     [user_info]
     USERNAME = admin
     PASSWORD = NewRecoveryPassword123!
     ```
  3. Restart `splunkd`. Splunk reads `user-seed.conf`, regenerates a fresh `/etc/passwd` with just `admin`, and automatically deletes the plaintext `user-seed.conf`.
  4. Restore the custom non-admin accounts from `passwd.bak`.

### Pitfall 2: Setting `lockoutThreshold = 0` (No Lockout)
- **The Anti-Pattern:** Disabling lockout to prevent users from complaining about being locked out.
- **The Risk:** Exposing port 8000 or port 8089 to brute-force dictionary attacks. A single automated hydra script can crack native passwords within minutes.
- **The Fix:** Always enforce `lockoutThreshold = 5` and monitor `index=_audit action=login_attempt status=failure` for automated alerts.

### Pitfall 3: Reusing Long-Lived Admin Tokens in Public Repositories
- **The Anti-Pattern:** Creating a token for `user=admin` with `expires_on=+365d` and hardcoding it in a GitHub Actions `.yml` file.
- **The Risk:** If the repository leaks, attackers gain complete `admin_all_objects` access to the Splunk cluster.
- **The Fix:** Create dedicated least-privilege service accounts (e.g. `svc_deployer` with only `edit_tcp` or `search`), issue short-lived tokens, and rotate them using automated vaults (HashiCorp Vault or AWS Secrets Manager).

---

## 🛠️ 6. Cyber Range Lab: The Admin Shadow Provisioner

Test your skills in the dedicated hands-on scenario:  
👉 **[Room P5-03: The Admin Shadow Provisioner](../Labs/Room_P5_03_Native_Auth_and_REST_User_Mgmt.md)**

### Mission Brief:
- **Scenario:** A rogue insider threat or compromised developer workstation secretly provisioned an unauthorized backdoor account (`shadow_operator`) on the central Search Head with `admin` privileges.
- **Objective:**
  1. Inspect `$SPLUNK_HOME/etc/passwd` and identify the rogue backdoor account.
  2. Terminate and delete the unauthorized user via the Splunk CLI.
  3. Harden `authentication.conf` with enterprise password rules (14 characters, complexity, lockout threshold).
  4. Mint an authorized, short-lived JWT Bearer token for the legitimate security team and capture the operational flag `FLAG{N4T1V3_P4SSWD_H4RD3N3D_J3NK1NS_T0K3N}`.

---

## 🧠 7. End-of-Chapter Self-Check Quiz

#### Q1: In `$SPLUNK_HOME/etc/passwd`, what algorithm does the prefix `$6$` indicate in the stored password hash?
- **A)** MD5 crypt
- **B)** Blowfish (bcrypt)
- **C)** SHA-512 crypt
- **D)** DES legacy crypt

#### Q2: What is the correct CLI command to unlock a user account named `operator_dan` that has exceeded the failed login threshold?
- **A)** `splunk reset user operator_dan --unlock`
- **B)** `splunk unlock-user operator_dan`
- **C)** `splunk edit user operator_dan -locked false`
- **D)** `splunk user unlock operator_dan`

#### Q3: Which configuration file governs password complexity, expiration limits, and account lockout thresholds for native Splunk users?
- **A)** `authorize.conf`
- **B)** `server.conf`
- **C)** `authentication.conf`
- **D)** `web.conf`

#### Q4: When token-based authentication is enabled in `tokens.conf`, what HTTP header format must be sent in a REST API request to authenticate via a JWT token?
- **A)** `Proxy-Authorization: SplunkToken <token>`
- **B)** `Authorization: Bearer <token>` (or `Authorization: Splunk <token>`)
- **C)** `X-Splunk-Signature: <token>`
- **D)** `Cookie: session_token=<token>`

#### Q5: If an administrator needs to securely reset a forgotten admin password on an offline instance, which temporary file should be created in `$SPLUNK_HOME/etc/system/local/`?
- **A)** `admin.conf`
- **B)** `user-seed.conf`
- **C)** `password.seed`
- **D)** `reset-credentials.conf`

---

### 📝 Quiz Answer Key
- **Q1: C** — In Unix/Linux crypt convention, `$1$` is MD5, `$5$` is SHA-256, and `$6$` is SHA-512 crypt.
- **Q2: B** — `/opt/splunk/bin/splunk unlock-user <username>` is the dedicated CLI utility.
- **Q3: C** — `authentication.conf` under the `[password_rules]` stanza controls all password policies.
- **Q4: B** — Standard HTTP `Authorization: Bearer <token>` or `Authorization: Splunk <token>`.
- **Q5: B** — `user-seed.conf` allows defining initial or recovery admin credentials and is automatically consumed and destroyed by `splunkd` upon startup.
