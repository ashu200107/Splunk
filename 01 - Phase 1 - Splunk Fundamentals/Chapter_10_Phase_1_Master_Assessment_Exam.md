# 🎯 Phase 1 Master Assessment: Beginner ➔ Production ➔ Interview Level Exam

> **The Splunk Enterprise Administrator Examination** | Phase 1 Capstone  
> **Candidate:** Aspiring Enterprise Splunk Administrator  
> **Evaluation Mode:** Technical Recruiter & Senior Architect Grading  
> **Status:** 🟢 **EVALUATED & SCORED (Comprehensive Score: 50.5 / 120 - 4.2 / 10)**

---

## 📊 Candidate Submission & Interview Scorecard

| Question # | Tier | Topic Area | Score (/10) | Status | Senior Architect & Recruiter Key Takeaway |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **Q1** | Tier 1 | Timeless Event Extraction Fallback | **8.5 / 10** | 🟢 Pass | Good intuition on current ingestion time; also falls back to file `mtime`. |
| **Q2** | Tier 1 | Intermediate Forwarders in DMZ | **5.0 / 10** | 🟡 Review | Acts as network proxy/bridge in DMZ. UFs cannot do data masking. |
| **Q3** | Tier 1 | Sourcetype Override Hierarchy | **4.0 / 10** | 🟡 Review | Parsing Phase (`props/transforms`) overrides Input Phase (`inputs.conf`). |
| **Q4** | Tier 1 | HEC Port & Auth Headers | **3.0 / 10** | 🔴 Gap | HEC uses Port `8088` (HTTPS) & `Authorization: Splunk <Token>` header. |
| **Q5** | Tier 2 | User Context Storage & Precedence | **7.5 / 10** | 🟢 Pass | Stored in `etc/users/<user>/<app>/local/`. User context wins in search. |
| **Q6** | Tier 2 | Bucket Unix Epoch Dissection | **8.0 / 10** | 🟢 Pass | Identified latest/oldest timestamps. `105` is the local unique Bucket ID. |
| **Q7** | Tier 2 | Regex Filtering to nullQueue | **0.0 / 10** | 🔴 Gap | Use `DEST_KEY = queue` & `FORMAT = nullQueue` in `transforms.conf`. |
| **Q8** | Tier 2 | TRUNCATE Event Splitting Mechanics | **5.0 / 10** | 🟡 Review | Splunk splits event at 10,000 bytes into a new broken event (no crash). |
| **Q9** | Tier 3 | SmartStore Remote Object Tiering | **4.5 / 10** | 🟡 Review | Local SSD acts as cache; master copy lives in Cloud Object Storage (S3/GCS). |
| **Q10** | Tier 3 | btool check Syntax Validation | **3.0 / 10** | 🔴 Gap | The CLI command to scan for typos and errors is `splunk btool check`. |
| **Q11** | Tier 3 | Phone-Home Interval Scaling (DS) | **0.0 / 10** | 🔴 Gap | Tune `phoneHomeIntervalInSecs = 600` in `deploymentclient.conf`. |
| **Q12** | Tier 3 | Fishbucket Reset & followTail | **2.0 / 10** | 🔴 Gap | Cleaning fishbucket causes full re-indexing. Use `followTail = 1` to prevent. |
| **TOTAL** | **All Tiers** | **Comprehensive Exam Score** | **50.5 / 120** | **4.2 / 10** | **Action: Review the 5 Target Gap Topics below before Phase 2.** |

---

## 🟢 TIER 1: Beginner / Foundational Level

### 📌 Question 1: Timestamps & Extraction Fallbacks
> **Question:** If an application emits a log event that contains **no timestamp anywhere in its text** (e.g., `User admin logged in from internal network`), what fallback mechanism does Splunk use to assign the `_time` metadata field?

