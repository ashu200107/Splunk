# 🎮 Room P5-07: The Fortress Hardening Audit

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-07: The Fortress Hardening Audit        ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: CIS Benchmarks, Non-Root, Port Lockdown  💎 REWARD: 300 XP     │
│ ⏱️ ESTIMATED TIME: 45 Mins                         🛡️ CATEGORY: Security │
│ 🏆 PREREQUISITE: Room P5-01 through Room P5-06                         │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: High-Severity Audit Findings — Production Penetration Test!**  
> An external cybersecurity audit team completed a vulnerability assessment of your Indexing cluster (`idx-prod-01`).  
>  
> The auditors issued three Critical Findings:  
> 1. The `splunkd` process is running with operating system `root` privileges.  
> 2. The Indexer is exposing an unauthenticated Web UI on port 8000 disclosing software versions.  
> 3. An internal operator illicitly added the `admin` role to a standard user account last night!  
>  
> Your mission as the Lead Splunk Security & Compliance Architect:  
> 1. Migrate the indexer process to the non-root `splunk` service user.  
> 2. Disable Splunk Web (`startwebserver = 0`) to eliminate port 8000.  
> 3. Harden `web.conf` with security headers and banner suppression.  
> 4. Forensically interrogate `index=_audit` to catch the rogue administrator and capture all 4 flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Indexer Node:         idx-prod-01 (10.10.15.80)                            │
│ • Service User:         splunk:splunk (UID 1001 / GID 1001)                  │
│ • Web Config:           /opt/splunk/etc/system/local/web.conf                │
│ • Server Config:        /opt/splunk/etc/system/local/server.conf             │
│ • Forensic Audit Index: index=_audit                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Auditing the Running Process & Demoting Root (75 XP)

### 📖 Incident Details
Log in to `idx-prod-01` via SSH and inspect running processes:
```bash
ps aux | grep splunkd
```

Output:
```text
root     14202  4.2  8.1 1928340 655432 ?  Sl   08:00   1:12 splunkd -p 8089 restart
```
The daemon is running as `root`! Any remote code execution bug instantly yields complete control over the Linux host.

### 🛠️ Execution Plan
1. Stop the instance:
   ```bash
   /opt/splunk/bin/splunk stop
   ```
2. Reassign file ownership to the `splunk` system account:
   ```bash
   chown -R splunk:splunk /opt/splunk
   ```
3. Update systemd boot-start:
   ```bash
   /opt/splunk/bin/splunk enable boot-start -user splunk --systemd-managed 1
   systemctl start Splunkd
   ```
4. Verify non-root execution:
   ```bash
   ps -ef | grep splunkd | grep -v grep
   # Must show user 'splunk', NOT 'root'!
   ```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What flag passed to `/opt/splunk/bin/splunk enable boot-start` specifies the non-root operating system account that should execute the Splunk daemon under systemd?  
*(Answer Format: `-**** <username>`)*

<details>
<summary>💡 Need a Hint?</summary>
-user
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>-user splunk</code> (or <code>-user</code>)
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{NON_ROOT_DAEMON_LEAST_PRIVILEGE_RESTORED}
```

---

## 🎯 TASK 2: Eliminating Unnecessary Web Attack Surfaces (75 XP)

### 📖 Tactical Objective
Dedicated Indexer nodes have no need for a browser interface. Terminate the Web UI daemon and close port 8000.

### 🛠️ Configuration
Edit `/opt/splunk/etc/system/local/web.conf`:

```ini
[settings]
startwebserver = 0
```

Restart `splunkd`:
```bash
/opt/splunk/bin/splunk restart
```

Verify that port 8000 is closed:
```bash
ss -tulpn | grep 8000
```
Command returns zero listening sockets.

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What setting in `web.conf` under the `[settings]` stanza disables the Splunk Web server completely?  
*(Answer Format: `************** = *`)*

<details>
<summary>💡 Need a Hint?</summary>
startwebserver = 0
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>startwebserver = 0</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{PORT_8000_SHUTDOWN_ATTACK_SURFACE_MINIMIZED}
```

---

## 🎯 TASK 3: Banner Masking & Security Headers (75 XP)

### 📖 Tactical Objective
On search head nodes where Splunk Web MUST remain open, mask the version number to prevent automated vulnerability scanners from fingerprinting build versions.

### 🛠️ Configuration
On the Search Head, edit `/opt/splunk/etc/system/local/web.conf`:

```ini
[settings]
support_info = false
tools.sessions.secure = true
tools.sessions.httponly = true
x_frame_options = SAMEORIGIN
```

Reload web settings:
```bash
/opt/splunk/bin/splunk reload web
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which parameter in `web.conf` suppresses version numbers, build metadata, and operating system signatures from the Splunk Web login banner?  
*(Answer Format: `************`)*

<details>
<summary>💡 Need a Hint?</summary>
support_info
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>support_info</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{BANNER_RECONNAISSANCE_SUPPRESSED_SECURE}
```

---

## 🎯 TASK 4: Forensic Interrogation of `index=_audit` (75 XP)

### 📖 Tactical Objective
A disgruntled administrator secretly elevated user `intern_carl` to the `admin` role yesterday evening. Identify the perpetrator and timestamp by forensically querying `index=_audit`.

### 🛠️ SPL Forensic Query
Execute in the Search Head:
```spl
index=_audit action IN ("edit_user", "add_user") target_user="intern_carl"
| table _time user action target_user roles
```

Output:
```text
_time                 user              action     target_user   roles
--------------------  ----------------  ---------  ------------  -----
2026-10-16 23:42:15   rogue_admin_dave  edit_user  intern_carl   user;admin
```

`rogue_admin_dave` executed the unauthorized privilege escalation at 23:42:15!

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
In Splunk audit logs within `index=_audit`, which field stores the username of the account that executed an administrative configuration change?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
user
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>user</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{C1S_F0RTR3SS_H4RD3N3D_AUD1T_M4ST3R}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Non-Root Execution**: Running Splunk as `root` is a critical security failure; run as `splunk:splunk` and use `setcap` if privileged ports (< 1024) are required.
2. **Minimize Surface Area**: Disable Splunk Web (`startwebserver = 0`) on all nodes except dedicated Search Heads.
3. **Audit Trails are King**: `index=_audit` provides an unalterable record of all queries, user edits, and privilege modifications for incident response.
