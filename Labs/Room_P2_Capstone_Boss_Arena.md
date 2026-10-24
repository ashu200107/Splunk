# 🎮 Room P2-Capstone: The Enterprise Multi-Tier Boss Arena

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ FINAL BOSS ROOM: Enterprise Multi-Tier Arena ⭐ DIFFICULTY: Hard    │
│ 🎯 TOPIC: Full Cluster Triage & Recovery   💎 REWARD: 400 XP           │
│ ⏱️ ESTIMATED TIME: 45 Mins                 🛡️ CATEGORY: Capstone Trial │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Priority 0 — Black Friday Midnight Meltdown!  
> It is 02:00 AM on Black Friday. The company is generating $500,000 per minute in online sales.  
> Suddenly, four critical alarms light up the NOC:  
> 1. **Alarm 1:** The Heavy Forwarder crashed on restart with a port 8089 bind error, and local disks are bleeding space!  
> 2. **Alarm 2:** The Indexer Cluster ingestion has frozen with `indexQueue 100% full`.  
> 3. **Alarm 3:** A WAN outage severed communication to the License Master. Leadership fears logs are being dropped.  
> 4. **Alarm 4:** AWS Lambda checkout services are failing to send telemetry with `HTTP 403 Forbidden`.  
> You are the Lead Enterprise Splunk Architect on call. You must resolve all four outages, verify the cluster topology, and capture all 4 capstone flags!

---

## 🗺️ Mission Architecture & Target Network

![Complete Enterprise Multi-Tier Architecture 3D](../assets/27_complete_multitier_architecture_3d.jpg)
*Figure C.1: The Complete Multi-Tier Production Topology under Triage*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Forwarder Tier:       192.168.1.50 (Heavy Forwarder / Splunk Enterprise)    │
│ • Indexer Cluster:      192.168.1.101, 192.168.1.102 (S2S Port 9997, HEC 8088)│
│ • License Master:       192.168.1.200:8089 (Central Bank Vault)               │
│ • Monitoring Console:   192.168.1.10:8000 (Distributed Telemetry Hub)        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Heavy Forwarder Triage & Disk Rescue (100 XP)

### 📖 Incident Details
The Heavy Forwarder host (`192.168.1.50`) is failing to launch `splunkd` because port `8089` is collided.  
Furthermore, `df -h /opt/splunk` shows available disk space dropped from 200 GB to 10 GB in 12 hours!

### 🛠️ Hands-on Triage
1. Change the management port to `8090`:
   ```bash
   sudo /opt/splunk/bin/splunk set splunkd-port 8090
   ```
2. Inspect `/opt/splunk/etc/system/local/outputs.conf` and inject the mandatory safeguard:
   ```ini
   [indexAndForward]
   index = false
   ```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What two configurations resolved Alarm 1?  
*(Answer Format: Changed port to **** and set index = ***** in [indexAndForward])*

<details>
<summary>💡 Need a Hint?</summary>Port 8090 and index = false.</details>
<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Changed port to 8090 and set index = false in [indexAndForward]</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{HF_PORT_8090_AND_INDEX_FALSE_HERO}
```

---

## 🎯 TASK 2: Rescuing the Saturated Indexers (100 XP)

### 📖 Incident Details
In the Monitoring Console, `indexQueue` is pinned at 100% across all Indexers, while CPU utilization is only 14%.  
You run an `fio` storage benchmark and discover the virtual disks are only delivering 180 IOPS!

### 🛠️ Hands-on Triage
1. The storage engineering team hot-migrates the storage volumes to high-performance NVMe SSDs delivering **1,500 IOPS** ($\ge 1,200\text{ IOPS}$ spec).
2. You permanently disable Transparent Huge Pages (THP) via Systemd:
   ```bash
   echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
   ```
3. You verify `indexQueue` drains to 0%!

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What minimum sustained random write IOPS benchmark did you enforce to permanently clear the `indexQueue` saturation?  
*(Answer Format: `*,*** IOPS`)*

<details>
<summary>💡 Need a Hint?</summary>One thousand two hundred.</details>
<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>1,200 IOPS</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{THP_NEVER_1200_IOPS_SAN_CERTIFIED}
```

---

## 🎯 TASK 3: Defusing the License Master Outage (100 XP)

### 📖 Incident Details
A WAN outage disconnected the Indexers from `https://192.168.1.200:8089`.  
The CTO is on the phone asking if Black Friday orders are being dropped.

### 🛠️ Hands-on Triage
1. You verify the **72-hour disconnection grace period**.
2. You confirm that even if the daily license volume is exceeded, Splunk **never stops indexing incoming data**.
3. You show the executive the live indexing graphs continuing uninterrupted!

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
How many hours can the Indexers operate at 100% indexing speed without contacting the License Master before search restrictions kick in?  
*(Answer Format: `** hours`)*

<details>
<summary>💡 Need a Hint?</summary>3 full days.</details>
<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>72 hours</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{72HR_GRACE_SEVERED_WAN_DEFENDER}
```

---

## 🎯 TASK 4: Fixing the HEC AWS Lambda Gate (100 XP)

### 📖 Incident Details
AWS Lambda functions are throwing `HTTP 403 Forbidden` errors when pushing checkout events to `https://192.168.1.101:8088/services/collector/event`.

### 🛠️ Hands-on Triage
You inspect the request headers in AWS CloudWatch:
```http
Authorization: Bearer e8a7d3c2-4b5f-4a1e-92c8-112233445566
```
The developer used the standard `Bearer` keyword instead of `Splunk`!  
You update the Lambda environment variable to:
```http
Authorization: Splunk e8a7d3c2-4b5f-4a1e-92c8-112233445566
```
The endpoint immediately returns `{"text":"Success","code":0}`!

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What prefix string fixed the developer's HTTP 403 error?  
*(Answer Format: `******`)*

<details>
<summary>💡 Need a Hint?</summary>Splunk.</details>
<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Splunk</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{HEC_TOKEN_AUTHORIZATION_SPLUNK_FIX}
```

---

## 🏆 Final Boss Room Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 👑 CONGRATULATIONS, ARCHITECT! FINAL BOSS ROOM CONQUERED!               │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 400 / 400 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Production Skills Certified:                                         │
│   ✔ Heavy Forwarder Port Offset (8090) & index=false Safeguard         │
│   ✔ Storage Benchmark (1,200 IOPS) & indexQueue Recovery               │
│   ✔ 72-Hour License Disconnection Invariant                            │
│   ✔ HEC Token Authorization & Indexer Acknowledgement                  │
│                                                                        │
│ 🎓 PHASE 2 MASTERED! PROMOTED TO: Splunk Enterprise Architect (3,050 XP)│
│ 🚀 UNLOCKED: Phase 3 — Deep Data Onboarding & Parsing Pipeline         │
└────────────────────────────────────────────────────────────────────────┘
```
