# 🎮 Room P6-06: Zero-Downtime Fleet Maintenance

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P6-06: Zero-Downtime Fleet Maintenance      ⭐ DIFFICULTY: Med  │
│ 🎯 TOPIC: App Lifecycle, Restart Behaviors & Client State               │
│ 💎 REWARD: 250 XP                                  🛡️ CATEGORY: Fleet Ops│
│ ⏱️ ESTIMATED TIME: 35 Mins                                              │
│ 🏆 PREREQUISITE: Room P6-01 through Room P6-05                         │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical Operational Emergency — The Ingestion Blackout!**  
> An urgent alert has flashed across the global operations bridge:  
>  
> At 02:00 AM, the SecOps team deployed an updated threat intelligence feed (`Org_threat_intel_lookups`) containing 50,000 newly blocked malicious domains.  
>  
> Catastrophe immediately followed:  
> 1. Because `restartSplunkd = true` was carelessly enabled on the server class, **3,500 forwarders simultaneously killed their `splunkd` processes and rebooted**!  
> 2. The sudden mass disconnection of 3,500 TCP connections triggered queue backpressure, lost active tailing cursors, and flooded Indexers with TCP reconnection SYN packets.  
> 3. Worse, on 50 critical payment gateway forwarders, a newly added `inputs.conf` monitor was staged with `restartSplunkd = false`, leaving the critical audit logs completely unread!  
> 4. To top it off, a decommissioned legacy application (`Org_legacy_snmp_poller`) was unlinked from `serverclass.conf` last week, but the forwarders are **still executing the legacy poller** and polluting the network!  
>  
> Your mission as the Lead Enterprise Fleet Orchestrator:  
> 1. Triage `serverclass.conf` and configure zero-downtime hot-reloading for lookup tables.  
> 2. Enforce proper restart behaviors on input monitor stanzas to bring dormant ingestion online.  
> 3. Execute the official 3-phase de-provisioning runbook to eradicate orphaned zombie apps.  
> 4. Leverage `stateOnClient = noop` for safe external automation staging, capturing all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Deployment Server:    ds-prod-01 (10.100.5.20:8089)                        │
│ • Production Forwarder: uf-payment-gateway-01 (10.150.2.14)                  │
│ • Server Class Config:  /opt/splunk/etc/system/local/serverclass.conf        │
│ • App Repository:       /opt/splunk/etc/deployment-apps/                     │
│   ├── Org_threat_intel_lookups                                               │
│   ├── Org_payment_audit_inputs                                               │
│   └── Org_legacy_snmp_poller                                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: serverclass.conf Specification](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Serverclassconf)  
> - 📖 [Splunk Docs: Configure Client Restart & App Lifecycle Behaviors](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Serverclassconfexamples)  
> - 📖 [Splunk Docs: Manage App Deployment State on Clients](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Aboutdeploymentserver)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 6.2 (Configure application restart behaviors using `restartSplunkd` and `issueReload`) & Objective 6.3 (Manage application deployment states: `enabled`, `disabled`, and `noop`).

---

## 🎯 TASK 1: Neutralizing the Threat Intel Lookup Restart Storm (75 XP)

### 📖 Incident Details
Log in to `ds-prod-01` and view the flawed stanza in `serverclass.conf`:
```bash
grep -A 5 "Org_threat_intel_lookups" /opt/splunk/etc/system/local/serverclass.conf
```

Output:
```ini
[serverClass:Global_Forwarder_Fleet:app:Org_threat_intel_lookups]
restartSplunkd = true     <-- FATAL ERROR! Causes 3,500 forwarders to reboot on CSV updates!
stateOnClient = enabled
```

Because threat intelligence lookup tables update every 6 hours, forwarders are entering restart storms 4 times a day!

### 🛠️ Remediation Steps
1. Edit `/opt/splunk/etc/system/local/serverclass.conf`:
   ```ini
   [serverClass:Global_Forwarder_Fleet:app:Org_threat_intel_lookups]
   restartSplunkd = false
   issueReload = true
   stateOnClient = enabled
   ```
2. Trigger a targeted reload of `Global_Forwarder_Fleet`:
   ```bash
   /opt/splunk/bin/splunk reload deploy-server -class Global_Forwarder_Fleet -auth admin:SecureSplunkPass2026!
   ```
3. Inspect `splunkd.log` on `uf-payment-gateway-01`. The forwarder downloads the CSV update and applies it in-flight without interrupting active data collection.

### 🚩 Flag 1 Verification
What setting pair allows deployment clients to accept app updates with zero daemon downtime while soft-reloading configurations?

<details>
<summary>💡 Need a hint?</summary>
Set <code>restartSplunkd = false</code> and <code>issueReload = true</code>.
</details>

**Flag:** `FLAG{SPLUNK_RESTART_STORM_NEUTRALIZED}`

---

## 🎯 TASK 2: Enforcing Mandatory Restarts on Ingestion Inputs (50 XP)

### 📖 Incident Details
On `uf-payment-gateway-01`, security auditors report that audit logs in `/var/log/payment/pci_audit.log` are not reaching Splunk Indexers.

