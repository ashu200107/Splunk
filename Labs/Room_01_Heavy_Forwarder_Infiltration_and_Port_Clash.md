# 🎮 Room 01: The Heavy Forwarder Port Clash & Triage

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: The Heavy Forwarder Port Clash   ⭐ DIFFICULTY: Easy-Medium   │
│ 🎯 TOPIC: Forwarder Tier & Data Routing   💎 REWARD: 200 XP            │
│ ⏱️ ESTIMATED TIME: 30 Mins                🛡️ CATEGORY: Cluster Ops     │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Welcome to your first day on the enterprise operations team!  
> At 02:45 AM, an automated P1 alert woke up the on-call engineer:  
> *"CRITICAL: Heavy Forwarder daemon crashed on restart. Management port 8089 refused connection. Log forwarding to Indexer tier stalled!"*  
> To make matters worse, disk space alerts are flashing amber on the forwarder host.  
> Your mission is to enter the lab environment, identify the port collision, fix the management listener, stop the local disk overflow, and verify that clean, masked events are flowing across TCP 9997.

---

## 🗺️ Mission Architecture & Target Network

![2-VM Setup 3D Topology](../assets/21_hf_uf_indexer_3d_topology.jpg)
*Figure 1.1: 2-VM Target Architecture (HF Host: 192.168.1.50 | Indexer Host: 192.168.1.100)*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET SPECIFICATIONS                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Forwarder Host (VM 1):  192.168.1.50  (Heavy Forwarder / Splunk Enterprise)│
│ • Indexer Host (VM 2):    192.168.1.100 (Central Enterprise Indexer)         │
│ • S2S Ingestion Port:     TCP 9997                                           │
│ • Management REST Port:   Target: 8090 (Collided default: 8089)             │
│ • Web UI Port:            Disabled (CLI-only forwarder)                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Reconnaissance & Port Collision Triage (50 XP)

### 📖 Scenario Context
When deploying a Heavy Forwarder alongside other daemons or testing on a shared system, the default Splunk management port (`8089`) conflicts with an existing listener. Splunk fails to start, throwing:
```text
An error occurred: Port 8089 is already bound by another process.
Could not start splunkd.
```

### 🛠️ Interactive Admin Mission
1. Investigate active network ports listening on the Linux host:
   ```bash
   sudo ss -tulpn | grep 8089
   # or
   sudo netstat -tulpn | grep 8089
   ```
2. Identify which CLI command or configuration file changes the management port of Splunk to **`8090`** without manually editing files while the daemon is down.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What single Splunk CLI command is executed to update the management port (`splunkd-port`) to `8090`?  
*(Answer Format: `splunk set splunkd-port ****`)*

<details>
<summary>💡 Need a Hint?</summary>
The binary is `/opt/splunk/bin/splunk`. Use the subcommand `set` followed by the parameter name and the target port.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Command:</b> <code>splunk set splunkd-port 8090</code><br/>
This writes directly into <code>$SPLUNK_HOME/etc/system/local/web.conf</code> or <code>server.conf</code> under the <code>[httpServer]</code> or <code>[general]</code> stanza (<code>mgmtHostPort = 127.0.0.1:8090</code>).
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{MGMT_PORT_8090_OFFSET}
```

---

## 🎯 TASK 2: The Silent Disk Killer — `outputs.conf` Audit (50 XP)

![Heavy Forwarder Internal Engine](../assets/22_hf_core_components_3d.jpg)
*Figure 1.2: Heavy Forwarder 4-Stage Engine (Input ➔ Parsing ➔ Routing ➔ Output)*

### 📖 Scenario Context
A Heavy Forwarder runs full Splunk Enterprise binaries. By default, unless explicitly told otherwise, its indexing pipeline will write a local copy of every incoming event to its own disk (`/opt/splunk/var/lib/splunk/defaultdb`) **while also forwarding it**!  
On a 500 GB/day pipe, the HF's disk will hit 100% saturation in less than 48 hours.

### 🛠️ Interactive Admin Mission
Audit `/opt/splunk/etc/system/local/outputs.conf` on the Heavy Forwarder to ensure local indexing is completely deactivated.

```ini
[indexAndForward]
index = false

