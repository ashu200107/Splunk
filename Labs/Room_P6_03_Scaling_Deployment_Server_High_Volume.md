# 🎮 Room P6-03: The 10,000-Node Thundering Herd

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P6-03: The 10,000-Node Thundering Herd     ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: High-Scale DS, phoneHome & Socket Tuning 💎 REWARD: 300 XP     │
│ ⏱️ ESTIMATED TIME: 45 Mins                         🛡️ CATEGORY: Fleet Ops│
│ 🏆 PREREQUISITE: Room P6-01 & Room P6-02                               │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical Performance Incident — Deployment Server Crash!**  
> Over the weekend, the cloud infrastructure team expanded the enterprise fleet from 1,000 forwarders to **10,000 forwarders**.  
>  
> At 09:00 AM on Monday, the central Deployment Server (`ds-prod-01`) suffered a complete service collapse:  
> 1. `splunkd` CPU hit 100% and stayed pinned at maximum utilization.  
> 2. The Linux kernel threw thousands of errors: `socket: too many open files (errno 24)`.  
> 3. Forwarders across the global network timed out during phoneHome polling, causing deployment operations to halt completely!  
>  
> Your mission as the Lead Enterprise Fleet Orchestrator:  
> 1. Calculate the catastrophic request rate and re-engineer `phoneHomeIntervalInSecs`.  
> 2. Package and stage the optimized `Org_all_deploymentclient` baseline app.  
> 3. Tune Linux kernel file descriptors and TCP socket recycling parameters.  
> 4. Enforce network bandwidth caps in `serverclass.conf` and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Deployment Server:    ds-prod-01 (10.100.5.20:8089)                        │
│ • Fleet Size:           10,000 Universal Forwarders                          │
│ • Deployment App:       /opt/splunk/etc/deployment-apps/                     │
│                         Org_all_deploymentclient                             │
│ • Server Class Config:  /opt/splunk/etc/system/local/serverclass.conf        │
│ • OS Limits File:       /etc/security/limits.conf                            │
│ • Kernel Sysctl File:   /etc/sysctl.conf                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Docs: Plan a Deployment Server Deployment](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Planadeployment)  
> - 📖 [Splunk Docs: Tune Deployment Client Polling Intervals](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Tunedeploymentclient)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 6.1 (Deployment server capacity planning and scaling considerations) & Objective 6.2 (Optimize polling intervals).

---

## 🎯 TASK 1: Calculating the Thundering Herd Request Rate (75 XP)

### 📖 Incident Details
Log in to `ds-prod-01` and inspect the active polling interval across the fleet:
```bash
grep -rn "phoneHomeIntervalInSecs" /opt/splunk/etc/deployment-apps/
```

Output:
```text
/opt/splunk/etc/deployment-apps/Org_all_deploymentclient/default/deploymentclient.conf:2:phoneHomeIntervalInSecs = 30
```

The DevOps team set `phoneHomeIntervalInSecs = 30` seconds!  
$$\text{Request Rate} = \frac{10,000 \text{ forwarders}}{30 \text{ seconds}} = \mathbf{333.3\text{ requests / second!}}$$

333 HTTPS REST handshakes per second completely overwhelmed `splunkd`'s HTTP listener and exhausted the Linux socket table.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
With 10,000 active forwarders and a 30-second polling interval, how many HTTP REST phoneHome requests hit the Deployment Server every minute?  
*(Answer Format: `******`)*

<details>
<summary>💡 Need a Hint?</summary>
(10000 / 30) * 60 = 20,000 requests per minute
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>20000</code> — Over 20,000 requests per minute flood the single port 8089 listener.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{THUNDERING_HERD_CALCULATION_UNMASKED}
```

---

## 🎯 TASK 2: Re-Engineering `phoneHomeIntervalInSecs` to 900s (75 XP)

### 📖 Tactical Objective
Re-calibrate the polling interval to 15 minutes (**900 seconds**) in `Org_all_deploymentclient`.  
This will drop the incoming request rate from **333.3 RPS down to 11.1 RPS**—a 96.7% reduction in load!

### 🛠️ Configuration
On `ds-prod-01`, edit `/opt/splunk/etc/deployment-apps/Org_all_deploymentclient/default/deploymentclient.conf`:

```ini
[deployment-client]
phoneHomeIntervalInSecs = 900

