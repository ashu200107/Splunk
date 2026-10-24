# 🕹️ Room P3-02: The Sourcetype Taxonomy & Ingestion Surgery

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 02  
> **Difficulty:** Intermediate | **XP Reward:** `200 XP` | **Estimated Time:** 30 mins  
> **Target Scenario:** Enterprise SIEM Data Ingestion & Sourcetype Remediation  
> **Prerequisites:** Chapter 02 (Sourcetype Strategy & Best Practices)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
The SOC Director escalated a P1 ticket: **The PCI-DSS Compliance Security Dashboard is completely empty!**  
Alert searches looking for network perimeter breaches rely on the Common Information Model (CIM) data model `Network_Traffic`. Because upstream sourcetypes were misconfigured, the accelerated data models cannot identify incoming events.

Your mission is to audit the ingestion pipeline, eliminate non-standard sourcetypes, split incoming mixed syslog over UDP 514 into standard vendor sourcetypes, and eliminate orphaned `...-too_small` auto-generated entries to capture all 4 flags!

---

## 🧭 Task 1: Non-Standard Sourcetype Discovery & CIM Remediation

The edge network team onboarded a cluster of Cisco ASA firewalls with this custom stanza:

```ini
# /opt/splunkforwarder/etc/apps/fincorp_network/local/inputs.conf
[monitor:///var/log/network/cisco_firewalls/*.log]
disabled = false
index = network
sourcetype = cisco_firewall_v2
```

Because `sourcetype = cisco_firewall_v2` is non-standard, the official `Splunk_TA_cisco-asa` app ignores the data, resulting in zero extracted fields (`src_ip`, `dest_ip`, `action`).

### Question 1.1
What is the official Splunk standard sourcetype for Cisco ASA firewalls that automatically activates the Technology Add-on and CIM data models?

<details>
<summary>💡 Hint</summary>
The vendor is <code>cisco</code> and the product is <code>asa</code>. How does Splunk separate them in standard taxonomy?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Answer:</strong> <code>cisco:asa</code><br/>
<strong>Correct Stanza:</strong><br/>
<pre><code>[monitor:///var/log/network/cisco_firewalls/*.log]
disabled = false
index = network
sourcetype = cisco:asa</code></pre>
<strong>Flag 1:</strong> <code>THM{CIM_STANDARD_TAXONOMY_RESTORED}</code>
</details>

---

## 🧭 Task 2: Syslog Port 514 Dynamic Splitting

A centralized Heavy Forwarder (`hf-syslog-01`) listens for raw UDP syslog from switches, Linux servers, and Palo Alto firewalls on port 514:

```ini
# /opt/splunk/etc/apps/syslog_ingest/local/inputs.conf
[udp://514]
connection_host = dns
index = network
sourcetype = syslog
```

All incoming data is currently stamped with the generic sourcetype `syslog`. Searches for Palo Alto traffic are taking 15 minutes because Splunk has to scan all Linux and switch logs!

### Question 2.1
Configure `props.conf` and `transforms.conf` on the Heavy Forwarder to dynamically inspect incoming syslog and rewrite the sourcetype to `pan:traffic` if the log line contains `,TRAFFIC,`.

<details>
<summary>💡 Hint</summary>
In <code>props.conf</code>, apply a <code>TRANSFORMS-</code> directive under <code>[syslog]</code>. In <code>transforms.conf</code>, use <code>DEST_KEY = MetaData:Sourcetype</code> and <code>FORMAT = sourcetype::pan:traffic</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[syslog]
TRANSFORMS-palo_alto_route = force_pan_traffic</code></pre>
<strong>transforms.conf:</strong><br/>
<pre><code>[force_pan_traffic]
REGEX = ,TRAFFIC,
DEST_KEY = MetaData:Sourcetype
FORMAT = sourcetype::pan:traffic</code></pre>
<strong>Flag 2:</strong> <code>THM{DYNAMIC_SYSLOG_SOURCETYPE_ROUTING_ACTIVE}</code>
</details>

---

## 🧭 Task 3: Defeating the `...-too_small` Horror

An admin set up a file monitor for a newly launched microservice without specifying `sourcetype`:

```ini
[monitor:///var/log/microservices/auth_tokens.log]
disabled = false
index = security
```

Because `auth_tokens.log` is rotated frequently and only has 3 lines when opened, Splunk generated an ugly sourcetype:
`auth_tokens.log-too_small`

### Question 3.1
Why did Splunk append `-too_small` to the sourcetype, and what single parameter in `inputs.conf` completely prevents Splunk from guessing?

<details>
<summary>💡 Hint</summary>
When Splunk has to guess the format of a file with fewer than 100 lines, it falls back to <code>&lt;filename&gt;-too_small</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> When a file contains fewer lines than Splunk's format recognition threshold (~100 lines), Splunk's auto-detection fails and assigns the filename with a <code>-too_small</code> suffix.<br/>
<strong>Fix:</strong> Explicitly declare <code>sourcetype = fincorp:auth:tokens</code> in <code>inputs.conf</code>.<br/>
<strong>Flag 3:</strong> <code>THM{EXPLICIT_SOURCETYPE_DEFEATS_TOO_SMALL}</code>
</details>

---

## 🧭 Task 4: Case Sensitivity Audit

A junior developer runs the following search and reports that all web servers have crashed:
```spl
index=web sourcetype="Nginx:Access" | stats count
```
Result: `0 events found`.  
However, the forwarder is actively streaming 5,000 events/sec with `sourcetype = nginx:access`.

### Question 4.1
Explain why the search returned 0 events and what rule must be enforced across all Splunk apps regarding sourcetype casing.

<details>
<summary>💡 Hint</summary>
Are sourcetypes in Splunk search case-sensitive or case-insensitive?
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>Explanation:</strong> Sourcetypes in Splunk are strictly <strong>case-sensitive</strong> at search time. Searching for <code>Nginx:Access</code> will never match indexed metadata stored as <code>nginx:access</code>.<br/>
<strong>Rule:</strong> All sourcetypes must be 100% lowercase across the entire enterprise.<br/>
<strong>Flag 4:</strong> <code>THM{STRICT_LOWERCASE_SOURCETYPE_ENFORCEMENT}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `4 / 4`
- **XP Earned:** `+200 XP`
- **Key Takeaway:** You have mastered Splunk's standard sourcetype taxonomy, prevented generic `syslog` performance chokes, implemented dynamic `transforms.conf` sourcetype overrides, and eradicated case-sensitivity blindspots!
