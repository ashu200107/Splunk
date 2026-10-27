# 🎮 Room P6-02: Server Class Precision Surgery

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P6-02: Server Class Precision Surgery      ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: serverclass.conf, Whitelists & Filtering 💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 40 Mins                         🛡️ CATEGORY: Fleet Ops│
│ 🏆 PREREQUISITE: Room P6-01 (Deployment Server)                        │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical Fleet Incident — Configuration Contamination!**  
> An urgent change request was executed to roll out the Apache Web telemetry add-on (`Org_apache_web_inputs`) across the production web tier.  
>  
> However, an hour after deployment, alerts lit up the NOC:  
> 1. Ten production web forwarders (`pci-web-05` through `14`) never received the update because of a broken index in `serverclass.conf`!  
> 2. Windows IIS servers in the DMZ were accidentally deployed Linux shell scripts, causing forwarder startup failures!  
> 3. Staging and QA servers (`web-stg-01`) received production configurations and started routing test events into production indexes!  
>  
> Your mission as the Lead Enterprise Fleet Orchestrator:  
> 1. Repair the numerical sequencing gap in `whitelist.<n>`.  
> 2. Enforce `machineTypesFilter` to protect Windows systems.  
> 3. Deploy `blacklist.<n>` rules to isolate non-production nodes.  
> 4. Suppress daemon restarts for lookup apps and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Deployment Server:    ds-master-01 (10.200.10.50:8089)                     │
│ • Target Forwarders:    pci-web-01..14 (Linux x86_64)                        │
│ • Contaminated Nodes:   win-iis-01..04 (Windows x64), web-stg-01 (Staging)   │
│ • Configuration File:   /opt/splunk/etc/system/local/serverclass.conf        │
│ • Managed Apps:         Splunk_TA_nix, Org_apache_web_inputs,                │
│                         Org_ip_threat_lookups                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: Filter Deployment Clients](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Filterclients)  
> - 📖 [Splunk Docs: serverclass.conf Reference](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Serverclassconf)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 6.2 (Configure server classes) & Objective 6.3 (Filter clients using IP, hostname, and machine type).

---

## 🎯 TASK 1: Fixing the Whitelist Numerical Sequencing Gap (60 XP)

### 📖 Incident Details
Log in to `ds-master-01` and inspect `/opt/splunk/etc/system/local/serverclass.conf`:

```ini
[serverClass:PCI_Web_Fleet]
whitelist.0 = pci-web-01*
whitelist.1 = pci-web-02*
whitelist.3 = pci-web-*
```

Notice the gap! `whitelist.2` is missing.  
Because Splunk's parser processes `whitelist.<n>` as a contiguous zero-indexed array, it parses `.0` and `.1`, encounters the gap where `.2` should be, and **abruptly terminates whitelist evaluation**! As a result, `whitelist.3` is completely ignored, and nodes `pci-web-05` through `14` are never updated.

### 🛠️ Configuration Fix
Edit `/opt/splunk/etc/system/local/serverclass.conf` and clean up the sequence:

```ini
[serverClass:PCI_Web_Fleet]
whitelist.0 = pci-web-*
```

Validate with `btool`:
```bash
/opt/splunk/bin/splunk btool serverclass list serverClass:PCI_Web_Fleet --debug
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What integer index must all `whitelist.<n>` and `blacklist.<n>` lists start with in `serverclass.conf`?  
*(Answer Format: `*`)*

<details>
<summary>💡 Need a Hint?</summary>
0
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>0</code> — Whitelists and blacklists in Splunk configuration stanzas must strictly begin with index 0.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{WHITELIST_NUMERICAL_GAP_REPAIRED_SUCCESS}
```

---

## 🎯 TASK 2: Restricting Architectures via `machineTypesFilter` (60 XP)

### 📖 Tactical Objective
Prevent Linux bash scripts in `Splunk_TA_nix` and `Org_apache_web_inputs` from being deployed to Windows IIS forwarders.

