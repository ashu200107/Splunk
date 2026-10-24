# 🕹️ Room P3-09: KV Store & Lookup Infiltration

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 09  
> **Difficulty:** Intermediate | **XP Reward:** `250 XP` | **Estimated Time:** 35 mins  
> **Target Scenario:** Enterprise Threat Intelligence Integration & KV Store Migration  
> **Prerequisites:** Chapter 09 (Lookups Architecture: CSV, Automatic & KV Store)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
The SOC is responding to an active cyber intrusion.  
The incident response team needs to correlate millions of network connection logs against an internal Threat Intelligence blacklist.  
However:
1. The automated asset lookup broke because the input field in application events was changed from `user_id` to `account_number`.
2. A junior analyst uploaded a massive 400 MB CSV threat list, causing Search Head memory exhaustion and triggering `max_memtable_bytes` disk-swapping alerts.
3. The automated threat containment script needs a dynamic, writeable database table to store newly discovered attacker IP addresses in real time.

Your mission is to repair the automatic lookup mapping, migrate the bloated threat list into an indexed **KV Store collection**, verify port 8191 MongoDB status, and capture all 5 administrative flags!

---

## 🧭 Task 1: Repairing Broken Automatic Lookup Mappings

The lookup definition `[customer_enrichment]` maps `account_num` from `customers.csv`:
```ini
# transforms.conf
[customer_enrichment]
filename = customers.csv
```
However, the application events provide the field as `client_account`.  
The current broken configuration in `props.conf`:
```ini
LOOKUP-customer = customer_enrichment account_num OUTPUT full_name, risk_score
```
Because the event does not contain the literal field `account_num`, zero customer details are extracted!

### Question 1.1
Fix the `LOOKUP-` directive in `props.conf` to map the event field `client_account` into the lookup key `account_num`.

<details>
<summary>💡 Hint</summary>
Use the <code>AS</code> keyword: <code>account_num AS client_account</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Correct props.conf:</strong><br/>
<pre><code>[fincorp:banking:app]
LOOKUP-customer = customer_enrichment account_num AS client_account OUTPUT full_name, risk_score</code></pre>
<strong>Flag 1:</strong> <code>THM{AUTOMATIC_LOOKUP_FIELD_ALIAS_RESTORED}</code>
</details>

---

## 🧭 Task 2: Provisioning an Enterprise KV Store (`collections.conf`)

The CISO ordered that the 400 MB flat CSV threat list be migrated to an embedded MongoDB KV Store collection named `active_threat_intel` with fields:
- `ip` (string)
- `malware_family` (string)
- `confidence_score` (number)
- `first_seen` (time)

### Question 2.1
Write the exact stanza to define this typed collection in `collections.conf`.

<details>
<summary>💡 Hint</summary>
Use <code>enforceTypes = true</code> and declare each <code>field.&lt;name&gt; = &lt;type&gt;</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>collections.conf:</strong><br/>
<pre><code>[active_threat_intel]
enforceTypes = true
field.ip = string
field.malware_family = string
field.confidence_score = number
field.first_seen = time</code></pre>
<strong>Flag 2:</strong> <code>THM{TYPED_KVSTORE_COLLECTION_PROVISIONED}</code>
</details>

---

## 🧭 Task 3: Defining the KV Store Lookup in `transforms.conf`

Now that the collection exists, you must create the lookup definition so Splunk search commands can interact with it.

### Question 3.1
Write the `transforms.conf` stanza linking lookup definition `[threat_intel_lookup]` to collection `active_threat_intel`.

<details>
<summary>💡 Hint</summary>
Specify <code>external_type = kvstore</code>, <code>collection = active_threat_intel</code>, and list the fields in <code>fields_list</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>transforms.conf:</strong><br/>
<pre><code>[threat_intel_lookup]
external_type = kvstore
collection = active_threat_intel
fields_list = _key, ip, malware_family, confidence_score, first_seen</code></pre>
<strong>Flag 3:</strong> <code>THM{KVSTORE_TRANSFORMS_BRIDGE_ACTIVATED}</code>
</details>

---

## 🧭 Task 4: Dynamic Threat Ingestion via SPL

The incident response team identified a new malicious command-and-control server:
- `ip`: `203.0.113.88`
- `malware_family`: `Emotet`
- `confidence_score`: `98`

### Question 4.1
Write the single SPL pipeline query to insert this new threat record into `threat_intel_lookup`.

<details>
<summary>💡 Hint</summary>
Generate the record using <code>| makeresults</code>, evaluate fields with <code>eval</code>, and pipe to <code>| outputlookup</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>SPL Query:</strong><br/>
<pre><code>| makeresults 
| eval ip="203.0.113.88", malware_family="Emotet", confidence_score=98, first_seen=now() 
| outputlookup threat_intel_lookup</code></pre>
<strong>Flag 4:</strong> <code>THM{DYNAMIC_SPL_OUTPUTLOOKUP_COMMIT}</code>
</details>

---

## 🧭 Task 5: Port 8191 MongoDB Health Triage

During a Search Head restart, KV Store lookups begin throwing errors:
`KV Store process (mongod) failed to initialize on port 8191!`

### Question 5.1
Where does Splunk write the diagnostic logs for the KV Store MongoDB process on Linux, and what CLI command checks whether the KV Store is healthy and in `ready` state?

<details>
<summary>💡 Hint</summary>
Log is located under <code>$SPLUNK_HOME/var/log/splunk/mongod.log</code>. CLI status is checked via <code>splunk show kvstore-status</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Log Location:</strong> <code>/opt/splunk/var/log/splunk/mongod.log</code><br/>
<strong>CLI Health Check:</strong><br/>
<pre><code>/opt/splunk/bin/splunk show kvstore-status</code></pre>
<strong>Flag 5:</strong> <code>THM{MONGOD_PORT_8191_HEALTH_VERIFIED}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+250 XP`
- **Key Takeaway:** You have mastered automatic CSV lookup mapping, engineered enterprise KV Store collections in `collections.conf`, executed dynamic SPL read/write operations, and triaged port 8191 MongoDB daemons!
