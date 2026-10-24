# 🛡️ Chapter 06 (Phase 5): Securing Splunk Communications — End-to-End TLS/mTLS, S2S Port 9997 & Web UI PKI

> **The Splunk Administrator's Definitive Handbook** | Phase 5: Authentication, RBAC & Security Administration  
> **Day:** 44 | **Milestone:** Enterprise PKI Architecture, Mutual TLS (mTLS) & Wire-Speed Cryptography  
> **Current Rank:** Master Splunk Architect (7,600 XP) $\rightarrow$ *Promotion Target: Splunk Security & Cryptographic Architect (9,000+ XP)*  
> **Second Brain File:** `Chapter_06_Securing_Splunk_Communications_TLS.md`  
> **Interactive Cyber Range Lab:** [Room P5-06: The S2S Man-in-the-Middle Defense](../Labs/Room_P5_06_Securing_Splunk_Communications_TLS.md) `[350 XP]`

---

## 🏰 1. The Everyday Analogy: The Armored Convoy & The Two-Way Cryptographic Seal

Imagine a high-value physical security operation:

- **The Danger of Open Postcards (Cleartext Network Traffic):**  
  If bank branches transport bags of gold and transaction ledgers in open cardboard boxes on city buses (unencrypted port 9997 or port 8000), any rogue passenger with a magnifying glass (Wireshark / ARP spoofing / tap) can read passwords, credit card numbers, and intercept data in real time!
- **Level 1: The One-Way Armored Truck (One-Way TLS / Web UI):**  
  When you visit your bank branch (Splunk Web UI on port 8000), you look at the bank's front facade and check their municipal charter (Public SSL Certificate signed by a trusted Certificate Authority). You verify they are the legitimate bank, and everything you say to the teller inside is soundproofed.
- **Level 2: The Two-Way Armored Convoy (Mutual TLS / mTLS on S2S Port 9997):**  
  Now imagine an automated armored courier (Universal Forwarder) pulling up to the central vault (Indexer) to deposit cash.
  1. The vault demands: *"Show me your government badge (`clientCert`), signed by our internal Private CA, and prove your vehicle ID matches `forwarder-corp.internal`!"*
  2. Simultaneously, the courier demands: *"Before I drop a single gold bar, show me your vault license (`serverCert`), prove it hasn't expired, and let me verify your cryptographic signature!"*
  3. Both parties inspect each other's credentials simultaneously (**Mutual TLS / mTLS**). If a rogue rogue forwarder tries to dump fake poisoned data or a rogue server tries to impersonate the indexer, the vault gates slam shut!
- **The Danger of the "Default Yellow Factory Lock" (Default Splunk Certs):**  
  Splunk ships from the factory with a generic self-signed certificate (`$SPLUNK_HOME/etc/auth/default/`). It uses a well-known public private key and the default password `password`! Using default certs in production is like leaving the factory padlock on your vault—anyone who downloads Splunk can decrypt your traffic!

