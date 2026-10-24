# 🛡️ Chapter 07 (Phase 5): Splunk Hardening & Compliance Auditing — CIS Benchmarks, Port Lockdown & `_audit` Forensics

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 45 | **Milestone:** Enterprise Defensive Hardening, Non-Root Lockdown & Forensic Audit Trail Analysis  
> **Current Rank:** Master Splunk Architect (7,950 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_07_Splunk_Hardening_and_Audit_Forensics.md`  
> **Interactive Cyber Range Lab:** [Room P5-07: The Fortress Hardening Audit](../Labs/Room_P5_07_Splunk_Hardening_and_Audit_Forensics.md) `[300 XP]`

---

## 🏰 1. The Everyday Analogy: The Fortified Citadel & The Black-Box Flight Recorder

Imagine an ancient stone fortress safeguarding the kingdom's crown jewels:

- **The Danger of Unlocked Backdoors (Default Exposure):**  
  If the fortress keeps 20 side gates open to the forest, allows civilian tourists to wander into the armory, and runs under the identity of the King himself (running as Linux `root`), a single compromised arrow boy can seize the throne and burn down the entire city!
- **Rule 1: De-Elevating the Guard (Non-Root Execution & Linux Capabilities):**  
  The fortress guards are ordered to shed their royal armor. They operate as ordinary guards (`splunk` service user). If a guard needs to open the main drawbridge on low-numbered ports (< 1024), they aren't given absolute crown authority; they are granted a tiny, specific mechanical token (**Linux Kernel Capability: `cap_net_bind_service`**)—allowing them to operate the drawbridge and nothing else!
- **Rule 2: Sealing Unnecessary Drawbridges (Port & Service Lockdown):**  
  On guard outposts that only store grain (Indexers and Forwarders), the castle architect boards up the visitor observation tower (**disabling Splunk Web: `startwebserver = 0`**). Why expose a web interface on a machine that only processes machine data?
- **Rule 3: The Tamper-Proof Black Box Flight Recorder (`index=_audit`):**  
  Inside the throne room sits an indestructible, glass-encased ledger. Every time any guard opens a door, looks through a telescope (executes a search query), promotes a soldier, or fails to remember the daily password, an invisible quill permanently engraves their name, exact timestamp, IP address, and full query in stone. Even the King cannot erase the stone ledger without tripping the alarms!

In Splunk Enterprise, **System Hardening, CIS Benchmarking, and `_audit` Monitoring** form the defensive baseline required for SOC2, PCI-DSS 4.0, ISO 27001, and HIPAA compliance.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│               SPLUNK ENTERPRISE HARDENING & AUDIT FORENSIC ARCHITECTURE                   │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   HOST & KERNEL HARDENING LAYER                                                           │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ • Dedicated Non-Root User: splunk:splunk (UID 1001)                               │   │
│   │ • Strict Permissions: chmod 700 /opt/splunk | umask 027                           │   │
│   │ • Linux Capabilities: setcap 'cap_net_bind_service=+ep' /opt/splunk/bin/splunkd   │   │
│   │ • Systemd Unit: CapabilityBoundingSet=CAP_NET_BIND_SERVICE                       │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │                                             │
│   NETWORK & PORT LOCKDOWN LAYER             │                                             │
│   ┌─────────────────────────────────────────┴─────────────────────────────────────────┐   │
│   │ • Indexers / Forwarders: web.conf [settings] startwebserver = 0 (Kill Port 8000)  │   │
│   │ • Port 8089 REST Lockdown: iptables / firewalld whitelist to Management Subnet    │   │
│   │ • Disable Outdated Ciphers: sslVersions = tls1.2, tls1.3                          │   │
│   │ • Obscure Version Footprints: web.conf support_info = false                       │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │                                             │
│   FORENSIC IMMUTABLE AUDIT TRAIL LAYER      │                                             │
│   ┌─────────────────────────────────────────┴─────────────────────────────────────────┐   │
│   │                                   index=_audit                                    │   │
│   │  • User Query Tracking: action=search, info=granted, user=*, search="index=*"     │   │
│   │  • Access Governance: action=edit_user, action=add_role, target_user=shadow       │   │
│   │  • Brute-Force Monitoring: action=login_attempt, status=failure, count > 5        │   │
│   │  • Forwarder Audit: FwdData: target_host, rate_bytes, data_loss_prevention        │   │
│   └───────────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. The 5-Step CIS Compliance Hardening Journey

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                   THE 5-STEP CIS COMPLIANCE HARDENING JOURNEY                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. PRINCIPLE OF LEAST PRIVILEGE EXECUTION                                               │
│    • Migrate splunkd off root execution to non-root `splunk:splunk` service account.   │
│    • Set directory ownership: `chown -R splunk:splunk /opt/splunk`.                     │
│    • Configure umask 027 in splunk-launch.conf to prevent world-readable artifacts.     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. PRIVILEGED PORT BINDING VIA LINUX CAPABILITIES                                       │
│    • Grant `cap_net_bind_service` to allow syslog binding on port 514 without root.     │
│    • Or bind high ports (e.g. 1514) and redirect via iptables/firewalld.                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. ATTACK SURFACE MINIMIZATION (PORT LOCKDOWNS)                                         │
│    • Disable Splunk Web (port 8000) on all non-Search-Head nodes (`startwebserver = 0`).│
│    • Restrict management port 8089 to dedicated internal administrative jump boxes.     │
│    • Disable unauthenticated app installation and internet access in server.conf.       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. CRYPTOGRAPHIC & CIPHER SUITE HARDENING                                               │
│    • Deprecate SSLv3, TLS 1.0, and TLS 1.1 across all `*.conf` files.                  │
│    • Restrict ciphers to ECDHE-RSA-AES256-GCM-SHA384 and modern PFS cipher suites.      │
│    • Enable HSTS and secure cookies in web.conf.                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. CONTINUOUS AUDIT LOGGING & SIEM COMPLIANCE MONITORING                                │
│    • Validate ingestion into `index=_audit` and `index=_internal`.                      │
│    • Schedule alerts for privileged role escalations and administrative logins.         │
│    • Enforce 1-year to 7-year cold/frozen retention for compliance audit buckets.        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 Operating System Level Hardening: The Non-Root Standard

Running Splunk as the operating system `root` user is the single most dangerous violation in enterprise administration. If a malicious app, crafted XML, or command injection vulnerability is triggered, the attacker instantly gains full root access to the underlying Linux kernel!

#### Migration from Root to Non-Root User:
```bash
# 1. Create dedicated system user and group
useradd -r -m -s /sbin/nologin -c "Splunk Service User" splunk

# 2. Stop running instance
/opt/splunk/bin/splunk stop

# 3. Recursively reclaim filesystem ownership
chown -R splunk:splunk /opt/splunk

# 4. Enforce strict directory permissions
chmod 700 /opt/splunk

# 5. Enable systemd management under the non-root user
/opt/splunk/bin/splunk enable boot-start -user splunk --systemd-managed 1
```

#### Low-Port Binding Without Root (`setcap`):
If your Heavy Forwarder or Indexer needs to listen directly on privileged ports (like UDP/TCP 514 for Syslog) without running as root:

```bash
setcap 'cap_net_bind_service=+ep' /opt/splunk/bin/splunkd
```

---

### 4.2 Network & Service Lockdown: Disabling Splunk Web

Indexers, Heavy Forwarders, License Managers, and Cluster Managers do not require a Web UI. Running port 8000 on these nodes introduces unnecessary attack surfaces.

File: `$SPLUNK_HOME/etc/system/local/web.conf`
```ini
[settings]
# Completely disable Splunk Web daemon and shut down port 8000
startwebserver = 0
```

Apply immediately:
```bash
/opt/splunk/bin/splunk restart
```

Verify that port 8000 is closed:
```bash
ss -tulpn | grep -E "8000|splunkd"
```

---

### 4.3 Restricting the Splunkd Management Bus (Port 8089)

Port 8089 exposes the entire REST API of the Splunk instance. In a hardened environment:

1. **Firewall Access Controls:** Restrict inbound traffic on port 8089 to Search Heads, Deployers, and authorized management subnets using `firewalld`:
   ```bash
   firewall-cmd --permanent --zone=internal --add-source=10.10.10.0/24
   firewall-cmd --permanent --zone=internal --add-port=8089/tcp
   firewall-cmd --permanent --zone=public --remove-port=8089/tcp
   firewall-cmd --reload
   ```
2. **Server Configuration Hardening:**
   File: `$SPLUNK_HOME/etc/system/local/server.conf`
   ```ini
   [applicationsManagement]
   # Block unauthenticated internet downloads of apps
   allowInternetAccess = false

   [sslConfig]
   sslVersions = tls1.2, tls1.3
   ```

---

### 4.4 Web UI Banner & Information Masking (`web.conf`)

Attackers scan web banners to fingerprint the exact Splunk version and research known CVE exploits.

File: `$SPLUNK_HOME/etc/system/local/web.conf`
```ini
[settings]
# Hide software version, OS info, and build number from login screen
support_info = false

# Enforce secure cookies (prevents cross-site scripting session hijacking)
tools.sessions.secure = true
tools.sessions.httponly = true

# Modern X-Frame Options (Anti-Clickjacking)
x_frame_options = SAMEORIGIN
```

---

### 4.5 Compliance Auditing with `index=_audit`

Splunk maintains an internal, immutable audit journal in `index=_audit`. This index tracks **every single administrative action and search query**.

#### Key Audit Events & Search Recipes:

```spl
# 1. Investigate All Searches Executed by a Specific User
index=_audit action=search info=granted user=analyst_bob
| table _time user search total_run_time scan_count

# 2. Detect Privileged Role & User Modifications
index=_audit action IN ("edit_user", "add_user", "remove_user", "change_password")
| table _time user action target_user roles

# 3. Identify Brute-Force Password Spraying Attempts
index=_audit action=login_attempt status=failure
| stats count by clientip, user
| where count >= 5
| sort - count

# 4. Audit who executed the destructive '| delete' command
index=_audit search="*|*delete*"
| table _time user search
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

### Pitfall 1: Running Splunk under `root` to "Fix File Permission Errors"
- **The Anti-Pattern:** When log ingestion fails due to `Permission Denied` on `/var/log/messages`, administrators simply restart Splunk as `root`.
- **The Disaster:** Running Splunk as root violates every major security compliance framework (SOC2, PCI-DSS, ISO 27001). Splunk creates internal `.tsidx` and bucket files with `root:root` permissions, permanently breaking the instance when it is later switched back to a service account.
- **The Fix:** Grant read access to system logs using Linux POSIX Access Control Lists (ACLs):
  ```bash
  setfacl -m u:splunk:r /var/log/messages
  ```

### Pitfall 2: Overlooking Audit Index Data Retention
- **The Anti-Pattern:** Leaving `index=_audit` with default small retention settings (e.g. 500 MB max size).
- **The Disaster:** High search volume causes audit buckets to age out and get deleted after 3 weeks. When external compliance auditors request forensic evidence from 6 months ago, the data is gone!
- **The Fix:** Explicitly size `index=_audit` in `indexes.conf` with a 365-day or 7-year frozen retention policy to meet regulatory mandates.

### Pitfall 3: Failing to Lock Down `limits.conf` Export Limits
- **The Anti-Pattern:** Leaving CSV/JSON export limits unbounded.
- **The Risk:** Disgruntled users or compromised accounts execute:
  `index=* | head 5000000 | outputcsv exfiltrated_data.csv`
  and download proprietary corporate data through the browser.
- **The Fix:** Restrict export capabilities and throttle export job quotas in `authorize.conf` and `limits.conf`.

---

## 🛠️ 6. Cyber Range Lab: The Fortress Hardening Audit

Test your skills in the dedicated hands-on scenario:  
👉 **[Room P5-07: The Fortress Hardening Audit](../Labs/Room_P5_07_Splunk_Hardening_and_Audit_Forensics.md)**

### Mission Brief:
- **Scenario:** A third-party security firm completed a penetration test on your indexing tier. They reported that indexers are running Splunk Web on port 8000, running as Linux `root`, and disclosing software versions in HTTP response headers.
- **Objective:**
  1. Audit the running processes and migrate the instance to run under the `splunk` system user.
  2. Disable Splunk Web on the indexer node (`startwebserver = 0`).
  3. Strip banner disclosures and enforce HSTS and secure cookies.
  4. Query `index=_audit` to unmask an administrator who illicitly modified user permissions and capture the flag `FLAG{C1S_F0RTR3SS_H4RD3N3D_AUD1T_M4ST3R}`.

---

## 🧠 7. End-of-Chapter Self-Check Quiz

#### Q1: Which Linux kernel capability allows a non-root `splunkd` process to bind directly to privileged network ports below 1024 (such as TCP/UDP port 514)?
- **A)** `CAP_SYS_ADMIN`
- **B)** `CAP_NET_BIND_SERVICE`
- **C)** `CAP_NET_RAW`
- **D)** `CAP_DAC_OVERRIDE`