- **Candidate Answer:** *The fallback mechanism the splunk wil use to assign the `_time` metadata field is it will mention the time when universal forwader will send the log to indexer and add the time stamp.*
- **Evaluation Score:** **8.5 / 10** 🎯
- **💡 Senior Architect Polish:**
  - When an event has **no timestamp in its text**, Splunk falls back to:
    1. The **file's last modification time (`mtime`)**, OR
    2. The **current indexing / ingestion arrival time** (`DATETIME_CONFIG = CURRENT`).

---

### 📌 Question 2: Forwarder Topologies & DMZ Architecture
> **Question:** What is an **Intermediate Forwarder** (Forwarding Tier), and why would a financial enterprise place one in a DMZ between edge Universal Forwarders and internal core Indexers?

- **Candidate Answer:** *the immediate forwader is used to perform 2 layer the data masking of transaction data because the data maskingg is performed by universal forwader. once the primary forwader will perform the data masking then the intermediate forewarder will perform the data masking 2nd time.*
- **Evaluation Score:** **5.0 / 10**
- **💡 Senior Architect Polish:**
  - ⚠️ **Key Rule:** Universal Forwarders **CANNOT perform data masking** (UFs lack a parsing engine).
  - An **Intermediate Forwarder** (in a **DMZ**) acts as a **network security proxy**:
    - Internal security policies forbid opening direct firewall ports (Port `9997`) from 5,000 edge servers directly to core Indexers.
    - 5,000 edge UFs send data to **2 Intermediate Forwarders in the DMZ**, and only those 2 DMZ machines are permitted through the internal firewall to reach the Indexers!

```text
[5,000 App Servers] ──► [DMZ Intermediate Forwarders] ──► (Internal Firewall) ──► [Core Indexers]
```

---

### 📌 Question 3: Metadata & Sourcetyping Rules
> **Question:** If an administrator sets `sourcetype = access_combined` in `inputs.conf` on a forwarder, but an Indexer has a `props.conf`/`transforms.conf` rule that rewrites the sourcetype to `access_secure` during parsing, **which sourcetype is permanently indexed on disk?**

- **Candidate Answer:** *the sourcetype = access_combined is permenantly indexed on disk.*
- **Evaluation Score:** **4.0 / 10**
- **💡 Senior Architect Polish:**
  - **Downstream Parsing Phase always WINS over Input Phase.**
  - `inputs.conf` sets the initial metadata during the Input Phase, but `props.conf`/`transforms.conf` on the indexer rewrites it during the Parsing Phase.
  - The final sourcetype written permanently to disk is **`access_secure`**!

---

### 📌 Question 4: Modern Ingestion & HEC Authentication
> **Question:** What is the default port used by the **HTTP Event Collector (HEC)**, and what specific HTTP header or token format must client applications supply in their REST request to push JSON data to Splunk?

- **Candidate Answer:** *the default port 8191 is used by the HEC and*
- **Evaluation Score:** **3.0 / 10**
- **💡 Senior Architect Polish:**
  - **HEC Default Port:** **`8088` (HTTPS)** *(Port 8191 is KV Store sync)*.
  - **Authentication Header:** Applications must pass the token in the `Authorization` header:
  ```bash
  curl -k https://splunk-indexer:8088/services/collector \
    -H "Authorization: Splunk 12345678-ABCD-EF00-1122-334455667788" \
    -d '{"event": "User login success", "sourcetype": "json_app"}'
  ```

---

## 🟡 TIER 2: Production Administrator & Operational Level

### 📌 Question 5: User Context Storage & Precedence
> **Question:** When a user creates a private saved search or dashboard inside the Splunk Web UI:
> 1. In which exact directory path under `$SPLUNK_HOME/etc/users/` is that configuration stored?
> 2. In the Search/User context, does this private configuration have higher or lower priority than an app-level `local/` configuration?

- **Candidate Answer:** *Ans 1. the exact directory path under $SPLUNK_HOME/etc/users/user name/dashboard. Ans 2. private user configuration have higher or lower precedence than an app-level local configuration*
- **Evaluation Score:** **7.5 / 10** 🎯
- **💡 Senior Architect Polish:**
  1. **Exact Directory Path:** `$SPLUNK_HOME/etc/users/<username>/<app_name>/local/` (e.g., `savedsearches.conf`).
  2. **Precedence:** In the **User/Search Context**, private user configurations have **HIGHER precedence** than app-level `local/` settings for that user!

