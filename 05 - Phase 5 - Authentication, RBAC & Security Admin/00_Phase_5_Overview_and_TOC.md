# 📚 Phase 5: Authentication, RBAC & Security Administration — Handbook & TOC

> **The Splunk Administrator's Definitive Handbook** | Phase 5  
> **Target Audience:** Enterprise Splunk Administrators, SOC Lead Engineers & Security Architects  
> **Prerequisites:** Phase 1 (Fundamentals), Phase 2 (Topologies), Phase 3 (Onboarding), Phase 4 (Advanced SPL)  
> **Core Objective:** Master Splunk Enterprise Identity Governance, Role-Based Access Control (RBAC), Granular Index-Level Search Filters (`srchFilter`), LDAP/Active Directory & SAML 2.0 SSO, End-to-End TLS/mTLS Encryption across all tiers, and Hardened Compliance Auditing.

---

## 🎯 Phase 5 Roadmap & Curriculum (Days 39–46)

```mermaid
graph TD
    subgraph RBACTier ["Role-Based Access Control & Authorization"]
        C1["Ch 01: User & Role Architecture<br/>(Default roles, Custom roles, Granular inheritance, authorize.conf)"]
        C2["Ch 02: Capabilities Management & Search Filters<br/>(srchIndexesAllowed, srchIndexesDefault, srchFilter security scoping)"]
        C3["Ch 03: Native Authentication & CLI/REST Management<br/>(passwd, user-seed, REST user provisioning, token auth)"]
    end

    subgraph FederationTier ["Enterprise Identity & SSO Integration"]
        C4["Ch 04: LDAP & Active Directory Integration<br/>(authentication.conf, user/group mapping, failover strategies)"]
        C5["Ch 05: SAML 2.0 SSO Integration<br/>(Okta, Azure AD, PingFederate, attribute mapping, metadata exchange)"]
    end

    subgraph CryptoTier ["Cryptographic Hardening & PKI Infrastructure"]
        C6["Ch 06: Securing Splunk Communications (TLS/mTLS)<br/>(Web UI certs, Splunk-to-Splunk s2s encryption, UF-to-IDX TLS)"]
        C7["Ch 07: Splunk Hardening & Compliance Auditing<br/>(Port lockdowns, CLI restrictions, CIS benchmarks, _audit analytics)"]
        C8["Ch 08: Phase 5 Capstone Lab & Master Milestone Exam<br/>(Production Enterprise RBAC, SAML, and End-to-End PKI Rollout)"]
    end

    C1 --> C2 --> C3 --> C4 --> C5 --> C6 --> C7 --> C8

    style C1 fill:#fef3c7,stroke:#d97706,stroke-width:2px
    style C2 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style C3 fill:#dcfce7,stroke:#16a34a,stroke-width:2px
    style C4 fill:#f3e8ff,stroke:#9333ea,stroke-width:2px
    style C5 fill:#fce7f3,stroke:#db2777,stroke-width:2px
    style C6 fill:#ffedd5,stroke:#ea580c,stroke-width:2px
    style C7 fill:#ccfbf1,stroke:#0d9488,stroke-width:2px
    style C8 fill:#fef08a,stroke:#b45309,stroke-width:3px
```

---

## 📖 Chapter Directory & 🎮 Cyber Range Arena (Phase 5)

| Chapter | Day | Topic Name | Practical Focus | Cyber Range Room (THM / HTB Style) | XP Reward |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **01** | **39** | **User & Role Architecture** | Custom roles, inheritance hierarchies, `authorize.conf`, default roles | [Room P5-01: The RBAC Vault Infiltration](../Labs/Room_P5_01_User_and_Role_Architecture.md) | `250 XP` |
| **02** | **40** | **Capabilities & Search Filters** | `srchIndexesAllowed`, `srchIndexesDefault`, `srchFilter` index row isolation | [Room P5-02: The Search Filter Sandbox Trap](../Labs/Room_P5_02_Capabilities_and_Search_Filters.md) | `250 XP` |
| **03** | **41** | **Native Auth & CLI/REST Mgmt** | `passwd`, `splunk edit user`, REST API `/services/authentication/users` | [Room P5-03: The Admin Shadow Provisioner](../Labs/Room_P5_03_Native_Auth_and_REST_User_Mgmt.md) | `200 XP` |
| **04** | **42** | **LDAP & Active Directory** | `authentication.conf`, AD group-to-role mappings, multi-domain failover | [Room P5-04: Active Directory Forest Synchronization](../Labs/Room_P5_04_LDAP_Active_Directory_Integration.md) | `300 XP` |
| **05** | **43** | **SAML 2.0 SSO Integration** | Okta / Azure AD integration, SP metadata, IdP certificate verification | [Room P5-05: The SAML Identity Federation Breakout](../Labs/Room_P5_05_SAML_SSO_Federation.md) | `300 XP` |
| **06** | **44** | **Securing Splunk (TLS/mTLS)** | Web UI HTTPS, S2S encryption port 9997, UF-to-IDX mutual TLS, CA certs | [Room P5-06: The S2S Man-in-the-Middle Defense](../Labs/Room_P5_06_Securing_Splunk_Communications_TLS.md) | `350 XP` |
| **07** | **45** | **Hardening & Compliance Auditing** | CIS benchmark hardening, port lockdown, CLI access security, `_audit` | [Room P5-07: The Fortress Hardening Audit](../Labs/Room_P5_07_Splunk_Hardening_and_Audit_Forensics.md) | `300 XP` |
| **08** | **46** | **Phase 5 Capstone Lab & Exam** | Enterprise RBAC, SAML, mTLS PKI rollout, 10 Master Milestone Scenarios | [Room P5-Capstone: Enterprise Security Architecture Gauntlet](../Labs/Room_P5_Capstone_Enterprise_Security_Architecture.md) | `500 XP` |

---

## 🏆 Phase 5 Graduation Criteria & Operator Rank

```text
╔══════════════════════════════════════════════════════════════════════════╗
║               PHASE 5 OPERATOR PROMOTION MILESTONES                      ║
╠══════════════════════════════════════════════════════════════════════════╣
║ • Starting Rank:    Master Splunk Architect (6,550 XP)                   ║
║ • Phase 5 Points:   +2,450 XP (8 Cyber Range Rooms + Capstone Exam)      ║
║ • Promotion Target: Splunk Security & Cryptographic Architect (9,000 XP) ║
║ • Certification:    Splunk Certified Enterprise Security Administrator   ║
╚══════════════════════════════════════════════════════════════════════════╝
```
