# 🎮 Room P2-02: Splunk Enterprise Linux Deployment & Systemd Hardening

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: Production Linux Deployment       ⭐ DIFFICULTY: Medium        │
│ 🎯 TOPIC: Non-Root User, Systemd, user-seed💎 REWARD: 200 XP            │
│ ⏱️ ESTIMATED TIME: 30 Mins                🛡️ CATEGORY: Production Sec  │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Security Lockdown Mission!  
> A critical external penetration test flagged our Splunk cluster:  
> *"CRITICAL AUDIT FAILURE: Splunk Enterprise is running directly as the `root` superuser. Any remote execution or app vulnerability grants complete kernel compromise of the underlying host!"*  
> Furthermore, if the server reboots, Splunk does not start automatically because nobody enabled the Systemd service.  
> Your mission as the enterprise administrator is to deploy Splunk Enterprise using production best practices: create a dedicated unprivileged **`splunk` service account**, automate credential provisioning with **`user-seed.conf`**, configure `$SPLUNK_HOME/bin/splunk enable boot-start -user splunk`, and lock down file permissions!

---

## 🗺️ Mission Architecture & Installation Paths

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 📁 SPLUNK PRODUCTION DIRECTORY & PERMISSION SPECS                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Dedicated User & Group: splunk:splunk (UID/GID 1001)                       │
│ • Binary Installation:    /opt/splunk/                                       │
│ • Data Storage Mount:     /opt/splunk/var/lib/splunk/ (chown -R splunk:splunk)│
│ • Service Daemon:         systemd unit (/etc/systemd/system/Splunkd.service) │
│ • Admin Seed File:        /opt/splunk/etc/system/local/user-seed.conf        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: The Non-Root Service Account (50 XP)

### 📖 Technical Recon
Running Splunk as `root` violates CIS benchmarks, SOC 2, and PCI-DSS compliance.  
Create a locked system service account:
```bash
sudo groupadd splunk
sudo useradd -m -r -g splunk -d /opt/splunk -s /bin/bash splunk
```

Extract the tarball into `/opt/splunk`:
```bash
sudo tar -xzf splunk-9.2.x-linux-2.6-amd64.tgz -C /opt
sudo chown -R splunk:splunk /opt/splunk
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
Why is it considered an extreme security vulnerability to run Splunk Enterprise under the `root` Linux account in production?  
- [A] Splunk will fail to index logs from Windows servers.
- [B] Splunk apps with custom Python scripts or shell lookups execute with root privileges, allowing malicious or vulnerable code to compromise the entire host.
- [C] Root accounts cannot open TCP port 9997.
- [D] Root accounts consume double the daily license quota.

<details>
<summary>💡 Need a Hint?</summary>
Think about least-privilege security and arbitrary code execution in apps.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] Least privilege. Third-party or community apps could execute arbitrary shell commands with root privileges, leading to complete machine takeover.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{NON_ROOT_SPLUNK_USER_LEAST_PRIVILEGE}
```

---

## 🎯 TASK 2: Silent Credential Seeding (`user-seed.conf`) (50 XP)

### 📖 Technical Recon
In automated enterprise deployments (Ansible, Terraform, Puppet), you cannot have an engineer sitting at a keyboard typing the initial administrator username and password.  
Splunk supports unattended first-time boot via **`user-seed.conf`**:

`/opt/splunk/etc/system/local/user-seed.conf`:
```ini
[user_info]
USERNAME = admin
PASSWORD = ComplexSecretPassw0rd!123
```

On first startup, Splunk reads this file, hashes the password with SHA-512, writes the hash into `passwd`, and **automatically deletes or empties `user-seed.conf`** so plain-text passwords do not remain on disk!

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the name of the configuration file placed inside `$SPLUNK_HOME/etc/system/local/` to seed the initial admin username and password during silent installation?  
*(Answer Format: `*********.conf`)*

<details>
<summary>💡 Need a Hint?</summary>
"user" followed by "seed".
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>File:</b> <code>user-seed.conf</code><br/>
Declared under <code>[user_info]</code> stanza.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{USER_SEED_CONF_SILENT_PROVISIONING}
```

---

## 🎯 TASK 3: Systemd Service Integration (50 XP)

### 📖 Technical Recon
To ensure Splunk starts automatically on system reboot and runs strictly under the `splunk` user account, execute:

```bash
sudo /opt/splunk/bin/splunk enable boot-start \
    -user splunk \
    -systemd-managed 1
```

This creates the unit file at `/etc/systemd/system/Splunkd.service` configured with `User=splunk` and `Group=splunk`.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What flag must be passed to `splunk enable boot-start` to ensure Splunk creates a modern native Systemd service unit rather than legacy init.d SysV scripts?  
*(Answer Format: -**************** *)*

<details>
<summary>💡 Need a Hint?</summary>
Starts with `-systemd...`
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Flag:</b> <code>-systemd-managed 1</code><br/>
Command: <code>splunk enable boot-start -user splunk -systemd-managed 1</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{SYSTEMD_MANAGED_ONE_BOOT_START}
```

---

## 🎯 TASK 4: Binding Privileged Ports (Cap-Bind-Service) (50 XP)

### 📖 Technical Recon
If Splunk runs as non-root user `splunk`, Linux forbids it from binding to privileged ports (< 1024), such as Syslog **UDP 514**.  
To allow the non-root splunk binary to bind port 514 without running as root:

```bash
sudo setcap 'cap_net_bind_service=+ep' /opt/splunk/bin/splunkd
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Which Linux POSIX capability is granted to `/opt/splunk/bin/splunkd` using `setcap` to allow non-root Splunk to bind to privileged ports (< 1024) like Syslog 514?  
*(Answer Format: `cap_***_****_*******`)*

<details>
<summary>💡 Need a Hint?</summary>
`cap_net_bind_...`
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Capability:</b> <code>cap_net_bind_service</code><br/>
This grants permission to bind ports below 1024 without root privileges.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{CAP_NET_BIND_SERVICE_SYSLOG_514}
```

---

## 🏆 Room P2-02 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM P2-02 COMPLETE                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 200 / 200 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Dedicated splunk User Isolation, user-seed.conf,   │
│   Native Systemd Unit Deployment, cap_net_bind_service Hardening       │
│                                                                        │
│ ➡️ NEXT ROOM: Room P2-03 — Universal Forwarder Fleet Rollout & ACK    │
└────────────────────────────────────────────────────────────────────────┘
```
