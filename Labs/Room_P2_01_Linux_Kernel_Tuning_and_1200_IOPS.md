# 🎮 Room P2-01: Linux Kernel Hardening & The 1,200 IOPS Benchmark

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🏷️ ROOM: Kernel Hardening & Sizing        ⭐ DIFFICULTY: Medium        │
│ 🎯 TOPIC: THP Disablement, ulimits, IOPS  💎 REWARD: 200 XP            │
│ ⏱️ ESTIMATED TIME: 30 Mins                🛡️ CATEGORY: OS Hardening    │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room:** The Sluggish Indexer Crisis!  
> At 10:15 AM, the infrastructure team spun up 4 new Linux VMs for an Indexer Cluster.  
> However, ingestion throughput is 60% lower than expected, searches take minutes to return, and the Monitoring Console is throwing severe red alerts:  
> *"WARN: Transparent Huge Pages (THP) is enabled. System memory latency degraded!"*  
> *"WARN: ulimit open files is 1024. Splunk risk of file handle exhaustion!"*  
> Your mission as the enterprise administrator is to harden the Linux kernel, permanently kill THP via Systemd, set production `ulimits` to 64,000, and run an `fio` benchmark to certify **1,200 sustained IOPS**!

---

## 🗺️ Mission Architecture & Hardware Specs

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ SPLUNK REFERENCE HARDWARE SPECIFICATION (Mid-to-High Volume)              │
├──────────────────────────────────────────────────────────────────────────────┤
│ • CPU Cores:       16 to 24 Physical Cores (64-bit x86_64)                   │
│ • RAM:             64 GB to 128 GB ECC RAM                                   │
│ • Storage IOPS:    Minimum 1,200 sustained 4k random write IOPS              │
│ • Filesystem:      XFS (or ext4 with dir_index)                              │
│ • Kernel Tuning:   THP = never, ulimits open files >= 64,000                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TASK 1: Transparent Huge Pages (THP) Disablement (50 XP)

### 📖 Technical Recon
Linux kernels enable **Transparent Huge Pages (THP)** by default to allocate memory in 2MB chunks for database applications.  
For Splunk's high-frequency small memory allocations, THP causes catastrophic memory lockups, latency spikes, and CPU starvation. Splunk requires THP to be set to **`never`**.

### 🛠️ Production Fix
Verify current status:
```bash
cat /sys/kernel/mm/transparent_hugepage/enabled
# If [always] or [madvise] is bracketed, THP is active!
```

Create persistent Systemd unit `/etc/systemd/system/disable-thp.service`:
```ini
[Unit]
Description=Disable Transparent Huge Pages (THP)
DefaultDependencies=no
After=sysinit.target local-fs.target
Before=mongod.service splunk.service

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled && echo never > /sys/kernel/mm/transparent_hugepage/defrag'

[Install]
WantedBy=basic.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now disable-thp.service
```

---

### ❓ Challenge Questions — Task 1

#### Question 1.1
What string value must be written to `/sys/kernel/mm/transparent_hugepage/enabled` to satisfy Splunk's production hardware requirements?  
*(Answer Format: `*****`)*

<details>
<summary>💡 Need a Hint?</summary>
A 5-letter word meaning "at no time".
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Value:</b> <code>never</code><br/>
Setting THP to <code>never</code> eliminates aggressive memory defragmentation locks.
</details>

**🚩 Capture the Flag 1.1:**
```text
FLAG{DISABLE_THP_NEVER_KERNEL_STABILITY}
```

---

## 🎯 TASK 2: Linux `ulimits` Hardening (50 XP)

### 📖 Technical Recon
Splunk actively opens thousands of sockets, search buckets, journals, and TSIDX files concurrently.  
The default Linux limit of `1024` open files (`nofile`) causes Splunk to crash with:
`FATAL: Too many open files`.

### 🛠️ Production Fix
In `/etc/security/limits.conf`:
```text
splunk          soft    nofile          64000
splunk          hard    nofile          64000
splunk          soft    nproc           20480
splunk          hard    nproc           20480
splunk          soft    fsize           unlimited
splunk          hard    fsize           unlimited
```

---

### ❓ Challenge Questions — Task 2

#### Question 2.1
What is the recommended minimum `nofile` (open file descriptors) limit required by Splunk Enterprise in `/etc/security/limits.conf`?  
*(Answer Format: `**,***`)*

<details>
<summary>💡 Need a Hint?</summary>
Sixty-four thousand.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Limit:</b> <code>64,000</code><br/>
Configuring <code>nofile 64000</code> prevents premature thread and socket crashes under peak enterprise loads.
</details>

**🚩 Capture the Flag 2.1:**
```text
FLAG{SIXTY_FOUR_THOUSAND_OPEN_FILES}
```

---

## 🎯 TASK 3: Storage IOPS Certification via `fio` (50 XP)

### 📖 Technical Recon
Never trust cloud storage claims without benchmarking. Run `fio` (Flexible I/O Tester):

```bash
sudo fio --name=splunk_bench --ioengine=libaio --rw=randwrite \
    --bs=4k --numjobs=4 --size=1G --runtime=30 --time_based \
    --filename=/opt/splunk/var/lib/splunk/test.fio
```

---

### ❓ Challenge Questions — Task 3

#### Question 3.1
What is the minimum sustained random write IOPS required by Splunk for production Indexers to prevent `indexQueue` blockage?  
*(Answer Format: `*,*** IOPS`)*

<details>
<summary>💡 Need a Hint?</summary>
Twelve hundred.
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Answer:</b> <code>1,200 IOPS</code><br/>
Hardware below 1,200 sustained IOPS will choke the indexing pipeline and lead to severe data ingestion latency.
</details>

**🚩 Capture the Flag 3.1:**
```text
FLAG{TWELVE_HUNDRED_SUSTAINED_IOPS_PASS}
```

---

## 🎯 TASK 4: Filesystem Mount Options (`noatime`) (50 XP)

### 📖 Technical Recon
Every time Linux reads a file, it writes the access timestamp (`atime`) back to disk metadata. For Splunk indexers reading millions of TSIDX entries per minute, this doubles write overhead!

---

### ❓ Challenge Questions — Task 4

#### Question 4.1
Which mount option should be specified in `/etc/fstab` for the partition hosting Splunk data directories to eliminate unnecessary disk access timestamp updates?  
*(Answer Format: `*******`)*

<details>
<summary>💡 Need a Hint?</summary>
"No access time" = `no...`
</details>

<details>
<summary>🔓 Solution Walkthrough</summary>
<b>Mount Option:</b> <code>noatime</code><br/>
In <code>/etc/fstab</code>: <code>/dev/sdb1 /opt/splunk/var/lib/splunk xfs defaults,noatime 0 0</code>.
</details>

**🚩 Capture the Flag 4.1:**
```text
FLAG{NOATIME_ELIMINATES_METADATA_WRITES}
```

---

## 🏆 Room P2-01 Completion Summary

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎉 CONGRATULATIONS, OPERATOR! ROOM P2-01 COMPLETE                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Total XP Earned: 200 / 200 XP                                        │
│ • Flags Captured: 4 / 4                                                │
│ • Skills Verified: Permanent THP Disablement via Systemd,              │
│   ulimits 64k Hardening, 1,200 IOPS fio Benchmark, noatime Mount      │
│                                                                        │
│ ➡️ NEXT ROOM: Room P2-02 — Splunk Enterprise Linux Deployment & Systemd│
└────────────────────────────────────────────────────────────────────────┘
```
