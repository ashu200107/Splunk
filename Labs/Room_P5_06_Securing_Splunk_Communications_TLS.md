# 🎮 Room P5-06: The S2S Man-in-the-Middle Defense

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P5-06: The S2S MITM Defense                ⭐ DIFFICULTY: Hard   │
│ 🎯 TOPIC: Mutual TLS (mTLS), S2S 9997 & PKI Chains 💎 REWARD: 350 XP     │
│ ⏱️ ESTIMATED TIME: 50 Mins                         🛡️ CATEGORY: Security │
│ 🏆 PREREQUISITE: Room P5-01 through Room P5-05                         │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical Cyber Threat — Ingestion Pipeline Eavesdropping!**  
> A red team security assessment identified that the primary transaction forwarder (`uf-atm-01`) was streaming unencrypted banking telemetry over TCP port 9997 to `idx-corp-01`.  
>  
> An attacker positioned on the local network segment used ARP cache poisoning to intercept cleartext cooked events. Furthermore, a rogue machine was able to inject spoofed syslog events directly into the indexer because the port did not demand a client certificate!  
>  
> Your mission as the Lead Splunk Cryptographic Architect:  
> 1. Audit the forwarder's `outputs.conf` and replace cleartext TCP with encrypted TLS.  
> 2. Configure the indexer's `inputs.conf` with `[splunktcp-ssl:9997]` and mandate client authentication (`requireClientCert = true`).  
> 3. Enforce strict server verification (`sslVerifyServerCert = true` and `sslCommonNameToCheck`).  
> 4. Verify mTLS certificate validation using OpenSSL and capture all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Indexer:              idx-corp-01 (10.150.10.101:9997)                     │
│ • Universal Forwarder:  uf-atm-01 (10.150.20.50)                             │
│ • Root CA Certificate:  /opt/splunk/etc/auth/certs/corpRootCA.pem            │
│ • Indexer Server Cert:  /opt/splunk/etc/auth/certs/idx_server.pem            │
│ • Forwarder Client Cert:/opt/splunk/etc/auth/certs/uf_client.pem             │
│ • Target Configs:       inputs.conf (Indexer) / outputs.conf (Forwarder)     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Auditing the Cleartext S2S Ingestion Stream (85 XP)

### 📖 Incident Details
Log in to `uf-atm-01` and inspect `/opt/splunkforwarder/etc/system/local/outputs.conf`:

```ini
[tcpout]
defaultGroup = indexer_cluster

[tcpout:indexer_cluster]
server = 10.150.10.101:9997
```

There are no SSL/TLS parameters defined. The Universal Forwarder connects over plain TCP, allowing anyone sniffing traffic to reconstruct sensitive raw event journals.

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the default TCP listening port used by Splunk indexers to receive Splunk-to-Splunk (S2S) forwarder data streams?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
9997
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>9997</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{CLEARTEXT_S2S_9997_VULNERABILITY_CONFIRMED}
```

---

## 🎯 TASK 2: Hardening the Indexer with Mutual TLS (`inputs.conf`) (90 XP)

### 📖 Tactical Objective
Configure `idx-corp-01` to listen on port 9997 using TLS 1.2/1.3, presenting `idx_server.pem`, and mandating mutual client certificate verification against the enterprise Root CA.

### 🛠️ Configuration
On `idx-corp-01`, edit `/opt/splunk/etc/system/local/inputs.conf`:

```ini
[splunktcp-ssl:9997]
serverCert = /opt/splunk/etc/auth/certs/idx_server.pem
sslPassword = EnterpriseKeyPassphrase2026!
sslRootCAPath = /opt/splunk/etc/auth/certs/corpRootCA.pem
requireClientCert = true
sslVersions = tls1.2, tls1.3
```

Restart or reload the input pipeline:
```bash
/opt/splunk/bin/splunk restart
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which boolean parameter in `inputs.conf` enforces mutual TLS by rejecting any forwarder connection that does not present a client certificate signed by the trusted Root CA?  
*(Answer Format: `***************** = ****`)*

