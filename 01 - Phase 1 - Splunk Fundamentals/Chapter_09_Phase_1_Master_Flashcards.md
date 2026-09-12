# 🗂️ Phase 1 Master Flashcards Deck: Splunk Fundamentals

> **The Splunk Administrator's Active-Recall Deck** | Complete Phase 1 Review (Chapters 01–07)  
> **Location:** End of Phase 1 Capstone  
> **How to Use:** Read the **Question (Front)**, test yourself in your mind, then reveal the **Answer & Architect Polish (Back)**.

---

## 🗃️ Deck 1: Machine Data & Schema-on-Read (Chapter 01)

| Card # | Question (Front) | Answer & Key Architectural Detail (Back) |
| :---: | :--- | :--- |
| **FC-01** | What is Machine Data? | **Unstructured, high-volume time-series data** generated 24/7 by software, servers, and hardware containing timestamps and event activity. |
| **FC-02** | What are the 5 default metadata fields automatically attached to every Splunk event? | **`_time`** (Epoch UTC), **`host`** (origin hostname/IP), **`source`** (file path or network input), **`sourcetype`** (data format definition), and **`index`** (destination datastore). |
| **FC-03** | How does **Schema-on-Read** differ from traditional relational **Schema-on-Write**? | In **Schema-on-Write (SQL)**, table columns must be predefined before writing. In **Schema-on-Read (Splunk)**, raw text is written directly to disk and fields are extracted dynamically via regex at search time. |
| **FC-04** | What happens in Splunk if an application changes its log format (e.g. adding 3 new fields)? | **Ingestion never breaks.** Splunk continues indexing the raw text without errors, and the new fields can be searched immediately using search-time field extractions. |
| **FC-05** | What are the 3 major business use cases for Splunk in an enterprise? | **1. Security & SIEM (Splunk ES)**, **2. IT Operations & Troubleshooting (ITSI)**, and **3. Business Analytics & IoT**. |

---

## 🗃️ Deck 2: Core Components & Topology Roles (Chapter 02)

| Card # | Question (Front) | Answer & Key Architectural Detail (Back) |
| :---: | :--- | :--- |
| **FC-06** | Why should you **never** install a Heavy Forwarder on 500 general application servers? | **Resource consumption.** HFs run a full Splunk binary with Python and require 1–2 GB RAM and dedicated CPU cores. Universal Forwarders (UFs) should be used instead (<2% CPU, ~50MB RAM). |
| **FC-07** | What is the primary architectural purpose of a **Heavy Forwarder (HF)**? | **Parsing at the edge**, data anonymization/PII masking via regex, routing specific events to third-party syslog/Kafka, and executing complex modular API inputs. |
| **FC-08** | In a distributed search, what is the exact difference between the work done by the **Indexer (Map)** and the **Search Head (Reduce)**? | **Indexer (Map):** Scans disk `.tsidx` files, extracts matching raw events from `journal.zst`, and generates partial statistical aggregations.<br/>**Search Head (Reduce):** Consolidates partial results from all indexers, computes final stats (`stats`, `eval`), and renders UI dashboards. |
| **FC-09** | Which management component distributes app bundles to **Search Head Cluster (SHC)** members? | **The SHC Deployer** (using `splunk apply shcluster-bundle`). |
| **FC-10** | Which management component coordinates bucket replication and peer health across an **Indexer Cluster**? | **The Cluster Manager (CM)** (formerly Master Node). |
| **FC-11** | Which management component manages configuration apps on **Universal Forwarders**? | **The Deployment Server (DS)** (configured via `serverclass.conf`). |

---

## 🗃️ Deck 3: The 4 Pipeline Phases & Queues (Chapter 03)

