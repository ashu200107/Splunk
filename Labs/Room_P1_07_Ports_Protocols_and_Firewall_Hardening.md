# 🎮 Room P1-07: The Network Port Matrix & Firewall Defense

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: Network Port Matrix & Firewalls   ⭐ DIFFICULTY: Easy-Medium   │
│ 🎯 TOPIC: Ports 9997, 8089, 8000, 8191, nc💎 REWARD: 200 XP            │
│ ⏱️ ESTIMATED TIME: 30 Mins                🛡️ CATEGORY: Network Sec     │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Perimeter Lockout & Broken Connections!  
> At 06:00 AM, the network security team applied a new zero-trust firewall policy across all corporate subnets.  
> Immediately, 500 forwarders disconnected, search heads lost contact with indexers, and the Web UI became unreachable!  
> The firewall engineer says: *"Give me the exact list of ports, protocols, and source/destination directions, or everything stays blocked."*  
> Your mission as the enterprise administrator is to define the **Splunk Production Port Matrix**, test port reachability using **`nc` (Netcat)**, verify the KV Store port, and restore connectivity!

---

## 🗺️ Mission Architecture & Port Topology

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌐 SPLUNK CORE NETWORK PORT MATRIX                                          │
├───────┬──────────┬──────────────────────┬────────────────────────────────────┤
│ PORT  │ PROTOCOL │ TRAFFIC TYPE         │ SOURCE ➔ DESTINATION               │
├───────┼──────────┼──────────────────────┼────────────────────────────────────┤
│ 9997  │ TCP      │ Splunk-to-Splunk S2S │ Forwarders ➔ Indexer Peers         │
│ 8089  │ HTTPS    │ Splunkd REST API     │ Management / SH ➔ All Components   │
│ 8000  │ HTTP/S   │ Splunk Web UI        │ End Users / Admins ➔ Search Heads  │
│ 8191  │ TCP      │ App Key Value Store  │ Internal Loopback (127.0.0.1)      │
│ 8088  │ HTTPS    │ HTTP Event Collector │ App APIs / Microservices ➔ HEC     │
│ 9887  │ TCP      │ Indexer Replication  │ Indexer Peer ➔ Indexer Peer        │
└───────┴──────────┴──────────────────────┴────────────────────────────────────┘
```

---

## 🎯 TASK 1: The Splunk-to-Splunk (S2S) Ingestion Port (50 XP)

### 📖 Technical Recon
Universal Forwarders and Heavy Forwarders send raw and parsed log streams to Indexers using the proprietary **Splunk-to-Splunk (S2S)** protocol.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the standard default TCP port configured on Indexers (`inputs.conf [splunktcp://...]`) to receive log streams from forwarders?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
Four nines and a seven.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Port:</b> <code>9997</code><br/>
Configured inside <code>/opt/splunk/etc/system/local/inputs.conf</code>:
<pre>
[splunktcp://9997]
disabled = 0
</pre>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{PORT_9997_S2S_INGESTION_STANDARD}
```

---

## 🎯 TASK 2: The REST API & Management Port (50 XP)

### 📖 Technical Recon
Every administrative action—Deployment Server heartbeats, Search Head query dispatch, Monitoring Console telemetry, and License Master verification—communicates over the secure REST API port.

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which port and protocol serve as the internal Splunk management backbone (`splunkd`), listening on all Splunk Enterprise servers?  
- [A] TCP Port 80
- [B] HTTPS TCP Port 8089
- [C] UDP Port 53
- [D] TCP Port 21

<details>
<summary>💡 Need a Hint?</summary>
Think of the port used by the License Master and Search Peers.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] HTTPS TCP Port 8089. The <code>splunkd</code> daemon communicates over encrypted TLS on port 8089.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{PORT_8089_MANAGEMENT_REST_API}
```

---

## 🎯 TASK 3: The KV Store Internal Port (50 XP)

### 📖 Technical Recon
Splunk uses an embedded MongoDB instance known as the **App Key Value Store (KV Store)** for stateful lookups, search history, and alert tracking.

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What is the default TCP port utilized by the Splunk App Key Value Store (KV Store)?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
Eight-one-nine-one.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Port:</b> <code>8191</code><br/>
The KV Store binds to port 8191 on loopback (127.0.0.1) by default, or communicates cluster-wide for Search Head clustering.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{PORT_8191_APP_KV_STORE}
```

---

## 🎯 TASK 4: Netcat (`nc`) Network Validation Probe (50 XP)

### 📖 Technical Recon
Never blame Splunk software when a firewall is silently blocking a port. An administrator uses Netcat (`nc`) to verify socket reachability in 2 seconds without logging into the remote machine:

```bash
# Test TCP S2S port 9997
nc -zvw3 192.168.1.100 9997

# Test HTTPS Management port 8089
nc -zvw3 192.168.1.100 8089
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
In the command `nc -zvw3 192.168.1.100 9997`, what does the `-z` flag instruct Netcat to do?  
- [A] Compress the payload using zip.
- [B] Zero-I/O mode: poll for a listening daemon without sending any data.
- [C] Reboot the remote server.
- [D] Encrypt the connection with SSL.

<details>
<summary>💡 Need a Hint?</summary>
Does `-z` send heavy data or just scan/probe the listening state?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] Zero-I/O mode. It opens a TCP handshake to verify the port is open and immediately closes it without transmitting data.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{NETCAT_ZERO_IO_SOCKET_PROBE}
```

---

## 🏆 Room P1-07 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM P1-07 COMPLETE                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 200 / 200 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: S2S Port 9997, REST Port 8089, KV Store Port 8191, │
│   Netcat Zero-I/O Firewall Socket Probing                              │
│                                                                        │
│ 🏅 PHASE 1 CYBER RANGE COMPLETE! ALL 7 FOUNDATIONAL ROOMS CONQUERED!   │
│ ➡️ ADVANCING TO: Phase 2 Enterprise Topology & Kernel Hardening        │
└────────────────────────────────────────────────────────────────────────┘
```
