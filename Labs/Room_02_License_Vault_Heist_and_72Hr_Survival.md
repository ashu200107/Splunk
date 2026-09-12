# 🎮 Room 02: The Central License Vault Heist & 72-Hour Survival

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: The Central License Vault        ⭐ DIFFICULTY: Medium        │
│ 🎯 TOPIC: License Master, Quotas & Slaves 💎 REWARD: 250 XP            │
│ ⏱️ ESTIMATED TIME: 35 Mins                🛡️ CATEGORY: Management Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** P1 Executive Emergency!  
> At 09:15 AM, the Chief Information Security Officer (CISO) called an emergency bridge:  
> *"Our WAN link to Datacenter-West has been cut by construction crews. The Indexer cluster cannot reach our central License Master! Our SIEM is going to shut down, and we will lose all security audit logs!"*  
> The SOC is panicked. Management wants to purchase an emergency temporary license immediately.  
> As the Splunk Administrator, your job is to triage the cluster, verify the **72-hour grace period**, configure slave URIs in `server.conf`, and educate leadership on what actually happens during a license violation.

---

## 🗺️ Mission Architecture & Target Network

![License Manager 3D Cutaway](../assets/23_license_manager_3d.jpg)
*Figure 2.1: Central License Master Vault & Distributed Indexer Slaves*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET SPECIFICATIONS                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ • License Master (Vault):  192.168.1.50:8089 (Enterprise 500GB License Key)  │
│ • Indexer Slave 01:        192.168.1.101     (Reporting usage hourly)       │
│ • Indexer Slave 02:        192.168.1.102     (Reporting usage hourly)       │
│ • Heartbeat / REST Port:   HTTPS TCP 8089                                   │
│ • Built-in Grace Period:   72 Hours                                         │
│ • Warning Threshold:       5 Warnings in 30 rolling days                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Slave Pairing & `server.conf` Verification (60 XP)

### 📖 Scenario Context
Indexer Slaves do NOT have local license files installed. They hold **$0 locally** and act as "Debit Cards", communicating back to the central bank vault at `https://192.168.1.50:8089`.

### 🛠️ Interactive Admin Mission
1. To pair an Indexer Slave to the central License Master via CLI:
   ```bash
   sudo /opt/splunk/bin/splunk edit licenser-localslave \
       -master_uri https://192.168.1.50:8089 \
       -auth admin:password
   ```
2. Inspect the resulting configuration file on the Indexer:
   ```bash
   cat /opt/splunk/etc/system/local/server.conf
   ```

Expected stanza:
```ini
[license]
master_uri = https://192.168.1.50:8089
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the exact stanza name in `server.conf` where `master_uri` is defined on an Indexer Slave?  
*(Answer Format: `[*******]`)*

<details>
<summary>💡 Need a Hint?</summary>
It is a 7-letter word representing your entitlement to use the software.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Stanza:</b> <code>[license]</code><br/>
Inside <code>/opt/splunk/etc/system/local/server.conf</code>:
<pre>
[license]
master_uri = https://192.168.1.50:8089
</pre>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{SERVER_CONF_LICENSE_MASTER_URI}
```

---

## 🎯 TASK 2: The 72-Hour Disconnection Timer (65 XP)

### 📖 Scenario Context
The WAN link to the License Master is severed. Indexer Slaves cannot contact `https://192.168.1.50:8089`.  
The CISO is convinced that Splunk will stop indexing logs immediately.

### 🛠️ Technical Deep Dive
Splunk has a built-in safety net:
1. When an Indexer loses connectivity to its License Master, it enters a **72-hour grace period**.
2. During these 72 hours, **indexing runs at 100% full speed**. Zero events are dropped.
3. If connectivity is restored before 72 hours elapse, the timer resets to zero and no violation occurs.

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
If an Indexer is disconnected from its License Master for 48 hours and then connectivity is restored, how many license warnings are generated on the cluster?  
*(Answer Format: `*` warnings)*

<details>
<summary>💡 Need a Hint?</summary>
Does the disconnection exceed the 72-hour threshold?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>0 warnings</code><br/>
Because 48 hours is well within the 72-hour grace period, the slave recovers seamlessly. No warnings or violations are registered.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{SEVENTY_TWO_HOUR_UNINTERRUPTED_GRACE}
```

---

## 🎯 TASK 3: Debunking the "Data Loss" Myth (65 XP)

### 📖 Scenario Context
A massive security incident occurred yesterday, causing firewalls to emit **550 GB** of logs—exceeding the company's daily license quota of **500 GB** by 10%.  
An executive claims: *"Splunk stopped indexing our logs as soon as we passed 500 GB!"*

### 🛠️ Truth in Production
In Splunk Enterprise:
- **Indexing NEVER stops** due to license quota overages.
- Splunk writes an event to `_internal` recording a daily violation warning.
- A warning is just a yellow flag on the field.
- Only if you accumulate **5 warnings within a rolling 30-day window** does the license pool lock.
- Even when locked, **indexing continues 24/7/365**! Only user search queries via the Web UI / REST are temporarily blocked until a reset key or new license is applied.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
In Splunk Enterprise, how many daily violation warnings within a rolling 30-day window cause search functionality to be locked?  
*(Answer Format: `*` warnings)*

<details>
<summary>💡 Need a Hint?</summary>
Count the fingers on one hand!
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>5 warnings</code><br/>
On the 5th warning in a 30-day rolling period, the license state transitions to violation. Searches return "License violation: Search disabled", but indexing pipeline is NEVER throttled.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{FIVE_WARNINGS_THIRTY_DAYS_NO_DATA_LOSS}
```

---

## 🎯 TASK 4: Quota Pools & Departmental Stacks (60 XP)

### 📖 Scenario Context
The enterprise has 3 departments sharing the 500 GB license:
- **SOC / Security:** 250 GB
- **DevOps / Microservices:** 150 GB
- **IT Infrastructure:** 100 GB

If DevOps floods Splunk with debug logs and exceeds 150 GB, we want **only DevOps to be warned**, without affecting the SOC pool.

### 🛠️ Interactive Admin Mission
In the License Manager Web UI (`Settings` ➔ `Licensing` ➔ `Licenses & Pools`):
1. Create a pool named `Pool_DevOps` allocated to 150 GB.
2. Assign the DevOps indexer slaves to `Pool_DevOps`.

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the primary architectural benefit of dividing a central enterprise license into multiple Pools?  
- [A] It allows Indexers to run on Windows instead of Linux.
- [B] It isolates noisy departments so their spikes do not trigger warnings on critical departments (e.g. SOC).
- [C] It encrypts data stored on disk.
- [D] It makes searches run twice as fast.

<details>
<summary>💡 Need a Hint?</summary>
Think about noisy neighbour prevention in shared environments.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] Pool isolation prevents a noisy department from consuming the entire enterprise quota and triggering cluster-wide warnings.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{POOL_ISOLATION_NOISY_NEIGHBOR_SHIELD}
```

---

## 🏆 Room 02 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM 02 COMPLETE                         │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 250 / 250 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: server.conf master_uri, 72-Hour Disconnection Grace,│
│   5-Warning Rule, No-Data-Loss Invariant, Quota Pool Isolation         │
│                                                                        │
│ ➡️ NEXT ROOM: Room 03 — Monitoring Console: Queue Jam Triage           │
└────────────────────────────────────────────────────────────────────────┘
```