[target-broker:deploymentServer]
targetUri = ds-prod-01.corp.internal:8089
```

Reload the deployment server:
```bash
/opt/splunk/bin/splunk reload deploy-server -auth admin:SplunkAdmin123!
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the recommended polling interval (in seconds) for enterprise Splunk deployments managing 10,000 forwarders to maintain steady-state operations?  
*(Answer Format: `***`)*

<details>
<summary>💡 Need a Hint?</summary>
900
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>900</code> (15 minutes)
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{PHONE_HOME_POLL_INTERVAL_OPTIMIZED_900S}
```

---

## 🎯 TASK 3: Tuning Linux OS File Descriptors & Sockets (75 XP)

### 📖 Tactical Objective
Eliminate the `errno 24 Too many open files` kernel bottleneck by expanding the file descriptor ceiling and socket backlog.

### 🛠️ Step 1: Update File Descriptors (`/etc/security/limits.conf`)
```text
splunk    soft    nofile    65535
splunk    hard    nofile    65535
splunk    soft    nproc     20480
splunk    hard    nproc     20480
```

### 🛠️ Step 2: Scale Kernel TCP Sockets (`/etc/sysctl.conf`)
```ini
net.core.somaxconn = 4096
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
net.ipv4.ip_local_port_range = 1024 65535
```

Apply immediately:
```bash
sysctl -p
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What is the minimum recommended `nofile` (open file descriptors) limit for enterprise Splunk instances running high-scale management daemons?  
*(Answer Format: `*****`)*

<details>
<summary>💡 Need a Hint?</summary>
65535
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>65535</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{LINUX_SOCKET_LIMITS_EXPANDED_65535}
```

---

## 🎯 TASK 4: Throttling Bandwidth in `serverclass.conf` (75 XP)

### 📖 Tactical Objective
Prevent 10,000 forwarders from saturating the 10GbE network interface when downloading new apps simultaneously. Enforce a 15 MB/s (`15000` KB/s) aggregate download cap.

### 🛠️ Configuration
On `ds-prod-01`, edit `/opt/splunk/etc/system/local/serverclass.conf`:

```ini
[global]
repositoryLocation = $SPLUNK_HOME/etc/deployment-apps
targetRepositoryLocation = $SPLUNK_HOME/etc/apps
maxBandwidth = 15000
```

Reload deployment server:
```bash
/opt/splunk/bin/splunk reload deploy-server -auth admin:SplunkAdmin123!
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the final Master Flag for Room P6-03?  
*(Answer Format: `FLAG{...}`)*

<details>
<summary>💡 Need a Hint?</summary>
FLAG{THUND3R1NG_H3RD_SC4L3D_900S_P0LL}
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>FLAG{THUND3R1NG_H3RD_SC4L3D_900S_P0LL}</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{THUND3R1NG_H3RD_SC4L3D_900S_P0LL}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Calculate Request Rates Early**: Always evaluate $N / \text{phoneHomeIntervalInSecs}$ to predict server load before rolling out thousands of forwarders.
2. **Increase to 900s–1800s**: A 15-minute polling interval is optimal for large fleets, keeping request rates under 15 RPS.
3. **Scale the Operating System**: Set `nofile = 65535` and accelerate TCP socket reuse (`tcp_tw_reuse = 1`) to eliminate socket exhaustion.
4. **Throttle WAN Downloads**: Use `maxBandwidth` in `serverclass.conf` to protect production network pipes during major app deployments.
