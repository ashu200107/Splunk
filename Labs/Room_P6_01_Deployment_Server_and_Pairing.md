# 🎮 Room P6-01: The Rogue Forwarder Fleet

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P6-01: The Rogue Forwarder Fleet           ⭐ DIFFICULTY: Easy-Med│
│ 🎯 TOPIC: deploymentclient.conf, serverclass.conf  💎 REWARD: 250 XP     │
│ ⏱️ ESTIMATED TIME: 35 Mins                         🛡️ CATEGORY: Fleet Ops│
│ 🏆 PREREQUISITE: Phase 5 Complete (Security Master)                    │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Fleet Ingestion Failure — Orphaned Payment Gateways!**  
> A DevOps deployment team launched 50 new Linux microservice nodes hosting the enterprise credit card processing engine.  
>  
> However, zero payment logs are arriving at the indexing tier! The SOC has confirmed that the Universal Forwarders installed on the instances are completely unconfigured:  
> 1. They have no `outputs.conf` and do not know where indexers live.  
> 2. They have never contacted the central Deployment Server (`ds-master-01:8089`).  
>  
> Your mission as the Lead Enterprise Fleet Orchestrator:  
> 1. Configure `deploymentclient.conf` to establish the `phoneHome` handshake to the Deployment Server.  
> 2. Build the baseline indexer routing app in `$SPLUNK_HOME/etc/deployment-apps/`.  
> 3. Define the `Payment_Gateways` server class with automated restart triggers.  
> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: Configure Deployment Clients](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Configuredeploymentclients)  
> - 📖 [Splunk Docs: serverclass.conf Specification](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Serverclassconf)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 6.2 (Deploy applications to target clients) & 6.3 (Configure deployment server pairing via `targetUri`).

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Deployment Server:    ds-master-01 (10.20.10.50:8089)                      │
│ • Target Forwarder:     uf-payment-01 (10.20.20.101)                         │
│ • Apps Repository:      /opt/splunk/etc/deployment-apps/                     │
│ • Server Class Config:  /opt/splunk/etc/system/local/serverclass.conf        │
│ • Client Config:        /opt/splunkforwarder/etc/system/local/               │
│                         deploymentclient.conf                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Pairing the Forwarder with the Deployment Server (60 XP)

### 📖 Incident Details
Log in to `uf-payment-01` and verify that the forwarder is currently disconnected:
```bash
/opt/splunkforwarder/bin/splunk list deploy-poll -auth admin:SplunkAdmin123!
```
Output:
```text
No deployment server configured.
```

### 🛠️ Configuration
Create `/opt/splunkforwarder/etc/system/local/deploymentclient.conf`:

```ini
[deployment-client]
phoneHomeIntervalInSecs = 60

[target-broker:deploymentServer]
targetUri = ds-master-01.corp.internal:8089
```

Restart the forwarder daemon:
```bash
/opt/splunkforwarder/bin/splunk restart
```

Verify connection establishment:
```bash
/opt/splunkforwarder/bin/splunk list deploy-poll -auth admin:SplunkAdmin123!
```
Returns: `Deployment Server: ds-master-01.corp.internal:8089`

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the name of the stanza header in `deploymentclient.conf` where the `targetUri` parameter is defined?  
*(Answer Format: `[*****************************]`)*

<details>
<summary>💡 Need a Hint?</summary>
[target-broker:deploymentServer]
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>[target-broker:deploymentServer]</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{DEPLOYMENT_CLIENT_PHONE_HOME_ESTABLISHED}
```

---

## 🎯 TASK 2: Staging the Baseline Routing App (60 XP)

### 📖 Tactical Objective
On the Deployment Server (`ds-master-01`), create a new managed application bundle named `Org_all_indexer_base` that distributes the primary `outputs.conf` pointing to the indexing cluster (`idx01:9997, idx02:9997`).

### 🛠️ Directory & Configuration Staging
On `ds-master-01`:
```bash
# 1. Create app structure
mkdir -p /opt/splunk/etc/deployment-apps/Org_all_indexer_base/default