| Card # | Question (Front) | Answer & Key Architectural Detail (Back) |
| :---: | :--- | :--- |
| **FC-12** | What are the 4 sequential phases of the Splunk Data Pipeline? | **1. Input Phase** $\rightarrow$ **2. Parsing Phase** $\rightarrow$ **3. Indexing Phase** $\rightarrow$ **4. Search Phase**. |
| **FC-13** | Does event line breaking (`LINE_BREAKER`) occur on a Universal Forwarder? | **No.** UFs only package raw data into 64KB chunks during the Input Phase. Line breaking happens during the **Parsing Phase** on an Indexer or Heavy Forwarder. |
| **FC-14** | What is the exact sequence of internal memory queues on an Indexer? | **`input_queue` $\rightarrow$ `parsing_queue` $\rightarrow$ `agg_queue` $\rightarrow$ `typing_queue` $\rightarrow$ `index_queue` $\rightarrow$ Disk IO**. |
| **FC-15** | What happens inside an Indexer when its storage disk is saturated with slow IOPS? | The **`index_queue` fills to 100%**. Backpressure cascades upstream (`typing_queue` $\rightarrow$ `agg_queue` $\rightarrow$ `parsing_queue` $\rightarrow$ `input_queue`), causing the TCP 9997 receiver to pause incoming data from forwarders. |
| **FC-16** | What is the purpose of enabling `useACK = true` in `outputs.conf`? | **Guaranteed data delivery.** The forwarder retains raw log blocks in memory until the Indexer sends an acknowledgment that the events have been written safely to disk. |

---

## 🗃️ Deck 4: Directory Structure & Config Precedence (Chapter 04)

| Card # | Question (Front) | Answer & Key Architectural Detail (Back) |
| :---: | :--- | :--- |
| **FC-17** | What is the **S-A-A-S** configuration precedence order in the System/Ingestion context? | **1. System Local** (Highest) $\rightarrow$ **2. App Local** $\rightarrow$ **3. App Default** $\rightarrow$ **4. System Default** (Lowest). |
| **FC-18** | What happens to files inside `/opt/splunk/etc/system/default/` during a Splunk upgrade? | **They are completely wiped and overwritten** with new vendor factory defaults. Never edit files in `default/`! |
| **FC-19** | If `index = main` is in `app/default/inputs.conf` and `index = security` is in `app/local/inputs.conf`, which index receives the data? | **`index = security`** (`app/local` overrides `app/default`). |
| **FC-20** | What is "Attribute Merging" (The Pizza Customizer Rule)? | Splunk merges configuration stanzas key-by-key. Higher-priority files only override the specific keys they define without deleting the rest of the stanza settings. |
| **FC-21** | What CLI command shows the effective merged configuration and origin filepaths? | **`splunk btool <conf_name> list --debug`** (e.g. `splunk btool inputs list --debug`). |
| **FC-22** | Where is Splunk's internal file pointer and MD5 hash database located? | **`$SPLUNK_HOME/var/lib/splunk/fishbucket`** (Tracks 256-byte checksums to prevent re-indexing). |

---

## 🗃️ Deck 5: Index Storage & The 5 Bucket Stages (Chapter 05)

| Card # | Question (Front) | Answer & Key Architectural Detail (Back) |
| :---: | :--- | :--- |
| **FC-23** | What are the 4 superpowers of creating dedicated indexes instead of using `main`? | **1. Faster search speed**, **2. Role-Based Access Control (RBAC)**, **3. Independent data retention lifespans**, and **4. Storage size quotas**. |
| **FC-24** | What are the 5 sequential bucket stages in a Splunk index? | **Hot** $\rightarrow$ **Warm** $\rightarrow$ **Cold** $\rightarrow$ **Frozen** $\rightarrow$ **Thawed**. |
| **FC-25** | What are the 3 core files located inside every bucket? | **1. `journal.zst`** (compressed raw logs), **2. `.tsidx`** (inverted keyword index), and **3. `bloomfilter`** (probabilistic lookup table). |
| **FC-26** | What triggers a Hot bucket to roll into a Warm bucket? | **1. Bucket size reached (`maxDataSize`)**, **2. Time span expired (`maxHotSpanSecs`)**, or **3. Splunk service restart (`splunk restart`)**. |
| **FC-27** | What is the difference in searchability between a Cold bucket and a Frozen bucket? | **Cold buckets are 100% searchable.** Frozen buckets are **completely unsearchable** because their `.tsidx` files are stripped/purged. |
| **FC-28** | How do you make an archived Frozen bucket searchable again? | Copy the bucket folder into the index's **`thaweddb/`** directory and run: `/opt/splunk/bin/splunk rebuild <thawed_bucket_dir>`. |