In Splunk Enterprise, **End-to-End TLS and Mutual TLS (mTLS)** encrypt every byte traversing the wire—from forwarder ingestion to search head map-reduce dispatch.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│               SPLUNK ENTERPRISE THREE-TIER PKI ENCRYPTION ARCHITECTURE                    │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   TIER 1: WEB UI ACCESS (HTTPS 8000)                                                      │
│   ┌────────────────┐           TLS 1.3 / HTTPS (Port 8000)        ┌───────────────────┐   │
│   │  SOC Analyst   │ ───────────────────────────────────────────> │ Splunk Search Head│   │
│   │ (Web Browser)  │   [web.conf: enableSplunkWebSSL = true]      │ (web.conf PKI)    │   │
│   └────────────────┘   [Custom Public CA / Wildcard Cert]         └─────────┬─────────┘   │
│                                                                             │             │
│   TIER 2: SPLUNKD MANAGEMENT BUS (PORT 8089)                                │             │
│   ┌───────────────────┐        Mutual TLS / mTLS (Port 8089)                │             │
│   │  Deployer / CM /  │ <───────────────────────────────────────────────────┤             │
│   │  License Manager  │   [server.conf: sslRootCAPath = rootCA.pem]         │             │
│   └───────────────────┘   [server.conf: sslVerifyServerCert = true]         │             │
│                                                                             │             │
│   TIER 3: DATA INGESTION PIPELINE (S2S PORT 9997)                           ▼             │
│   ┌────────────────────┐       Mutual S2S TLS (Port 9997)         ┌───────────────────┐   │
│   │Universal Forwarder │ ───────────────────────────────────────> │  Splunk Indexer   │   │
│   │   (UF / HF)        │   • Client Cert: uf_client.pem           │ (Peer Cluster)    │   │
│   ├────────────────────┤   • Server Cert: idx_server.pem          ├───────────────────┤   │
│   │ [outputs.conf]     │   • sslCommonNameToCheck = idx*.corp     │ [inputs.conf]     │   │
│   │ sslVerifyServerCert│   • requireClientCert = true             │ [splunktcp-ssl:   │   │
│   │   = true           │   • Internal Corporate Root CA           │  9997]            │   │
│   └────────────────────┘                                          └───────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. The 5-Step Mutual TLS (mTLS) Ingestion Handshake

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               THE 5-STEP MUTUAL TLS (mTLS) S2S INGESTION HANDSHAKE                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. TCP SYN & TLS CLIENT HELLO (Port 9997)                                               │
│    • Universal Forwarder initiates connection to Indexer:9997.                          │
│    • Sends supported TLS cipher suites (e.g. `TLS_AES_256_GCM_SHA384`, TLS 1.3).       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. SERVER HELLO & CERTIFICATE PRESENTATION                                              │
│    • Indexer responds with selected cipher and presents its `serverCert` chain.         │
│    • Indexer issues `CertificateRequest` payload demanding client certificate!          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. FORWARDER VALIDATION OF INDEXER IDENTITY                                             │
│    • UF verifies Indexer's certificate against `sslRootCAPath` (Corporate CA).          │
│    • Evaluates `sslCommonNameToCheck`: Ensures CN/SAN matches `idx*.corp.internal`.     │
│    • Checks certificate expiration dates (`NotAfter`).                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. FORWARDER CERTIFICATE PRESENTATION & MUTUAL PROOF                                    │
│    • UF presents its `clientCert` and signs a nonce using its private key.              │
│    • Indexer validates client cert against corporate root CA (`rootCA.pem`).            │
│    • Indexer evaluates `requireClientCert = true`: If valid $\rightarrow$ Handshake done!│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. ENCRYPTED S2S COOKED STREAM TRANSMISSION                                             │
│    • Ephemeral symmetric AES-256 session keys are established.                          │
│    • Log payloads travel across the wire completely impervious to packet sniffing!      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 4. Technical Deep Dive

### 4.1 The Three Independent Splunk Encryption Tiers

A common misconception among administrators is that enabling SSL in one configuration encrypts everything. In reality, Splunk has **three completely isolated encryption layers**:

