# 🎮 Room 04: HEC Token Security & Cloud Ingestion Triage

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: HEC Token Security & Cloud Triage ⭐ DIFFICULTY: Medium        │
│ 🎯 TOPIC: HTTP Event Collector & JSON API  💎 REWARD: 250 XP            │
│ ⏱️ ESTIMATED TIME: 35 Mins                 🛡️ CATEGORY: Edge & Cloud API│
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** Emergency Incident — Serverless Data Loss!  
> At 14:10 PM, the cloud engineering team launched 100 microservice containers on AWS ECS and Lambda.  
> They cannot install the Universal Forwarder binary inside ephemeral serverless containers.  
> Furthermore, developers configured an insecure, unauthenticated webhook dumping thousands of unencrypted HTTP logs into the `main` index!  
> Your mission as the enterprise administrator is to lock down HEC, enforce **TLS encryption on Port 8088**, generate a dedicated **least-privilege HEC token** restricted strictly to `cloud_telemetry`, test ingestion with `curl`, and enable **Indexer Acknowledgement (`useACK = 1`)**!

---

## 🗺️ Mission Architecture & Target Network

![Splunk HEC Architecture 3D](../assets/25_hec_architecture_3d.jpg)
*Figure 4.1: HEC High-Speed REST Ingestion (Cloud Microservices ➔ HTTPS Port 8088 ➔ Token Gate ➔ Indexer Cluster)*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET SPECIFICATIONS                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Ingestion Endpoint Host: 192.168.1.100:8088 (Splunk Indexer / HEC Engine)  │
│ • Protocol & Security:     HTTPS (TLS Enabled)                               │
│ • Target Index:            cloud_telemetry                                   │
│ • Target Sourcetype:       lambda:json                                       │
│ • Authentication Header:   Authorization: Splunk <UUID>                      │
│ • Ingestion Endpoints:     /services/collector/event                         │
│                            /services/collector/raw                           │
│                            /services/collector/ack                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Activating Global HEC & Port 8088 (60 XP)

### 📖 Scenario Context
By default, the HTTP Event Collector engine is turned off (`disabled = 1`).  
To activate HEC across the enterprise, you must declare global settings in `/opt/splunk/etc/system/local/inputs.conf`.

### 🛠️ Interactive Admin Mission
In `/opt/splunk/etc/system/local/inputs.conf`:
```ini
[http]
disabled = 0
port = 8088
enableSSL = 1
```

Restart splunkd or reload inputs:
```bash
sudo /opt/splunk/bin/splunk restart
```

Verify that port 8088 is actively listening:
```bash
sudo ss -tulpn | grep 8088
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What is the exact stanza name used in `inputs.conf` to configure global settings (port, SSL, thread limits) for the HTTP Event Collector?  
*(Answer Format: `[****]`)*

<details>
<summary>💡 Need a Hint?</summary>
A 4-letter protocol name for web traffic.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Stanza:</b> <code>[http]</code><br/>
Inside <code>/opt/splunk/etc/system/local/inputs.conf</code>:
<pre>
[http]
disabled = 0
port = 8088
enableSSL = 1
</pre>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{HEC_GLOBAL_STANZA_PORT_8088}
```

---

## 🎯 TASK 2: Generating Scoped Tokens (Least Privilege) (65 XP)

### 📖 Scenario Context
Developers requested a token. If you don't restrict the token with the **`indexes`** setting, the client can specify `index=security` or `index=audit` in their JSON payload and pollute sensitive compliance indexes!

### 🛠️ Interactive Admin Mission
Create a scoped token in `/opt/splunk/etc/system/local/inputs.conf`:
```ini
[http://aws_lambda_token]
disabled = 0
token = e8a7d3c2-4b5f-4a1e-92c8-112233445566
index = cloud_telemetry
indexes = cloud_telemetry
sourcetype = lambda:json
```

* **`index`**: Default index if omitted in the payload.
* **`indexes`**: Whitelist of permitted indexes. If the client tries to write elsewhere, Splunk rejects the payload with HTTP 400!

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
Which parameter in `[http://<token_name>]` defines the comma-separated whitelist of indexes the token is legally allowed to write to?  
*(Answer Format: `*******`)*