<details>
<summary>💡 Need a Hint?</summary>
requireClientCert = true
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>requireClientCert = true</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{INDEXER_REQUIRE_CLIENT_CERT_MTLS_ACTIVE}
```

---

## 🎯 TASK 3: Configuring Forwarder Mutual TLS (`outputs.conf`) (85 XP)

### 📖 Tactical Objective
Equip `uf-atm-01` with its client certificate (`uf_client.pem`), specify the corporate Root CA, and enforce server hostname validation.

### 🛠️ Configuration
On `uf-atm-01`, edit `/opt/splunkforwarder/etc/system/local/outputs.conf`:

```ini
[tcpout]
defaultGroup = secure_indexers

[tcpout:secure_indexers]
server = 10.150.10.101:9997

sslVersions = tls1.2, tls1.3
sslRootCAPath = /opt/splunk/etc/auth/certs/corpRootCA.pem
clientCert = /opt/splunk/etc/auth/certs/uf_client.pem
sslPassword = ClientKeyPassphrase2026!

# Anti-Spoofing & Anti-MITM Controls
sslVerifyServerCert = true
sslCommonNameToCheck = idx-corp-01.corp.internal
```

Restart the forwarder:
```bash
/opt/splunkforwarder/bin/splunk restart
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which parameter in `outputs.conf` specifies the expected Common Name (CN) or Subject Alternative Name (SAN) of the Indexer certificate to prevent DNS spoofing attacks?  
*(Answer Format: `********************`)*

<details>
<summary>💡 Need a Hint?</summary>
sslCommonNameToCheck
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>sslCommonNameToCheck</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{FORWARDER_OUTPUTS_MTLS_SERVER_VERIFIED}
```

---

## 🎯 TASK 4: Probing the Encrypted S2S Port with OpenSSL (90 XP)

### 📖 Tactical Objective
Verify that rogue forwarders lacking a signed client certificate are immediately rejected by the indexer.

### 🛠️ Verification Execution
From an unauthorized rogue machine, attempt an SSL connection to port 9997 without presenting a client certificate:

```bash
openssl s_client -connect 10.150.10.101:9997 -CAfile /opt/splunk/etc/auth/certs/corpRootCA.pem
```

Output:
```text
CONNECTED(00000003)
depth=1 C = US, O = Corp, CN = CorpRootCA
verify return:1
depth=0 C = US, O = Corp, CN = idx-corp-01.corp.internal
verify return:1
---
Certificate chain
 0 s:C = US, O = Corp, CN = idx-corp-01.corp.internal
   i:C = US, O = Corp, CN = CorpRootCA
---
Acceptable client certificate CA names
/C=US/O=Corp/CN=CorpRootCA
---
SSL handshake has read 2145 bytes and written 320 bytes
Verification: OK
---
read:errno=104 (Connection reset by peer)
```

The indexer sent an SSL alert and immediately dropped the connection (`errno=104 Connection reset by peer`) because the client failed to provide a mutual client certificate!

Now test with the legitimate client certificate:
```bash
openssl s_client -connect 10.150.10.101:9997 \
  -CAfile /opt/splunk/etc/auth/certs/corpRootCA.pem \
  -cert /opt/splunk/etc/auth/certs/uf_client.pem \
  -key /opt/splunk/etc/auth/certs/uf_client.key
```
Handshake succeeds completely! Data flow is 100% encrypted and mutually authenticated.

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What is the standard Linux networking error code (`errno=104`) returned when an indexer abruptly terminates an SSL connection due to missing client certificate credentials?  
*(Answer Format: `*************************`)*

<details>
<summary>💡 Need a Hint?</summary>
Connection reset by peer
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>Connection reset by peer</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{MTLS_S2S_P0RT_9997_M1TM_D3F3ND3D_8841}
```

---

## 🏆 Room Summary & Key Takeaways

1. **Three Isolated Tiers**: Web UI (8000), S2S Ingestion (9997), and Splunkd Management (8089) require independent TLS certificates and configuration.
2. **Never Use Default Certs**: Splunk's default certificates are publicly compromised; always generate enterprise PKI certificates signed by an internal Root CA.
3. **Enforce Mutual TLS (mTLS)**: Setting `requireClientCert = true` on the indexer and `sslVerifyServerCert = true` on forwarders guarantees bidirectional cryptographic trust.
