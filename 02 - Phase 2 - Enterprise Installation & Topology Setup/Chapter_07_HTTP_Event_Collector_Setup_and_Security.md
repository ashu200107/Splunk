# 📖 Chapter 07 (Phase 2): HTTP Event Collector (HEC) Setup, Tokens & Security

> **The Splunk Administrator's Handbook** | Phase 2: Enterprise Installation & Topology Setup  
> **Target Audience:** Complete Beginners to Enterprise Administrators  
> **Prerequisites:** Phase 2, Chapter 03 (Universal Forwarders) & Chapter 06 (Monitoring Console)

---

## ⚡ 1. The Master Analogy: "The VIP Fast-Pass Tollway"

Imagine an international highway toll plaza.  
Normally, trucks (Universal Forwarders) have to install a proprietary transceiver, pass through weight stations, and wait in dedicated lanes (TCP Port 9997).  
What if modern electric cars, scooters, and delivery drones (Serverless AWS Lambda, Docker containers, Kubernetes pods, Python scripts) want to send data without installing heavy hardware?  
They use the **HTTP Event Collector (HEC)**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               THE VIP FAST-PASS EXPRESS TOLLWAY METAPHOR               │
├───────────────────────────────────┬────────────────────────────────────┤
│ 🛣️ THE HEC FAST-PASS (PORT 8088)  │ 🚚 THE TRADITIONAL S2S TRUCK (9997)│
├───────────────────────────────────┼────────────────────────────────────┤
│ • Agentless (No forwarder binary).│ • Requires Universal Forwarder.    │
│ • Universal JSON/HTTP REST calls. │ • Proprietary Splunk S2S protocol. │
│ • Authenticated with a Token Key. │ • Configured via outputs.conf.     │
│ • Perfect for Cloud & Serverless. │ • Ideal for static physical VMs.   │
└───────────────────────────────────┴────────────────────────────────────┘
```

The **HTTP Event Collector (HEC)** is a high-speed, agentless REST API endpoint built directly into Splunk Enterprise and Heavy Forwarders. It enables developers, cloud services, and applications to transmit structured logs directly to Splunk over **HTTPS on Port 8088** using standard HTTP `POST` requests.

---

## 🗺️ 2. 3D Isometric HEC Architecture Blueprint

![Splunk HEC Architecture 3D](../assets/25_hec_architecture_3d.jpg)
*Figure 7.1: 3D Blueprint of Splunk HTTP Event Collector (HEC) Ingestion Funnel over HTTPS Port 8088*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌐 HEC ENTERPRISE SPECIFICATIONS                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Default Listener Port:   TCP 8088 (HTTPS/TLS)                              │
│ • Protocol:                HTTP 1.1 / HTTP 2 REST API (POST)                 │
│ • Authentication:          Authorization: Splunk <UUID_TOKEN>                │
│ • Event Endpoints:         /services/collector/event (JSON objects)          │
│                            /services/collector/raw (Raw text streams)        │
│                            /services/collector/ack (Acknowledgement status)  │
│ • Ingestion Latency:       Sub-second (In-memory token evaluation)           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 3. How HEC Operates Under the Hood

### 3.1 Global HEC Settings (`inputs.conf`)
HEC is controlled globally in `$SPLUNK_HOME/etc/system/local/inputs.conf` under the `[http]` stanza:

```ini
[http]
disabled = 0
port = 8088
enableSSL = 1
dedicatedIoThreads = 2
maxSockets = 10000
maxThreads = 0
```

* **`disabled = 0`**: Activates the HEC engine.
* **`port = 8088`**: Standard listening port.
* **`enableSSL = 1`**: Forces TLS/SSL encryption for data in transit.

---

### 3.2 Creating Individual HEC Tokens (`inputs.conf`)
Every application or team receives a unique **Token (GUID)**. This token enforces least privilege:

```ini
[http://payment_gateway_token]
disabled = 0
token = a1b2c3d4-e5f6-7890-abcd-ef1234567890
index = payment_prod
indexes = payment_prod,payment_dev
sourcetype = json:payment
useACK = 1
```

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🛡️ THE 3 GOLDEN SECURITY GATES OF AN HEC TOKEN                         │
├─────────────────┬──────────────────────────────────────────────────────┤
│ 1. Authentication│ The client must pass 'Splunk <token>' in the Header. │
│ 2. Index Boundary│ 'indexes = ...' defines which indexes the token is  │
│                 │ legally permitted to write to. Prevents data leaks!  │
│ 3. Default Tags │ 'index' and 'sourcetype' auto-tag logs if client     │
│                 │ forgets to specify them in the JSON payload.         │
└─────────────────┴──────────────────────────────────────────────────────┘
```

---

## 🧪 4. Hands-on Terminal Screencasts: Testing HEC with `curl`

### 4.1 Sending a Structured Event (`/services/collector/event`)
```bash
curl -k https://splunk-indexer:8088/services/collector/event \
   -H "Authorization: Splunk a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
   -d '{
         "event": "User login successful",
         "host": "k8s-pod-auth-77",
         "sourcetype": "auth:json",
         "fields": {
             "user": "alice",
             "status": "200",
             "region": "us-east-1"
         }
       }'
```

Expected Response from Splunk:
```json
{"text":"Success","code":0}
```

---

### 4.2 Sending Raw Logs (`/services/collector/raw`)
When microservices emit unstructured text lines rather than JSON:
```bash
curl -k https://splunk-indexer:8088/services/collector/raw \
   -H "Authorization: Splunk a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
   -d "2026-09-19 09:25:01 WARN Database connection pool exhausted on worker 04"
```

---

### 4.3 HEC Indexer Acknowledgement (`useACK = 1`)
In cloud environments, an HTTP 200 OK only means the web server received the packet. If the server crashes 1 millisecond later, the log is lost.  
When `useACK = 1` is enabled on the token:
1. The client generates a unique `X-Splunk-Request-Channel` GUID.
2. Splunk returns an `ackId` (e.g. `{"text":"Success","code":0,"ackId":1}`).
3. The client queries `/services/collector/ack?channel=<GUID>` to verify that `ackId: 1` was **physically written to disk**!

---

## 🚨 5. Real-World Administrator Troubleshooting Scenarios

### 🚨 Scenario A: "The Dreaded HTTP 403 Forbidden Error"
* **Symptom:** Developer scripts fail with `{"text":"Invalid token","code":4}`.
* **Root Cause:**
  1. Header format error: The developer used `Bearer <token>` instead of `Splunk <token>`.
  2. The token is disabled in `inputs.conf` (`disabled = 1`).
  3. Global HEC is disabled (`[http] disabled = 1`).

---

### 🚨 Scenario B: "The HTTP 400 Bad Request — Server is busy"
* **Symptom:** During high traffic, clients receive HTTP 400 errors.
* **Root Cause:** Upstream queues (`indexQueue`) are 100% full due to disk IOPS starvation. Splunk throttles incoming HTTP connections to prevent memory crashing!

---

## ⚡ 6. Rapid-Recall Flashcards

| # | Question (Front) | Answer (Back) |
| :-: | :--- | :--- |
| **01** | What is the default port used by Splunk HTTP Event Collector (HEC)? | **TCP Port 8088 (HTTPS)**. |
| **02** | What HTTP header prefix is required for HEC authentication? | **`Authorization: Splunk <UUID>`** |
| **03** | What configuration file and stanza declare HEC tokens? | **`inputs.conf`** under **`[http://<token_name>]`**. |
| **04** | Which endpoint is used to submit structured JSON events? | **`/services/collector/event`** |
| **05** | What parameter guarantees that HEC data has been written to disk? | **Indexer Acknowledgement (`useACK = 1`)**. |

---

## 🎮 Hands-On Cyber Range Challenge: Room 04 (TryHackMe / HTB Style)

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ARENA MISSION: Room 04 — HEC Token Security & Ingestion Triage      │
│ ⭐ DIFFICULTY: Medium | 💎 REWARD: 250 XP | ⏱️ TIME: 35 Mins           │
└────────────────────────────────────────────────────────────────────────┘
```

> **🚨 Incident Scenario:**  
> The DevOps team launched a serverless AWS Lambda microservice cluster.  
> The microservices cannot run the Universal Forwarder. Developers created an unauthorized HEC token writing to the `main` index without SSL.  
> You must configure global HEC on Port 8088, enforce TLS, create a restricted token scoped strictly to `index = cloud_telemetry`, and verify ingestion via `curl`!

### 🎯 Mission Checkpoint Questions

#### 1. What is the default listening port for Splunk HTTP Event Collector?
*(Answer Format: `****`)*
<details><summary>💡 Need a Hint?</summary>Eight thousand and eighty-eight.</details>
<details><summary>🔓 Reveal Answer</summary><b>Answer:</b> <code>8088</code></details>

#### 2. What keyword must precede the token inside the HTTP `Authorization` request header?
*(Answer Format: `******`)*
<details><summary>💡 Need a Hint?</summary>The name of the software!</details>
<details><summary>🔓 Reveal Answer</summary><b>Answer:</b> <code>Splunk</code> (e.g. <code>Authorization: Splunk &lt;token&gt;</code>)</details>

#### 3. What setting in `inputs.conf` enables Indexer Acknowledgement for an HEC token?
*(Answer Format: `****** = *`)*
<details><summary>💡 Need a Hint?</summary>useACK = 1</details>
<details><summary>🔓 Reveal Answer</summary><b>Answer:</b> <code>useACK = 1</code></details>

👉 **[Launch Full Interactive Lab: Room 04 & Capture All 4 Flags (250 XP)](../Labs/Room_04_HEC_Token_Security_and_JSON_Ingestion.md)**