---

### 📌 Question 6: Bucket Naming & Unix Epoch Analysis
> **Question:** Look closely at this production bucket folder name:
> `/opt/splunk/var/lib/splunk/security/db/db_1693440000_1693353600_105/`
> 1. Which timestamp is the **newest (latest)** event in the bucket, and which is the **oldest (earliest)**?
> 2. What does the final number **`105`** represent?

- **Candidate Answer:** *Ans 1. latest timestamp is 1693440000 and oldest is 1693353600. Ans 2.*
- **Evaluation Score:** **8.0 / 10** 🎯
- **💡 Senior Architect Polish:**
  - Structure: `db_<youngest_time>_<oldest_time>_<bucket_id>`
  - 1. **1693440000:** Latest / Newest event timestamp in the bucket (youngest).
  - 2. **1693353600:** Earliest / Oldest event timestamp in the bucket.
  - 3. **`105`:** The **local unique Bucket ID** (an incremental integer assigned by the indexer).

---

### 📌 Question 7: Data Hygiene & `nullQueue` Routing
> **Question:** Your enterprise is consuming 98% of its daily license. You discover an application is flooding Splunk with millions of useless lines containing `DEBUG: connection keepalive ok`.  
> How do you configure `props.conf` and `transforms.conf` to discard **only** these specific keepalive lines to `nullQueue` while allowing error events from the same file to be indexed?

- **Candidate Answer:** *no idea*
- **Evaluation Score:** **0.0 / 10**
- **💡 Senior Architect Polish:**
  - **Step 1: In `transforms.conf`:**
    ```ini
    [drop_keepalive_debug]
    REGEX = (?i)DEBUG:\s*connection\s*keepalive\s*ok
    DEST_KEY = queue
    FORMAT = nullQueue
    ```
  - **Step 2: In `props.conf`:**
    ```ini
    [my_app_sourcetype]
    TRANSFORMS-drop = drop_keepalive_debug
    ```
  - Matching events are routed to `nullQueue` and dropped from memory with **\$0 license cost**!

---

### 📌 Question 8: Event Truncation Mechanics (`TRUNCATE`)
> **Question:** By default, Splunk limits event length using `TRUNCATE = 10000` (10,000 bytes) in `props.conf`. What happens to a massive 35,000-byte Java stack trace when it arrives at the Indexer with default settings?

- **Candidate Answer:** *when a massive 35000 byte java stack trace arrive at indexer then it will process the first 10000 byte data and other will wait in a queue and it will overload the indexer and indexer may get crashe.*
- **Evaluation Score:** **5.0 / 10**
- **💡 Senior Architect Polish:**
  - Splunk **cuts the event at byte 10,000**.
  - The remaining 25,000 bytes are NOT queued and do NOT crash the indexer—they are treated as a **brand-new separate broken event**!
  - **The Fix:** Set `TRUNCATE = 50000` (or `TRUNCATE = 0` for unlimited) in `props.conf`.

---

## 🔴 TIER 3: Senior Architect & Scenario Interview Level

### 📌 Question 9: Modern SmartStore Storage Architecture
> **Question:** In modern cloud and Kubernetes deployments, Splunk uses **SmartStore** instead of traditional local Cold storage:
> 1. What is the fundamental difference between where local Hot/Warm cache buckets live vs. where the master copy of data lives?
> 2. What type of storage (e.g., AWS S3, GCP GCS, Azure Blob) acts as the remote storage tier?

- **Candidate Answer:** *Ans 1. the diffrence between the hot and warm cache buchet is that the hot bucket will write over the db where the warm bucket have only read permission and when the splunk restart or time expire hen it oes to warm bucket. Ans 2. frozen storage act as a remote storage tier.*
- **Evaluation Score:** **4.5 / 10**
- **💡 Senior Architect Polish:**
  - In **SmartStore**:
    1. Local Indexer disks (NVMe SSD) act as a **local cache** holding Hot and actively queried Warm buckets.
    2. The **authoritative master copy of ALL data (Warm + Cold)** lives in **Remote Object Storage** (AWS S3, GCP GCS, or Azure Blob).
    3. Cold storage on local disks is completely eliminated!