| Encryption Tier | Affected Network Ports | Primary Configuration File | Certificates Used |
| :--- | :---: | :---: | :--- |
| **Tier 1: Splunk Web UI** | `8000` (or `443`) | `$SPLUNK_HOME/etc/system/local/web.conf` | Commercial Public CA (DigiCert / Let's Encrypt / Enterprise Web CA) |
| **Tier 2: Splunk-to-Splunk (S2S)**| `9997` | Forwarder: `outputs.conf`<br/>Indexer: `inputs.conf` | Internal Enterprise PKI / Private CA (Mutual TLS) |
| **Tier 3: Splunkd Management Bus**| `8089` | All Instances: `server.conf` | Internal Enterprise PKI / Private CA (Search Head $\leftrightarrow$ Indexer REST) |

---

### 4.2 Tier 1: Hardening the Splunk Web UI (Port 8000)

File: `$SPLUNK_HOME/etc/system/local/web.conf`

```ini
[settings]
# Enable HTTPS on Web Port
enableSplunkWebSSL = true

# Absolute paths to private key and certificate
privKeyPath = /opt/splunk/etc/auth/splunkweb/splunkweb_private.key
serverCert = /opt/splunk/etc/auth/splunkweb/splunkweb_cert_chain.pem

# Cryptographic Protocol Hardening
sslVersions = tls1.2, tls1.3
cipherSuite = ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256

# Enforce HTTP Strict Transport Security (HSTS)
httpStrictTransportSecurity = max-age=31536000; includeSubDomains
```

> [!IMPORTANT]
> The file `splunkweb_cert_chain.pem` must contain the **Server Certificate first**, followed immediately by any **Intermediate CA certificates**, and optionally the **Root CA certificate** in PEM format.

---

### 4.3 Tier 2: Splunk-to-Splunk (S2S) Ingestion Encryption (Port 9997)

This is the most critical pipeline in enterprise security architectures.

#### A. Indexer-Side Configuration (`inputs.conf`)
File: `$SPLUNK_HOME/etc/system/local/inputs.conf`

```ini
[splunktcp-ssl:9997]
# Certificate presented to Forwarders
serverCert = /opt/splunk/etc/auth/s2s/idx_server.pem
sslPassword = $7$PrivatePassphraseHash

# Mutual TLS Enforcement: Demand valid client certificate from Forwarder
requireClientCert = true

# Trust Store containing internal corporate Root CA
sslRootCAPath = /opt/splunk/etc/auth/s2s/corpRootCA.pem

# Minimum TLS protocol
sslVersions = tls1.2, tls1.3
```

#### B. Forwarder-Side Configuration (`outputs.conf`)
File: `$SPLUNK_HOME/etc/system/local/outputs.conf` (Universal / Heavy Forwarder)

```ini
[tcpout]
defaultGroup = encrypted_indexers

[tcpout:encrypted_indexers]
server = 10.10.20.101:9997, 10.10.20.102:9997

# Enable SSL on TCP Out
sslVersions = tls1.2, tls1.3
sslRootCAPath = /opt/splunk/etc/auth/s2s/corpRootCA.pem

# Forwarder's Client Certificate for mTLS
clientCert = /opt/splunk/etc/auth/s2s/uf_client.pem
sslPassword = $7$ForwarderPassphraseHash

# Strictly Validate the Indexer's Identity (Anti-Spoofing / Anti-MITM)
sslVerifyServerCert = true
sslCommonNameToCheck = idx*.corp.internal
```

---

### 4.4 Tier 3: Management Port Encryption (Port 8089)

File: `$SPLUNK_HOME/etc/system/local/server.conf`

```ini
[sslConfig]
enableSplunkdSSL = true
sslVersions = tls1.2, tls1.3
serverCert = /opt/splunk/etc/auth/splunkd/server.pem
sslPassword = $7$ServerPassphraseHash
sslRootCAPath = /opt/splunk/etc/auth/splunkd/corpRootCA.pem

# Enforce strict certificate verification on REST calls
sslVerifyServerCert = true
sslCommonNameToCheck = splunk-*.corp.internal
```

---

### 4.5 Production OpenSSL Certificate Generation Workflow

To build your own enterprise PKI without relying on vulnerable default certificates:

```bash
# 1. Generate Private Root CA (4096-bit RSA)
openssl genrsa -aes256 -out corpRootCA.key 4096
openssl req -x509 -new -nodes -key corpRootCA.key -sha256 -days 3650 \
  -out corpRootCA.pem -subj "/C=US/ST=Texas/O=Corp/CN=CorpRootCA"

# 2. Generate Indexer Server Private Key & CSR
openssl genrsa -out idx_server.key 2048
openssl req -new -key idx_server.key -out idx_server.csr \
  -subj "/C=US/ST=Texas/O=Corp/CN=idx01.corp.internal"

# 3. Sign Indexer Certificate with Root CA (including SAN)
openssl x509 -req -in idx_server.csr -CA corpRootCA.pem -CAkey corpRootCA.key \
  -CAcreateserial -out idx_server.crt -days 730 -sha256

# 4. Bundle Server Certificate + Key into Splunk Unified PEM
cat idx_server.crt idx_server.key corpRootCA.pem > idx_server.pem
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

### Pitfall 1: Relying on Default Splunk Shipped Certificates
- **The Anti-Pattern:** Leaving `cacert.pem` and `server.pem` in `$SPLUNK_HOME/etc/auth/` untouched.
- **The Vulnerability:** Every attacker with internet access has the private key to Splunk's default certificates! Any passive network eavesdropper on port 9997 or 8089 can decrypt enterprise traffic effortlessly.
- **The Fix:** Deploy your own dedicated Root/Intermediate CA and replace all default certificates across every tier.

### Pitfall 2: Setting `sslVerifyServerCert = false`
- **The Anti-Pattern:** Disabling server certificate verification on forwarders to "make connections work quickly."
- **The Disaster:** Forwarders blindly trust **any** certificate presented on port 9997. An attacker conducting an ARP spoofing attack can stand up a fake indexer and steal all corporate logs without triggering a single error!
- **The Fix:** Always enforce `sslVerifyServerCert = true` and lock down `sslCommonNameToCheck = idx*.corp.internal`.

### Pitfall 3: Certificate Format & Missing Chain Fractures
- **The Anti-Pattern:** Providing only the leaf certificate in `serverCert` while the signing Intermediate CA is omitted.
- **The Failure:** Forwarders reject connections with `SSL alert number 48: unknown CA` or `unable to get local issuer certificate`.
- **The Fix:** Always bundle the full trust chain: Leaf Certificate $\rightarrow$ Intermediate CA $\rightarrow$ Root CA inside the single PEM file referenced by `serverCert`.

---

## 🛠️ 6. Cyber Range Lab: The S2S Man-in-the-Middle Defense

Test your skills in the dedicated hands-on scenario:  
👉 **[Room P5-06: The S2S Man-in-the-Middle Defense](../Labs/Room_P5_06_Securing_Splunk_Communications_TLS.md)**

### Mission Brief:
- **Scenario:** A penetration testing team successfully executed an ARP cache poisoning attack between a bank forwarder (`uf-atm-01`) and the central indexing tier (`idx-corp-01`). The forwarder was connecting over unencrypted port 9997, leaking live credit card transaction streams!
- **Objective:**
  1. Inspect `/opt/splunk/etc/system/local/outputs.conf` on the forwarder and identify the insecure plaintext stanza.
  2. Implement mutual TLS (mTLS) by binding `uf_client.pem` and configuring `sslVerifyServerCert = true`.
  3. Enforce `requireClientCert = true` on the indexer's `inputs.conf`.
  4. Block rogue forwarders without corporate CA certificates and capture the flag `FLAG{MTLS_S2S_P0RT_9997_M1TM_D3F3ND3D_8841}`.

---

## 🧠 7. End-of-Chapter Self-Check Quiz

#### Q1: Which configuration file and stanza configure Splunk-to-Splunk (S2S) TLS listening parameters on the Indexer tier?
- **A)** `outputs.conf` under `[tcpout-ssl:9997]`
- **B)** `inputs.conf` under `[splunktcp-ssl:9997]`
- **C)** `server.conf` under `[s2s_ssl]`
- **D)** `web.conf` under `[splunktcp:9997]`

#### Q2: What is the primary security risk of leaving `sslVerifyServerCert = false` in `outputs.conf` on Universal Forwarders?
- **A)** Forwarders consume twice as much network bandwidth.
- **B)** Forwarders cannot compress log payloads.
- **C)** Forwarders are vulnerable to Man-in-the-Middle (MITM) attacks because they do not validate the authenticity of the indexer's certificate.
- **D)** Forwarders stop sending data after 24 hours.

#### Q3: Which setting in `inputs.conf` mandates that connecting forwarders must present a valid, trusted client certificate before being allowed to stream data into the indexer?
- **A)** `requireClientCert = true`
- **B)** `enforceMutualSSL = 1`
- **C)** `clientCertMandatory = yes`
- **D)** `verifyForwarderToken = true`

#### Q4: Why is it critical to replace the default Splunk-shipped certificates (`etc/auth/default/`) with enterprise PKI certificates?
- **A)** Default certificates expire 30 days after installation.
- **B)** The private keys to default certificates are publicly distributed with every Splunk download, rendering the encryption trivial to decrypt.
- **C)** Default certificates do not support AES-256 ciphers.
- **D)** Default certificates disable index acceleration.

#### Q5: In `web.conf`, which setting enforces modern transport security by instructing browsers to exclusively interact with Splunk Web over HTTPS for a specified duration?
- **A)** `enforceWebTLS = true`
- **B)** `httpStrictTransportSecurity` (HSTS)
- **C)** `permanentSSLCookie`
- **D)** `secureBrowserRedirect = 1`

---

### 📝 Quiz Answer Key
- **Q1: B** — `inputs.conf` under `[splunktcp-ssl:9997]` defines the listening SSL endpoint for S2S.
- **Q2: C** — Without server cert verification, forwarders will connect to any rogue server presenting any certificate.
- **Q3: A** — `requireClientCert = true` enforces mutual TLS (mTLS) on the ingestion port.
- **Q4: B** — Default certificates share a universally known private key and default passphrase, leaving traffic exposed to decryption.
- **Q5: B** — `httpStrictTransportSecurity` configures the standard HSTS security header.