---

## 🗃️ Deck 6: Licensing Mechanics & Quotas (Chapter 06)

| Card # | Question (Front) | Answer & Key Architectural Detail (Back) |
| :---: | :--- | :--- |
| **FC-29** | What exact metric does Splunk Enterprise classic ingestion licensing measure? | **Daily volume of uncompressed raw log text** ingested across a rolling 24-hour window (resets at **Midnight UTC**). |
| **FC-30** | Do replicated bucket copies in an Indexer Cluster ($\text{RF}=3$) count against your license? | **No. Replication is 100% license-free.** If you ingest 100 GB with $\text{RF}=3$, you store 300 GB on disk but are billed for only 100 GB. |
| **FC-31** | Are `.tsidx` inverted index files and internal indexes (`_internal`) counted against your license? | **No. They are 100% license-exempt.** |
| **FC-32** | What is the difference between a License Warning and a License Violation? | Over quota at midnight = **1 Warning**.<br/>**5 Warnings within a rolling 30-day window = Hard License Violation** (disables user search capabilities). |
| **FC-33** | When a Splunk cluster enters a License Violation, does it stop ingesting logs? | **No! INGESTION NEVER STOPS.** Splunk continues indexing all incoming data without dropping a single event. |
| **FC-34** | How do Splunk licenses scale when you purchase additional capacity? | **They stack additively.** (Existing 1 TB License + New 500 GB License = 1.5 TB/Day Total Ingest Quota). |

---

## 🗃️ Deck 7: Network Ports & Firewall Matrix (Chapter 07)

| Card # | Question (Front) | Answer & Key Architectural Detail (Back) |
| :---: | :--- | :--- |
| **FC-35** | What port and protocol does a Web Browser use to access Splunk Web? | **Port `8000` (HTTPS)** (Browser $\rightarrow$ Search Head). |
| **FC-36** | What port is used for `splunkd` REST API management and forwarder phone-home? | **Port `8089` (HTTPS)**. |
| **FC-37** | What port is used by forwarders to send raw data streams to Indexers? | **Port `9997` (TCP)** (Splunk-to-Splunk S2S Protocol). |
| **FC-38** | What port is used for inter-indexer cluster bucket replication ($\text{RF}=3$)? | **Port `9887` (TCP)** (Indexer $\leftrightarrow$ Indexer peer streaming). |
| **FC-39** | What port is used for Search Head Cluster KV Store synchronization? | **Port `8191` (TCP)** (Search Head $\leftrightarrow$ Search Head). |
| **FC-40** | What is the fundamental directionality rule for Forwarder connections? | **Forwarders ALWAYS INITIATE outbound connections** to Indexers (`9997`) and Deployment Server (`8089`). The Deployment Server never connects into forwarders. |
| **FC-41** | What Linux command tests if Port 9997 is open on an Indexer from a forwarder terminal? | **`nc -zvw 3 <indexer_ip> 9997`** |

---

## 🏁 Phase 1 Complete Mastery!

With all 41 Flashcards mastered, you possess **complete architectural fluency** across the foundational mechanics of Splunk Enterprise!

👉 **Next Step:** Ready to build real servers? Proceed to **[Phase 2: Enterprise Installation & Topology Setup](../02%20-%20Phase%202%20-%20Enterprise%20Installation%20&%20Topology%20Setup/00_Phase_2_Overview_and_TOC.md)**!