---

### 📌 Question 10: Configuration Syntax & Error Validation
> **Question:** An administrator manually edited several `.conf` files on an Indexer, and now Splunk is behaving erratically.  
> What exact **`splunk btool`** command do you run to scan all configuration files across the entire instance for syntax errors, unrecognized settings, and typos?

- **Candidate Answer:** *when we edit manually the default .conf file then it will easre all the configuration and it will start from scratch.*
- **Evaluation Score:** **3.0 / 10**
- **💡 Senior Architect Polish:**
  - The command to validate syntax and catch typos across all configuration files is:
    ```bash
    /opt/splunk/bin/splunk btool check
    ```
  - (Add `--debug` to see file origins: `/opt/splunk/bin/splunk btool check --debug`).

---

### 📌 Question 11: Deployment Server Scalability & Phone-Home Tuning
> **Question:** An enterprise scales from 500 to 20,000 Universal Forwarders. Suddenly, the Deployment Server's CPU hits 100% and port 8089 hangs because thousands of forwarders check in at the same second.  
> Which parameter in `deploymentclient.conf` on the forwarders controls how frequently forwarders poll the Deployment Server, and what should you do to alleviate the bottleneck?

- **Candidate Answer:** *no idea*
- **Evaluation Score:** **0.0 / 10**
- **💡 Senior Architect Polish:**
  - In `deploymentclient.conf` on the forwarders:
    ```ini
    [deployment-client]
    phoneHomeIntervalInSecs = 600
    ```
  - **Default:** `60` seconds (too frequent for 20,000 agents!).
  - **Tuning:** Increase to `600` (10 minutes) or `1800` (30 minutes) to eliminate CPU and network bottlenecks on the Deployment Server.

---

### 📌 Question 12: Fishbucket Disaster & Duplicate Prevention
> **Question:** A junior administrator accidentally ran the destructive command:
> `/opt/splunk/bin/splunk clean eventdata -index _thefishbucket`
> 1. What will happen to all monitored log files on that server when Splunk restarts?
> 2. As a Senior Administrator, what setting in `inputs.conf` or operational action can prevent thousands of gigabytes of duplicate logs from flooding the cluster and blowing your daily license?

- **Candidate Answer:** *Ans 1. when we ran the above command and spunk restart then the fishbuckt will sart reading the file from where it stop reading/. Ans 2. no idea*
- **Evaluation Score:** **2.0 / 10**
- **💡 Senior Architect Polish:**
  - 1. **The Disaster:** Cleaning `_thefishbucket` wipes all MD5 checksum tracking pointers. When Splunk restarts, it assumes EVERY log file is completely brand new and **re-reads every file from byte 0**, causing massive duplicate indexing and potential license violations!
  - 2. **The Prevention:** In `inputs.conf`, configure:
    ```ini
    [monitor:///var/log/...]
    followTail = 1
    ```
    - `followTail = 1` forces Splunk to ignore all old historical content and only index **new lines written from this moment forward**.

---

## 🎯 Phase 1 Action Plan: 5 Target Topics to Master

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   5 TOPICS TO REINFORCE BEFORE PHASE 2                 │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 🧹 Data Hygiene: nullQueue routing in props.conf / transforms.conf  │
│ 2. 🐟 Fishbucket Mechanics: MD5 pointers & 'followTail = 1' safety     │
│ 3. 🌐 Port Precision: HEC = 8088 | KV Store = 8191 | REST = 8089       │
│ 4. 🔀 Metadata Precedence: Downstream Parsing Phase rewrites Inputs    │
│ 5. 🛠️ CLI Diagnostics: 'splunk btool check' & 'phoneHomeInterval'     │
└────────────────────────────────────────────────────────────────────────┘
```
