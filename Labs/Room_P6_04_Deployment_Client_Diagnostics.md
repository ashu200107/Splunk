# 🎮 Room P6-04: Deployment Client Diagnostic Runbook

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P6-04: Deployment Client Diagnostic Runbook ⭐ DIFFICULTY: Med  │
│ 🎯 TOPIC: Fleet Triage, GUID Collisions & Precision Reloads             │
│ 💎 REWARD: 250 XP                                  🛡️ CATEGORY: Fleet Ops│
│ ⏱️ ESTIMATED TIME: 35 Mins                                              │
│ 🏆 PREREQUISITE: Room P6-01, Room P6-02 & Room P6-03                   │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical Fleet Mystery — The Ghost Forwarders!**  
> Over the weekend, the Linux DevOps team deployed 150 new Kubernetes worker nodes running Splunk Universal Forwarders.  
>  
> On Monday morning, the Security Operations Center (SOC) reported a critical compliance gap:  
> 1. Even though 150 worker nodes are up and running, the Deployment Server (`ds-prod-01`) reports only **1 single active deployment client**!  
> 2. The single entry on the Deployment Server dashboard is constantly flickering between different IP addresses every 2 seconds.  
> 3. Meanwhile, 30 edge forwarders in the APAC retail store network have completely stopped checking in (`lastPhoneHomeTime` > 48 hours).  
> 4. To make matters worse, an engineer ran a full `splunk reload deploy-server` on a 6,000-forwarder production cluster, triggering a massive CPU spike!  
>  
> Your mission as the Senior Splunk Fleet Administrator:  
> 1. Investigate the 150 flickering forwarders and resolve the cloned VM/container GUID collision.  
> 2. Use `btool` and CLI diagnostic tools to uncover why the APAC retail forwarders are stuck in a DNS black hole.  
> 3. Execute a precision server class reload to update security apps without destabilizing the server.  
> 4. Author a production SPL audit query for the Splunk Monitoring Console to track stale forwarders, and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Deployment Server:    ds-prod-01 (10.100.5.20:8089)                        │
│ • Flawed K8s Workers:   k8s-node-[001..150].corp.local (10.200.10.x)         │
│ • APAC Edge Forwarder:  uf-apac-retail-01 (10.250.40.12)                     │
│ • Instance Config:      /opt/splunkforwarder/etc/instance.cfg                │
│ • Client Config:        /opt/splunkforwarder/etc/system/local/               │
│                         deploymentclient.conf                                │
│ • Server Class Config:  /opt/splunk/etc/system/local/serverclass.conf        │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: Monitor Deployment Clients](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Monitordeploymentclients)  
> - 📖 [Splunk Docs: Deployment Server REST API Endpoints](https://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTdeploy)  
> - 📖 [Splunk Docs: Troubleshoot the Deployment Server](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Troubleshootthedeploymentserver)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 6.2 (Monitor deployment client connections and resolve pairing failures) & Objective 6.3 (Execute and interpret CLI commands: `splunk list deploy-clients`, `splunk show deploy-poll`, `splunk reload deploy-server`).

---

## 🎯 TASK 1: Diagnosing & Remedying the Cloned GUID Collision (75 XP)

### 📖 Incident Details
Log in to `ds-prod-01` and list the connected deployment clients:
```bash
/opt/splunk/bin/splunk list deploy-clients -auth admin:SecureSplunkPass2026!
```

You observe that only one single K8s client appears:
```text
clientName=k8s-node-042
ip=10.200.10.42
guid=FA38B920-E501-4977-9E11-21B419DC8710
lastPhoneHomeTime=1730004510
```
Two seconds later, running the same command shows:
```text
clientName=k8s-node-119
ip=10.200.10.119
guid=FA38B920-E501-4977-9E11-21B419DC8710
lastPhoneHomeTime=1730004512
```

Both hosts share the exact same GUID `FA38B920-E501-4977-9E11-21B419DC8710`!  
The container base image was created from a running container where Splunk had already generated an `instance.cfg`.

### 🛠️ Remediation Steps
1. On each affected forwarder (or in the Dockerfile/entrypoint script), remove the stale instance configuration:
   ```bash
   rm -f /opt/splunkforwarder/etc/instance.cfg
   ```
2. Restart the Universal Forwarder:
   ```bash
   /opt/splunkforwarder/bin/splunk restart
   ```
3. Verify that a brand new, unique GUID is generated:
   ```bash
   cat /opt/splunkforwarder/etc/instance.cfg
   ```
4. Check `ds-prod-01` again. All 150 clients now report as distinct entries in the client registry.

### 🚩 Flag 1 Verification
What file stores the persistent GUID on a Splunk Universal Forwarder, and what flag is generated once the collision is resolved?

<details>
<summary>💡 Need a hint?</summary>
The file is located directly in <code>$SPLUNK_HOME/etc/instance.cfg</code>. When removed, Splunk automatically generates a random UUID on the next daemon startup.
</details>

**Flag:** `FLAG{SPLUNK_GUID_CLONE_COLLISION_RESOLVED}`

---

## 🎯 TASK 2: Uncovering the Silent DNS Black Hole on Edge Clients (50 XP)

### 📖 Incident Details
Log in to the APAC retail store edge forwarder `uf-apac-retail-01`. The forwarder is running, but it has not checked in for 48 hours.

Run the diagnostic polling status command:
```bash
/opt/splunkforwarder/bin/splunk show deploy-poll -auth admin:SecureSplunkPass2026!
```
Output:
```text
Deployment Server: ds-production.amer.corp.internal:8089
Phone home interval: 600 seconds
```

Now trace the configuration layer using `btool`:
```bash
/opt/splunkforwarder/bin/splunk btool deploymentclient list --debug
```
You notice:
```text
/opt/splunkforwarder/etc/apps/ZZZ_legacy_override/local/deploymentclient.conf [deployment-client]
/opt/splunkforwarder/etc/apps/ZZZ_legacy_override/local/deploymentclient.conf targetUri = ds-production.amer.corp.internal:8089
```

Test network reachability:
```bash
nc -zv -w 3 ds-production.amer.corp.internal 8089
```
Output: `nc: getaddrinfo for host "ds-production.amer.corp.internal" port 8089: Name or service not known`

An old decommissioning script left a legacy app `ZZZ_legacy_override` that overwrote the valid production Deployment Server FQDN (`ds-prod-01.corp.local:8089`) with a non-existent internal domain!

### 🛠️ Remediation Steps
1. Remove the rogue configuration override:
   ```bash
   rm -rf /opt/splunkforwarder/etc/apps/ZZZ_legacy_override
   ```
2. Verify with `btool` that `targetUri` reverts to the enterprise baseline:
   ```bash
   /opt/splunkforwarder/bin/splunk btool deploymentclient list --debug
   ```
3. Force an immediate phoneHome poll:
   ```bash
   /opt/splunkforwarder/bin/splunk restart
   ```
4. Verify DNS and TCP connection succeed:
   ```bash
   nc -zv ds-prod-01.corp.local 8089
   ```

### 🚩 Flag 2 Verification
**Flag:** `FLAG{SPLUNK_TARGET_URI_DNS_REPAIRED}`

---

## 🎯 TASK 3: Executing Precision Targeted Server Class Reload (50 XP)

### 📖 Incident Details
You need to push a high-priority vulnerability patch to the application `Splunk_TA_linux_security` assigned to server class `SecOps_Linux_Endpoints`.  
`ds-prod-01` currently manages 6,500 clients across 45 server classes.

Running a blanket `splunk reload deploy-server` would force `ds-prod-01` to recalculate checksums and verify phoneHome status for all 6,500 clients, causing a 100% CPU lockup!

### 🛠️ Execution Steps
Execute the precision reload targeting strictly the modified server class:
```bash
/opt/splunk/bin/splunk reload deploy-server -class SecOps_Linux_Endpoints -auth admin:SecureSplunkPass2026!
```

Verify in `splunkd.log`:
```bash
tail -n 25 /opt/splunk/var/log/splunk/splunkd.log | grep -E "DeploymentServer|SecOps_Linux_Endpoints"
```
Output confirms:
```text
INFO  DeploymentServer - Reloading server class: SecOps_Linux_Endpoints. Other 44 server classes untouched.
```

### 🚩 Flag 3 Verification
What command-line flag enables selective reloading of a specific server class without impacting other classes?

<details>
<summary>💡 Need a hint?</summary>
Use <code>splunk reload deploy-server -class &lt;ClassName&gt;</code>.
</details>

**Flag:** `FLAG{SPLUNK_PRECISION_RELOAD_CLASS_ENFORCED}`

---

## 🎯 TASK 4: Authoring the Splunk Monitoring Console Stale Forwarder Audit (75 XP)

### 📖 Incident Details
The SOC manager requires an automated alert that identifies any Universal Forwarder that has failed to phone home to the Deployment Server in the last **20 minutes**.

### 🛠️ Authoring the SPL Query
Run the following query in Splunk Web:

```spl
index=_internal sourcetype=splunkd group=subpools name=deploymentServer
| stats latest(_time) as last_contact by clientName, ip, machineType
| eval minutes_since_contact=round((now() - last_contact)/60, 1)
| where minutes_since_contact > 20
| table clientName, ip, machineType, minutes_since_contact
| sort - minutes_since_contact
```

The search instantly surfaces `uf-apac-retail-02` (34.2 mins since contact) and `uf-branch-tokyo-01` (45.1 mins since contact), allowing the infrastructure team to remediate edge network drops before data loss occurs!

### 🚩 Flag 4 Verification
**Flag:** `FLAG{SPLUNK_DMC_STALE_FORWARDER_AUDITED}`

---

## 🏆 Room Summary & Operator Promotion

```text
╔══════════════════════════════════════════════════════════════════════════╗
│                    ROOM P6-04 COMPLETION CERTIFICATE                     │
╠══════════════════════════════════════════════════════════════════════════╣
│ • Task 1: Cloned GUID Collision Resolution            [75 XP]            │
│ • Task 2: Deployment Client DNS Black Hole Triage     [50 XP]            │
│ • Task 3: Precision Server Class Targeted Reload      [50 XP]            │
│ • Task 4: Monitoring Console Stale Forwarder SPL      [75 XP]            │
│                                                                          │
│ 🏅 Total Room XP Earned: 250 XP                                          │
│ 🎖️ Master Status: Splunk Deployment Diagnostic Specialist               │
╚══════════════════════════════════════════════════════════════════════════╝
```
