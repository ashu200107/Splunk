# 🎮 Room P5-01: The RBAC Vault Infiltration

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-01: The RBAC Vault Infiltration         ⭐ DIFFICULTY: Easy-Med│
│ 🎯 TOPIC: authorize.conf, Custom Roles & Quotas   💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 35 Mins                         🛡️ CATEGORY: Security │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Triage of Unauthorized Administrative Access!**  
> An internal security review discovered serious access governance violations on the central Search Head:  
> 1. A third-party contractor account (`contractor_bob`) was mistakenly assigned both the `admin` and `can_delete` roles.
> 2. An unconstrained custom role named `developer_unlimited` has `srchDiskQuota = 0` (unlimited), causing dispatch partition disk exhaustion.
> 3. An external compliance auditor (`auditor_jane`) needs read access strictly limited to `index=compliance`, but has been granted access to `index=*`.
>
> You are the lead Splunk Security Administrator. You must audit `authorize.conf`, enforce the principle of least privilege, strip rogue capabilities, and capture all 4 operational flags!

---

## 🗺️ Mission Architecture & Target Environment

![RBAC Vault Infiltration 3D](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_user_and_role_architecture_3d_1792232469425.jpg)
*Figure P5-1.1: Role-Based Access Control Vault & Clearance Levels.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Search Head:          shc-captain-01 (192.168.1.10:8000)                   │
│ • Configuration File:   /opt/splunk/etc/system/local/authorize.conf          │
│ • User Directory:       /opt/splunk/etc/passwd                               │
│ • Target Audited Users: contractor_bob, auditor_jane                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Auditing Role Capabilities via Btool (60 XP)

### 📖 Incident Details
Log in to the Search Head via SSH and inspect effective role capabilities using `btool`:
```bash
/opt/splunk/bin/splunk btool authorize list role_admin --debug | grep -E "delete|capabilities"
```

Verify which role stanza grants the destructive `delete` capability.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the name of the built-in capability in Splunk Enterprise that authorizes a user to hide and mask indexed events using the `| delete` command?  
*(Answer Format: `******`)*

<details>
<summary>💡 Need a Hint?</summary>
delete
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>delete</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{DELETE_CAPABILITY_LEAST_PRIVILEGE_AUDITED}
```

---

## 🎯 TASK 2: Stripping the `can_delete` Privilege (60 XP)

### 📖 Incident Details
Inspect `/opt/splunk/etc/system/local/authorize.conf`.  
Remove `can_delete` from `contractor_bob`'s role mapping and ensure that `admin` never inherits `can_delete`:

```bash
/opt/splunk/bin/splunk edit user contractor_bob -roles user
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Why does Splunk Enterprise deliberately isolate the `delete` capability inside the `can_delete` role rather than granting it to `admin` by default?  
*(Answer Format: To prevent accidental ********** of data and maintain strict forensic audit **********)*

<details>
<summary>💡 Need a Hint?</summary>
destruction, compliance
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>To prevent accidental destruction of data and maintain strict forensic audit compliance</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{CAN_DELETE_ISOLATION_SAFEGUARD_VERIFIED}
```

---

## 🎯 TASK 3: Architecting the `external_auditor` Role (65 XP)

### 📖 Incident Details
Create a hardened custom role for the external auditor in `/opt/splunk/etc/system/local/authorize.conf`:

```ini
[role_external_auditor]
importRoles = user
srchIndexesAllowed = compliance
srchIndexesDefault = compliance
srchJobsQuota = 2
rtSrchJobsQuota = 0
srchDiskQuota = 200
```

Apply and reload the authentication subsystem:
```bash
/opt/splunk/bin/splunk reload auth
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which directive in `authorize.conf` imports all default search permissions from the `user` role into a new custom role?  
*(Answer Format: `*********** = user`)*

<details>
<summary>💡 Need a Hint?</summary>
importRoles = user
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>importRoles = user</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{IMPORT_ROLES_INHERITANCE_SECURED}
```

---

## 🎯 TASK 4: Enforcing Search Disk Quotas (65 XP)

### 📖 Incident Details
Prevent Search Head disk exhaustion by assigning a strict 200 MB disk limit to the auditor role using `srchDiskQuota`:

```bash
/opt/splunk/bin/splunk btool authorize list role_external_auditor --debug | grep srchDiskQuota
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What parameter in `authorize.conf` specifies the maximum total disk space in Megabytes that an individual user's active search dispatch artifacts can occupy?  
*(Answer Format: `*************`)*

<details>
<summary>💡 Need a Hint?</summary>
srchDiskQuota
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>srchDiskQuota</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{SRCH_DISK_QUOTA_DISPATCH_PROTECTED}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P5-01 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{DELETE_CAPABILITY_LEAST_PRIVILEGE_AUDITED}            ║
║ [X] FLAG 2.1: FLAG{CAN_DELETE_ISOLATION_SAFEGUARD_VERIFIED}              ║
║ [X] FLAG 3.1: FLAG{IMPORT_ROLES_INHERITANCE_SECURED}                     ║
║ [X] FLAG 4.1: FLAG{SRCH_DISK_QUOTA_DISPATCH_PROTECTED}                   ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You neutralized unauthorized admin access, engineered a compliant least-privilege role, and protected the cluster from resource exhaustion.  
> **Total XP Awarded:** `+250 XP`!  
> Next Mission: **[Chapter 02: Capabilities Management & Granular Search Filters (`srchFilter`)](../05%20-%20Phase%205%20-%20Authentication,%20RBAC%20&%20Security%20Admin/Chapter_02_Capabilities_and_Search_Filters.md)**!
