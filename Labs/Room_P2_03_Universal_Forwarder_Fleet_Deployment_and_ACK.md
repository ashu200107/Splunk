# 🎮 Room P2-03: Universal Forwarder Fleet Rollout & ACK Hardening

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: UF Fleet Rollout & Ingestion     ⭐ DIFFICULTY: Medium        │
│ 🎯 TOPIC: UF Deployment, inputs, outputs  💎 REWARD: 200 XP            │
│ ⏱️ ESTIMATED TIME: 30 Mins                🛡️ CATEGORY: Edge Ingestion  │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Emergency Log Collection Mission!  
> The SOC just opened an incident: 20 critical Nginx edge web servers in AWS are being targeted by credential stuffing attacks.  
> Currently, none of the servers forward logs to Splunk.  
> You have 45 minutes to roll out the **Splunk Universal Forwarder (UF)**, configure `/var/log/nginx/access.log` ingestion with metadata tags (`host`, `source`, `sourcetype`, `index`), establish load-balanced S2S forwarding to the Indexer cluster on port **`9997`**, and enable **`useACK=true`**!

---

## 🗺️ Mission Architecture & Ingestion Topology

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🚀 EDGE LOG INGESTION TARGET                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Forwarder Host:    web-edge-01 (10.0.1.50)                                 │
│ • Monitored Path:    /var/log/nginx/access.log                               │
│ • Assigned Target:   index = web_security, sourcetype = nginx:access         │
│ • Primary Indexers:  10.0.2.10:9997, 10.0.2.11:9997                          │
│ • Reliability Spec:  useACK = true (Indexer Acknowledgement)                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Silent UF Installation & `user-seed.conf` (50 XP)

### 📖 Technical Recon
Download and extract the lightweight Universal Forwarder tarball:
```bash
sudo tar -xzf splunkforwarder-9.2.x-linux-2.6-amd64.tgz -C /opt
```

Create `/opt/splunkforwarder/etc/system/local/user-seed.conf`:
```ini
[user_info]
USERNAME = admin
PASSWORD = EdgeForwarderPass!2026
```

Accept license automatically:
```bash
sudo /opt/splunkforwarder/bin/splunk start --accept-license --answer-yes
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
Which command-line argument allows the Splunk administrator to silently accept the end-user license agreement during automated forwarder installation?  
*(Answer Format: --**************)*

<details>
<summary>💡 Need a Hint?</summary>
`--accept-...`
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Flag:</b> <code>--accept-license</code><br/>
Command: <code>splunk start --accept-license --answer-yes</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{ACCEPT_LICENSE_SILENT_AUTOMATION}
```

---

## 🎯 TASK 2: Input Definition (`inputs.conf`) (50 XP)

### 📖 Technical Recon
Configure the file monitor stanza in `/opt/splunkforwarder/etc/system/local/inputs.conf`:
```ini
[monitor:///var/log/nginx/access.log]
disabled = 0
index = web_security
sourcetype = nginx:access
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the exact stanza prefix used in `inputs.conf` to monitor a continuously updated log file on disk?  
*(Answer Format: `[monitor://********]`)*

<details>
<summary>💡 Need a Hint?</summary>
Starts with `[monitor://` followed by the absolute file path.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Stanza:</b> <code>[monitor:///path/to/file.log]</code><br/>
This registers the file with Splunk's file status monitor and tracks seek pointers in the fishbucket.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{MONITOR_STANZA_FILE_WATCHER}
```

---

## 🎯 TASK 3: Load-Balanced S2S Forwarding (`outputs.conf`) (50 XP)

### 📖 Technical Recon
Universal Forwarders automatically auto-load-balance across multiple indexers, switching every 30 seconds (`autoLBFrequency = 30`) to distribute ingestion evenly.

In `/opt/splunkforwarder/etc/system/local/outputs.conf`:
```ini
[tcpout]
defaultGroup = indexer_cluster

[tcpout:indexer_cluster]
server = 10.0.2.10:9997, 10.0.2.11:9997
autoLBFrequency = 30
useACK = true
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What is the default auto-load-balancing frequency (`autoLBFrequency`) in seconds, after which a Universal Forwarder seamlessly switches its S2S data stream to the next Indexer in the pool?  
*(Answer Format: `**` seconds)*

<details>
<summary>💡 Need a Hint?</summary>
Half a minute.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Default:</b> <code>30 seconds</code><br/>
Splunk switches targets on an event boundary every 30 seconds to ensure even distribution across indexer disks.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{AUTO_LB_FREQUENCY_THIRTY_SECS}
```

---

## 🎯 TASK 4: Forwarder Status Verification (50 XP)

### 📖 Technical Recon
Verify active forwarding sockets from the CLI:
```bash
sudo /opt/splunkforwarder/bin/splunk list forward-server -auth admin:EdgeForwarderPass!2026
```

Expected output:
```text
Active forwards:
    tcp://10.0.2.10:9997    STATUS: Connected
    tcp://10.0.2.11:9997    STATUS: Connected
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Which Splunk CLI command is used to display all configured forwarder target servers and their current active connection status?  
*(Answer Format: `splunk list *************`)*

<details>
<summary>💡 Need a Hint?</summary>
"forward-server"
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Command:</b> <code>splunk list forward-server</code><br/>
Displays all connected, inactive, and disabled forwarding destinations.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{SPLUNK_LIST_FORWARD_SERVER}
```

---

## 🏆 Room P2-03 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM P2-03 COMPLETE                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 200 / 200 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: UF Silent Rollout, monitor:// Stanza Definition,    │
│   autoLBFrequency 30s Load Balancing, splunk list forward-server       │
│                                                                        │
│ ➡️ NEXT ROOM: Room 01 — Heavy Forwarder Port Clash & Triage            │
└────────────────────────────────────────────────────────────────────────┘
```
