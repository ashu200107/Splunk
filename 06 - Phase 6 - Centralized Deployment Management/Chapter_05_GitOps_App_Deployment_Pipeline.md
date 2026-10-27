# 🛠️ Chapter 05 (Phase 6): GitOps, CI/CD & Configuration Version Control for Splunk Apps

> **The Splunk Administrator's Definitive Handbook** | Phase 6: Centralized Deployment Management  
> **Day:** 51 | **Milestone:** Enterprise GitOps, CI/CD Automation, Splunk AppInspect CLI, `ksconf` Linting & Configuration Pipelines  
> **Current Rank:** Master Enterprise Fleet Orchestrator (10,000 XP) $\rightarrow$ *Promotion Target: Master Enterprise Fleet Orchestrator (11,100+ XP)*  
> **Second Brain File:** `Chapter_05_GitOps_App_Deployment_Pipeline.md`  
> **Interactive Cyber Range Lab:** [Room P6-05: The GitOps App Deployment Pipeline](../Labs/Room_P6_05_GitOps_App_Deployment_Pipeline.md) `[300 XP]`  
>  
> **Official Splunk Documentation Reference:**  
> - 📖 [Splunk Developer Docs: Test and Validate Apps with Splunk AppInspect](https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/)  
> - 📖 [Splunk Docs: Package and Deploy Apps via Deployment Server](https://docs.splunk.com/Documentation/Splunk/latest/Updating/Createadeploymentapp)  
> - 📖 [Splunk Docs: Deployment Server REST API Endpoint Reference](https://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTdeploy)  
> - 📖 [Splunk Docs: Configuration File Precedence & Directory Anatomy](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles)  
>  
> **Official Exam Blueprint Mapping:**  
> - 🎯 **Splunk Enterprise Certified Admin (SPLK-1003):** Section 6.0 — Deployment Server Management (6.1 Package modular Splunk applications for deployment server distribution; 6.2 Enforce configuration file standards and directory hygiene: `default` vs `local`; 6.3 Automate configuration validation and reload triggers).  
> - 🎯 **Splunk Core Certified Power User (SPLK-1002):** Section 4.0 — Creating and Managing Splunk Knowledge Objects within Apps.

---

## 🏭 1. The Everyday Analogy: The Aircraft Assembly Line & The Wind Tunnel Test

Imagine a commercial aerospace manufacturer building passenger airliners:

- **The Danger of Hand-Crafting on the Runway (Manual DS Editing):**  
  If aircraft mechanics were allowed to randomly climb onto the runway with handheld drills, solder loose wires into an engine mid-flight, and tape over warning sensors without logging the changes in an engineering ledger, catastrophic engine failures would be inevitable.
- **The Modern Automated Assembly Line (GitOps & CI/CD):**  
  In a modern aerospace facility:
  1. Every rivet, sensor, and bracket is designed in a computer-aided blueprint repository (**Git Version Control**).
  2. Before any component is manufactured, automated computer simulations and wind-tunnel stress tests verify that the design complies with rigorous safety standards (**Splunk AppInspect & `ksconf` Linter**).
  3. Once approved by two senior aerospace engineers (**Pull Request Peer Review**), the component is robotically fabricated and tested in a staging chamber (**Staging Deployment Server**).
  4. Only after passing all staging gates is the certified part deployed to active aircraft during scheduled maintenance (**Automated Webhook Sync to Production Fleet**).

In Splunk Enterprise, **GitOps App Deployment** eliminates the dangerous habit of manually editing `.conf` files directly on the production Deployment Server. It establishes a resilient, auditable, and automated delivery pipeline that protects thousands of forwarders from syntax errors, configuration drift, and catastrophic outages.

---

## 🗺️ 2. The Master Architectural Blueprint

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│               ENTERPRISE GITOPS & CI/CD SPLUNK APP DEPLOYMENT PIPELINE                    │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   DEVELOPER WORKSTATION                                                                   │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 1. Engineer authors modular app: Org_all_inputs/default/inputs.conf               │   │
│   │ 2. Pre-commit check: ksconf check && ksconf sort                                  │   │
│   │ 3. git push origin feature/update-syslog-ingest                                   │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │ Git Push                                    │
│                                             ▼                                             │
│   ENTERPRISE GIT REPOSITORY (GitHub / GitLab Enterprise)                                  │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ • Branch Protection: main is locked (Requires 2 Senior Admin approvals)          │   │
│   │ • CI/CD Runner Trigger: .gitlab-ci.yml / .github/workflows/splunk-appinspect.yml  │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │ Triggers Automated CI Job                   │
│                                             ▼                                             │
│   CI/CD AUTOMATION RUNNER                                                                 │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 1: Syntax & Stanza Linting  ──> ksconf check apps/*                          │   │
│   │ STEP 2: App Hygiene Check        ──> Verify NO 'local/' or '.git' folders exist   │   │
│   │ STEP 3: Security & Standards     ──> splunk-appinspect inspect apps/*            │   │
│   │ └── STATUS: PASSED (Merge Allowed)                                                │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │ Automated CD Webhook / SSH Sync             │
│                                             ▼                                             │
│   PRODUCTION DEPLOYMENT SERVER (ds-prod-01)                                               │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 1. Git pull into: /opt/splunk/etc/deployment-apps/                                │   │
│   │ 2. Fix filesystem ownership: chown -R splunk:splunk deployment-apps/              │   │
│   │ 3. Automated REST Reload:                                                         │   │
│   │    curl -k -u admin:pass https://localhost:8089                                   │   │
│   │         -X POST /services/deployment/server/config/_reload                        │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │ Staggered phoneHome Window                  │
│                                             ▼                                             │
│   ENTERPRISE FORWARDER FLEET (10,000+ Universal Forwarders)                               │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Forwarders download updated app checksums into: /opt/splunkforwarder/etc/apps/    │   │
│   └───────────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. The 5-Step GitOps App Deployment Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               THE 5-STEP GITOPS SPLUNK APP DEPLOYMENT LIFECYCLE                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. MODULAR APP AUTHORING & DIRECTORY HYGIENE                                            │
│    • Apps MUST only contain a `default/` directory and optional `metadata/local.meta`.  │
│    • NEVER commit a `local/` directory inside a deployment app package!                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. LOCAL PRE-COMMIT LINTING WITH KSCONF                                                 │
│    • Run syntax validation on all stanza structures: `ksconf check .`                   │
│    • Standardize stanza sorting: `ksconf sort --inplace default/inputs.conf`            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. AUTOMATED CI/CD VALIDATION (Splunk AppInspect)                                       │
│    • CI runner executes AppInspect CLI against the package:                             │
│      splunk-appinspect inspect <app_dir> --mode precert                                 │
│    • Pipeline fails immediately if manual overrides, plain credentials, or invalid     │
│      regex expressions are detected.                                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. PROTECTED BRANCH MERGE & SYNCHRONIZATION                                             │
│    • Pull Request approved by authorized Splunk Administrators.                         │
│    • CD agent or git-webhook pulls latest commits into `/opt/splunk/etc/deployment-apps/`│
│    • Permissions enforced: `chmod 750` and `chown -R splunk:splunk`.                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. ZERO-DOWNTIME CONFIGURATION RELOAD TRIGGER                                           │
│    • Pipeline invokes the Splunk REST API endpoint:                                     │
│      POST /services/deployment/server/config/_reload                                    │
│    • Deployment Server re-computes app bundle checksums and dispatches updates.         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 4. Technical Deep Dive: Tooling, Pipeline Scripts & REST Endpoints

### 4.1 Deployment App Directory Layout Standards

A properly engineered deployment application stored in Git must adhere to strict architectural anatomy:

```text
deployment-apps/
└── Org_all_linux_security/
    ├── app.manifest           <-- App packaging metadata & schema version
    ├── default/
    │   ├── app.conf           <-- Visible status, version, author, and description
    │   ├── inputs.conf        <-- Data collection inputs (monitor, batch)
    │   └── props.conf         <-- Parsing rules (TIME_PREFIX, SHOULD_LINEMERGE)
    ├── metadata/
    │   └── default.meta       <-- Access permissions and export scopes
    └── README.md              <-- Technical operational documentation
```

> [!IMPORTANT]
> **Why `default/` Only?**  
> When the Deployment Server distributes an app to a Universal Forwarder, the app is downloaded to `$SPLUNK_HOME/etc/apps/<app_name>/`.  
> If you package settings inside `local/`, local forwarder administrators or future deployment apps cannot easily override them. By keeping distributed configurations strictly in `default/`, you maintain a predictable configuration precedence hierarchy!

---

### 4.2 Installing and Using `ksconf` for Splunk Configuration Management

`ksconf` (Kintyre's Splunk Configuration Tool) is the enterprise standard CLI tool for maintaining `.conf` files in Git:

```bash
# Install ksconf via Python PIP
pip install --upgrade ksconf

# 1. Syntax check all .conf files in the repo (Catches unclosed brackets and duplicate keys)
ksconf check /path/to/repo/deployment-apps/

# 2. Sort stanzas alphabetically to avoid messy Git diff merge conflicts
ksconf sort --inplace /path/to/repo/deployment-apps/Org_all_inputs/default/inputs.conf

# 3. Compare configuration differences between two app versions
ksconf diff deployment-apps/Org_app_v1/default/inputs.conf deployment-apps/Org_app_v2/default/inputs.conf
```

---

### 4.3 Splunk AppInspect CLI: Automated Quality Gate

Splunk AppInspect analyzes apps against hundreds of official Splunk best-practice rules:

```bash
# Install official Splunk AppInspect CLI
pip install splunk-appinspect

# Run AppInspect in precertification mode with JSON report generation
splunk-appinspect inspect /opt/splunk/etc/deployment-apps/Org_all_linux_security \
  --mode precert \
  --output-file /tmp/appinspect_report.json

# Extract failure count using jq
cat /tmp/appinspect_report.json | jq '.summary.failure'
```

---

### 4.4 Automated CI/CD Pipeline (GitHub Actions Example)

Here is a production-grade GitHub Actions workflow (`.github/workflows/splunk-ci.yml`):

```yaml
name: Splunk App CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate-and-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Linting & AppInspect Tools
        run: |
          pip install --upgrade pip
          pip install ksconf splunk-appinspect

      - name: Verify Stanza Syntax via KSCONF
        run: |
          ksconf check deployment-apps/

      - name: Verify No 'local' Directories Exist in Apps
        run: |
          if find deployment-apps/ -type d -name "local" | grep .; then
            echo "CRITICAL: Found illegal 'local/' folder inside deployment-apps!"
            exit 1
          fi

      - name: Run Splunk AppInspect Quality Gate
        run: |
          for app in deployment-apps/*; do
            if [ -d "$app" ]; then
              echo "Inspecting app: $app"
              splunk-appinspect inspect "$app" --mode precert
            fi
          done

  deploy-to-ds:
    needs: validate-and-lint
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Deployment Server Git Sync & Reload
        run: |
          curl -k -u ${{ secrets.SPLUNK_ADMIN_USER }}:${{ secrets.SPLUNK_ADMIN_PASS }} \
            -X POST https://${{ secrets.SPLUNK_DS_HOST }}:8089/services/deployment/server/config/_reload
```

---

## ⚠️ 5. Common Production Pitfalls & Anti-Patterns

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│               5 CRITICAL GITOPS & APP CI/CD PITFALLS                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. THE ILLEGAL `local/` DIRECTORY COMMIT                                                │
│    • Symptom: Admins test changes on their local test box, copy `local/` into the app   │
│      bundle, and commit it to Git.                                                      │
│    • Impact: Breaks configuration precedence on the target forwarders, preventing local │
│      forwarder-specific overrides and causing btool confusion.                          │
│    • Fix: Enforce a CI rule that fails any PR containing a `local/` directory.         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. COMMITTING THE `.git/` DIRECTORY TO FORWARDERS                                       │
│    • Symptom: Admins run `git clone` directly inside `$SPLUNK_HOME/etc/deployment-apps/`│
│    • Impact: The Deployment Server bundles the entire `.git/` database (hundreds of MBs)│
│      into the app tarball and broadcasts it to 10,000 forwarders, wasting gigabytes!    │
│    • Fix: Clone to `/opt/splunk/git-staging/` and rsync only app contents to DS!       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. PLAINTEXT CREDENTIAL LEAKS IN GITOPS REPOSITORIES                                    │
│    • Symptom: Committing `passwords.conf` or plain API keys into Git.                   │
│    • Impact: Security vulnerability; exposure of enterprise credentials.                │
│    • Fix: Use Git pre-commit hooks (`trufflehog`, `git-secrets`) and Splunk encryption. │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. CONFIGURATION DRIFT (Direct Server Hot-Patching)                                     │
│    • Symptom: An engineer SSHes to the Deployment Server and edits `inputs.conf` live.  │
│    • Impact: The next automated Git sync wipes out the manual fix, causing recurrence!  │
│    • Fix: Remove write permissions on DS filesystem for human accounts.                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. WINDOWS CRLF CARRIAGE RETURN INFECTION                                               │
│    • Symptom: Linux forwarders fail to parse `.conf` files with bizarre syntax errors.  │
│    • Root Cause: Windows admin edited files with Notepad, injecting `\r\n` characters.  │
│    • Fix: Configure `.gitattributes` with `* text eol=lf`.                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 6. Cyber Range Practical Lab: Room P6-05

Ready to experience GitOps automation under production conditions?  
Enter the hands-on simulated arena:

👉 **[Enter Cyber Range Room P6-05: The GitOps App Deployment Pipeline](../Labs/Room_P6_05_GitOps_App_Deployment_Pipeline.md)** `[300 XP]`

You will debug a broken CI/CD pipeline, eliminate illegal `local/` directories, execute `ksconf` stanza sorting, and configure automated REST reload triggers!

---

## 📝 7. End-of-Chapter Self-Check Quiz

### Question 1 (SPLK-1003 Blueprint)
When packaging an application for distribution via the Splunk Deployment Server (`$SPLUNK_HOME/etc/deployment-apps/<app_name>/`), which directory structure represents official best practice?
- A) All `.conf` files must be placed directly in `$SPLUNK_HOME/etc/deployment-apps/<app_name>/local/`.
- B) All `.conf` files must be placed in `$SPLUNK_HOME/etc/deployment-apps/<app_name>/default/`, and no `local/` directory should be included in the deployment bundle.
- C) Configuration files must be split equally between `default/` and `local/` to enable two-tier inheritance.
- D) The application must be pre-compiled into a `.spl` tarball and placed in `$SPLUNK_HOME/var/run/`.

### Question 2 (CI/CD & Linting)
Which command-line utility from the `ksconf` suite allows an administrator to validate that all Splunk configuration files in a Git repository are syntactically valid (no missing closing brackets, valid stanza headers) before merging?
- A) `ksconf validate --all`
- B) `ksconf compile`
- C) `ksconf check <directory>`
- D) `ksconf lint --strict`

### Question 3 (Automation & REST API)
Following an automated Git pull that updates app bundles in `$SPLUNK_HOME/etc/deployment-apps/`, which REST API endpoint should the CI/CD pipeline invoke to force the Deployment Server to reload configurations without restarting `splunkd`?
- A) `POST /services/server/control/restart`
- B) `POST /services/deployment/server/config/_reload`
- C) `GET /services/apps/local/refresh`
- D) `POST /services/deployment/client/sync`

### Question 4 (Production Incident Scenario)
An administrator ran `git clone` directly inside `$SPLUNK_HOME/etc/deployment-apps/` to manage apps. Shortly after running `splunk reload deploy-server`, the WAN bandwidth between the Deployment Server and 5,000 edge forwarders saturated completely, and forwarders ran out of disk space in `/opt/splunkforwarder/etc/apps/`. What occurred?
- A) Splunk Deployment Server does not support Git repositories.
- B) The hidden `.git` directory was treated as an application directory, bundled into a massive tarball, and pushed to every forwarder in the fleet.
- C) The deployment server automatically executed `git push --all` to every forwarder IP.
- D) The forwarders rejected the Git SSL certificate and entered a continuous reconnect storm.

### Question 5 (Splunk AppInspect)
What is the primary function of running `splunk-appinspect inspect <app_dir> --mode precert` within an automated CI/CD pipeline?
- A) It automatically installs the app into production Splunk Cloud.
- B) It evaluates the application against Splunk's official architectural, security, and compatibility standards, catching prohibited commands, illegal directory paths, and malformed stanzas.
- C) It converts `.conf` files into optimized Python binary executables.
- D) It starts a temporary Splunk Enterprise Docker container to test data ingestion rates.

---

### 💡 Answers & In-Depth Explanations

1. **Answer: B**  
   *Explanation:* Deployment apps distributed to clients land in `$SPLUNK_HOME/etc/apps/<app_name>/`. Placing settings in `default/` ensures that any future local admin overrides on the client (or higher-precedence app settings) can take precedence properly. Committing `local/` in deployment packages is an anti-pattern that breaks configuration precedence on endpoints.
2. **Answer: C**  
   *Explanation:* `ksconf check <directory>` scans `.conf` files for syntax errors, unclosed bracket headers, duplicate stanzas, and formatting anomalies.
3. **Answer: B**  
   *Explanation:* The REST endpoint `POST /services/deployment/server/config/_reload` triggers the Deployment Server to re-read `serverclass.conf` and re-evaluate checksums for apps in `deployment-apps/` without restarting `splunkd`.
4. **Answer: B**  
   *Explanation:* The Deployment Server treats every subdirectory inside `deployment-apps/` as a deployable app unless excluded. Cloning a Git repo directly inside `deployment-apps/` causes the entire `.git` history folder to be treated as an app, packaged, and transmitted to forwarders!
5. **Answer: B**  
   *Explanation:* Splunk AppInspect validates apps against hundreds of official packaging, security, and design standards, ensuring that configuration files, scripts, and folder layouts meet production enterprise criteria.