# 2. Author outputs.conf
cat << 'EOF' > /opt/splunk/etc/deployment-apps/Org_all_indexer_base/default/outputs.conf
[tcpout]
defaultGroup = primary_indexers

[tcpout:primary_indexers]
server = 10.20.10.101:9997, 10.20.10.102:9997
useACK = true
EOF
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the exact directory name under `$SPLUNK_HOME/etc/deployment-apps/<app_name>/` where default configuration files like `outputs.conf` should reside?  
*(Answer Format: `*******`)*

<details>
<summary>💡 Need a Hint?</summary>
default
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>default</code> — Configurations in deployment-apps should always be placed in default/ so local admin overrides are preserved on clients.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{DEPLOYMENT_APP_OUTPUTS_STAGED_CLEANLY}
```

---

## 🎯 TASK 3: Mapping the Server Class with Auto-Restart (65 XP)

### 📖 Tactical Objective
Map the `Payment_Gateways` server class in `serverclass.conf` to match all payment hosts (`uf-payment-*`), deploy the `Org_all_indexer_base` app, and mandate that clients automatically restart `splunkd` after receiving the package.

### 🛠️ Configuration
On `ds-master-01`, edit `/opt/splunk/etc/system/local/serverclass.conf`:

```ini
[global]
repositoryLocation = $SPLUNK_HOME/etc/deployment-apps
targetRepositoryLocation = $SPLUNK_HOME/etc/apps

[serverClass:Payment_Gateways]
whitelist.0 = uf-payment-*
app:Org_all_indexer_base:restartSplunkd = true
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which boolean parameter syntax inside `serverclass.conf` instructs the client forwarder to restart its local `splunkd` service upon downloading an updated app?  
*(Answer Format: `***:<app_name>:************** = ****`)*

<details>
<summary>💡 Need a Hint?</summary>
app:<app_name>:restartSplunkd = true
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>app:<app_name>:restartSplunkd = true</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{SERVER_CLASS_PAYMENT_GATEWAYS_MAPPED}
```

---

## 🎯 TASK 4: Zero-Downtime Live Fleet Reload & Verification (65 XP)

### 📖 Tactical Objective
Notify the Deployment Server to re-scan `deployment-apps/` and recalculate checksums without restarting the DS host process.

### 🛠️ Execution & Verification
On `ds-master-01`:
```bash
/opt/splunk/bin/splunk reload deploy-server -auth admin:SplunkAdmin123!
```

Now monitor the client forwarder (`uf-payment-01`):
Within 60 seconds (the `phoneHome` window):
1. Client logs show:
   ```text
   INFO  DeploymentClient - Downloading app=Org_all_indexer_base
   INFO  DeploymentClient - Installed app=Org_all_indexer_base to /opt/splunkforwarder/etc/apps/
   INFO  DeploymentClient - Restarting splunkd as requested by serverclass
   ```
2. Check directory on client:
   ```bash
   ls -la /opt/splunkforwarder/etc/apps/Org_all_indexer_base/default/outputs.conf
   ```
   File exists and is active! Telemetry is now streaming to indexers on port 9997.

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the exact CLI command used to update Deployment Server checksums and deploy modified apps to clients without restarting Splunk?  
*(Answer Format: `****** ****** *************`)*

<details>
<summary>💡 Need a Hint?</summary>
splunk reload deploy-server
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>splunk reload deploy-server</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{D3PL0YM3NT_S3RV3R_FL33T_P41R3D_7721}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Client Pull Architecture**: Universal Forwarders initiate outbound connections to port 8089; the Deployment Server never connects directly to forwarders.
2. **Dedicated Staging Directory**: Managed apps live exclusively in `$SPLUNK_HOME/etc/deployment-apps/` on the DS and install into `$SPLUNK_HOME/etc/apps/` on clients.
3. **Always Reload, Don't Restart**: Use `splunk reload deploy-server` to refresh checksums instantly without severing active client polling sessions.
