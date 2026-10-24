# 🎮 Room P4-02: Transforming Commands Arena

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P4-02: Transforming Commands Arena        ⭐ DIFFICULTY: Medium │
│ 🎯 TOPIC: stats, chart, timechart, top & rare      💎 REWARD: 200 XP     │
│ ⏱️ ESTIMATED TIME: 35 Mins                         🛡️ CATEGORY: SPL Ops │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Priority 1 — Payment Gateway Degraded Performance!**  
> FinCorp’s core payment gateway (`index=payment sourcetype=payment:gateway`) is encountering latency spikes and dropped settlement orders.  
> The Head of Payment Operations requires four real-time analytical reports to present to executive leadership:  
> 1. P95 latency and failure volume per gateway provider.
> 2. A 2D cross-tabulation matrix of transaction status codes across payment providers.
> 3. An hourly timechart showing transaction velocity normalized to events-per-minute.
> 4. Outlier analysis revealing the rarest error codes in the environment.
>
> You are the Principal Splunk Architect on site. You must craft the transforming SPL queries and extract all 4 operational flags!

---

## 🗺️ Mission Architecture & Target Environment

![Transforming Commands 3D Engine](file:///home/venom/.gemini/antigravity/brain/622ecdda-f824-4deb-bcf2-e1c6985dfd9a/splunk_transforming_commands_stats_chart_3d_1792229962599.jpg)
*Figure P4-2.1: Transforming Commands Architecture & Map-Reduce Aggregation Engine.*

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET DATASET SCHEMA                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Index / Sourcetype:   index=payment sourcetype=payment:gateway             │
│ • Sample Fields:        provider (Visa, Mastercard, Amex, Swift, SEPA)       │
│                         status (APPROVED, DECLINED, TIMEOUT, SYSTEM_ERR)     │
│                         latency_ms (Numeric latency in milliseconds)         │
│                         error_code (ERR_01, ERR_88, ERR_TIMEOUT, etc.)       │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: SLA Latency & Failure Volume with `stats` (50 XP)

### 📖 Incident Details
Calculate the total transaction count, total declined transactions, average latency, and 95th percentile latency (`p95`) for each payment `provider`:

```spl
index=payment sourcetype=payment:gateway
| stats count AS total_tx,
        count(eval(status!="APPROVED")) AS failed_tx,
        avg(latency_ms) AS avg_latency,
        perc95(latency_ms) AS p95_latency
        BY provider
| eval p95_latency = round(p95_latency, 2), avg_latency = round(avg_latency, 2)
| sort - failed_tx
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
Which statistical aggregation function evaluates the 95th percentile value in `stats` to eliminate extreme outliers from SLA latency calculations?  
*(Answer Format: `******(**)`)*

<details>
<summary>💡 Need a Hint?</summary>
perc95()
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>perc95()</code>
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{STATS_PERC95_SLA_PRECISION_ACHIEVED}
```

---

## 🎯 TASK 2: 2D Cross-Tabulation Matrix with `chart` (50 XP)

### 📖 Incident Details
The Operations director wants a 2-dimensional grid showing the transaction count where rows represent `provider` and column headers represent `status`:

```spl
index=payment sourcetype=payment:gateway
| chart count OVER provider BY status limit=10 useother=f
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What parameter in the `chart` command ensures that categories beyond the top 10 are NOT bundled into a generic `OTHER` column?  
*(Answer Format: `********=*`)*

<details>
<summary>💡 Need a Hint?</summary>
useother=f
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>useother=f</code>
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{CHART_2D_MATRIX_USEOTHER_FALSE}
```

---

## 🎯 TASK 3: Continuous Rate Normalization with `timechart` (50 XP)

### 📖 Incident Details
Construct a time series graph displaying transaction volume in 1-hour increments, split by `provider`. Furthermore, normalize the rate to display the transaction count **per minute** within each hour bucket:

```spl
index=payment sourcetype=payment:gateway
| timechart span=1h per_minute(eval(status=="APPROVED")) AS approved_per_min BY provider
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
Which built-in `timechart` rate normalization function converts event counts within an arbitrary span interval into a standardized per-minute frequency?  
*(Answer Format: `**********()`)*

<details>
<summary>💡 Need a Hint?</summary>
per_minute()
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>per_minute()</code>
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{TIMECHART_PER_MINUTE_VELOCITY_STANDARDIZED}
```

---

## 🎯 TASK 4: Uncovering Stealth Outliers with `rare` (50 XP)

### 📖 Incident Details
Attackers frequently trigger uncommon, edge-case error codes to probe for vulnerabilities. Discover the least frequent `error_code` occurrences across each payment provider:

```spl
index=payment sourcetype=payment:gateway status!="APPROVED"
| rare limit=5 error_code by provider
```

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Which transforming command functions as the exact inverse of `top`, returning the least common values and their percentages in a dataset?  
*(Answer Format: `****`)*

<details>
<summary>💡 Need a Hint?</summary>
rare
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>rare</code>
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{RARE_ANOMALY_OUTLIER_DISCOVERY}
```

---

## 🏆 Final Room Clearance

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               ROOM P4-02 MISSION CLEARANCE TROPHY                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [X] FLAG 1.1: FLAG{STATS_PERC95_SLA_PRECISION_ACHIEVED}                  ║
║ [X] FLAG 2.1: FLAG{CHART_2D_MATRIX_USEOTHER_FALSE}                       ║
║ [X] FLAG 3.1: FLAG{TIMECHART_PER_MINUTE_VELOCITY_STANDARDIZED}          ║
║ [X] FLAG 4.1: FLAG{RARE_ANOMALY_OUTLIER_DISCOVERY}                       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **🎉 Outstanding Work!**  
> You mastered data transformations, multi-dimensional matrix charting, and time-series normalization.  
> **Total XP Awarded:** `+200 XP`!  
> Next Mission: **[Chapter 03: Event Manipulation & Multivalue Fields (`eval`, `rex`, `spath`, `mvexpand`, `nomv`)](../04%20-%20Phase%204%20-%20Advanced%20SPL%20&%20Search%20Optimization/Chapter_03_Event_Manipulation_and_Multivalue.md)**!