### 🛠️ Configuration
Update `[serverClass:PCI_Web_Fleet]` in `/opt/splunk/etc/system/local/serverclass.conf`:

```ini
[serverClass:PCI_Web_Fleet]
whitelist.0 = pci-web-*
machineTypesFilter = linux-x86_64
```

Verify with CLI:
```bash
/opt/splunk/bin/splunk list deploy-clients -auth admin:SplunkAdmin123! | grep -i "utsname"
```
Windows nodes reporting `windows-x64` are instantly disqualified from the Linux server class!

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which parameter in `serverclass.conf` filters deployment clients based on their operating system hardware and CPU architecture string?  
*(Answer Format: `******************`)*

<details>
<summary>💡 Need a Hint?</summary>
machineTypesFilter
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>machineTypesFilter</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{MACHINE_TYPES_FILTER_LINUX_ISOLATED}
```

---

## 🎯 TASK 3: Quarantine Staging Nodes with Blacklists (65 XP)

### 📖 Tactical Objective
Ensure that no staging, development, or QA nodes (e.g. `pci-web-stg-01`) ever receive production configs, even if their hostname begins with `pci-web-`.

### 🛠️ Configuration
Add a blacklist rule to `serverclass.conf`:

```ini
[serverClass:PCI_Web_Fleet]
whitelist.0 = pci-web-*
blacklist.0 = *-stg-*
blacklist.1 = *-dev-*
machineTypesFilter = linux-x86_64
```

Remember: **Blacklist ALWAYS overrides Whitelist!** Any host matching `*-stg-*` is blocked unconditionally.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
In Splunk Deployment Server evaluation order, which filter takes unconditional precedence when a host matches both: Whitelist or Blacklist?  
*(Answer Format: `*********`)*

<details>
<summary>💡 Need a Hint?</summary>
Blacklist
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Blacklist</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{BLACKLIST_PRECEDENCE_STAGING_ISOLATED}
```

---

## 🎯 TASK 4: Suppressing Restarts for Lookup Bundles (65 XP)

### 📖 Tactical Objective
The app `Org_ip_threat_lookups` distributes CSV IP reputation tables every 15 minutes. Restarting `splunkd` on 200 web servers every 15 minutes disrupts live traffic monitoring.  
Configure `restartSplunkd = false` specifically for the lookup app while keeping `restartSplunkd = true` for input apps.

### 🛠️ Configuration
In `/opt/splunk/etc/system/local/serverclass.conf`:

```ini
# Input app requires restart to initialize file monitoring
[serverClass:PCI_Web_Fleet:app:Org_apache_web_inputs]
restartSplunkd = true

# Lookup app overrides server class default to avoid service bounces
[serverClass:PCI_Web_Fleet:app:Org_ip_threat_lookups]
restartSplunkd = false
```

Reload the deployment server:
```bash
/opt/splunk/bin/splunk reload deploy-server -auth admin:SplunkAdmin123!
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the final Master Flag for Room P6-02?  
*(Answer Format: `FLAG{...}`)*

<details>
<summary>💡 Need a Hint?</summary>
FLAG{S3RV3R_CL4SS_PR3C1S1ON_F1LT3R_8812}
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>FLAG{S3RV3R_CL4SS_PR3C1S1ON_F1LT3R_8812}</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{S3RV3R_CL4SS_PR3C1S1ON_F1LT3R_8812}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Strict Zero-Indexed Arrays**: Never leave gaps in `whitelist.<n>` or `blacklist.<n>`; contiguous sequencing is mandatory.
2. **Machine Type Architecture Guardrails**: Always enforce `machineTypesFilter = linux-x86_64` or `windows-x64` to prevent cross-platform script execution errors.
3. **Blacklists Trump Whitelists**: Use blacklists as a safety catch to eliminate staging, lab, or decommissioned nodes from production pushes.
4. **App-Level Override Granularity**: Set `restartSplunkd = false` on lookups and knowledge apps to prevent disruptive daemon restarts across critical production nodes.
