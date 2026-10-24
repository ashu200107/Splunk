# 🕹️ Room P3-10: CIM Normalization Arena & Enterprise Security Setup

> **Phase 3: Data Onboarding & Parsing Pipeline** | Lab Room 10  
> **Difficulty:** Advanced | **XP Reward:** `300 XP` | **Estimated Time:** 40 mins  
> **Target Scenario:** Splunk Enterprise Security Blindspot & CIM Normalization  
> **Prerequisites:** Chapter 10 (Common Information Model & Technology Add-ons)

---

## 🎯 Mission Briefing

You are an Enterprise Splunk Detection & Ingestion Engineer at **FinCorp Global**.  
The CISO just inaugurated a brand-new **Splunk Enterprise Security (ES)** Security Operations Center.  
However, the **Notable Events Review Dashboard** shows zero alerts, even though an active adversary is launching brute-force attacks against the corporate SSL-VPN gateway!

Investigation reveals that the in-house VPN gateway logs are unnormalized:
1. IP addresses are labeled `remote_caller_ip` instead of CIM standard `src`.
2. Login outcome is logged as `RESULT=AUTH_SUCCESS` or `RESULT=AUTH_FAIL` instead of `action=success` or `action=failure`.
3. The events lack the required CIM tags: `tag=authentication` and `tag=privileged`.

Your mission is to construct the complete 4-piece CIM normalization pipeline in `props.conf`, `transforms.conf`, `eventtypes.conf`, and `tags.conf`, verify that the `Authentication` data model populates, and capture all 5 flags!

---

## 🧭 Task 1: Field Aliasing for the `Authentication` Data Model

A raw VPN event arrives as follows:
```text
2026-10-16 04:30:10 [FINCORP-VPN] AUTH_EVENT remote_caller_ip=198.51.100.77 internal_target=10.0.4.15 user_account="svc_admin" RESULT=AUTH_SUCCESS
```

The CIM `Authentication` data model requires:
- `src` (source IP address)
- `dest` (destination server IP)
- `user` (authenticated username)

### Question 1.1
Write the `FIELDALIAS-` directive in `props.conf` to map these raw fields to their CIM standard counterparts.

<details>
<summary>💡 Hint</summary>
Map <code>remote_caller_ip AS src</code>, <code>internal_target AS dest</code>, and <code>user_account AS user</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:vpn:auth]
FIELDALIAS-cim_auth = remote_caller_ip AS src, internal_target AS dest, user_account AS user</code></pre>
<strong>Flag 1:</strong> <code>THM{CIM_AUTHENTICATION_FIELDS_ALIASED}</code>
</details>

---

## 🧭 Task 2: Normalizing `action` via `EVAL-`

The CIM strictly requires that the `action` field contain either `"success"` or `"failure"`.  
The raw log outputs `RESULT=AUTH_SUCCESS` or `RESULT=AUTH_FAIL`.

### Question 2.1
Formulate the `EVAL-action` directive in `props.conf` using `case()` to translate `RESULT` into certified CIM action values.

<details>
<summary>💡 Hint</summary>
Use <code>case(RESULT=="AUTH_SUCCESS", "success", RESULT=="AUTH_FAIL", "failure", true(), "unknown")</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>props.conf:</strong><br/>
<pre><code>[fincorp:vpn:auth]
EVAL-action = case(RESULT=="AUTH_SUCCESS", "success", RESULT=="AUTH_FAIL", "failure", true(), "unknown")</code></pre>
<strong>Flag 2:</strong> <code>THM{CIM_ACTION_SUCCESS_FAILURE_NORMALIZED}</code>
</details>

---

## 🧭 Task 3: Defining the Eventtype (`eventtypes.conf`)

Before Splunk can apply tags to events, it must group matching events into an **eventtype**.

### Question 3.1
Write the stanza in `eventtypes.conf` to define `fincorp_vpn_login` for all events from `sourcetype=fincorp:vpn:auth`.

<details>
<summary>💡 Hint</summary>
Stanza syntax: <code>[eventtype_name] \n search = &lt;search_string&gt;</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>eventtypes.conf:</strong><br/>
<pre><code>[fincorp_vpn_login]
search = sourcetype=fincorp:vpn:auth</code></pre>
<strong>Flag 3:</strong> <code>THM{CIM_EVENTTYPE_VPN_LOGIN_REGISTERED}</code>
</details>

---

## 🧭 Task 4: Attaching Certified CIM Tags (`tags.conf`)

For the `Authentication` data model to recognize an event, it requires the event to carry the tag: `authentication`.

### Question 4.1
Write the `tags.conf` stanza to attach the `authentication` tag to `eventtype=fincorp_vpn_login`.

<details>
<summary>💡 Hint</summary>
Stanza syntax: <code>[eventtype=&lt;name&gt;] \n &lt;tag_name&gt; = enabled</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>tags.conf:</strong><br/>
<pre><code>[eventtype=fincorp_vpn_login]
authentication = enabled</code></pre>
<strong>Flag 4:</strong> <code>THM{AUTHENTICATION_CIM_TAG_ATTACHED}</code>
</details>

---

## 🧭 Task 5: Data Model Acceleration (DMA) Verification

Now that the complete 4-piece pipeline is in place, you must verify that the `Authentication` data model successfully captures the events.

### Question 5.1
Write the exact SPL search command using `| datamodel` to verify that `Authentication` events return counts grouped by `action`, `src`, and `user`.

<details>
<summary>💡 Hint</summary>
Syntax: <code>| datamodel Authentication Authentication search | stats count by Authentication.action, Authentication.src, Authentication.user</code>.
</details>

<details>
<summary>🔑 Solution & Flag</summary>
<strong>SPL Query:</strong><br/>
<pre><code>| datamodel Authentication Authentication search 
| stats count by Authentication.action, Authentication.src, Authentication.user</code></pre>
<strong>Flag 5:</strong> <code>THM{DATA_MODEL_ACCELERATION_AUTHENTICATION_VALIDATED}</code>
</details>

---

## 🏆 Room Summary & Badge
- **Total Flags Captured:** `5 / 5`
- **XP Earned:** `+300 XP`
- **Key Takeaway:** You have mastered end-to-end CIM normalization: `FIELDALIAS-` mapping, `EVAL-action` normalization, `eventtypes.conf` grouping, `tags.conf` taxonomic tagging, and `| datamodel` acceleration verification!