<details>
<summary>💡 Need a Hint?</summary>
The plural form of "index".
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Parameter:</b> <code>indexes</code><br/>
Example: <code>indexes = cloud_telemetry, cloud_dev</code>. This prevents unauthorized index spoofing.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{INDEXES_WHITELIST_LEAST_PRIVILEGE}
```

---

## 🎯 TASK 3: Ingesting Structured JSON via `curl` (65 XP)

### 📖 Scenario Context
You need to verify that your newly generated token is active and accepting data from edge microservices.

### 🛠️ Interactive Admin Mission
Execute the `curl` test from your terminal:
```bash
curl -k https://192.168.1.100:8088/services/collector/event \
   -H "Authorization: Splunk e8a7d3c2-4b5f-4a1e-92c8-112233445566" \
   -d '{
         "event": "Container initialized successfully",
         "host": "aws-lambda-worker-09",
         "fields": {
             "container_id": "c-99214",
             "runtime": "python3.12",
             "status": "HEALTHY"
         }
       }'
```

Expected Response:
```json
{"text":"Success","code":0}
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
If a developer runs `curl` with `-H "Authorization: Bearer <token>"`, what error message and HTTP status code does Splunk return?  
- [A] HTTP 200 OK
- [B] HTTP 403 Forbidden with `{"text":"Invalid token","code":4}`
- [C] HTTP 404 Not Found
- [D] HTTP 500 Internal Server Error

<details>
<summary>💡 Need a Hint?</summary>
What prefix does Splunk require in the Authorization header instead of "Bearer"?
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> [B] HTTP 403 Forbidden with <code>{"text":"Invalid token","code":4}</code>. Splunk requires the explicit prefix <code>Splunk &lt;token&gt;</code>.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{AUTHORIZATION_SPLUNK_PREFIX_MANDATORY}
```

---

## 🎯 TASK 4: Indexer Acknowledgement (`useACK = 1`) (60 XP)

### 📖 Scenario Context
In high-throughput microservices, an HTTP 200 OK only means the web server received the payload in RAM. If the Indexer crashes before writing to disk, events are lost.  
To guarantee end-to-end reliability, you enable **Indexer Acknowledgement** on the token.

### 🛠️ Interactive Admin Mission
In `/opt/splunk/etc/system/local/inputs.conf`:
```ini
[http://aws_lambda_token]
...
useACK = 1
```

When `useACK = 1` is active:
1. Client generates a random channel GUID header: `X-Splunk-Request-Channel: FE0ECFAD-13D5-401B-847D-77833BD77079`.
2. Splunk returns an `ackId`:
   ```json
   {"text":"Success","code":0,"ackId":1}
   ```
3. Client verifies completion by querying:
   ```bash
   curl -k https://192.168.1.100:8088/services/collector/ack?channel=FE0ECFAD-13D5-401B-847D-77833BD77079 \
       -H "Authorization: Splunk e8a7d3c2-4b5f-4a1e-92c8-112233445566" \
       -d '{"acks":[1]}'
   ```
4. If written to disk, Splunk returns: `{"acks":{"1":true}}`.

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
What HTTP header must the client supply when sending data to an HEC token that has `useACK = 1` enabled?  
*(Answer Format: `X-Splunk-*******-*******`)*

<details>
<summary>💡 Need a Hint?</summary>
X-Splunk-Request-...
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Header:</b> <code>X-Splunk-Request-Channel</code><br/>
This channel GUID isolates acknowledgement tracking per client connection.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{X_SPLUNK_REQUEST_CHANNEL_ACK_TRACKER}
```

---

## 🏆 Room 04 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM 04 COMPLETE                         │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 250 / 250 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Global inputs.conf [http], Token Scoping (indexes), │
│   curl JSON Payloads, Authorization Header, HEC useACK=1 Channels      │
│                                                                        │
│ 🏅 PHASE 2 CORE INGESTION MASTERED!                                    │
└────────────────────────────────────────────────────────────────────────┘
```
