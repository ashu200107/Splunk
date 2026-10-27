# 🎮 Room P6-05: The GitOps App Deployment Pipeline

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🕹️ ROOM P6-05: The GitOps App Deployment Pipeline   ⭐ DIFFICULTY: Hard │
│ 🎯 TOPIC: GitOps, KSCONF Linting, AppInspect & REST Automation          │
│ 💎 REWARD: 300 XP                                  🛡️ CATEGORY: DevOps  │
│ ⏱️ ESTIMATED TIME: 45 Mins                                              │
│ 🏆 PREREQUISITE: Room P6-01 through Room P6-04                         │
└────────────────────────────────────────────────────────────────────────┘
```

> **Briefing Room: Critical DevOps Incident — Pipeline Sabotage & Stale Deployments!**  
> An urgent security alert has been declared across the enterprise CI/CD infrastructure!  
>  
> A junior contractor pushed an untested app update to the GitOps repository `splunk-deployment-apps`:  
> 1. The CI/CD runner crashed with an exit code 1 because malformed stanza brackets were committed into `inputs.conf`.  
> 2. An illegal `local/` directory was bundled inside `Org_all_linux_security`, overriding enterprise security policies on 2,000 forwarders!  
> 3. Worse, the contractor accidentally committed the entire `.git` directory into `deployment-apps/`, which is threatening to saturate the WAN pipe to edge store locations.  
> 4. The automated deployment webhook failed to trigger because the REST reload script uses a deprecated URL format.  
>  
> Your mission as the Lead Enterprise Fleet Orchestrator:  
> 1. Audit the repository, purge illegal `local/` folders, and protect against `.git` bundle leakage.  
> 2. Use `ksconf` to locate syntax errors, standardize stanza sorting, and validate configuration integrity.  
> 3. Run Splunk AppInspect CLI to clear all pre-certification security checks.  
> 4. Author and test the automated REST API reload script to trigger zero-downtime updates on the Deployment Server, capturing all 4 operational flags!  

---

## 🗺️ Mission Architecture & Target Environment

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TARGET TOPOLOGY SPECS                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • GitOps Staging Root:  /home/splunkadmin/git-repos/splunk-deployment-apps/  │
│ • Production DS Path:   /opt/splunk/etc/deployment-apps/                     │
│ • Deployment Server:    https://ds-prod-01.corp.local:8089                   │
│ • Target App:           Org_all_linux_security                               │
│ • Config Files:         inputs.conf, props.conf, app.conf                    │
│ • Validation Tools:     ksconf, splunk-appinspect, curl, jq                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Developer Docs: Test and Validate Apps with Splunk AppInspect](https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/)  
> - 📖 [Splunk Docs: Package and Deploy Apps via Deployment Server](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Createadeploymentapp)  
> - 📖 [Splunk Docs: Deployment Server REST API Endpoint Reference](https://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTdeploy)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Objective 6.1 (Package modular Splunk applications for deployment server distribution) & Objective 6.2 (Enforce configuration file standards and directory hygiene: `default` vs `local`).

---

## 🎯 TASK 1: Purging Rogue `local/` Directories & Enforcing Git Hygiene (75 XP)

### 📖 Incident Details
Navigate to the staging repository:
```bash
cd /home/splunkadmin/git-repos/splunk-deployment-apps
```

Inspect the directory structure of the suspect application `Org_all_linux_security`:
```bash
find Org_all_linux_security -maxdepth 3
```

Output reveals a catastrophic directory violation:
```text
Org_all_linux_security
Org_all_linux_security/default
Org_all_linux_security/default/app.conf
Org_all_linux_security/local
Org_all_linux_security/local/inputs.conf    <-- ILLEGAL LOCAL DIRECTORY!
Org_all_linux_security/.git               <-- EMBEDDED GIT DATABASE!
```

If pushed to `deployment-apps/`, `local/inputs.conf` will prevent forwarder admins from configuring local path overrides, while `.git` will bloat the deployment bundle by 250 MB!

### 🛠️ Remediation Steps
1. Move the configuration settings from `local/inputs.conf` into `default/inputs.conf`:
   ```bash
   cat Org_all_linux_security/local/inputs.conf >> Org_all_linux_security/default/inputs.conf
   rm -rf Org_all_linux_security/local
   ```
2. Remove the embedded `.git` folder inside the app directory (ensure `.git` exists only at the repository root):
   ```bash
   rm -rf Org_all_linux_security/.git
   ```
3. Update `.gitignore` in the repository root to prevent future accidents:
   ```bash
   cat << 'EOF' >> .gitignore
   */local/
   *.swp
   *~
   .DS_Store
   EOF
   ```

### 🚩 Flag 1 Verification
What is the flag generated after purging illegal directories and verifying with `find`?

<details>
<summary>💡 Need a hint?</summary>
All deployed configuration files must reside strictly under <code>default/</code>.
</details>

**Flag:** `FLAG{SPLUNK_GITOPS_HYGIENE_ENFORCED}`

---

## 🎯 TASK 2: Stanza Linting & Syntax Repair with `ksconf` (75 XP)

### 📖 Incident Details
Run `ksconf check` against the repository to identify syntax faults:
```bash
ksconf check Org_all_linux_security/
```

Output:
```text
[ERROR] Org_all_linux_security/default/inputs.conf: Line 14: Malformed stanza header. Missing closing bracket: '[monitor:///var/log/audit/audit.log'
[ERROR] Org_all_linux_security/default/props.conf: Line 7: Duplicate key found: 'SHOULD_LINEMERGE'
```

### 🛠️ Remediation Steps
1. Edit `Org_all_linux_security/default/inputs.conf` and close the stanza header bracket:
   ```ini
   [monitor:///var/log/audit/audit.log]
   disabled = 0
   index = secops_linux
   sourcetype = linux:audit
   ```
2. Edit `Org_all_linux_security/default/props.conf` to eliminate the duplicate `SHOULD_LINEMERGE` setting.
3. Standardize and sort the stanzas alphabetically using `ksconf sort`:
   ```bash
   ksconf sort --inplace Org_all_linux_security/default/inputs.conf
   ksconf sort --inplace Org_all_linux_security/default/props.conf
   ```
4. Re-run `ksconf check`:
   ```bash
   ksconf check Org_all_linux_security/
   ```
   Output: `Success. All 3 files are syntactically valid.`

### 🚩 Flag 2 Verification
**Flag:** `FLAG{SPLUNK_KSCONF_SYNTAX_VERIFIED}`

---

## 🎯 TASK 3: Splunk AppInspect Precertification Quality Gate (75 XP)

### 📖 Incident Details
Run the official Splunk AppInspect CLI to verify that the application complies with enterprise security and packaging standards:

```bash
splunk-appinspect inspect Org_all_linux_security --mode precert --output-file /tmp/appinspect_report.json
```

View the report summary:
```bash
jq '.summary' /tmp/appinspect_report.json
```

Output:
```json
{
  "failure": 0,
  "error": 0,
  "warning": 0,
  "manual_check": 0,
  "passed": 48
}
```

The app achieves a **0-failure score**, verifying that no unapproved commands, plaintext credentials, or illegal relative path references exist!

### 🚩 Flag 3 Verification
**Flag:** `FLAG{SPLUNK_APPINSPECT_PRECERT_CLEARED}`

---

## 🎯 TASK 4: Automated Webhook Zero-Downtime REST Reload (75 XP)

### 📖 Incident Details
Synchronize the validated app to the Deployment Server:
```bash
rsync -av --delete Org_all_linux_security /opt/splunk/etc/deployment-apps/
chown -R splunk:splunk /opt/splunk/etc/deployment-apps/Org_all_linux_security
```

Now execute the automated REST configuration reload without restarting `splunkd`:
```bash
curl -k -s -u admin:SecureSplunkPass2026! \
  -X POST https://ds-prod-01.corp.local:8089/services/deployment/server/config/_reload \
  -H "Accept: application/json" | jq .
```

Inspect the response:
```json
{
  "links": {
    "self": "/services/deployment/server/config/_reload"
  },
  "messages": [
    {
      "type": "INFO",
      "text": "Deployment server configuration reloaded successfully."
    }
  ]
}
```

Verify in `splunkd.log`:
```bash
tail -n 10 /opt/splunk/var/log/splunk/splunkd.log | grep "Reloading serverclass"
```
The Deployment Server has re-computed bundle checksums and is serving the updated app to 2,000 forwarders with zero dropped connections!

### 🚩 Flag 4 Verification
**Flag:** `FLAG{SPLUNK_REST_AUTOMATED_RELOAD_SUCCESS}`

---

## 🏆 Room Summary & Operator Promotion

```text
╔══════════════════════════════════════════════════════════════════════════╗
│                    ROOM P6-05 COMPLETION CERTIFICATE                     │
╠══════════════════════════════════════════════════════════════════════════╣
│ • Task 1: Purge Rogue local/ & Git Hygiene            [75 XP]            │
│ • Task 2: KSCONF Stanza Syntax Validation & Sorting   [75 XP]            │
│ • Task 3: Splunk AppInspect Precertification Gate     [75 XP]            │
│ • Task 4: Automated REST Zero-Downtime Reload Hook    [75 XP]            │
│                                                                          │
│ 🏅 Total Room XP Earned: 300 XP                                          │
│ 🎖️ Master Status: Splunk GitOps & CI/CD Pipeline Specialist              │
╚══════════════════════════════════════════════════════════════════════════╝
```
