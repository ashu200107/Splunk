# 🕹️ Room P3-05: The NullQueue Trash Chute & Selective Routing

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 05  
> **Difficulty:** Intermediate | **XP Reward:** `250 XP` | **Estimated Time:** 35 mins  
> **Target Scenario:** License Quota Crisis & High-Value Wire Routing  
> **Prerequisites:** Chapter 05 (Advanced Index-Time Filtering & Routing)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
At 08:00 AM, the Monitoring Console triggered an automated P1 critical alert: **The central Splunk license exceeded its 5 TB daily limit by 650 GB!**  
If the cluster incurs 5 warnings in 30 days, search capabilities will lock up enterprise-wide!

Incident investigation reveals:
1. A misconfigured Kubernetes service is broadcasting 400,000 automated healthcheck pings per minute (`GET /healthz HTTP/1.1 200 OK`) into `index=web`.
2. A high-value corporate wire transfer stream (`fincorp:wire:transfer`) is mistakenly landing in the general `index=main` instead of the compliant, restricted vault `index=pci_vault`.

Your mission is to configure surgical regex filters in `props.conf` and `transforms.conf` on the Heavy Forwarder tier to incinerate the healthcheck flood to `nullQueue`, steer wire transfers to `pci_vault`, and capture all 5 administrative flags!

---

## 🧭 Task 1: Incinerating Healthchecks via `nullQueue`

The healthcheck log lines look like this:
```text
2026-10-15 08:14:02.102 [ingress-router-04] INFO - 10.244.1.1 - - [15/Oct/2026:08:14:02 +0000] "GET /healthz HTTP/1.1" 200 4 "-" "kube-probe/1.28"
```

### Question 1.1
Write the exact `props.conf` and `transforms.conf` stanzas to match any log line containing `GET /healthz` or `kube-probe` and immediately discard it into `nullQueue`.

<details>
<summary>💡 Hint</summary>
In <code>transforms.conf</code>, set <code>DEST_KEY = queue</code> and <code>FORMAT = nullQueue</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:ingress:web]
TRANSFORMS-drop_kube_health = discard_kube_probes</code></pre>
<strong>transforms.conf:</strong><br/>
<pre><code>[discard_kube_probes]
REGEX = (GET\s+/healthz|kube-probe)
DEST_KEY = queue
FORMAT = nullQueue</code></pre>
<strong>Flag 1:</strong> <code>THM{NULLQUEUE_HEALTHCHECK_VAPORIZED_ZERO_LICENSE}</code>
</details>

---

## 🧭 Task 2: The Two-Stage Whitelist Rescue Filter

A noisy third-party database appliance generates 50 GB of mundane trace logs per day. Your security team ONLY wants to index events that contain `SECURITY_ALERT` or `UNAUTHORIZED_ACCESS`. Everything else must be discarded!

### Question 2.1
Configure the two-stage whitelist filter in `props.conf` and `transforms.conf` to discard all events by default, while rescuing only matching security events back to `indexQueue`.

<details>
<summary>💡 Hint</summary>
In <code>props.conf</code>, list the discard stanza first, followed by the rescue stanza.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[thirdparty:db:app]
TRANSFORMS-filter_whitelist = discard_all_db_logs, rescue_security_db_logs</code></pre>
<strong>transforms.conf:</strong><br/>
<pre><code>[discard_all_db_logs]
REGEX = .
DEST_KEY = queue
FORMAT = nullQueue

[rescue_security_db_logs]
REGEX = (SECURITY_ALERT|UNAUTHORIZED_ACCESS)
DEST_KEY = queue
FORMAT = indexQueue</code></pre>
<strong>Flag 2:</strong> <code>THM{TWO_STAGE_WHITELIST_RESCUE_ACTIVE}</code>
</details>

---

## 🧭 Task 3: Content-Based Index Routing (`_MetaData:Index`)

The payment gateway outputs mixed transactions:
```text
2026-10-15 08:20:00 [TXN-94021] TYPE=WIRE_TRANSFER AMOUNT=1500000.00 CURRENCY=USD
2026-10-15 08:20:01 [TXN-94022] TYPE=STANDARD_AUTH AMOUNT=12.50 CURRENCY=USD
```
Events with `TYPE=WIRE_TRANSFER` must be dynamically steered into `index=pci_vault`.

### Question 3.1
Write the `transforms.conf` stanza using `DEST_KEY = _MetaData:Index` to steer any event with `TYPE=WIRE_TRANSFER` to `pci_vault`.

<details>
<summary>💡 Hint</summary>
Set <code>DEST_KEY = _MetaData:Index</code> and <code>FORMAT = pci_vault</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>transforms.conf:</strong><br/>
<pre><code>[route_wire_transfers]
REGEX = TYPE=WIRE_TRANSFER
DEST_KEY = _MetaData:Index
FORMAT = pci_vault</code></pre>
<strong>Flag 3:</strong> <code>THM{METADATA_INDEX_ROUTED_TO_PCI_VAULT}</code>
</details>

---

## 🧭 Task 4: Defeating the "Missing Target Index" Crash

During testing, a developer added this routing rule:
```ini
[route_crypto]
REGEX = TYPE=CRYPTO
DEST_KEY = _MetaData:Index
FORMAT = crypto_vault
```
As soon as crypto events arrived, the Heavy Forwarder generated hundreds of internal error warnings in `_internal`:
`Failed to parse event: target index 'crypto_vault' does not exist!`

### Question 4.1
Why did this error occur, and where must the administrator define `[crypto_vault]` before this routing rule can safely execute?

<details>
<summary>💡 Hint</summary>
In Splunk, can an index be created dynamically by a transforms rule, or must it exist in <code>indexes.conf</code>?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> Splunk cannot dynamically create indexes on the fly. If an event is routed to an index not declared in <code>indexes.conf</code> on the Indexer cluster, Splunk will drop or reject the event and log an internal error.<br/>
<strong>Remediation:</strong> Define <code>[crypto_vault]</code> with <code>homePath</code>, <code>coldPath</code>, and <code>thawedPath</code> in <code>indexes.conf</code> on the Indexer Cluster.<br/>
<strong>Flag 4:</strong> <code>THM{INDEXES_CONF_TARGET_DECLARATION_MANDATORY}</code>
</details>

---

## 🧭 Task 5: Routing Events Across Different Indexer Clusters

Your company operates two separate Splunk indexer clusters:
1. `cluster_domestic` (US servers)
2. `cluster_international` (EU servers)

Logs from `sourcetype = fincorp:wire:transfer` containing `REGION=EMEA` must be forwarded to `cluster_international`, while all other logs stay on `cluster_domestic`.

### Question 5.1
What `DEST_KEY` in `transforms.conf` routes matching events to a specific `[tcpout:<target>]` group defined in `outputs.conf`?

<details>
<summary>💡 Hint</summary>
The key is <code>_TCP_ROUTING</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong><br/>
<pre><code>[route_emea_to_international]
REGEX = REGION=EMEA
DEST_KEY = _TCP_ROUTING
FORMAT = cluster_international</code></pre>
<strong>Flag 5:</strong> <code>THM{TCP_ROUTING_CROSS_CLUSTER_STEERING}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+250 XP`
- **Key Takeaway:** You have mastered `nullQueue` license cost optimization, two-stage whitelist rescue pipelines, `_MetaData:Index` content routing, and cross-cluster `_TCP_ROUTING`!