Inspect the app on the client:
```bash
ls -la /opt/splunkforwarder/etc/apps/Org_payment_audit_inputs/default/inputs.conf
```
The file exists and contains a valid monitor stanza.  
However, checking `btool` on the forwarder:
```bash
/opt/splunkforwarder/bin/splunk btool inputs list --debug | grep "pci_audit.log"
```
The stanza is **completely missing from running memory**!

Inspect `serverclass.conf` on `ds-prod-01`:
```ini
[serverClass:Payment_Gateways:app:Org_payment_audit_inputs]
restartSplunkd = false    <-- FATAL ERROR! New inputs cannot initialize without a restart!
stateOnClient = enabled
```

### 🛠️ Remediation Steps
1. Update `serverclass.conf` on `ds-prod-01` to enforce `restartSplunkd = true`:
   ```ini
   [serverClass:Payment_Gateways:app:Org_payment_audit_inputs]
   restartSplunkd = true
   stateOnClient = enabled
   ```
2. Reload the server class:
   ```bash
   /opt/splunk/bin/splunk reload deploy-server -class Payment_Gateways -auth admin:SecureSplunkPass2026!
   ```
3. Once the forwarder phones home, it restarts `splunkd`, initializes the file tailing thread, and begins ingesting PCI audit events immediately!

### 🚩 Flag 2 Verification
**Flag:** `FLAG{SPLUNK_INPUTS_RESTART_ENFORCED}`

---

## 🎯 TASK 3: Safe App De-provisioning & Purging Zombie Apps (75 XP)

### 📖 Incident Details
A legacy app `Org_legacy_snmp_poller` was unlinked from `serverclass.conf` last month.  
However, running `ps aux | grep snmp` on `uf-payment-gateway-01` shows that the forwarder is still executing the Python polling script every 60 seconds!

Splunk Deployment Server **does not delete applications from clients** merely by removing their stanza from `serverclass.conf`.

### 🛠️ Execution: The 3-Phase De-provisioning Protocol
1. **Step 1: Re-attach and Disable on Fleet:**  
   Add the app stanza back to `serverclass.conf` with `stateOnClient = disabled` and `restartSplunkd = true`:
   ```ini
   [serverClass:Payment_Gateways:app:Org_legacy_snmp_poller]
   stateOnClient = disabled
   restartSplunkd = true
   ```
2. **Step 2: Reload and Verify Fleet Deactivation:**  
   ```bash
   /opt/splunk/bin/splunk reload deploy-server -class Payment_Gateways -auth admin:SecureSplunkPass2026!
   ```
   Wait for clients to phone home. The forwarder writes `state = disabled` to `app.conf` and kills the poller thread.
3. **Step 3: Remove the Directory or Unassign:**  
   Once the fleet verifies deactivation, cleanly remove the app from `serverclass.conf`.

### 🚩 Flag 3 Verification
**Flag:** `FLAG{SPLUNK_ORPHANED_APP_PURGED}`

---

## 🎯 TASK 4: Safe Staged Delivery via `stateOnClient = noop` (50 XP)

### 📖 Incident Details
The infrastructure team uses Ansible to orchestrate compliance upgrades across 1,000 servers.  
They want the Deployment Server to deliver the configuration bundle `Org_ansible_managed_compliance` to forwarders, but **strictly prohibit Splunk from enabling or restarting the app** until Ansible executes the official enterprise cutover!

### 🛠️ Execution Steps
Configure `serverclass.conf`:
```ini
[serverClass:Enterprise_Staging:app:Org_ansible_managed_compliance]
restartSplunkd = false
stateOnClient = noop
```

Reload the class:
```bash
/opt/splunk/bin/splunk reload deploy-server -class Enterprise_Staging -auth admin:SecureSplunkPass2026!
```

Verify on target forwarders:  
The app bundle is placed in `$SPLUNK_HOME/etc/apps/Org_ansible_managed_compliance`, but the forwarder's local enabled/disabled state is untouched. Ansible retains complete orchestration control!

### 🚩 Flag 4 Verification
**Flag:** `FLAG{SPLUNK_STATE_NOOP_STAGED}`

---

## 🏆 Room Summary & Operator Promotion

```text
╔══════════════════════════════════════════════════════════════════════════╗
│                    ROOM P6-06 COMPLETION CERTIFICATE                     │
╠══════════════════════════════════════════════════════════════════════════╣
│ • Task 1: Lookup Restart Storm Neutralization         [75 XP]            │
│ • Task 2: Mandatory Inputs Restart Enforcement        [50 XP]            │
│ • Task 3: Safe De-provisioning & Zombie App Exorcism  [75 XP]            │
│ • Task 4: Staged Orchestration via stateOnClient=noop  [50 XP]            │
│                                                                          │
│ 🏅 Total Room XP Earned: 250 XP                                          │
│ 🎖️ Master Status: Splunk App Lifecycle Specialist                        │
╚══════════════════════════════════════════════════════════════════════════╝
```