[tcpout]
defaultGroup = target_indexers

[tcpout:target_indexers]
server = 192.168.1.100:9997
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the exact stanza name and key-value pair that must be declared inside `outputs.conf` on a Heavy Forwarder to disable local disk indexing?  
*(Answer Format: `[stanzaName] key = value`)*

<details>
<summary>💡 Need a Hint?</summary>
The stanza starts with `[indexAnd...]` and the boolean value is `false`.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Configuration:</b><br/>
<code>[indexAndForward]</code><br/>
<code>index = false</code><br/>
Without this, the HF retains a copy of every event in hot/warm buckets, defeating the purpose of a stateless forwarder.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{INDEX_AND_FORWARD_INDEX_FALSE}
```

---

## 🎯 TASK 3: On-the-Wire Data Masking (PII Scrubber) (50 XP)

### 📖 Scenario Context
Compliance requires all incoming PCI-DSS payment logs to have 16-digit credit card numbers redacted **before** the data crosses the network into the Indexer cluster. Universal Forwarders cannot do this because they lack Python and regex parsing engines. The Heavy Forwarder must parse and scrub the stream in-memory.

### 🛠️ Interactive Admin Mission
In `/opt/splunk/etc/system/local/props.conf`:
```ini
[payment_gateway_logs]
TRANSFORMS-mask-cc = mask_credit_cards
# Or using SEDCMD:
SEDCMD-mask_cc = s/\d{4}-\d{4}-\d{4}-\d{4}/XXXX-XXXX-XXXX-XXXX/g
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Why can a Heavy Forwarder perform `SEDCMD` regex masking, whereas a Universal Forwarder cannot?  
*(Choose the core technical reason)*
- [A] Universal Forwarders do not have network access to port 9997.
- [B] Universal Forwarders lack the Python engine and full parsing pipeline binaries.
- [C] Universal Forwarders are only supported on Windows.
- [D] Universal Forwarders can only read CSV files.

<details>
<summary>💡 Need a Hint?</summary>
Remember the binary footprint: UF is a lightweight ~50MB C/C++ binary; HF is full ~600MB Splunk Enterprise with an embedded Python interpreter.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] Universal Forwarders lack the Python runtime and parsing pipeline libraries. They only read raw bytes from disk/sockets and package them into chunks.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{HF_EMBEDDED_PYTHON_PARSING_POWER}
```

---

## 🎯 TASK 4: Validating the Live S2S Stream (50 XP)

### 📖 Scenario Context
You've changed the port to `8090`, verified `index = false`, and configured the forwarding target to `192.168.1.100:9997`. Now, verify that the TCP Splunk-to-Splunk (S2S) connection is established and healthy.

### 🛠️ Interactive Admin Mission
Execute the verification command:
```bash
sudo /opt/splunk/bin/splunk list forward-server -auth admin:password
```

Expected Output:
```text
Active forwards:
    tcp://192.168.1.100:9997     STATUS: Connected
Configured but inactive forwards:
    None
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
If the status shows `Configured but inactive forwards: tcp://192.168.1.100:9997`, which command should you run from the HF terminal to test if the remote Indexer is actually listening on port 9997?  
*(Answer Format: `nc -zvw3 ***.***.***.*** ****`)*

<details>
<summary>💡 Need a Hint?</summary>
Use Netcat (`nc`) with zero-I/O (`-z`), verbose (`-v`), and a 3-second timeout (`-w3`).
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Command:</b> <code>nc -zvw3 192.168.1.100 9997</code><br/>
If it returns <code>Connection refused</code> or times out, check if <code>inputs.conf</code> on the Indexer has <code>[splunktcp://9997]</code> enabled or if an AWS Security Group / UFW firewall is blocking TCP 9997.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{NETCAT_S2S_PORT_9997_PROBE}
```

---

## 🏆 Room 01 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM 01 COMPLETE                         │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 200 / 200 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Port 8090 Offset, index=false Safeguard,           │
│   In-Memory Regex Masking, Netcat S2S Ingestion Testing                │
│                                                                        │
│ ➡️ NEXT ROOM: Room 02 — The Central License Vault Heist                │
└────────────────────────────────────────────────────────────────────────┘
```