#### Q2: What is the recommended production setting for `startwebserver` in `web.conf` on dedicated Indexer and Heavy Forwarder nodes?
- **A)** `startwebserver = 1`
- **B)** `startwebserver = 0`
- **C)** `startwebserver = false_on_indexer`
- **D)** `startwebserver = headless`

#### Q3: Which internal Splunk index permanently logs all user search queries, login attempts, user provisioning events, and permission modifications?
- **A)** `_internal`
- **B)** `_introspection`
- **C)** `_audit`
- **D)** `_telemetry`

#### Q4: Why is it considered an extreme security risk to run the Splunk daemon as the operating system `root` user?
- **A)** Root processes use twice as much RAM as standard processes.
- **B)** Any application vulnerability or code execution bug in Splunk grants the attacker full root compromise over the underlying operating system.
- **C)** Splunk cannot write TSIDX files when running as root.
- **D)** Search queries run 50% slower under root.

#### Q5: In `web.conf`, setting `support_info = false` accomplishes which defensive hardening objective?
- **A)** It disables tech support ticket submission from the Web UI.
- **B)** It masks the Splunk software version, build number, and OS details from the login screen to prevent reconnaissance.
- **C)** It disables the Monitoring Console dashboard.
- **D)** It disables user password reset requests.

---

### 📝 Quiz Answer Key
- **Q1: B** — `CAP_NET_BIND_SERVICE` allows binding ports < 1024 without granting full superuser permissions.
- **Q2: B** — `startwebserver = 0` disables the web server on non-Search-Head nodes.
- **Q3: C** — `index=_audit` is the dedicated regulatory audit index.
- **Q4: B** — Running as root means any compromised app or script executes with unchecked kernel-level authority.
- **Q5: B** — `support_info = false` removes version and build numbers from public display, hindering automated banner scraping.
